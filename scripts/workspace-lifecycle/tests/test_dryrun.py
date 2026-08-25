#!/usr/bin/env python3
"""Dry-run tests for workspace-lifecycle-gated-cleanup task 2.2.

Verification contract: the default dry-run is read-only with stable
repeated-scan behavior — `git status --porcelain` and an in-scope file-list
checksum are identical before and after two consecutive dry-runs. All
workspace targets are synthetic test fixtures; report writes are scoped to
a test report directory only.

Usage: python3 openspec-store/scripts/workspace-lifecycle/tests/test_dryrun.py
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import dryrun  # noqa: E402
import retention  # noqa: E402

TOOL_DIR = Path(__file__).resolve().parents[1]
CLI = TOOL_DIR / "workspace-lifecycle.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
RETENTION_FIXTURE = FIXTURES / "retention-inventory.protected-and-candidate.json"
AUTHORITY_FIXTURE = FIXTURES / "authority-observations.fixture.json"

RUN_ONE_AT = "2026-08-25T15:00:00Z"
RUN_TWO_AT = "2026-08-25T16:00:00Z"
OBSERVED_AT = "2026-08-25T14:30:00Z"

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


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    )
    return result.stdout


def make_git_workspace(root: Path) -> Path:
    repo = root / "repo-alpha"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "fixture@example.com")
    git(repo, "config", "user.name", "Fixture")
    (repo / "README.md").write_text("synthetic fixture\n", encoding="utf-8")
    git(repo, "add", "README.md")
    git(repo, "commit", "-qm", "fixture initial")
    return repo


def file_list_checksum(root: Path, exclude: Path) -> str:
    items = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        try:
            path.relative_to(exclude)
            continue  # report outputs are the explicitly scoped writes
        except ValueError:
            pass
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        items.append(f"{path.relative_to(root)}:{digest}")
    return hashlib.sha256("\n".join(items).encode("utf-8")).hexdigest()


def workspace_observations(repo: Path) -> list:
    head = git(repo, "rev-parse", "HEAD").strip()
    repo_str = str(repo)
    return [
        {
            "authority": "git",
            "canonical_path": repo_str,
            "subject": "main",
            "observed_at": OBSERVED_AT,
            "facts": {
                "repo_identity": f"{repo_str}/.git",
                "worktree_id": "main",
                "branch": "main",
                "detached": False,
                "revision": head,
                "dirty": False,
                "generated_only": False,
                "unpushed": False,
                "merged_into_target": False,
                "ancestor_of_target": False,
            },
        },
        {
            "authority": "git",
            "canonical_path": f"{repo_str}-worktrees/feature-merged",
            "subject": "feature-merged",
            "observed_at": OBSERVED_AT,
            "facts": {
                "repo_identity": f"{repo_str}/.git",
                "worktree_id": "wt-feature-merged",
                "branch": "feature-merged",
                "detached": False,
                "revision": head,
                "dirty": False,
                "generated_only": False,
                "unpushed": False,
                "merged_into_target": True,
                "ancestor_of_target": True,
            },
        },
        {
            "authority": "orca",
            "canonical_path": f"{repo_str}-worktrees/feature-merged",
            "subject": "ws-feature-merged",
            "observed_at": OBSERVED_AT,
            "facts": {
                "workspace_id": "ws-feature-merged",
                "isPinned": False,
                "agent_state": "working",
                "live_terminal": True,
                "terminal_state": "connected",
                "attached_pty": False,
                "host_activity": True,
                "child_worktrees": [],
                "parent_worktree": None,
            },
        },
        {
            "authority": "git",
            "canonical_path": f"{repo_str}-worktrees/deploy-source-snapshot",
            "subject": "deploy-source-snapshot",
            "observed_at": OBSERVED_AT,
            "facts": {
                "repo_identity": f"{repo_str}/.git",
                "worktree_id": "wt-deploy-snapshot",
                "branch": "deploy-source-snapshot",
                "detached": True,
                "revision": head,
                "dirty": False,
                "generated_only": False,
                "unpushed": False,
                "merged_into_target": False,
                "ancestor_of_target": True,
            },
        },
        {
            "authority": "runtime",
            "canonical_path": f"{repo_str}-data/mystery.db",
            "subject": "mystery.db",
            "observed_at": OBSERVED_AT,
            "facts": {
                "kind": "database",
                "owner": "",
                "active": False,
                "available": False,
            },
        },
    ]


def test_dry_run_report_content() -> None:
    print("=== T1: default dry-run emits manifest + human summary without applying ===")
    with tempfile.TemporaryDirectory(prefix="lifecycle-dryrun-") as tmp:
        root = Path(tmp)
        repo = make_git_workspace(root)
        report_dir = root / "reports"
        inventory = retention.load_inventory(RETENTION_FIXTURE)
        document, written = dryrun.run_dry_run(
            workspace_observations(repo), inventory, "plan-test-0001",
            RUN_ONE_AT, report_dir=report_dir,
        )
        check("manifest mode is dry-run", document["mode"] == "dry-run")
        check("five observations correlate into four paths",
              len(document["entries"]) == 4, str(len(document["entries"])))
        by_path = {e["canonical_path"]: e for e in document["entries"]}
        conflict = by_path[f"{repo}-worktrees/feature-merged"]
        check("conflicted worktree PROTECTED in report",
              conflict["classification"] == "PROTECTED")
        snapshot = by_path[f"{repo}-worktrees/deploy-source-snapshot"]
        check("proven ancestor snapshot RECLAIMABLE (review-only proposal)",
              snapshot["classification"] == "RECLAIMABLE"
              and snapshot["proposed_owner_action"]["action"]
              == "propose_retirement_review")
        manifest_path, summary_path = written
        check("report files written to scoped dir",
              manifest_path.is_file() and summary_path.is_file()
              and manifest_path.parent == report_dir)
        summary = summary_path.read_text(encoding="utf-8")
        check("summary names dry-run mode and counts",
              "Dry-Run Summary" in summary and "Mode: dry-run" in summary
              and "PROTECTED:" in summary and "RECLAIMABLE:" in summary)
        check("summary lists review-only candidates, not deletions",
              "review-only proposals" in summary
              and "delete" not in summary.lower())


def test_two_consecutive_dry_runs_are_non_mutating() -> None:
    print("=== T2: git status and file-list checksum identical across two dry-runs ===")
    with tempfile.TemporaryDirectory(prefix="lifecycle-dryrun-") as tmp:
        root = Path(tmp)
        repo = make_git_workspace(root)
        report_dir = root / "reports"
        inventory = retention.load_inventory(RETENTION_FIXTURE)
        obs = workspace_observations(repo)

        status_before = git(repo, "status", "--porcelain")
        checksum_before = file_list_checksum(root, report_dir)

        doc_one, _ = dryrun.run_dry_run(obs, inventory, "plan-test-0002",
                                        RUN_ONE_AT, report_dir=report_dir)
        status_mid = git(repo, "status", "--porcelain")
        checksum_mid = file_list_checksum(root, report_dir)

        doc_two, _ = dryrun.run_dry_run(obs, inventory, "plan-test-0002",
                                        RUN_TWO_AT, report_dir=report_dir)
        status_after = git(repo, "status", "--porcelain")
        checksum_after = file_list_checksum(root, report_dir)

        check("git status --porcelain unchanged after run 1",
              status_mid == status_before, repr((status_before, status_mid)))
        check("in-scope file-list checksum unchanged after run 1",
              checksum_mid == checksum_before)
        check("git status --porcelain unchanged after run 2",
              status_after == status_before, repr((status_before, status_after)))
        check("in-scope file-list checksum unchanged after run 2",
              checksum_after == checksum_before)
        check("report dir holds exactly one manifest + one summary (no duplicates)",
              sorted(p.name for p in report_dir.iterdir())
              == sorted({f"cleanup-manifest-{doc_one['plan_identity'][:16]}.json",
                         f"cleanup-summary-{doc_one['plan_identity'][:16]}.txt"}),
              str(sorted(p.name for p in report_dir.iterdir())))
        check("second run overwrote the same report files",
              len(list(report_dir.iterdir())) == 2)


def test_repeated_scan_is_stable() -> None:
    print("=== T3: repeated scan produces stable classifications and identity ===")
    with tempfile.TemporaryDirectory(prefix="lifecycle-dryrun-") as tmp:
        root = Path(tmp)
        repo = make_git_workspace(root)
        inventory = retention.load_inventory(RETENTION_FIXTURE)
        obs = workspace_observations(repo)
        doc_one, _ = dryrun.run_dry_run(obs, inventory, "plan-test-0003",
                                        RUN_ONE_AT)
        doc_two, _ = dryrun.run_dry_run(obs, inventory, "plan-test-0003",
                                        RUN_TWO_AT)
        check("plan identity stable across runs",
              doc_one["plan_identity"] == doc_two["plan_identity"])
        decisions_one = [(e["canonical_path"], e["classification"], e["blockers"])
                         for e in doc_one["entries"]]
        decisions_two = [(e["canonical_path"], e["classification"], e["blockers"])
                         for e in doc_two["entries"]]
        check("classifications and blockers stable across runs",
              decisions_one == decisions_two)
        paths_one = [e["canonical_path"] for e in doc_one["entries"]]
        check("no duplicate cleanup entries",
              len(paths_one) == len(set(paths_one)))


def test_cli_end_to_end_dry_run() -> None:
    print("=== T4: CLI default mode runs a read-only dry-run end to end ===")
    with tempfile.TemporaryDirectory(prefix="lifecycle-dryrun-") as tmp:
        root = Path(tmp)
        report_dir = root / "reports"
        result = subprocess.run(
            [sys.executable, str(CLI),
             "--observations", str(AUTHORITY_FIXTURE),
             "--retention", str(RETENTION_FIXTURE),
             "--report-dir", str(report_dir),
             "--plan-id", "plan-cli-test",
             "--generated-at", RUN_ONE_AT],
            capture_output=True, text=True,
        )
        check("CLI exits 0", result.returncode == 0, result.stderr)
        check("CLI prints human summary",
              "Dry-Run Summary" in result.stdout and "Mode: dry-run" in result.stdout)
        files = sorted(p.name for p in report_dir.iterdir())
        check("CLI wrote manifest + summary to scoped dir",
              len(files) == 2 and files[0].startswith("cleanup-manifest-")
              and files[1].startswith("cleanup-summary-"), str(files))
        manifest_doc = json.loads((report_dir / files[0]).read_text(encoding="utf-8"))
        check("CLI manifest validates with retention identity",
              manifest_doc["retention_policy"]["available"] is True
              and manifest_doc["mode"] == "dry-run")


def main() -> int:
    test_dry_run_report_content()
    test_two_consecutive_dry_runs_are_non_mutating()
    test_repeated_scan_is_stable()
    test_cli_end_to_end_dry_run()
    print(f"\n=== RESULTS: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
