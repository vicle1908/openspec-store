#!/usr/bin/env python3
"""End-to-end dry-run fixture tests for workspace-lifecycle-gated-cleanup
task 4.2.

Verification contract: each end-to-end fixture produces the expected
classification, blocker, and redacted manifest. Fixtures cover an active
OpenSpec change, an untracked archive move, an active Orca workspace, a
merged deployment snapshot, a detached unique worktree, pinned/child/
orphaned Orca records, retention-protected evidence, and secret-containing
observations. Report writes are scoped to a temporary report directory;
all workspace targets are synthetic fixtures.

Usage: python3 openspec-store/scripts/workspace-lifecycle/tests/test_e2e_dryrun.py
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import dryrun  # noqa: E402
import manifest  # noqa: E402
import retention  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
E2E_FIXTURE = FIXTURES / "e2e-dryrun.fixture.json"
RETENTION_FIXTURE = FIXTURES / "retention-inventory.protected-and-candidate.json"

GENERATED_AT = "2026-08-25T21:00:00Z"
PLAN_ID = "plan-e2e-fixture"

PASS = 0
FAIL = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ok   {name}")
    else:
        FAIL += 1
        print(f"  FAIL {name} {detail}")


def run_scan(report_dir: Path) -> dict:
    raw = json.loads(E2E_FIXTURE.read_text(encoding="utf-8"))
    inventory = retention.load_inventory(RETENTION_FIXTURE)
    document, written = dryrun.run_dry_run(
        raw, inventory, PLAN_ID, GENERATED_AT, report_dir=report_dir
    )
    assert written is not None
    return document


def entry_by_path(document: dict, path: str) -> dict:
    return next(e for e in document["entries"] if e["canonical_path"] == path)


def test_expected_classifications_and_blockers(document: dict) -> None:
    print("=== T1: each fixture produces its expected classification ===")
    expectations = [
        ("/fixtures/e2e/store/openspec/changes/active-change",
         "PROTECTED", ["openspec_active_change:active-change"]),
        ("/fixtures/e2e/store/openspec/changes/archive/moved-change",
         "PROTECTED", ["openspec_untracked_archive_move:moved-change"]),
        ("/fixtures/e2e/worktrees/feature-live",
         "PROTECTED", ["orca_live_terminal:ws-feature-live",
                       "orca_agent_working:ws-feature-live",
                       "orca_host_activity"]),
        ("/fixtures/e2e/worktrees/deploy-source-2026-07",
         "RECLAIMABLE", []),
        ("/fixtures/e2e/worktrees/unique-detached",
         "REVIEW_REQUIRED",
         ["detached_unique_revision:0ddba11000000000000000000000000000000003"]),
        ("/fixtures/e2e/worktrees/pinned-wt", "PROTECTED", ["orca_pinned"]),
        ("/fixtures/e2e/worktrees/parent-wt", "PROTECTED",
         ["orca_child_worktrees"]),
        ("/fixtures/e2e/worktrees/orphaned-wt",
         "REVIEW_REQUIRED", ["orca_orphaned_terminal:term-orphaned"]),
        ("/fixtures/retention/reports/archive-readiness-2026-08.md",
         "PROTECTED",
         ["retention:retention_protected_class:"
          "retained evidence or report owner:openspec-store"]),
        ("/fixtures/e2e/service/secret-runtime",
         "PROTECTED", ["runtime_owner:database:mystery-db"]),
    ]
    check("ten distinct fixture paths scanned",
          len(document["entries"]) == len(expectations),
          str(len(document["entries"])))
    for path, expected_class, expected_blockers in expectations:
        entry = entry_by_path(document, path)
        check(f"{Path(path).name}: {expected_class}",
              entry["classification"] == expected_class,
              entry["classification"])
        for blocker in expected_blockers:
            check(f"{Path(path).name}: blocker {blocker}",
                  blocker in entry["blockers"], str(entry["blockers"]))

    snapshot = entry_by_path(
        document, "/fixtures/e2e/worktrees/deploy-source-2026-07")
    check("snapshot records ancestor preservation evidence",
          any(e.startswith("ancestor_of_target:d3ad")
              for e in snapshot["evidence"]),
          str(snapshot["evidence"]))


def test_manifest_is_redacted(document: dict) -> None:
    print("=== T2: secret-containing observations yield a redacted manifest ===")
    serialized = json.dumps(document)
    for secret in ("sk-live-e2e-999", "hunter2-e2e", "leak-me"):
        check(f"secret value absent: {secret[:7]}...", secret not in serialized)
    for key in ("api_key", "db_password", "request_body"):
        check(f"secret-shaped key absent: {key}", f'"{key}"' not in serialized)

    entry = entry_by_path(document, "/fixtures/e2e/service/secret-runtime")
    runtime_obs = next(o for o in entry["observations"]
                       if o["authority"] == "runtime")
    check("non-secret owner/endpoint metadata retained",
          runtime_obs["facts"].get("owner") == "mystery-db"
          and runtime_obs["facts"].get("endpoint")
          == "postgres://localhost:5432/mystery"
          and runtime_obs["facts"].get("active") is True,
          str(runtime_obs["facts"]))
    try:
        manifest.validate_manifest(document)
        check("redacted manifest passes strict validation", True)
    except manifest.ManifestError as exc:
        check("redacted manifest passes strict validation", False, str(exc))


def test_report_writes_scoped_to_report_dir() -> None:
    print("=== T3: report writes are scoped and mode is dry-run ===")
    with tempfile.TemporaryDirectory(prefix="wl-e2e-") as tmp:
        report_dir = Path(tmp)
        document = run_scan(report_dir)
        written = sorted(p.name for p in report_dir.iterdir())
        check("manifest and summary written to the report dir only",
              len(written) == 2
              and any(n.startswith("cleanup-manifest-") for n in written)
              and any(n.startswith("cleanup-summary-") for n in written),
              str(written))
        check("manifest mode is dry-run", document.get("mode") == "dry-run")
        check("retention policy attached",
              document["retention_policy"].get("available") is True)

        manifest_path = next(
            p for p in report_dir.iterdir()
            if p.name.startswith("cleanup-manifest-"))
        on_disk = json.loads(manifest_path.read_text(encoding="utf-8"))
        check("on-disk manifest matches in-memory document",
              on_disk["plan_identity"] == document["plan_identity"])
        check("on-disk manifest is redacted too",
              "sk-live-e2e-999" not in manifest_path.read_text(encoding="utf-8"))


def test_repeated_scan_is_stable() -> None:
    print("=== T4: repeated scan of unchanged fixtures is stable ===")
    with tempfile.TemporaryDirectory(prefix="wl-e2e-stable-") as tmp:
        first = run_scan(Path(tmp))
        second = run_scan(Path(tmp))
        check("plan identity stable across repeated scans",
              first["plan_identity"] == second["plan_identity"])
        check("classifications stable across repeated scans",
              [(e["canonical_path"], e["classification"])
               for e in first["entries"]]
              == [(e["canonical_path"], e["classification"])
                  for e in second["entries"]])
        reports = sorted(p.name for p in Path(tmp).iterdir())
        check("no duplicate reports created", len(reports) == 2, str(reports))


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="wl-e2e-main-") as tmp:
        document = run_scan(Path(tmp))
        test_expected_classifications_and_blockers(document)
        test_manifest_is_redacted(document)
    test_report_writes_scoped_to_report_dir()
    test_repeated_scan_is_stable()
    print(f"\n=== RESULTS: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
