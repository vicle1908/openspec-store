#!/usr/bin/env python3
"""External Execution Packet Generator and Validator.

Generates and validates structured External Execution Packets (EEPs) governing operations
executed outside the central store (e.g. host roots, launchd plists, package managers, Notion,
AgentMemory).

Standard library only. Value-blind by contract: never stores or emits unredacted secrets.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"

# Standard mandatory exclusions for safe external operations
DEFAULT_EXCLUSIONS = [
    ".env",
    "*.pem",
    "*.key",
    "id_rsa*",
    "id_ed25519*",
    "omniroute_data",
    "docker_volumes",
    "credentials",
    "secrets",
]

SECRET_PATTERNS = [
    r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----",
    r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{16,}\b",
    r"\bsk-[A-Za-z0-9_-]{20,}\b",
    r"\bsk-ant-[A-Za-z0-9_-]{20,}\b",
    r"\bAIza[0-9A-Za-z\-_]{35}\b",
]

VALID_STATUSES = {"COMPLETED", "FAILED", "BLOCKED", "PENDING"}


@dataclass
class PacketTimestamps:
    started_at: str
    completed_at: str
    duration_seconds: float = 0.0


@dataclass
class ItemCounts:
    inspected: int = 0
    modified: int = 0
    created: int = 0
    pruned: int = 0
    retained: int = 0
    skipped: int = 0


@dataclass
class PreservationStatus:
    source_preserved: bool = True
    backup_path: str | None = None
    details: str = "Source state preserved without data loss"


@dataclass
class CollisionStatus:
    collision_detected: bool = False
    quarantined_pids: list[int] = field(default_factory=list)
    details: str = "No port or filesystem collisions detected"


@dataclass
class ReadbackVerification:
    verified: bool = True
    status: str = "PASSED"
    active_version: str | None = None
    readback_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class AuthorizationScope:
    scope_authorized: bool = False
    approved_by: str = ""
    approval_token_or_reason: str = ""
    target_root_approved: bool = False


@dataclass
class ExternalExecutionPacket:
    schema_version: str
    packet_id: str
    target_root: str
    source_commit: str
    command: str | list[str]
    timestamps: PacketTimestamps
    exit_code: int
    item_counts: ItemCounts
    preservation_status: PreservationStatus
    collision_status: CollisionStatus
    readback_verification: ReadbackVerification
    evidence_hashes: dict[str, str]
    exclusions: list[str]
    authorization: AuthorizationScope
    status: str


def _resolve_source_commit() -> str:
    """Resolve current git commit SHA if in a repository, else return fallback."""
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if out:
            return out
    except Exception:
        pass
    return "0000000000000000000000000000000000000000"


def _parse_iso(ts_str: str) -> datetime.datetime | None:
    """Parse ISO 8601 timestamp string into datetime."""
    if not ts_str:
        return None
    # Replace Z with +00:00 for python fromisoformat
    clean = ts_str.replace("Z", "+00:00")
    try:
        return datetime.datetime.fromisoformat(clean)
    except Exception:
        return None


def create_packet(
    target_root: str,
    source_commit: str | None = None,
    command: str | list[str] = "",
    started_at: str | None = None,
    completed_at: str | None = None,
    exit_code: int = 0,
    item_counts: dict[str, int] | None = None,
    source_preserved: bool = True,
    backup_path: str | None = None,
    preservation_details: str = "Source state preserved",
    collision_detected: bool = False,
    quarantined_pids: list[int] | None = None,
    collision_details: str = "No collisions detected",
    readback_verified: bool = True,
    readback_status: str = "PASSED",
    active_version: str | None = None,
    readback_data: dict[str, Any] | None = None,
    evidence_hashes: dict[str, str] | None = None,
    exclusions: list[str] | None = None,
    scope_authorized: bool = False,
    approved_by: str = "",
    approval_token_or_reason: str = "",
    target_root_approved: bool = False,
    status: str | None = None,
    packet_id: str | None = None,
) -> dict[str, Any]:
    """Create a structured External Execution Packet dictionary."""
    commit = source_commit or _resolve_source_commit()

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_iso = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")

    t_start_str = started_at or now_iso
    t_end_str = completed_at or now_iso

    dt_start = _parse_iso(t_start_str) or now_utc
    dt_end = _parse_iso(t_end_str) or now_utc
    duration = max(0.0, (dt_end - dt_start).total_seconds())

    if not packet_id:
        h = hashlib.sha256(f"{target_root}:{commit}:{t_start_str}:{command}".encode()).hexdigest()[:12]
        packet_id = f"eep-{dt_start.strftime('%Y%m%d-%H%M%S')}-{h}"

    # Determine status if not explicitly given
    if status is None:
        if not scope_authorized:
            status = "BLOCKED"
        elif exit_code != 0:
            status = "FAILED"
        else:
            status = "COMPLETED"

    counts = ItemCounts()
    if item_counts:
        counts.inspected = int(item_counts.get("inspected", 0))
        counts.modified = int(item_counts.get("modified", 0))
        counts.created = int(item_counts.get("created", 0))
        counts.pruned = int(item_counts.get("pruned", 0))
        counts.retained = int(item_counts.get("retained", 0))
        counts.skipped = int(item_counts.get("skipped", 0))

    final_exclusions = list(exclusions) if exclusions is not None else list(DEFAULT_EXCLUSIONS)

    packet = ExternalExecutionPacket(
        schema_version=SCHEMA_VERSION,
        packet_id=packet_id,
        target_root=str(target_root),
        source_commit=str(commit),
        command=command,
        timestamps=PacketTimestamps(
            started_at=t_start_str,
            completed_at=t_end_str,
            duration_seconds=duration,
        ),
        exit_code=int(exit_code),
        item_counts=counts,
        preservation_status=PreservationStatus(
            source_preserved=bool(source_preserved),
            backup_path=backup_path,
            details=preservation_details,
        ),
        collision_status=CollisionStatus(
            collision_detected=bool(collision_detected),
            quarantined_pids=list(quarantined_pids or []),
            details=collision_details,
        ),
        readback_verification=ReadbackVerification(
            verified=bool(readback_verified),
            status=readback_status,
            active_version=active_version,
            readback_data=dict(readback_data or {}),
        ),
        evidence_hashes=dict(evidence_hashes or {}),
        exclusions=final_exclusions,
        authorization=AuthorizationScope(
            scope_authorized=bool(scope_authorized),
            approved_by=str(approved_by),
            approval_token_or_reason=str(approval_token_or_reason),
            target_root_approved=bool(target_root_approved),
        ),
        status=status,
    )

    return asdict(packet)


def validate_packet(packet_input: dict[str, Any] | str | Path) -> tuple[bool, list[str]]:
    """Validate that an External Execution Packet conforms to the required contract.

    Returns (is_valid, error_messages).
    """
    errors: list[str] = []

    if isinstance(packet_input, (str, Path)):
        if isinstance(packet_input, str) and (packet_input.strip().startswith("{") or "\n" in packet_input):
            try:
                packet = json.loads(packet_input)
            except Exception as e:
                return False, [f"Invalid JSON payload: {e}"]
        else:
            path = Path(packet_input)
            if not path.is_file():
                return False, [f"Packet file not found: {path}"]
            try:
                with open(path, "r", encoding="utf-8") as f:
                    packet = json.load(f)
            except Exception as e:
                return False, [f"Failed to read packet file {path}: {e}"]
    elif isinstance(packet_input, dict):
        packet = packet_input
    else:
        return False, [f"Invalid packet input type: {type(packet_input)}"]

    # 1. Schema version
    if packet.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"Invalid schema_version '{packet.get('schema_version')}'; expected '{SCHEMA_VERSION}'")

    # 2. Packet ID
    if not packet.get("packet_id") or not isinstance(packet.get("packet_id"), str):
        errors.append("Missing or invalid packet_id")

    # 3. Target root
    target_root = packet.get("target_root")
    if not target_root or not isinstance(target_root, str):
        errors.append("Missing or invalid target_root")
    elif not (target_root.startswith("/") or target_root.startswith("~")):
        errors.append(f"target_root must be an absolute path or home-relative path: '{target_root}'")

    # 4. Source commit
    commit = packet.get("source_commit")
    if not commit or not isinstance(commit, str) or len(commit) < 7:
        errors.append(f"Missing or invalid source_commit: '{commit}'")

    # 5. Command
    cmd = packet.get("command")
    if not cmd or (isinstance(cmd, (str, list)) and len(cmd) == 0):
        errors.append("Missing bounded execution command")

    # 6. Timestamps
    ts = packet.get("timestamps")
    if not isinstance(ts, dict):
        errors.append("Missing timestamps object")
    else:
        dt_start = _parse_iso(ts.get("started_at", ""))
        dt_end = _parse_iso(ts.get("completed_at", ""))
        if not dt_start:
            errors.append(f"Invalid started_at timestamp: '{ts.get('started_at')}'")
        if not dt_end:
            errors.append(f"Invalid completed_at timestamp: '{ts.get('completed_at')}'")
        if dt_start and dt_end and dt_end < dt_start:
            errors.append("completed_at precedes started_at timestamp")

    # 7. Exit code
    if not isinstance(packet.get("exit_code"), int):
        errors.append(f"exit_code must be an integer, got: {type(packet.get('exit_code'))}")

    # 8. Item counts
    counts = packet.get("item_counts")
    if not isinstance(counts, dict):
        errors.append("Missing item_counts object")
    else:
        for k in ("inspected", "modified", "created", "pruned", "retained", "skipped"):
            if k in counts and not isinstance(counts[k], int):
                errors.append(f"item_counts.{k} must be an integer")

    # 9. Preservation status
    pres = packet.get("preservation_status")
    if not isinstance(pres, dict):
        errors.append("Missing preservation_status object")
    elif "source_preserved" not in pres or not isinstance(pres["source_preserved"], bool):
        errors.append("preservation_status.source_preserved must be a boolean")

    # 10. Collision status
    coll = packet.get("collision_status")
    if not isinstance(coll, dict):
        errors.append("Missing collision_status object")
    elif "collision_detected" not in coll or not isinstance(coll["collision_detected"], bool):
        errors.append("collision_status.collision_detected must be a boolean")

    # 11. Readback verification
    rb = packet.get("readback_verification")
    if not isinstance(rb, dict):
        errors.append("Missing readback_verification object")
    elif "verified" not in rb or not isinstance(rb["verified"], bool):
        errors.append("readback_verification.verified must be a boolean")

    # 12. Exclusions
    exclusions = packet.get("exclusions")
    if not isinstance(exclusions, list) or len(exclusions) == 0:
        errors.append("Missing or empty exclusions list; must explicitly exclude secrets and protected volumes")
    else:
        excl_str = " ".join(str(e).lower() for e in exclusions)
        has_secret_excl = any(s in excl_str for s in [".env", "secret", "key", "credential", "pem"])
        has_vol_excl = any(v in excl_str for v in ["volume", "omniroute_data", "docker"])
        if not has_secret_excl:
            errors.append("exclusions list must include secret/key exclusion patterns (.env, credentials)")
        if not has_vol_excl:
            errors.append("exclusions list must include protected volume patterns (docker_volumes, omniroute_data)")

    # 13. Evidence hashes
    hashes = packet.get("evidence_hashes")
    if not isinstance(hashes, dict):
        errors.append("evidence_hashes must be a dictionary")

    # 14. Authorization & Status Gate
    auth = packet.get("authorization")
    status = packet.get("status")
    if status not in VALID_STATUSES:
        errors.append(f"Invalid status '{status}'; must be one of {sorted(VALID_STATUSES)}")

    if not isinstance(auth, dict):
        errors.append("Missing authorization object")
    else:
        scope_authorized = auth.get("scope_authorized", False)
        if not isinstance(scope_authorized, bool):
            errors.append("authorization.scope_authorized must be a boolean")
        elif not scope_authorized:
            if status == "COMPLETED":
                errors.append(
                    "Scope authorization missing: action lacks explicit scope authorization; status cannot be COMPLETED"
                )

    # 15. Value-blind secret scan
    raw_str = json.dumps(packet)
    for pat in SECRET_PATTERNS:
        if re.search(pat, raw_str):
            errors.append(f"Packet contains unredacted credential or private key matching pattern '{pat}'")

    return len(errors) == 0, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or validate External Execution Packets (EEPs).")
    subparsers = parser.add_subparsers(dest="subcommand", help="Subcommand: create or validate")

    # Create subcommand
    create_p = subparsers.add_parser("create", help="Generate an External Execution Packet")
    create_p.add_argument("--target-root", required=True, help="Target host root path (e.g. /opt/homebrew, ~/.npm-global)")
    create_p.add_argument("--source-commit", help="Source git commit SHA (auto-detected if omitted)")
    create_p.add_argument("--command", required=True, help="Bounded execution command")
    create_p.add_argument("--exit-code", type=int, default=0, help="Process exit code (default: 0)")
    create_p.add_argument("--started-at", help="Start timestamp ISO 8601 UTC")
    create_p.add_argument("--completed-at", help="End timestamp ISO 8601 UTC")
    create_p.add_argument("--scope-authorized", action="store_true", help="Assert explicit scope authorization")
    create_p.add_argument("--approved-by", default="", help="Identifier of approving operator")
    create_p.add_argument("--approval-reason", default="", help="Approval token or justification reason")
    create_p.add_argument("--target-root-approved", action="store_true", help="Explicit confirmation of target root")
    create_p.add_argument("--inspected", type=int, default=0, help="Inspected items count")
    create_p.add_argument("--modified", type=int, default=0, help="Modified items count")
    create_p.add_argument("--created", type=int, default=0, help="Created items count")
    create_p.add_argument("--pruned", type=int, default=0, help="Pruned items count")
    create_p.add_argument("--retained", type=int, default=0, help="Retained items count")
    create_p.add_argument("--no-source-preserved", action="store_true", help="Flag if source was not preserved")
    create_p.add_argument("--preservation-details", default="Source state preserved", help="Preservation details")
    create_p.add_argument("--collision-detected", action="store_true", help="Flag if collision occurred")
    create_p.add_argument("--collision-details", default="No collisions detected", help="Collision details")
    create_p.add_argument("--readback-status", default="PASSED", help="Readback verification status")
    create_p.add_argument("--active-version", help="Active executable version readback")
    create_p.add_argument("--evidence-hash", action="append", default=[], help="Evidence hash in KEY=HASH format")
    create_p.add_argument("--exclusion", action="append", default=[], help="Additional exclusion pattern")
    create_p.add_argument("--status", choices=sorted(VALID_STATUSES), help="Explicit packet status")
    create_p.add_argument("--output", "-o", help="Output JSON path (stdout if omitted)")

    # Validate subcommand
    val_p = subparsers.add_parser("validate", help="Validate an External Execution Packet")
    val_p.add_argument("packet_file", nargs="?", help="Path to packet JSON file or JSON string")
    val_p.add_argument("--file", "-f", help="Path to packet JSON file")
    val_p.add_argument("--strict", action="store_true", help="Exit 1 on validation error")

    args = parser.parse_args()

    if args.subcommand == "create":
        evidence_hashes: dict[str, str] = {}
        for eh in args.evidence_hash:
            if "=" in eh:
                k, v = eh.split("=", 1)
                evidence_hashes[k.strip()] = v.strip()

        exclusions = list(DEFAULT_EXCLUSIONS)
        if args.exclusion:
            exclusions.extend(args.exclusion)

        counts = {
            "inspected": args.inspected,
            "modified": args.modified,
            "created": args.created,
            "pruned": args.pruned,
            "retained": args.retained,
            "skipped": 0,
        }

        packet = create_packet(
            target_root=args.target_root,
            source_commit=args.source_commit,
            command=args.command,
            started_at=args.started_at,
            completed_at=args.completed_at,
            exit_code=args.exit_code,
            item_counts=counts,
            source_preserved=not args.no_source_preserved,
            preservation_details=args.preservation_details,
            collision_detected=args.collision_detected,
            collision_details=args.collision_details,
            readback_verified=True,
            readback_status=args.readback_status,
            active_version=args.active_version,
            evidence_hashes=evidence_hashes,
            exclusions=exclusions,
            scope_authorized=args.scope_authorized,
            approved_by=args.approved_by,
            approval_token_or_reason=args.approval_reason,
            target_root_approved=args.target_root_approved,
            status=args.status,
        )

        valid, errors = validate_packet(packet)
        if not valid:
            print(f"ERROR: Generated packet failed internal validation: {errors}", file=sys.stderr)
            return 1

        json_text = json.dumps(packet, indent=2)
        if args.output:
            out_p = Path(args.output)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            out_p.write_text(json_text + "\n", encoding="utf-8")
        else:
            print(json_text)
        return 0

    elif args.subcommand == "validate":
        target = args.file or args.packet_file
        if not target:
            print("ERROR: Must provide packet JSON file or payload to validate", file=sys.stderr)
            return 1
        if target == "-":
            target = sys.stdin.read()
        valid, errors = validate_packet(target)
        if valid:
            print("External Execution Packet: VALID (conforms to schema and contract)")
            return 0
        else:
            print("External Execution Packet: INVALID", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            return 1

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
