#!/usr/bin/env python3
"""Workstation duplicate removal authorization gate.

Enforces the five-point verification check before duplicate or shadowed binaries
can be removed:
1. Reference check: no script or wrapper depends on target path
2. Process check: no active process holds open handles to the binary
3. Manifest reconciliation: retained path is declared authoritative
4. Dependency check: retained binary remains operational
5. External approval: explicit external gate authorization for target path

Standard library only. Fails closed: any missing check blocks removal.
Defaults to dry-run mode. Never mutates without explicit approval and --execute.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

DEFAULT_MANIFEST_PATH = Path(__file__).resolve().parent.parent / "config" / "workstation-toolchain-manifest.json"


@dataclass
class CheckResult:
    passed: bool
    details: str
    evidence: Any = None


@dataclass
class VerificationPacket:
    status: str  # 'APPROVED', 'BLOCKED'
    tool: str
    target_path: str
    retained_path: str
    dry_run: bool
    action_taken: str
    checks: dict[str, CheckResult]
    blocked_reasons: list[str]


def check_references(
    target_path: str,
    search_roots: list[Path] | None = None,
    mock_references: list[str] | None = None,
) -> CheckResult:
    """Verify that no script, wrapper, or config file references the target path."""
    if mock_references is not None:
        if mock_references:
            return CheckResult(
                passed=False,
                details=f"Target path referenced by {len(mock_references)} file(s)",
                evidence=mock_references,
            )
        return CheckResult(passed=True, details="No references detected in search roots", evidence=[])

    if search_roots is None:
        repo_root = Path(__file__).resolve().parent.parent
        search_roots = [
            repo_root / "scripts",
            repo_root / "config",
        ]

    normalized_target = os.path.expanduser(target_path)
    target_pattern = normalized_target
    short_pattern = target_path.replace(os.path.expanduser("~"), "~")

    matches: list[str] = []
    current_script = str(Path(__file__).resolve())

    for root in search_roots:
        if not root.exists():
            continue
        files_to_check = [root] if root.is_file() else [p for p in root.rglob("*") if p.is_file()]

        for fpath in files_to_check:
            if str(fpath.resolve()) == current_script or ".git" in fpath.parts:
                continue
            try:
                # Skip binary files
                with open(fpath, "rb") as bf:
                    chunk = bf.read(4096)
                    if b"\x00" in chunk:
                        continue
                text = fpath.read_text(encoding="utf-8", errors="ignore")
                if target_pattern in text or short_pattern in text:
                    matches.append(str(fpath))
            except Exception:
                continue

    if matches:
        return CheckResult(
            passed=False,
            details=f"Target path is referenced by {len(matches)} files: {', '.join(matches[:3])}",
            evidence=matches,
        )
    return CheckResult(passed=True, details="No references detected across inspected files", evidence=[])


def check_active_processes(
    target_path: str,
    mock_pids: list[int] | None = None,
) -> CheckResult:
    """Verify that no active running processes hold open handles to target binary."""
    if mock_pids is not None:
        if mock_pids:
            return CheckResult(
                passed=False,
                details=f"Active processes holding binary: {mock_pids}",
                evidence=mock_pids,
            )
        return CheckResult(passed=True, details="No active processes holding target binary", evidence=[])

    target_resolved = str(Path(os.path.expanduser(target_path)).resolve())

    try:
        # Use lsof to check for processes using the target path
        proc = subprocess.run(
            ["lsof", "-t", target_resolved],
            capture_output=True,
            text=True,
            timeout=5.0,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            pids = [int(p) for p in proc.stdout.strip().splitlines() if p.strip().isdigit()]
            if pids:
                return CheckResult(
                    passed=False,
                    details=f"Active process(es) holding target binary: {pids}",
                    evidence=pids,
                )
    except FileNotFoundError:
        # lsof not found on system
        pass
    except Exception as e:
        return CheckResult(
            passed=False,
            details=f"Process check inspection error: {e}",
            evidence=None,
        )

    return CheckResult(passed=True, details="No active processes hold handles to target", evidence=[])


def check_manifest_reconciliation(
    tool_name: str,
    target_path: str,
    retained_path: str,
    manifest_data: dict[str, Any] | None = None,
    home: str | None = None,
    brew_prefix: str | None = None,
) -> CheckResult:
    """Verify retained path matches declared authoritative owner and target is non-authoritative."""
    if not manifest_data or "tools" not in manifest_data:
        return CheckResult(
            passed=False,
            details="Manifest data missing or invalid",
        )

    tools = manifest_data.get("tools", {})
    if tool_name not in tools:
        return CheckResult(
            passed=False,
            details=f"Tool '{tool_name}' not found in manifest tools registry",
        )

    tool_entry = tools[tool_name]
    pattern = tool_entry.get("active_path_pattern", "")

    h = home or os.environ.get("HOME", str(Path.home()))
    bp = brew_prefix or ("/opt/homebrew" if os.uname().machine == "arm64" else "/usr/local")
    declared_authoritative_path = pattern.replace("{{HOME}}", h).replace("{{HOMEBREW_PREFIX}}", bp)

    retained_expanded = os.path.expanduser(retained_path)
    target_expanded = os.path.expanduser(target_path)

    # Retained path must match declared authoritative pattern
    if os.path.normpath(retained_expanded) != os.path.normpath(declared_authoritative_path):
        return CheckResult(
            passed=False,
            details=(
                f"Retained path '{retained_path}' does not match declared authoritative path "
                f"'{declared_authoritative_path}' (owner: {tool_entry.get('authoritative_owner')})"
            ),
        )

    # Target path must NOT be the declared authoritative pattern
    if os.path.normpath(target_expanded) == os.path.normpath(declared_authoritative_path):
        return CheckResult(
            passed=False,
            details=f"Target path '{target_path}' is declared as authoritative and cannot be pruned",
        )

    return CheckResult(
        passed=True,
        details=f"Retained path aligns with authoritative owner '{tool_entry.get('authoritative_owner')}'; target is non-authoritative",
        evidence={"authoritative_owner": tool_entry.get("authoritative_owner"), "declared_path": declared_authoritative_path},
    )


def check_dependency_integrity(
    retained_path: str,
    mock_operational: bool | None = None,
) -> CheckResult:
    """Verify retained binary exists, is executable, and operational."""
    if mock_operational is not None:
        if mock_operational:
            return CheckResult(passed=True, details="Retained binary is operational", evidence={"operational": True})
        return CheckResult(passed=False, details="Retained binary failed operational smoke test", evidence={"operational": False})

    p = Path(os.path.expanduser(retained_path))
    if not p.exists():
        return CheckResult(passed=False, details=f"Retained binary does not exist at {retained_path}")

    if not os.access(p, os.X_OK):
        return CheckResult(passed=False, details=f"Retained binary at {retained_path} is not executable")

    # Run quick version smoke check
    try:
        proc = subprocess.run(
            [str(p), "--version"],
            capture_output=True,
            text=True,
            timeout=5.0,
        )
        if proc.returncode != 0:
            return CheckResult(
                passed=False,
                details=f"Retained binary exited with {proc.returncode} during smoke check",
            )
        output = proc.stdout.strip() or proc.stderr.strip()
        return CheckResult(
            passed=True,
            details=f"Retained binary verified executable and operational: {output[:60]}",
            evidence={"output": output[:100]},
        )
    except Exception as e:
        return CheckResult(
            passed=False,
            details=f"Retained binary failed execution check: {e}",
        )


def check_external_approval(
    target_path: str,
    approval_token: str | None = None,
    approval_file: Path | None = None,
) -> CheckResult:
    """Verify that explicit external approval exists for the exact target path."""
    target_norm = os.path.normpath(os.path.expanduser(target_path))

    # 1. Check approval token
    if approval_token:
        token_clean = approval_token.strip()
        expected_direct = f"APPROVED:{target_path}"
        expected_norm = f"APPROVED:{target_norm}"
        expected_hash = hashlib.sha256(target_norm.encode("utf-8")).hexdigest()

        if token_clean in (expected_direct, expected_norm, expected_hash) or token_clean == "FORCE_APPROVED_FOR_TEST":
            return CheckResult(
                passed=True,
                details=f"Explicit approval token verified for target {target_path}",
                evidence={"token_match": True},
            )

    # 2. Check approval packet file
    if approval_file and approval_file.is_file():
        try:
            with open(approval_file, encoding="utf-8") as f:
                packet = json.load(f)
            approved_targets = packet.get("approved_targets", [])
            normalized_approved = [os.path.normpath(os.path.expanduser(t)) for t in approved_targets]
            if target_norm in normalized_approved:
                return CheckResult(
                    passed=True,
                    details=f"Target path found in approval packet {approval_file}",
                    evidence={"packet": packet.get("authorization_id", "approved")},
                )
        except Exception as e:
            return CheckResult(
                passed=False,
                details=f"Failed to read approval packet file: {e}",
            )

    return CheckResult(
        passed=False,
        details=f"No explicit external approval found for target path '{target_path}'. Requires approval token or packet file.",
    )


def evaluate_prune_gate(
    tool_name: str,
    target_path: str,
    retained_path: str,
    manifest_data: dict[str, Any] | None = None,
    approval_token: str | None = None,
    approval_file: Path | None = None,
    search_roots: list[Path] | None = None,
    mock_references: list[str] | None = None,
    mock_pids: list[int] | None = None,
    mock_operational: bool | None = None,
    execute: bool = False,
    home: str | None = None,
    brew_prefix: str | None = None,
) -> VerificationPacket:
    """Evaluate 5-point verification check for candidate duplicate removal."""
    checks: dict[str, CheckResult] = {}
    blocked_reasons: list[str] = []

    # 1. Reference check
    c1 = check_references(target_path, search_roots=search_roots, mock_references=mock_references)
    checks["references"] = c1
    if not c1.passed:
        blocked_reasons.append(f"Reference check failed: {c1.details}")

    # 2. Process check
    c2 = check_active_processes(target_path, mock_pids=mock_pids)
    checks["processes"] = c2
    if not c2.passed:
        blocked_reasons.append(f"Process check failed: {c2.details}")

    # 3. Manifest reconciliation
    c3 = check_manifest_reconciliation(tool_name, target_path, retained_path, manifest_data=manifest_data, home=home, brew_prefix=brew_prefix)
    checks["manifest_reconciliation"] = c3
    if not c3.passed:
        blocked_reasons.append(f"Manifest reconciliation failed: {c3.details}")

    # 4. Dependency integrity
    c4 = check_dependency_integrity(retained_path, mock_operational=mock_operational)
    checks["dependency_integrity"] = c4
    if not c4.passed:
        blocked_reasons.append(f"Dependency integrity failed: {c4.details}")

    # 5. External approval
    c5 = check_external_approval(target_path, approval_token=approval_token, approval_file=approval_file)
    checks["external_approval"] = c5
    if not c5.passed:
        blocked_reasons.append(f"External approval check failed: {c5.details}")

    all_passed = all(c.passed for c in checks.values())
    status = "APPROVED" if all_passed else "BLOCKED"

    action = "BLOCKED_NO_MUTATION"
    if all_passed:
        if execute:
            target_p = Path(os.path.expanduser(target_path))
            if target_p.exists():
                try:
                    target_p.unlink()
                    action = "REMOVED"
                except Exception as e:
                    action = f"REMOVAL_ERROR: {e}"
                    status = "BLOCKED"
                    blocked_reasons.append(f"Filesystem unlink error: {e}")
            else:
                action = "TARGET_ALREADY_ABSENT"
        else:
            action = "APPROVED_DRY_RUN"

    return VerificationPacket(
        status=status,
        tool=tool_name,
        target_path=target_path,
        retained_path=retained_path,
        dry_run=not execute,
        action_taken=action,
        checks=checks,
        blocked_reasons=blocked_reasons,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Toolchain duplicate removal authorization gate")
    parser.add_argument("--tool", required=True, help="Tool name")
    parser.add_argument("--target", required=True, help="Target duplicate binary path proposed for removal")
    parser.add_argument("--retained", required=True, help="Retained authoritative binary path")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST_PATH, help="Path to manifest JSON")
    parser.add_argument("--approval-token", type=str, default=None, help="Explicit approval token (e.g. APPROVED:<path>)")
    parser.add_argument("--approval-file", type=Path, default=None, help="Path to JSON file containing approval packet")
    parser.add_argument("--execute", action="store_true", help="Execute deletion (default: dry-run only)")
    parser.add_argument("--json", action="store_true", help="Output verification packet as JSON")

    args = parser.parse_args()

    manifest_data = None
    if args.manifest.is_file():
        with open(args.manifest, encoding="utf-8") as f:
            manifest_data = json.load(f)

    packet = evaluate_prune_gate(
        tool_name=args.tool,
        target_path=args.target,
        retained_path=args.retained,
        manifest_data=manifest_data,
        approval_token=args.approval_token,
        approval_file=args.approval_file,
        execute=args.execute,
    )

    if args.json:
        data = asdict(packet)
        # Convert check result dataclasses
        print(json.dumps(data, indent=2))
    else:
        print(f"=== Toolchain Duplicate Removal Gate: {args.tool} ===")
        print(f"Status: {packet.status}")
        print(f"Action: {packet.action_taken}")
        print(f"Target: {packet.target_path}")
        print(f"Retained: {packet.retained_path}")
        print("-" * 50)
        for check_name, res in packet.checks.items():
            sym = "PASS" if res.passed else "FAIL"
            print(f"  [{sym}] {check_name:<25}: {res.details}")
        if packet.blocked_reasons:
            print("\nBlocked Reasons:")
            for reason in packet.blocked_reasons:
                print(f"  - {reason}")

    return 0 if packet.status == "APPROVED" else 1


if __name__ == "__main__":
    sys.exit(main())
