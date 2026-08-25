"""Default read-only dry-run for workspace lifecycle cleanup.

Task 2.2 contract: the default operation is a read-only dry-run producing a
machine-readable manifest and a human-readable summary without deleting,
moving, pruning, resetting, checking out, pushing, archiving, staging, or
mutating files, branches, worktrees, OpenSpec changes, processes,
containers, databases, or indexes. Repeated scans of unchanged state
produce stable classifications and stable path identities and do not create
duplicate cleanup actions.

Observations are provided by the authority adapters (task 1.1 contract);
this module never queries live systems itself. Report writes are scoped to
the caller-supplied report directory only; nothing else is written.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping, Optional, Tuple

import classify
import manifest
import retention
from observations import correlate, load_observations


def scan(
    records: Mapping,
    retention_inventory: Optional[retention.RetentionInventory],
    plan_id: str,
    generated_at: str,
    workspace_root: str = "~/Developer",
) -> dict:
    """Classify correlated records into a validated dry-run manifest."""
    entries = []
    for path in sorted(records):
        record = records[path]
        result = classify.classify_path(record, retention_inventory)
        entries.append(
            manifest.build_entry(
                path,
                record.observations,
                result.classification,
                result.blockers,
                result.evidence,
                generated_at,
            )
        )
    return manifest.build_manifest(
        plan_id, entries, generated_at, retention_inventory, workspace_root
    )


def render_summary(document: Mapping) -> str:
    """Human-readable dry-run summary (proposals only, nothing applied)."""
    counts = {name: 0 for name in manifest.CLASSIFICATIONS}
    for entry in document["entries"]:
        counts[entry["classification"]] += 1
    policy = document["retention_policy"]
    policy_line = (
        f"available ({policy['policy_identity']})"
        if policy.get("available")
        else "UNAVAILABLE — artifact reclaimability blocked (fail closed)"
    )
    lines = [
        "Workspace Lifecycle Cleanup — Dry-Run Summary",
        "=============================================",
        "Mode: dry-run (no mutations performed)",
        f"Generated: {document['generated_at']}",
        f"Plan id: {document['plan_id']}",
        f"Plan identity: {document['plan_identity']}",
        f"Retention policy: {policy_line}",
        f"Paths scanned: {len(document['entries'])}",
    ]
    for name in manifest.CLASSIFICATIONS:
        lines.append(f"  {name}: {counts[name]}")
    candidates = [
        entry["canonical_path"]
        for entry in document["entries"]
        if entry["classification"] == "RECLAIMABLE"
    ]
    lines.append(f"Reclaimable candidates (review-only proposals): {len(candidates)}")
    lines.extend(f"  - {path}" for path in candidates)
    skipped = [
        (entry["canonical_path"], entry["blockers"])
        for entry in document["entries"]
        if entry["classification"] in ("PROTECTED", "REVIEW_REQUIRED")
    ]
    lines.append(f"Skipped paths (protected or review-required): {len(skipped)}")
    lines.extend(f"  - {path} [{'; '.join(blockers)}]" for path, blockers in skipped)
    return "\n".join(lines) + "\n"


def write_report(document: Mapping, report_dir: Path) -> Tuple[Path, Path]:
    """Write manifest + summary into the scoped report directory only.

    File names derive from the plan identity, so repeated scans of unchanged
    state overwrite the same reports instead of creating duplicates.
    Serialization is deterministic (sorted keys, fixed indent).
    """
    report_dir = Path(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    short = str(document["plan_identity"])[:16]
    manifest_path = report_dir / f"cleanup-manifest-{short}.json"
    summary_path = report_dir / f"cleanup-summary-{short}.txt"
    manifest_path.write_text(
        json.dumps(document, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    summary_path.write_text(render_summary(document), encoding="utf-8")
    return manifest_path, summary_path


def run_dry_run(
    raw_observations: Iterable[Mapping],
    retention_inventory: Optional[retention.RetentionInventory],
    plan_id: str,
    generated_at: str,
    report_dir: Optional[Path] = None,
    workspace_root: str = "~/Developer",
) -> Tuple[dict, Optional[Tuple[Path, Path]]]:
    """Full default dry-run: validate, correlate, classify, report."""
    records = correlate(load_observations(list(raw_observations)))
    document = scan(records, retention_inventory, plan_id, generated_at, workspace_root)
    written = write_report(document, report_dir) if report_dir is not None else None
    return document, written
