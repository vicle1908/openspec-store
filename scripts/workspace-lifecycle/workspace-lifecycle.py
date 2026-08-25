#!/usr/bin/env python3
"""workspace-lifecycle.py — workspace lifecycle cleanup tool (default: dry-run).

Usage:
  workspace-lifecycle.py --observations FILE [--retention FILE]
                         [--report-dir DIR] [--plan-id ID] [--generated-at TS]

The default mode is the read-only dry-run scan: it validates authority
observations (task 1.1 contract), applies the retention exclusion layer
(task 0.2 handoff), classifies paths with fail-closed precedence (task 1.2),
and writes a machine-readable manifest plus a human-readable summary into
the report directory (task 2.1 schema). It reports proposed owner actions
without applying them.

This tool never deletes, moves, prunes, resets, checks out, pushes, stages,
archives, or mutates files, branches, worktrees, OpenSpec changes,
processes, containers, databases, or indexes. Approved retirement is a
separate lifecycle operation (design Decision 4) and is not implemented by
the dry-run.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dryrun  # noqa: E402
import retention  # noqa: E402

DEFAULT_REPORT_DIR = Path.home() / "Developer" / ".workspace-lifecycle"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="workspace-lifecycle.py",
        description="Read-only workspace lifecycle dry-run (no mutations).",
    )
    parser.add_argument(
        "--observations",
        required=True,
        help="JSON file: list of authority observations (task 1.1 contract)",
    )
    parser.add_argument(
        "--retention",
        default=str(retention.DEFAULT_INVENTORY_PATH),
        help="retention inventory path (fail-closed when unavailable)",
    )
    parser.add_argument(
        "--report-dir",
        default=str(DEFAULT_REPORT_DIR),
        help="scoped directory for manifest/summary reports",
    )
    parser.add_argument("--plan-id", default="plan-manual-run")
    parser.add_argument(
        "--generated-at",
        default=None,
        help="ISO8601 observation time (default: now; supply for replay/tests)",
    )
    args = parser.parse_args(argv)

    try:
        raw_observations = json.loads(
            Path(args.observations).read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read observations: {exc}", file=sys.stderr)
        return 2

    inventory = retention.load_or_unavailable(Path(args.retention))
    generated_at = args.generated_at or datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    try:
        document, written = dryrun.run_dry_run(
            raw_observations,
            inventory,
            args.plan_id,
            generated_at,
            report_dir=Path(args.report_dir),
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    sys.stdout.write(dryrun.render_summary(document))
    if written:
        manifest_path, summary_path = written
        print(f"\nManifest: {manifest_path}")
        print(f"Summary:  {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
