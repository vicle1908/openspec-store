#!/usr/bin/env python3
"""Git preservation gate tests for workspace-lifecycle-gated-cleanup task 3.2.

Verification contract: unpushed, unique, dirty, and ambiguous candidates
remain REVIEW_REQUIRED. Preservation gates cover clean status,
generated-only dirt classification, merge ancestry or squash-equivalence
evidence, remote/backup reachability, and detached revision preservation
(spec "Merge and preservation proof"). All unsatisfied outcomes are
REVIEW-class, never PROTECTED, because the preservation gate is a
retirement-time check rather than a classification.

Usage: python3 openspec-store/scripts/workspace-lifecycle/tests/test_retirement_git.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import observations  # noqa: E402
import retirement  # noqa: E402

OBSERVED_AT = "2026-08-25T18:00:00Z"
REVISION = "abcd000000000000000000000000000000000001"

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


def git_obs(path: str, subject: str = None, **overrides) -> dict:
    """Clean, merge-preserved Git observation; overrides introduce the case."""
    facts = {
        "repo_identity": f"{path}/.git",
        "worktree_id": f"wt-{Path(path).name}",
        "branch": Path(path).name,
        "detached": False,
        "revision": REVISION,
        "dirty": False,
        "generated_only": False,
        "unpushed": False,
        "squash_merged": False,
        "content_equivalent": False,
        "merged_into_target": True,
        "ancestor_of_target": False,
        "remote_reachable": False,
        "backup_reachable": False,
    }
    facts.update(overrides)
    return {
        "authority": "git",
        "canonical_path": path,
        "subject": subject or Path(path).name,
        "observed_at": OBSERVED_AT,
        "facts": facts,
    }


def index_obs(path: str, provider: str = "graphify") -> dict:
    """Index-authority observation proving generated-output ownership."""
    return {
        "authority": "index",
        "canonical_path": path,
        "subject": provider,
        "observed_at": OBSERVED_AT,
        "facts": {
            "provider": provider,
            "freshness": "FRESH",
            "watcher_active": False,
            "dirty": False,
        },
    }


def record_for(*raw_observations) -> observations.PathRecord:
    loaded = observations.load_observations(list(raw_observations))
    path = loaded[0].canonical_path
    return observations.correlate(loaded)[path]


def test_merged_ancestry_satisfies_gate() -> None:
    print("=== T1: clean merged branch passes on merge ancestry ===")
    record = record_for(git_obs("/fixtures/retire/merged-wt"))
    result = retirement.git_preservation_gate(record)
    check("gate satisfied", result.satisfied is True, str(result.blockers))
    check("merge ancestry recorded as evidence",
          f"merge_ancestry:{REVISION}" in result.evidence,
          str(result.evidence))
    check("no review flag on satisfied gate", result.review_required is False)


def test_detached_ancestor_snapshot_passes() -> None:
    print("=== T2: clean detached ancestor snapshot passes with proof ===")
    record = record_for(
        git_obs("/fixtures/retire/deploy-source-wt", detached=True,
                merged_into_target=False, ancestor_of_target=True)
    )
    result = retirement.git_preservation_gate(record)
    check("gate satisfied", result.satisfied is True, str(result.blockers))
    check("detached ancestor proof recorded",
          f"detached_ancestor_proven:{REVISION}" in result.evidence,
          str(result.evidence))
    check("merge ancestry evidence retained",
          f"merge_ancestry:{REVISION}" in result.evidence,
          str(result.evidence))


def test_detached_unique_revision_is_review() -> None:
    print("=== T3: detached unique revision remains REVIEW_REQUIRED ===")
    record = record_for(
        git_obs("/fixtures/retire/unique-detached-wt", detached=True,
                merged_into_target=False, ancestor_of_target=False)
    )
    result = retirement.git_preservation_gate(record)
    check("gate blocks unique detached revision", result.satisfied is False)
    check("blocker names the unique revision",
          f"git_detached_unique_revision:{REVISION}" in result.blockers,
          str(result.blockers))
    check("block is review-class", result.review_required is True)


def test_detached_revision_preserved_by_remote_or_backup() -> None:
    print("=== T4: detached revision preserved by remote/backup passes ===")
    remote = record_for(
        git_obs("/fixtures/retire/remote-detached-wt", detached=True,
                merged_into_target=False, remote_reachable=True)
    )
    result = retirement.git_preservation_gate(remote)
    check("remote reachability satisfies the gate",
          result.satisfied is True
          and f"remote_reachable:{REVISION}" in result.evidence,
          f"{result.blockers} {result.evidence}")

    backup = record_for(
        git_obs("/fixtures/retire/backup-detached-wt", detached=True,
                merged_into_target=False, backup_reachable=True)
    )
    result = retirement.git_preservation_gate(backup)
    check("backup reachability satisfies the gate",
          result.satisfied is True
          and f"backup_reachable:{REVISION}" in result.evidence,
          f"{result.blockers} {result.evidence}")


def test_unpushed_history_is_review() -> None:
    print("=== T5: unpushed history remains REVIEW_REQUIRED ===")
    record = record_for(git_obs("/fixtures/retire/unpushed-wt", unpushed=True))
    result = retirement.git_preservation_gate(record)
    check("gate blocks unpushed history", result.satisfied is False)
    check("blocker names the unpushed revision",
          f"git_unpushed_history:{REVISION}" in result.blockers,
          str(result.blockers))
    check("block is review-class (preservation approval required)",
          result.review_required is True)


def test_non_generated_dirt_is_review() -> None:
    print("=== T6: non-generated dirt remains REVIEW_REQUIRED ===")
    record = record_for(git_obs("/fixtures/retire/dirty-wt", dirty=True))
    result = retirement.git_preservation_gate(record)
    check("gate blocks non-generated dirt", result.satisfied is False)
    check("blocker names non-generated dirt",
          "git_non_generated_dirt" in result.blockers, str(result.blockers))
    check("block is review-class", result.review_required is True)


def test_generated_only_dirt_classification() -> None:
    print("=== T7: generated-only dirt needs index confirmation ===")
    confirmed_path = "/fixtures/retire/generated-confirmed-wt"
    confirmed = record_for(
        git_obs(confirmed_path, dirty=True, generated_only=True),
        index_obs(confirmed_path),
    )
    result = retirement.git_preservation_gate(confirmed)
    check("index-confirmed generated dirt does not block",
          result.satisfied is True, str(result.blockers))
    check("confirmed generated dirt recorded as evidence",
          f"generated_only_dirt_confirmed:{REVISION}" in result.evidence,
          str(result.evidence))

    unconfirmed = record_for(
        git_obs("/fixtures/retire/generated-unconfirmed-wt", dirty=True,
                generated_only=True)
    )
    result = retirement.git_preservation_gate(unconfirmed)
    check("unconfirmed generated dirt remains REVIEW_REQUIRED",
          result.satisfied is False
          and "git_generated_dirt_unconfirmed" in result.blockers
          and result.review_required is True,
          str(result.blockers))


def test_squash_equivalence_evidence() -> None:
    print("=== T8: squash-merge needs content-equivalence evidence ===")
    proven = record_for(
        git_obs("/fixtures/retire/squash-proven-wt", squash_merged=True,
                content_equivalent=True, merged_into_target=False)
    )
    result = retirement.git_preservation_gate(proven)
    check("proven squash equivalence satisfies the gate",
          result.satisfied is True, str(result.blockers))
    check("squash equivalence proof recorded",
          f"squash_equivalence_proven:{REVISION}" in result.evidence,
          str(result.evidence))

    ambiguous = record_for(
        git_obs("/fixtures/retire/squash-ambiguous-wt", squash_merged=True,
                content_equivalent=False, merged_into_target=False)
    )
    result = retirement.git_preservation_gate(ambiguous)
    check("ambiguous squash equivalence remains REVIEW_REQUIRED",
          result.satisfied is False
          and "git_squash_equivalence_unresolved" in result.blockers
          and result.review_required is True,
          str(result.blockers))


def test_missing_preservation_proof_is_review() -> None:
    print("=== T9: clean but unpreserved history remains REVIEW_REQUIRED ===")
    record = record_for(
        git_obs("/fixtures/retire/no-proof-wt", merged_into_target=False)
    )
    result = retirement.git_preservation_gate(record)
    check("gate blocks without preservation proof", result.satisfied is False)
    check("blocker names missing preservation proof",
          "git_preservation_not_proven" in result.blockers,
          str(result.blockers))
    check("block is review-class", result.review_required is True)


def test_no_git_observations_fails_closed() -> None:
    print("=== T10: missing Git observations fail closed ===")
    record = record_for({
        "authority": "runtime",
        "canonical_path": "/fixtures/retire/no-git-wt",
        "subject": "no-git-owner",
        "observed_at": OBSERVED_AT,
        "facts": {"kind": "process", "owner": "", "active": False,
                  "available": True},
    })
    result = retirement.git_preservation_gate(record)
    check("gate blocks without Git observations", result.satisfied is False)
    check("blocker names missing observations",
          result.blockers == ("git_no_observations",), str(result.blockers))
    check("block is review-class", result.review_required is True)


def test_unsatisfied_outcomes_are_review_class() -> None:
    print("=== T11: every unsatisfied outcome is REVIEW-class ===")
    blocked_records = [
        record_for(git_obs("/fixtures/retire/audit-unpushed", unpushed=True)),
        record_for(git_obs("/fixtures/retire/audit-detached", detached=True,
                           merged_into_target=False)),
        record_for(git_obs("/fixtures/retire/audit-dirty", dirty=True)),
        record_for(git_obs("/fixtures/retire/audit-squash", squash_merged=True,
                           merged_into_target=False)),
        record_for(git_obs("/fixtures/retire/audit-noproof",
                           merged_into_target=False)),
    ]
    for record in blocked_records:
        result = retirement.git_preservation_gate(record)
        check(f"review-class for {Path(record.canonical_path).name}",
              result.satisfied is False and result.review_required is True,
              f"satisfied={result.satisfied} review={result.review_required}")


def main() -> int:
    test_merged_ancestry_satisfies_gate()
    test_detached_ancestor_snapshot_passes()
    test_detached_unique_revision_is_review()
    test_detached_revision_preserved_by_remote_or_backup()
    test_unpushed_history_is_review()
    test_non_generated_dirt_is_review()
    test_generated_only_dirt_classification()
    test_squash_equivalence_evidence()
    test_missing_preservation_proof_is_review()
    test_no_git_observations_fails_closed()
    test_unsatisfied_outcomes_are_review_class()
    print(f"\n=== RESULTS: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
