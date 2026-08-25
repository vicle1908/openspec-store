#!/usr/bin/env python3
"""Orca retirement precondition tests for workspace-lifecycle-gated-cleanup
task 3.1.

Verification contract: fixtures cover pinned, orphaned, interrupted,
child-before-parent, and released-handle transitions. All fixtures are
synthetic; no real Orca state is queried or mutated.

Usage: python3 openspec-store/scripts/workspace-lifecycle/tests/test_retirement_orca.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import observations  # noqa: E402
import retirement  # noqa: E402

OBSERVED_AT = "2026-08-25T17:00:00Z"

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


def orca_obs(path: str, subject: str = None, **overrides) -> dict:
    """Fully released Orca observation; overrides introduce the condition."""
    facts = {
        "workspace_id": f"ws-{Path(path).name}",
        "isPinned": False,
        "agent_state": "idle",
        "live_terminal": False,
        "terminal_state": "closed",
        "attached_pty": False,
        "host_activity": False,
        "child_worktrees": [],
        "parent_worktree": None,
        "file_handles_released": True,
    }
    facts.update(overrides)
    return {
        "authority": "orca",
        "canonical_path": path,
        "subject": subject or f"ws-{Path(path).name}",
        "observed_at": OBSERVED_AT,
        "facts": facts,
    }


def record_for(*raw_observations) -> observations.PathRecord:
    loaded = observations.load_observations(list(raw_observations))
    path = loaded[0].canonical_path
    return observations.correlate(loaded)[path]


def test_pinned_worktree_blocked() -> None:
    print("=== T1: pinned worktree cannot retire ===")
    record = record_for(orca_obs("/fixtures/retire/pinned-wt", isPinned=True))
    result = retirement.orca_preconditions(record)
    check("pinned precondition blocks", result.satisfied is False)
    check("blocker names the pin",
          any(b.startswith("orca_pinned") for b in result.blockers),
          str(result.blockers))
    check("pin is a PROTECTED-class block, not review",
          result.review_required is False)


def test_orphaned_terminal_is_review_block() -> None:
    print("=== T2: orphaned unresolved terminal blocks as REVIEW_REQUIRED ===")
    record = record_for(
        orca_obs("/fixtures/retire/orphaned-wt", terminal_state="orphaned",
                 subject="term-orphaned")
    )
    result = retirement.orca_preconditions(record)
    check("orphaned terminal blocks retirement", result.satisfied is False)
    check("block is review-class (no filesystem removal proposed)",
          result.review_required is True)
    check("blocker names the orphaned terminal",
          any(b.startswith("orca_orphaned_terminal_unresolved") for b in result.blockers),
          str(result.blockers))


def test_working_and_interrupted_agents_blocked() -> None:
    print("=== T3: working/interrupted agents cannot retire ===")
    for state in ("working", "interrupted"):
        record = record_for(
            orca_obs(f"/fixtures/retire/agent-{state}", agent_state=state)
        )
        result = retirement.orca_preconditions(record)
        check(f"{state} agent blocks",
              result.satisfied is False
              and any(b == f"orca_agent_{state}:ws-agent-{state}"
                      for b in result.blockers),
              str(result.blockers))


def test_child_before_parent_ordering() -> None:
    print("=== T4: children retire before parents ===")
    parent = record_for(
        orca_obs("/fixtures/retire/parent-wt",
                 child_worktrees=["/fixtures/retire/child-wt"])
    )

    result = retirement.orca_preconditions(parent)
    check("listed child without state fails closed",
          result.satisfied is False
          and any(b.startswith("orca_active_child_worktrees") for b in result.blockers),
          str(result.blockers))

    result = retirement.orca_preconditions(
        parent, child_states={"/fixtures/retire/child-wt": "PROTECTED"}
    )
    check("active child blocks the parent",
          result.satisfied is False
          and "orca_active_child_worktrees:/fixtures/retire/child-wt" in result.blockers,
          str(result.blockers))

    result = retirement.orca_preconditions(
        parent, child_states={"/fixtures/retire/child-wt": "RECLAIMED"}
    )
    check("retired child clears the parent precondition",
          result.satisfied is True and result.blockers == (),
          str(result.blockers))


def test_file_handle_release_transition() -> None:
    print("=== T5: file-handle release requires explicit evidence ===")
    held = record_for(
        orca_obs("/fixtures/retire/handles-wt", file_handles_released=False)
    )
    result = retirement.orca_preconditions(held)
    check("held file handles block Git removal",
          result.satisfied is False
          and any(b.startswith("orca_file_handles_held") for b in result.blockers),
          str(result.blockers))

    missing_evidence = record_for(
        {
            "authority": "orca",
            "canonical_path": "/fixtures/retire/no-evidence-wt",
            "subject": "ws-no-evidence",
            "observed_at": OBSERVED_AT,
            "facts": {
                "workspace_id": "ws-no-evidence", "isPinned": False,
                "agent_state": "idle", "live_terminal": False,
                "terminal_state": "closed", "attached_pty": False,
                "host_activity": False, "child_worktrees": [],
            },
        }
    )
    result = retirement.orca_preconditions(missing_evidence)
    check("missing release evidence fails closed",
          result.satisfied is False
          and any(b.startswith("orca_file_handles_held") for b in result.blockers),
          str(result.blockers))

    released = record_for(
        orca_obs("/fixtures/retire/released-wt", file_handles_released=True)
    )
    result = retirement.orca_preconditions(released)
    check("released handles clear the precondition",
          result.satisfied is True, str(result.blockers))


def test_live_session_blockers() -> None:
    print("=== T6: connected terminal, host activity, and PTY block ===")
    cases = [
        ("connected terminal",
         dict(live_terminal=True, terminal_state="connected"),
         "orca_terminal_connected"),
        ("host activity", dict(host_activity=True), "orca_host_activity"),
        ("attached PTY", dict(attached_pty=True), "orca_attached_pty"),
    ]
    for name, overrides, expected in cases:
        record = record_for(orca_obs(f"/fixtures/retire/{expected}", **overrides))
        result = retirement.orca_preconditions(record)
        check(f"{name} blocks retirement",
              result.satisfied is False
              and any(b.startswith(expected) for b in result.blockers),
              str(result.blockers))


def test_fully_released_worktree_passes() -> None:
    print("=== T7: fully released Orca worktree satisfies preconditions ===")
    record = record_for(orca_obs("/fixtures/retire/clear-wt"))
    result = retirement.orca_preconditions(record)
    check("all preconditions satisfied", result.satisfied is True,
          str(result.blockers))
    check("no blockers and no review flag",
          result.blockers == () and result.review_required is False)


def test_non_orca_path_not_governed() -> None:
    print("=== T8: non-Orca paths are not governed by Orca preconditions ===")
    record = record_for({
        "authority": "git",
        "canonical_path": "/fixtures/retire/plain-git-wt",
        "subject": "plain-git-wt",
        "observed_at": OBSERVED_AT,
        "facts": {"repo_identity": "/fixtures/retire/repo/.git",
                  "worktree_id": "wt-plain", "branch": "plain-git-wt",
                  "detached": False,
                  "revision": "9999000000000000000000000000000000000099",
                  "dirty": False, "unpushed": False,
                  "ancestor_of_target": True},
    })
    check("path is not Orca-managed", retirement.is_orca_managed(record) is False)
    result = retirement.orca_preconditions(record)
    check("Orca preconditions vacuously satisfied",
          result.satisfied is True and result.blockers == ())


def main() -> int:
    test_pinned_worktree_blocked()
    test_orphaned_terminal_is_review_block()
    test_working_and_interrupted_agents_blocked()
    test_child_before_parent_ordering()
    test_file_handle_release_transition()
    test_live_session_blockers()
    test_fully_released_worktree_passes()
    test_non_orca_path_not_governed()
    print(f"\n=== RESULTS: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
