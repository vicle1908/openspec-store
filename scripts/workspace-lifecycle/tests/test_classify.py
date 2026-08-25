#!/usr/bin/env python3
"""Classification tests for workspace-lifecycle-gated-cleanup task 1.2.

Verification contract: focused tests cover active OpenSpec, live Orca
terminal, runtime ownership unknown, detached unique revision, proven
ancestor snapshot, and protected retention class exclusion from candidates.
Classification precedence is PROTECTED > REVIEW_REQUIRED > RECLAIMABLE >
RECLAIMED, with unknown ownership failing closed.

Usage: python3 openspec-store/scripts/workspace-lifecycle/tests/test_classify.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import classify  # noqa: E402
import observations  # noqa: E402
import retention  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
AUTHORITY_FIXTURE = FIXTURES / "authority-observations.fixture.json"
RETENTION_FIXTURE = FIXTURES / "retention-inventory.protected-and-candidate.json"

CONFLICT_PATH = "/fixtures/lifecycle/repo-alpha-worktrees/feature-merged"
SNAPSHOT_PATH = "/fixtures/lifecycle/repo-alpha-worktrees/deploy-source-2026-07"
RETENTION_PROTECTED_PATH = "/fixtures/retention/reports/archive-readiness-2026-08.md"
RETENTION_CANDIDATE_PATH = "/fixtures/retention/tmp/ephemeral-pytest-cache"
UNGOVERNED_WORKTREE_PATH = "/fixtures/lifecycle/repo-alpha-worktrees/merged-clean"

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


def authority_records() -> dict:
    raw = json.loads(AUTHORITY_FIXTURE.read_text(encoding="utf-8"))
    return observations.correlate(observations.load_observations(raw))


def make_record(path: str, *raw_observations) -> observations.PathRecord:
    loaded = observations.load_observations(list(raw_observations))
    return observations.correlate(loaded)[path]


def git_obs(path: str, **facts) -> dict:
    base = {
        "repo_identity": f"{path}/.git",
        "worktree_id": f"wt-{Path(path).name}",
        "branch": Path(path).name,
        "detached": False,
        "revision": "ffff000000000000000000000000000000000009",
        "dirty": False,
        "generated_only": False,
        "unpushed": False,
        "merged_into_target": False,
        "ancestor_of_target": False,
    }
    base.update(facts)
    return {
        "authority": "git",
        "canonical_path": path,
        "subject": str(facts.get("branch") or Path(path).name),
        "observed_at": "2026-08-25T13:00:00Z",
        "facts": base,
    }


def retention_inventory() -> retention.RetentionInventory:
    return retention.load_inventory(RETENTION_FIXTURE)


def test_active_openspec_is_protected() -> None:
    print("=== T1: active OpenSpec change is PROTECTED ===")
    records = authority_records()
    record = records["/fixtures/lifecycle/store/openspec/changes/active-change"]
    result = classify.classify_path(record, retention_inventory())
    check("classified PROTECTED", result.classification == "PROTECTED", result.classification)
    check(
        "blocker names the active change",
        any(b == "openspec_active_change:active-change" for b in result.blockers),
        str(result.blockers),
    )


def test_live_orca_terminal_wins_conflict() -> None:
    print("=== T2: live Orca terminal overrides merged-git lean (most restrictive wins) ===")
    records = authority_records()
    record = records[CONFLICT_PATH]
    result = classify.classify_path(record, retention_inventory())
    check("classified PROTECTED", result.classification == "PROTECTED", result.classification)
    for expected in ("orca_live_terminal:ws-feature-merged", "orca_agent_working:ws-feature-merged", "orca_host_activity"):
        check(f"blocker present: {expected}", expected in result.blockers, str(result.blockers))

    unpushed_and_live = make_record(
        "/fixtures/lifecycle/precedence-path",
        git_obs("/fixtures/lifecycle/precedence-path", unpushed=True),
        {
            "authority": "orca",
            "canonical_path": "/fixtures/lifecycle/precedence-path",
            "subject": "ws-precedence",
            "observed_at": "2026-08-25T13:00:01Z",
            "facts": {"workspace_id": "ws-precedence", "live_terminal": True,
                      "terminal_state": "connected", "agent_state": "idle",
                      "isPinned": False, "attached_pty": False,
                      "host_activity": False, "child_worktrees": []},
        },
    )
    result = classify.classify_path(unpushed_and_live, retention_inventory())
    check(
        "PROTECTED outranks REVIEW_REQUIRED (unpushed + live terminal)",
        result.classification == "PROTECTED",
        result.classification,
    )


def test_runtime_ownership_unknown_blocks_reclaimability() -> None:
    print("=== T3: runtime ownership unknown blocks reclaimability ===")
    records = authority_records()
    mystery = records["/fixtures/lifecycle/mystery-db"]
    result = classify.classify_path(mystery, retention_inventory())
    check("classified REVIEW_REQUIRED", result.classification == "REVIEW_REQUIRED", result.classification)
    check(
        "blocker names unknown runtime ownership",
        any(b.startswith("runtime_ownership_unknown") for b in result.blockers),
        str(result.blockers),
    )

    proven_but_unknown_runtime = make_record(
        "/fixtures/lifecycle/proven-but-unknown-runtime",
        git_obs("/fixtures/lifecycle/proven-but-unknown-runtime",
                detached=True, ancestor_of_target=True,
                revision="eeee000000000000000000000000000000000005"),
        {
            "authority": "runtime",
            "canonical_path": "/fixtures/lifecycle/proven-but-unknown-runtime",
            "subject": "mystery-watcher",
            "observed_at": "2026-08-25T13:00:02Z",
            "facts": {"kind": "index_watcher", "owner": "", "active": False,
                      "available": False},
        },
    )
    result = classify.classify_path(proven_but_unknown_runtime, retention_inventory())
    check(
        "proven preservation still blocked by unknown runtime ownership",
        result.classification == "REVIEW_REQUIRED",
        result.classification,
    )


def test_detached_unique_revision_is_review_required() -> None:
    print("=== T4: detached unique revision is REVIEW_REQUIRED ===")
    record = make_record(
        "/fixtures/lifecycle/repo-alpha-worktrees/unique-detached",
        git_obs("/fixtures/lifecycle/repo-alpha-worktrees/unique-detached",
                detached=True, ancestor_of_target=False,
                remote_reachable=False, backup_reachable=False,
                revision="cccc000000000000000000000000000000000003"),
    )
    result = classify.classify_path(record, retention_inventory())
    check("classified REVIEW_REQUIRED", result.classification == "REVIEW_REQUIRED", result.classification)
    check(
        "blocker records the unique revision",
        "detached_unique_revision:cccc000000000000000000000000000000000003" in result.blockers,
        str(result.blockers),
    )


def test_proven_ancestor_snapshot_is_reclaimable() -> None:
    print("=== T5: proven ancestor snapshot is RECLAIMABLE ===")
    record = make_record(
        SNAPSHOT_PATH,
        git_obs(SNAPSHOT_PATH, detached=True, ancestor_of_target=True,
                revision="dddd000000000000000000000000000000000004"),
    )
    result = classify.classify_path(record, retention_inventory())
    check("classified RECLAIMABLE", result.classification == "RECLAIMABLE", result.classification)
    check(
        "evidence records the ancestor proof",
        any(e.startswith("ancestor_of_target:") for e in result.evidence),
        str(result.evidence),
    )
    check("no blockers on a proven reclaimable path", result.blockers == (), str(result.blockers))


def test_protected_retention_class_excluded_from_candidates() -> None:
    print("=== T6: protected retention class excluded from lifecycle candidates ===")
    inventory = retention_inventory()
    paths = [RETENTION_PROTECTED_PATH, RETENTION_CANDIDATE_PATH, UNGOVERNED_WORKTREE_PATH]
    results = {}
    for path in paths:
        record = observations.PathRecord(path, [])
        if path == UNGOVERNED_WORKTREE_PATH:
            record = make_record(
                path, git_obs(path, merged_into_target=True, ancestor_of_target=True)
            )
        results[path] = classify.classify_path(record, inventory)

    candidates = [p for p in paths if results[p].classification == "RECLAIMABLE"]
    check(
        "protected retention path is PROTECTED",
        results[RETENTION_PROTECTED_PATH].classification == "PROTECTED",
        results[RETENTION_PROTECTED_PATH].classification,
    )
    check(
        "protected retention path excluded from candidates",
        RETENTION_PROTECTED_PATH not in candidates,
        str(candidates),
    )
    check(
        "exclusion blocker records retention class",
        any("retained evidence or report" in b for b in results[RETENTION_PROTECTED_PATH].blockers),
        str(results[RETENTION_PROTECTED_PATH].blockers),
    )
    check(
        "candidate-class path stays review-only (not a candidate)",
        results[RETENTION_CANDIDATE_PATH].classification == "REVIEW_REQUIRED"
        and RETENTION_CANDIDATE_PATH not in candidates,
        results[RETENTION_CANDIDATE_PATH].classification,
    )
    check(
        "review-only blocker names the candidate gate",
        any("retention_candidate_review_only" in b for b in results[RETENTION_CANDIDATE_PATH].blockers),
        str(results[RETENTION_CANDIDATE_PATH].blockers),
    )
    check(
        "ungoverned proven worktree remains the only candidate",
        candidates == [UNGOVERNED_WORKTREE_PATH],
        str(candidates),
    )


def test_unknown_ownership_fails_closed() -> None:
    print("=== T7: unknown ownership fails closed ===")
    record = observations.PathRecord("/fixtures/lifecycle/unknown-path", [])
    result = classify.classify_path(record, retention_inventory())
    check("classified REVIEW_REQUIRED", result.classification == "REVIEW_REQUIRED", result.classification)
    check("unknown_ownership blocker present", "unknown_ownership" in result.blockers, str(result.blockers))
    check("never RECLAIMABLE", result.classification != "RECLAIMABLE")


def test_additional_guards() -> None:
    print("=== T8: additional precedence guards ===")
    inventory = retention_inventory()

    dirty = make_record(
        "/fixtures/lifecycle/dirty-work",
        git_obs("/fixtures/lifecycle/dirty-work", dirty=True),
    )
    result = classify.classify_path(dirty, inventory)
    check(
        "non-generated dirt is PROTECTED",
        result.classification == "PROTECTED"
        and "non_generated_uncommitted_content" in result.blockers,
        f"{result.classification} {result.blockers}",
    )

    unpushed = make_record(
        "/fixtures/lifecycle/unpushed-branch",
        git_obs("/fixtures/lifecycle/unpushed-branch", unpushed=True),
    )
    result = classify.classify_path(unpushed, inventory)
    check(
        "unpushed history is REVIEW_REQUIRED",
        result.classification == "REVIEW_REQUIRED" and "unpushed_history" in result.blockers,
        f"{result.classification} {result.blockers}",
    )

    orphaned = authority_records()["/fixtures/lifecycle/repo-alpha-worktrees/orphaned-wt"]
    result = classify.classify_path(orphaned, inventory)
    check(
        "orphaned unresolved terminal is REVIEW_REQUIRED",
        result.classification == "REVIEW_REQUIRED"
        and any(b.startswith("orca_orphaned_terminal") for b in result.blockers),
        f"{result.classification} {result.blockers}",
    )

    reclaimed = make_record(
        "/fixtures/lifecycle/reclaimed-wt",
        {
            "authority": "git",
            "canonical_path": "/fixtures/lifecycle/reclaimed-wt",
            "subject": "reclaimed-wt",
            "observed_at": "2026-08-25T13:00:03Z",
            "facts": {"approved_retirement_recorded": True},
        },
    )
    result = classify.classify_path(reclaimed, inventory)
    check(
        "recorded approved transition yields RECLAIMED",
        result.classification == "RECLAIMED",
        result.classification,
    )

    record = make_record(
        SNAPSHOT_PATH,
        git_obs(SNAPSHOT_PATH, detached=True, ancestor_of_target=True,
                revision="dddd000000000000000000000000000000000004"),
    )
    result = classify.classify_path(record, None)
    check(
        "missing retention inventory caps reclaimability (fail closed)",
        result.classification == "REVIEW_REQUIRED"
        and "retention_inventory_unavailable" in result.blockers,
        f"{result.classification} {result.blockers}",
    )


def main() -> int:
    test_active_openspec_is_protected()
    test_live_orca_terminal_wins_conflict()
    test_runtime_ownership_unknown_blocks_reclaimability()
    test_detached_unique_revision_is_review_required()
    test_proven_ancestor_snapshot_is_reclaimable()
    test_protected_retention_class_excluded_from_candidates()
    test_unknown_ownership_fails_closed()
    test_additional_guards()
    print(f"\n=== RESULTS: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
