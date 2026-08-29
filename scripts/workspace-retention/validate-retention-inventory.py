#!/usr/bin/env python3
"""Validate and load the workspace artifact retention inventory.

This is the read-only producer/loader for the retention policy handoff defined
by the `workspace-artifact-retention-policy` OpenSpec change (design.md
Decisions 8 and 9). It enforces the machine-readable inventory schema, the
approval digest, and provenance freshness, and it derives the cleanup handoff
(exclusion list + review proposals). It NEVER deletes, relocates, or mutates
any retained path, and it NEVER reads or records credential values.

Behavior mapped to change tasks:

- Task 2.1 (schema): rejects a missing policy identity, any secret or
  request/response-body field, and a structurally malformed provenance.
- Task 2.2 (store/load): loads the operational inventory, preserves the policy
  identity, and rejects an unapproved (digest mismatch) or malformed document.
- Task 2.3 (freshness): downgrades an entry whose provenance is stale or
  missing to ``REVIEW_REQUIRED``. Staleness is determined by provenance type:

    repo_revision       -> recorded revision must match the current git HEAD
    evidence_identity   -> referenced evidence artifact must exist
    runtime_observation -> observed_at must be present, parseable, not future

- Task 3.1 (exclusion handoff): emits ``exclusions`` — every effective
  ``PROTECTED`` entry with a recorded class + owner reason cleanup SHALL honor.
- Task 3.2 (review-only candidates): emits ``review_proposals`` — reclamation
  candidates proposed for operator review, never auto-deleted (this tool is
  read-only and performs no filesystem mutation).
- Task 4.2 (adapter fail-closed): an entry whose owner is ``UNKNOWN`` (for
  example an unavailable LaunchAgent or container adapter) can never be
  ``RECLAIMABLE``/``RECLAIMED``; it is downgraded to ``REVIEW_REQUIRED``.

Exit codes:
  0  schema valid and approved (freshness downgrades are reported, not fatal)
  1  schema validation failed (missing identity / forbidden field / malformed)
  2  approval check failed (digest mismatch or missing approval file)
  3  inventory file missing or unreadable
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

POLICY_NAME = "workspace-artifact-retention-policy"

RETENTION_CLASSES = {
    "active index state",
    "generated index or cache",
    "tracked permanent fixture",
    "temporary or ephemeral test fixture",
    "runtime state or database",
    "retained evidence or report",
    "retained rollback or snapshot",
    "operator-owned preserved file",
}

POLICY_STATES = {"PROTECTED", "REVIEW_REQUIRED", "RECLAIMABLE", "RECLAIMED"}

PROVENANCE_TYPES = {"repo_revision", "evidence_identity", "runtime_observation"}

# Field names that must never appear anywhere in a retention record. Their
# presence is a schema violation (task 2.1) because credentials and
# request/response bodies are explicit non-goals of the policy.
FORBIDDEN_KEYS = {
    "secret", "secrets", "password", "passwd", "token", "access_token",
    "api_key", "apikey", "credential", "credentials", "private_key",
    "request_body", "response_body", "authorization", "cookie", "session_token",
}

EXIT_OK = 0
EXIT_SCHEMA = 1
EXIT_UNAPPROVED = 2
EXIT_MISSING = 3


def expand(path: str) -> str:
    return str(Path(path).expanduser())


def parse_iso(value: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_head(path: str) -> str | None:
    """Return the current HEAD revision for the repository containing path.

    Read-only. Returns None when git is unavailable or the path is not inside
    a repository; callers fail closed toward REVIEW_REQUIRED.
    """
    target = Path(expand(path))
    target = target if target.is_dir() else target.parent
    if not target.exists():
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(target), "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=15,
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None
    revision = result.stdout.strip()
    return revision or None


def find_forbidden(node, trail: str = "$") -> list[str]:
    """Recursively report any forbidden key names in the document."""
    violations: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if str(key).lower() in FORBIDDEN_KEYS:
                violations.append(f"forbidden field '{key}' at {trail}")
            violations.extend(find_forbidden(value, f"{trail}.{key}"))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            violations.extend(find_forbidden(value, f"{trail}[{index}]"))
    return violations


def _nonempty_str(value) -> bool:
    return isinstance(value, str) and value.strip() != ""


def validate_schema(doc) -> list[str]:
    """Structural validation (task 2.1). Returns a list of error strings."""
    errors: list[str] = []

    if not isinstance(doc, dict):
        return ["inventory document must be a JSON object"]

    errors.extend(find_forbidden(doc))

    # Policy identity is required.
    if doc.get("policy") != POLICY_NAME:
        errors.append(
            f"policy must be '{POLICY_NAME}', got {doc.get('policy')!r}"
        )
    if not _nonempty_str(doc.get("policy_version")):
        errors.append("missing identity: policy_version is required")
    if not _nonempty_str(doc.get("policy_identity")):
        errors.append("missing identity: policy_identity is required")

    generated_at = doc.get("generated_at")
    if not _nonempty_str(generated_at):
        errors.append("generated_at is required")
    else:
        try:
            parse_iso(generated_at)
        except Exception:
            errors.append("generated_at is not a valid ISO8601 timestamp")

    approval = doc.get("approval")
    if not isinstance(approval, dict):
        errors.append("approval must be an object")
    else:
        if not isinstance(approval.get("approved"), bool):
            errors.append("approval.approved must be a boolean")
        if not _nonempty_str(approval.get("digest")):
            errors.append("approval.digest is required")
        if not _nonempty_str(approval.get("approved_at")):
            errors.append("approval.approved_at is required")
        if not _nonempty_str(approval.get("approved_by")):
            errors.append("approval.approved_by is required")

    entries = doc.get("entries")
    if not isinstance(entries, list):
        errors.append("entries must be a list")
        return errors

    for i, entry in enumerate(entries):
        prefix = f"entries[{i}]"
        if not isinstance(entry, dict):
            errors.append(f"{prefix} must be an object")
            continue
        if not _nonempty_str(entry.get("path")):
            errors.append(f"{prefix}.path is required")
        if entry.get("class") not in RETENTION_CLASSES:
            errors.append(f"{prefix}.class is not a reviewed retention class")
        if entry.get("policy_state") not in POLICY_STATES:
            errors.append(f"{prefix}.policy_state is not a valid policy state")
        if not _nonempty_str(entry.get("owner")):
            errors.append(f"{prefix}.owner is required")
        if not _nonempty_str(entry.get("justification")):
            errors.append(f"{prefix}.justification is required")
        if not isinstance(entry.get("candidate"), bool):
            errors.append(f"{prefix}.candidate must be a boolean")

        provenance = entry.get("provenance")
        if not isinstance(provenance, dict):
            errors.append(f"{prefix}.provenance must be an object")
        elif provenance.get("type") not in PROVENANCE_TYPES:
            errors.append(
                f"{prefix}.provenance.type must be one of "
                f"{sorted(PROVENANCE_TYPES)}"
            )

        review = entry.get("review")
        if not isinstance(review, dict):
            errors.append(f"{prefix}.review must be an object")
        else:
            if not _nonempty_str(review.get("reviewed_at")):
                errors.append(f"{prefix}.review.reviewed_at is required")
            if not _nonempty_str(review.get("reviewed_by")):
                errors.append(f"{prefix}.review.reviewed_by is required")

    return errors


def check_freshness(entry: dict) -> tuple[bool, str]:
    """Provenance freshness (task 2.3). Fails closed toward REVIEW_REQUIRED."""
    provenance = entry.get("provenance") or {}
    ptype = provenance.get("type")

    if ptype == "repo_revision":
        revision = provenance.get("revision")
        if not _nonempty_str(revision):
            return False, "repo_revision provenance missing revision"
        head = git_head(entry.get("path", ""))
        if head is None:
            return False, "repo_revision provenance: git HEAD unavailable (fail closed)"
        if head != revision:
            return False, (
                f"repo_revision provenance stale: recorded {revision[:12]} "
                f"!= HEAD {head[:12]}"
            )
        return True, "repo_revision matches current HEAD"

    if ptype == "evidence_identity":
        evidence = provenance.get("evidence")
        if not _nonempty_str(evidence):
            return False, "evidence_identity provenance missing evidence reference"
        if not Path(expand(evidence)).exists():
            return False, f"evidence_identity provenance stale: {evidence} not found"
        return True, "evidence reference present"

    if ptype == "runtime_observation":
        observed_at = provenance.get("observed_at")
        if not _nonempty_str(observed_at):
            return False, "runtime_observation provenance missing observed_at"
        try:
            when = parse_iso(observed_at)
        except Exception:
            return False, "runtime_observation provenance has unparseable observed_at"
        if when > datetime.now(timezone.utc):
            return False, "runtime_observation observed_at is in the future"
        return True, "runtime observation recorded"

    return False, "provenance missing or unrecognized type"


def check_approval(raw: bytes, approval_path: Path) -> tuple[bool, str]:
    """Approval digest check (task 2.2). Read-only."""
    if not approval_path.exists():
        return False, f"approval digest file not found: {approval_path}"
    try:
        content = approval_path.read_text().strip()
    except Exception as exc:  # pragma: no cover - defensive
        return False, f"approval digest unreadable: {exc}"
    recorded = content.split()[0] if content else ""
    actual = hashlib.sha256(raw).hexdigest()
    if recorded.lower() == actual.lower():
        return True, "approval digest matches"
    return False, "approval digest mismatch (unapproved or modified)"


def evaluate(doc: dict) -> dict:
    """Apply freshness + fail-closed rules and build the handoff report."""
    results = []
    for entry in doc.get("entries", []):
        fresh, reason = check_freshness(entry)
        effective = entry.get("policy_state") if fresh else "REVIEW_REQUIRED"

        # Task 4.2: an UNKNOWN owner (for example an unavailable LaunchAgent or
        # container adapter) can never be reclaimed; fail closed.
        owner = (entry.get("owner") or "").strip()
        if owner.upper() == "UNKNOWN" and effective in ("RECLAIMABLE", "RECLAIMED"):
            effective = "REVIEW_REQUIRED"
            reason = reason + "; owner UNKNOWN blocks reclamation (adapter unavailable)"

        results.append({
            "path": entry.get("path"),
            "class": entry.get("class"),
            "policy_state": entry.get("policy_state"),
            "owner": owner,
            "candidate": entry.get("candidate"),
            "effective_state": effective,
            "fresh": fresh,
            "freshness_reason": reason,
        })

    def count(state: str) -> int:
        return sum(1 for r in results if r["effective_state"] == state)

    # Task 3.1: effective-PROTECTED entries form the exclusion list handed to
    # cleanup, each with a recorded class + owner reason.
    exclusions = [
        {
            "path": r["path"],
            "class": r["class"],
            "owner": r["owner"],
            "reason": (
                f"protected retention class '{r['class']}' owned by "
                f"{r['owner']}; cleanup SHALL skip"
            ),
        }
        for r in results if r["effective_state"] == "PROTECTED"
    ]

    # Task 3.2: reclamation candidates are proposed for operator review, never
    # auto-deleted. This tool is read-only and performs no filesystem mutation.
    review_proposals = [
        {
            "path": r["path"],
            "class": r["class"],
            "owner": r["owner"],
            "effective_state": r["effective_state"],
            "reason": "reclamation candidate; propose for operator review, do not auto-delete",
        }
        for r in results
        if (r["candidate"] is True or r["policy_state"] == "RECLAIMABLE")
        and r["effective_state"] != "PROTECTED"
        and r["owner"].upper() != "UNKNOWN"
    ]

    return {
        "policy": doc.get("policy"),
        "policy_identity": doc.get("policy_identity"),
        "policy_version": doc.get("policy_version"),
        "generated_at": doc.get("generated_at"),
        "loaded_at": now_iso(),
        "entries": results,
        "exclusions": exclusions,
        "review_proposals": review_proposals,
        "summary": {
            "total": len(results),
            "protected": count("PROTECTED"),
            "review_required": count("REVIEW_REQUIRED"),
            "reclaimable": count("RECLAIMABLE"),
            "reclaimed": count("RECLAIMED"),
            "stale_downgraded": sum(1 for r in results if not r["fresh"]),
            "exclusions": len(exclusions),
            "review_proposals": len(review_proposals),
        },
    }


def default_approval_path(inventory_path: Path) -> Path:
    return inventory_path.parent / (inventory_path.stem + ".approval.sha256")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate and load the workspace artifact retention "
                    "inventory (read-only)."
    )
    parser.add_argument(
        "--inventory",
        default=str(Path.home() / "Developer" / ".workspace-retention" /
                    "retention-inventory.json"),
        help="Path to the retention inventory JSON.",
    )
    parser.add_argument(
        "--approval", default=None,
        help="Path to the approval digest file (defaults to "
             "<inventory stem>.approval.sha256 beside the inventory).",
    )
    parser.add_argument(
        "--json", action="store_true", dest="as_json",
        help="Emit the machine-readable handoff report as JSON.",
    )
    args = parser.parse_args(argv)

    inventory_path = Path(expand(args.inventory))
    if not inventory_path.exists():
        print(f"ERROR: inventory not found: {inventory_path}", file=sys.stderr)
        return EXIT_MISSING

    approval_path = (
        Path(expand(args.approval)) if args.approval
        else default_approval_path(inventory_path)
    )

    raw = inventory_path.read_bytes()
    try:
        doc = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        print(f"SCHEMA REJECTED: malformed JSON: {exc}", file=sys.stderr)
        return EXIT_SCHEMA

    errors = validate_schema(doc)
    if errors:
        print("SCHEMA REJECTED:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return EXIT_SCHEMA

    approved, approval_reason = check_approval(raw, approval_path)
    report = evaluate(doc)
    report["approved"] = approved
    report["approval_reason"] = approval_reason

    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        print(f"policy_identity : {report['policy_identity']}")
        print(f"policy_version  : {report['policy_version']}")
        print(f"approved        : {approved} ({approval_reason})")
        s = report["summary"]
        print(
            f"entries         : {s['total']} total | "
            f"{s['protected']} protected | "
            f"{s['review_required']} review_required | "
            f"{s['reclaimable']} reclaimable | "
            f"{s['reclaimed']} reclaimed | "
            f"{s['stale_downgraded']} stale-downgraded"
        )
        print(
            f"handoff         : {s['exclusions']} exclusions | "
            f"{s['review_proposals']} review proposals"
        )
        for entry in report["entries"]:
            marker = "ok" if entry["fresh"] else "STALE"
            print(
                f"  [{marker}] {entry['path']} :: "
                f"{entry['policy_state']} -> {entry['effective_state']} "
                f"({entry['freshness_reason']})"
            )

    if not approved:
        print(f"UNAPPROVED: {approval_reason}", file=sys.stderr)
        return EXIT_UNAPPROVED
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
