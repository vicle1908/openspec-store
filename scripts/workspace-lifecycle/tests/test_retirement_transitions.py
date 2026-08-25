#!/usr/bin/env python3
"""Ordered retirement transition tests for workspace-lifecycle-gated-cleanup
task 3.3.

Verification contract: simulated failure at each transition leaves
completed/pending steps auditable and performs no compensating direct
deletion. Child Orca worktrees retire before parents, Orca
workspace/file-handle release precedes Git worktree removal, branch
deletion is last, and OpenSpec paths defer to OpenSpec lifecycle commands.

Usage: python3 openspec-store/scripts/workspace-lifecycle/tests/test_retirement_transitions.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import observations  # noqa: E402
import retirement  # noqa: E402

OBSERVED_AT = "2026-08-25T19:00:00Z"
REVISION = "beef000000000000000000000000000000000042"

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


def git_obs(path: str, **overrides) -> dict:
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
        "subject": Path(path).name,
        "observed_at": OBSERVED_AT,
        "facts": facts,
    }


def orca_obs(path: str, **overrides) -> dict:
    """Fully released Orca observation; overrides introduce the case."""
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
        "subject": f"ws-{Path(path).name}",
        "observed_at": OBSERVED_AT,
        "facts": facts,
    }


def openspec_obs(path: str, change: str) -> dict:
    return {
        "authority": "openspec",
        "canonical_path": path,
        "subject": change,
        "observed_at": OBSERVED_AT,
        "facts": {"change": change, "incomplete_tasks": 3,
                  "untracked": False, "archived": False},
    }


def record_for(*raw_observations) -> observations.PathRecord:
    loaded = observations.load_observations(list(raw_observations))
    path = loaded[0].canonical_path
    return observations.correlate(loaded)[path]


def orca_plan(path: str = "/fixtures/retire/order-wt") -> retirement.RetirementRecord:
    """Actionable plan for an Orca-managed path with all gates satisfied."""
    record = record_for(orca_obs(path), git_obs(path))
    return retirement.plan_retirement(record, f"plan-{Path(path).name}")


def test_openspec_paths_defer() -> None:
    print("=== T1: OpenSpec paths defer to OpenSpec lifecycle commands ===")
    path = "/fixtures/retire/store/openspec/changes/some-change"
    record = record_for(openspec_obs(path, "some-change"), git_obs(path))
    plan = retirement.plan_retirement(record, "plan-openspec")
    check("record deferred to OpenSpec",
          plan.state == retirement.RECORD_DEFERRED, plan.state)
    check("no generic transitions authorized", plan.steps == {})
    check("deferral blocker retained",
          plan.blockers == ("openspec_lifecycle_deferral",),
          str(plan.blockers))
    check("classification stays REVIEW_REQUIRED",
          plan.classification == "REVIEW_REQUIRED")
    try:
        plan.record_transition(retirement.GIT_WORKTREE_STEP, True)
        check("generic removal refused for OpenSpec path", False,
              "no error raised")
    except retirement.TransitionError:
        check("generic removal refused for OpenSpec path", True)


def test_unsatisfied_gates_block_planning() -> None:
    print("=== T2: unsatisfied gates block transition planning ===")
    unpushed = record_for(
        git_obs("/fixtures/retire/blocked-unpushed", unpushed=True)
    )
    plan = retirement.plan_retirement(unpushed, "plan-unpushed")
    check("preservation failure blocks the plan",
          plan.state == retirement.RECORD_BLOCKED, plan.state)
    check("preservation blocker retained",
          f"git_unpushed_history:{REVISION}" in plan.blockers,
          str(plan.blockers))
    check("blocked plan authorizes no transitions", plan.steps == {})

    pinned_path = "/fixtures/retire/blocked-pinned"
    pinned = record_for(
        orca_obs(pinned_path, isPinned=True), git_obs(pinned_path)
    )
    plan = retirement.plan_retirement(pinned, "plan-pinned")
    check("orca precondition failure blocks the plan",
          plan.state == retirement.RECORD_BLOCKED, plan.state)
    check("orca blocker retained",
          any(b.startswith("orca_pinned") for b in plan.blockers),
          str(plan.blockers))
    try:
        plan.record_transition(retirement.GIT_WORKTREE_STEP, True)
        check("blocked plan refuses recording", False, "no error raised")
    except retirement.TransitionError:
        check("blocked plan refuses recording", True)


def test_happy_path_follows_ownership_order() -> None:
    print("=== T3: full retirement follows ownership order ===")
    plan = orca_plan()
    check("four ordered steps planned",
          tuple(plan.steps) == retirement.TRANSITION_STEPS,
          str(tuple(plan.steps)))
    check("plan starts in progress and review-held",
          plan.state == retirement.RECORD_IN_PROGRESS
          and plan.classification == "REVIEW_REQUIRED")

    plan.record_transition(retirement.ORCA_CHILDREN_STEP, True,
                           "no active children")
    plan.record_transition(retirement.ORCA_RELEASE_STEP, True,
                           "file handles released")
    plan.record_transition(retirement.GIT_WORKTREE_STEP, True,
                           "worktree absent from registry")
    check("branch deletion only after worktree removal",
          plan.state == retirement.RECORD_IN_PROGRESS
          and plan.pending_steps == (retirement.GIT_BRANCH_STEP,))
    plan.record_transition(retirement.GIT_BRANCH_STEP, True,
                           "branch reference deleted")
    check("record completed", plan.state == retirement.RECORD_COMPLETED)
    check("RECLAIMED only after the approved transition is recorded",
          plan.classification == "RECLAIMED")
    check("every transition audited in order",
          [entry[0] for entry in plan.audit]
          == ["plan"] + list(retirement.TRANSITION_STEPS),
          str(plan.audit))


def test_out_of_order_transitions_refused() -> None:
    print("=== T4: out-of-order transitions are refused ===")
    plan = orca_plan()
    for step in (retirement.GIT_WORKTREE_STEP, retirement.GIT_BRANCH_STEP,
                 retirement.ORCA_RELEASE_STEP):
        try:
            plan.record_transition(step, True)
            check(f"{step} before its turn refused", False, "no error raised")
        except retirement.TransitionError:
            check(f"{step} before its turn refused", True)
    check("refusals leave the plan untouched",
          plan.pending_steps == retirement.TRANSITION_STEPS
          and plan.state == retirement.RECORD_IN_PROGRESS)

    plan.record_transition(retirement.ORCA_CHILDREN_STEP, True)
    plan.record_transition(retirement.ORCA_RELEASE_STEP, True)
    try:
        plan.record_transition(retirement.GIT_BRANCH_STEP, True)
        check("branch deletion before worktree removal refused", False,
              "no error raised")
    except retirement.TransitionError:
        check("branch deletion before worktree removal refused", True)
    try:
        plan.record_transition("filesystem_rm_rf", True)
        check("unknown step refused", False, "no error raised")
    except retirement.TransitionError:
        check("unknown step refused", True)


def test_failure_at_each_transition_is_auditable() -> None:
    print("=== T5: failure at each transition leaves an auditable record ===")
    steps = retirement.TRANSITION_STEPS
    for index, failing_step in enumerate(steps):
        plan = orca_plan(f"/fixtures/retire/fail-at-{index}")
        for prior in steps[:index]:
            plan.record_transition(prior, True, "simulated success")
        plan.record_transition(failing_step, False, "simulated failure")

        check(f"failure at {failing_step}: state FAILED",
              plan.state == retirement.RECORD_FAILED, plan.state)
        check(f"failure at {failing_step}: record stays REVIEW_REQUIRED",
              plan.classification == "REVIEW_REQUIRED", plan.classification)
        check(f"failure at {failing_step}: completed steps audited",
              plan.completed_steps == steps[:index],
              str(plan.completed_steps))
        check(f"failure at {failing_step}: failed step named",
              plan.failed_step == failing_step, str(plan.failed_step))
        check(f"failure at {failing_step}: remaining steps stay pending",
              plan.pending_steps == steps[index + 1:],
              str(plan.pending_steps))
        # No compensating direct deletion: nothing past the failure is
        # skipped or silently completed; every step is accounted exactly
        # once and the record exposes no removal action.
        accounted = (plan.completed_steps + (plan.failed_step,)
                     + plan.pending_steps)
        check(f"failure at {failing_step}: no compensating deletion",
              accounted == steps, str(accounted))


def test_explicit_retry_after_failure() -> None:
    print("=== T6: retry is explicit and safe ===")
    plan = orca_plan()
    plan.record_transition(retirement.ORCA_CHILDREN_STEP, True)
    plan.record_transition(retirement.ORCA_RELEASE_STEP, True)
    plan.record_transition(retirement.GIT_WORKTREE_STEP, False,
                           "worktree removal failed")
    try:
        plan.record_transition(retirement.GIT_BRANCH_STEP, True)
        check("skipping the failed step refused", False, "no error raised")
    except retirement.TransitionError:
        check("skipping the failed step refused", True)

    plan.record_transition(retirement.GIT_WORKTREE_STEP, True,
                           "retry succeeded")
    check("retry clears the failure and resumes in progress",
          plan.state == retirement.RECORD_IN_PROGRESS
          and plan.failed_step is None, plan.state)
    plan.record_transition(retirement.GIT_BRANCH_STEP, True)
    check("retry path completes to RECLAIMED",
          plan.state == retirement.RECORD_COMPLETED
          and plan.classification == "RECLAIMED")
    check("failure and retry both audited",
          (retirement.GIT_WORKTREE_STEP, retirement.STEP_FAILED,
           "worktree removal failed") in plan.audit
          and (retirement.GIT_WORKTREE_STEP, retirement.STEP_COMPLETED,
               "retry succeeded") in plan.audit,
          str(plan.audit))


def test_plain_git_path_skips_orca_steps() -> None:
    print("=== T7: non-Orca paths plan only Git transitions ===")
    record = record_for(git_obs("/fixtures/retire/plain-git-wt"))
    plan = retirement.plan_retirement(record, "plan-plain-git")
    check("only Git steps planned",
          tuple(plan.steps) == (retirement.GIT_WORKTREE_STEP,
                                retirement.GIT_BRANCH_STEP),
          str(tuple(plan.steps)))
    plan.record_transition(retirement.GIT_WORKTREE_STEP, True)
    plan.record_transition(retirement.GIT_BRANCH_STEP, True)
    check("plain Git retirement completes",
          plan.state == retirement.RECORD_COMPLETED
          and plan.classification == "RECLAIMED")


def test_terminal_records_refuse_recording() -> None:
    print("=== T8: completed and deferred records refuse further recording ===")
    plan = orca_plan()
    for step in retirement.TRANSITION_STEPS:
        plan.record_transition(step, True)
    try:
        plan.record_transition(retirement.GIT_BRANCH_STEP, True)
        check("completed record refuses recording", False, "no error raised")
    except retirement.TransitionError:
        check("completed record refuses recording", True)

    path = "/fixtures/retire/store/openspec/changes/done-change"
    deferred = retirement.plan_retirement(
        record_for(openspec_obs(path, "done-change"), git_obs(path)),
        "plan-deferred",
    )
    try:
        deferred.record_transition(retirement.ORCA_CHILDREN_STEP, True)
        check("deferred record refuses recording", False, "no error raised")
    except retirement.TransitionError:
        check("deferred record refuses recording", True)


def main() -> int:
    test_openspec_paths_defer()
    test_unsatisfied_gates_block_planning()
    test_happy_path_follows_ownership_order()
    test_out_of_order_transitions_refused()
    test_failure_at_each_transition_is_auditable()
    test_explicit_retry_after_failure()
    test_plain_git_path_skips_orca_steps()
    test_terminal_records_refuse_recording()
    print(f"\n=== RESULTS: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
