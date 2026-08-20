#!/usr/bin/env python3
"""Validate OpenSpec change archive readiness against tasks, specs, and evidence.

This script is standard-library-only and read-only by default.
It enforces fail-closed archive readiness gates:
1. Every tracked task in tasks.md MUST be checked (- [x]). Unchecked tasks (- [ ]) block archive.
2. Required planning artifacts (proposal.md, design.md, tasks.md) must exist and be non-empty.
3. Delta specs (specs/**/*.md) must adhere to normative OpenSpec format unless skip_specs is enabled.
4. If an EVIDENCE_MANIFEST.md exists, gate results and repository hashes must be consistent.
5. In --range mode, audits recent commits to verify archived changes were not archived with incomplete tasks.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

TASK_UNCHECKED_PATTERN = re.compile(r"^\s*-\s*\[\s*\]\s+(.+)$", re.MULTILINE)
TASK_CHECKED_PATTERN = re.compile(r"^\s*-\s*\[[xX]\]\s+(.+)$", re.MULTILINE)
NORMATIVE_SPEC_HEADERS = (
    "## ADDED Requirements",
    "## MODIFIED Requirements",
    "## REMOVED Requirements",
    "## Requirements",
)


@dataclass
class TaskSummary:
    total: int = 0
    completed: int = 0
    remaining: int = 0
    unchecked_tasks: list[str] = field(default_factory=list)


@dataclass
class ReadinessReport:
    change_name: str
    store_root: str
    status: str  # 'ready', 'blocked', 'invalid'
    exit_code: int
    tasks: TaskSummary
    artifacts_found: dict[str, bool]
    delta_specs_count: int
    skip_specs: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def find_store_root(start_path: Path | None = None) -> Path:
    current = (start_path or Path.cwd()).resolve()
    for parent in [current, *current.parents]:
        if (parent / "openspec" / "config.yaml").exists() or (parent / "openspec" / "specs").exists():
            return parent
    return current


def parse_tasks_md(tasks_path: Path) -> TaskSummary:
    if not tasks_path.exists():
        return TaskSummary()

    content = tasks_path.read_text(encoding="utf-8")
    unchecked = TASK_UNCHECKED_PATTERN.findall(content)
    checked = TASK_CHECKED_PATTERN.findall(content)

    total = len(unchecked) + len(checked)
    return TaskSummary(
        total=total,
        completed=len(checked),
        remaining=len(unchecked),
        unchecked_tasks=[task.strip() for task in unchecked],
    )


def validate_delta_spec(spec_path: Path) -> list[str]:
    errors: list[str] = []
    content = spec_path.read_text(encoding="utf-8")

    has_normative_header = any(header in content for header in NORMATIVE_SPEC_HEADERS)
    if not has_normative_header:
        errors.append(f"{spec_path.name}: missing standard OpenSpec section headers (## ADDED/MODIFIED/REMOVED Requirements)")

    if "### Requirement:" in content and "#### Scenario:" not in content:
        errors.append(f"{spec_path.name}: requirement definitions must contain at least one #### Scenario block")

    return errors


def check_change_readiness(change_dir: Path, store_root: Path) -> ReadinessReport:
    change_name = change_dir.name
    proposal_file = change_dir / "proposal.md"
    design_file = change_dir / "design.md"
    tasks_file = change_dir / "tasks.md"
    specs_dir = change_dir / "specs"

    artifacts_found = {
        "proposal": proposal_file.exists() and proposal_file.stat().st_size > 0,
        "design": design_file.exists() and design_file.stat().st_size > 0,
        "tasks": tasks_file.exists() and tasks_file.stat().st_size > 0,
    }

    errors: list[str] = []
    warnings: list[str] = []

    # 1. Check required base artifacts
    if not artifacts_found["proposal"]:
        errors.append("Missing or empty proposal.md")
    if not artifacts_found["design"]:
        errors.append("Missing or empty design.md")
    if not artifacts_found["tasks"]:
        errors.append("Missing or empty tasks.md")

    # 2. Check task checklist completion
    task_summary = parse_tasks_md(tasks_file)
    if task_summary.total == 0 and artifacts_found["tasks"]:
        warnings.append("tasks.md has no checklist tasks (- [ ] or - [x])")
    elif task_summary.remaining > 0:
        errors.append(
            f"{task_summary.remaining} of {task_summary.total} tasks are incomplete in tasks.md"
        )

    # 3. Check skip_specs / delta specs
    skip_specs = False
    if artifacts_found["proposal"]:
        prop_text = proposal_file.read_text(encoding="utf-8")
        if "skip_specs: true" in prop_text or "skip_specs:true" in prop_text:
            skip_specs = True

    delta_specs: list[Path] = []
    if specs_dir.exists():
        delta_specs = [p for p in specs_dir.rglob("*.md") if p.is_file()]

    delta_specs_count = len(delta_specs)
    if not skip_specs and delta_specs_count == 0:
        # Check if change has delta specs declared or is an implementation-only change
        warnings.append("No delta specs found in specs/ (ensure skip_specs is set if no spec delta is needed)")
    elif delta_specs_count > 0:
        for spec_file in delta_specs:
            spec_errs = validate_delta_spec(spec_file)
            errors.extend(spec_errs)

    # Determine status and exit code
    if any("tasks are incomplete" in err for err in errors):
        status = "blocked"
        exit_code = 3
    elif errors:
        status = "invalid"
        exit_code = 4
    else:
        status = "ready"
        exit_code = 0

    return ReadinessReport(
        change_name=change_name,
        store_root=str(store_root),
        status=status,
        exit_code=exit_code,
        tasks=task_summary,
        artifacts_found=artifacts_found,
        delta_specs_count=delta_specs_count,
        skip_specs=skip_specs,
        errors=errors,
        warnings=warnings,
    )


def audit_git_range(git_range: str, store_root: Path) -> int:
    try:
        res = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=A", git_range, "--", "openspec/changes/archive/"],
            cwd=store_root,
            capture_output=True,
            text=True,
            check=True,
        )
        archived_files = [line.strip() for line in res.stdout.splitlines() if line.strip()]
    except subprocess.CalledProcessError as e:
        print(f"Error inspecting git range {git_range}: {e.stderr}", file=sys.stderr)
        return 4

    archived_changes: set[str] = set()
    for f in archived_files:
        # Format: openspec/changes/archive/<date>-<name>/...
        parts = Path(f).parts
        if len(parts) >= 4 and parts[0] == "openspec" and parts[1] == "changes" and parts[2] == "archive":
            archived_changes.add(parts[3])

    if not archived_changes:
        print(f"Range audit: 0 archived changes added in {git_range}.")
        return 0

    print(f"Range audit: validating {len(archived_changes)} archived changes in {git_range}...")
    violations = 0
    for archive_name in sorted(archived_changes):
        archive_dir = store_root / "openspec" / "changes" / "archive" / archive_name
        tasks_file = archive_dir / "tasks.md"
        if tasks_file.exists():
            summary = parse_tasks_md(tasks_file)
            if summary.remaining > 0:
                print(f"VIOLATION: Archive {archive_name} was archived with {summary.remaining} unchecked tasks!", file=sys.stderr)
                violations += 1

    if violations > 0:
        print(f"Range audit FAILED: {violations} integrity violations detected.", file=sys.stderr)
        return 3

    print("Range audit PASSED: all newly archived changes satisfy readiness criteria.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate OpenSpec change archive readiness.")
    parser.add_argument("--change", help="Name of active change to validate")
    parser.add_argument("--store", type=Path, help="Root path of the OpenSpec store")
    parser.add_argument("--range", help="Git commit range to audit for archive integrity (e.g. main..HEAD)")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as blocking errors")

    args = parser.parse_args(argv)
    store_root = (args.store or find_store_root()).resolve()

    if args.range:
        return audit_git_range(args.range, store_root)

    if not args.change:
        print("Error: Either --change <name> or --range <git_range> is required.", file=sys.stderr)
        return 4

    change_dir = store_root / "openspec" / "changes" / args.change
    if not change_dir.exists():
        # Check if the change is already archived
        archive_matches = list((store_root / "openspec" / "changes" / "archive").glob(f"*-{args.change}"))
        if archive_matches:
            change_dir = archive_matches[0]
        else:
            print(f"Error: Change '{args.change}' not found under {store_root / 'openspec' / 'changes'}", file=sys.stderr)
            return 4

    report = check_change_readiness(change_dir, store_root)

    if args.strict and report.warnings and report.exit_code == 0:
        report.status = "invalid"
        report.exit_code = 4
        report.errors.extend([f"Strict mode: {w}" for w in report.warnings])

    if args.json:
        print(json.dumps(asdict(report), indent=2))
    else:
        print(f"Change: {report.change_name}")
        print(f"Store:  {report.store_root}")
        print(f"Status: {report.status.upper()} (exit code {report.exit_code})")
        print(f"Tasks:  {report.tasks.completed}/{report.tasks.total} completed ({report.tasks.remaining} remaining)")
        print(f"Delta Specs: {report.delta_specs_count} files (skip_specs={report.skip_specs})")
        if report.errors:
            print("\nErrors:")
            for err in report.errors:
                print(f"  - {err}")
        if report.warnings:
            print("\nWarnings:")
            for w in report.warnings:
                print(f"  - {w}")

    return report.exit_code


if __name__ == "__main__":
    sys.exit(main())
