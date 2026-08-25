#!/usr/bin/env python3
"""Approval tests for workspace-lifecycle-gated-cleanup task 2.3.

Verification contract: operator approval is recorded against the exact plan
identity and requires a fresh pre-action observation; stale or mismatched
approval is rejected before any lifecycle mutation. All inputs are synthetic
fixtures; nothing is mutated.

Usage: python3 openspec-store/scripts/workspace-lifecycle/tests/test_approval.py
"""

from __future__ import annotations

import inspect
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import approval  # noqa: E402
import classify  # noqa: E402
import manifest  # noqa: E402
import observations  # noqa: E402
import retention  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
RETENTION_FIXTURE = FIXTURES / "retention-inventory.protected-and-candidate.json"

RECLAIMABLE_PATH = "/fixtures/approval/reclaimable-wt"
PROTECTED_PATH = "/fixtures/approval/live-wt"

GENERATED_AT = "2026-08-25T17:00:00Z"
OBSERVED_AT = "2026-08-25T16:30:00Z"
APPROVED_AT = "2026-08-25T17:30:00Z"
PRE_ACTION_AT = "2026-08-25T17:55:00Z"
NOW = "2026-08-25T18:00:00Z"

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


def git_obs(path: str, observed_at: str, **extra) -> dict:
    facts = {
        "repo_identity": "/fixtures/approval/repo/.git",
        "worktree_id": f"wt-{Path(path).name}",
        "branch": Path(path).name,
        "detached": True,
        "revision": "abab0000000000000000000000000000000000ab",
        "dirty": False,
        "generated_only": False,
        "unpushed": False,
        "merged_into_target": False,
        "ancestor_of_target": True,
    }
    facts.update(extra)
    return {
        "authority": "git",
        "canonical_path": path,
        "subject": Path(path).name,
        "observed_at": observed_at,
        "facts": facts,
    }


def orca_live_obs(path: str, observed_at: str) -> dict:
    return {
        "authority": "orca",
        "canonical_path": path,
        "subject": f"ws-{Path(path).name}",
        "observed_at": observed_at,
        "facts": {
            "workspace_id": f"ws-{Path(path).name}",
            "isPinned": False,
            "agent_state": "working",
            "live_terminal": True,
            "terminal_state": "connected",
            "attached_pty": False,
            "host_activity": True,
            "child_worktrees": [],
            "parent_worktree": None,
        },
    }


def inventory() -> retention.RetentionInventory:
    return retention.load_inventory(RETENTION_FIXTURE)


def build_plan() -> dict:
    raw = [
        git_obs(RECLAIMABLE_PATH, OBSERVED_AT),
        git_obs(PROTECTED_PATH, OBSERVED_AT),
        orca_live_obs(PROTECTED_PATH, OBSERVED_AT),
    ]
    records = observations.correlate(observations.load_observations(raw))
    entries = []
    for path in sorted(records):
        result = classify.classify_path(records[path], inventory())
        entries.append(
            manifest.build_entry(
                path, records[path].observations, result.classification,
                result.blockers, result.evidence, GENERATED_AT,
            )
        )
    return manifest.build_manifest("plan-approval-0001", entries, GENERATED_AT, inventory())


def valid_approval(plan: dict) -> approval.ApprovalRecord:
    return approval.make_approval(
        plan_id=plan["plan_id"],
        plan_identity=plan["plan_identity"],
        operator="operator-fixture",
        approval_note="Reviewed dry-run manifest; approve retirement review of the proven snapshot worktree.",
        approved_at=APPROVED_AT,
        paths=[RECLAIMABLE_PATH],
    )


def fresh_pre_action(path: str = RECLAIMABLE_PATH, observed_at: str = PRE_ACTION_AT) -> dict:
    records = observations.correlate(
        observations.load_observations([git_obs(path, observed_at)])
    )
    return records


def test_valid_approval_authorizes() -> None:
    print("=== T1: exact plan identity + fresh pre-action observation authorizes ===")
    plan = build_plan()
    result = approval.validate_approval(
        valid_approval(plan), plan, fresh_pre_action(), inventory(), now=NOW,
    )
    check("authorized", result.authorized is True, str(result.rejections))
    check("approved path recorded", result.approved_paths == (RECLAIMABLE_PATH,))


def test_mismatched_approval_rejected() -> None:
    print("=== T2: mismatched approval is rejected before any mutation ===")
    plan = build_plan()

    wrong_id = approval.make_approval(
        "plan-different", plan["plan_identity"], "operator-fixture",
        "note", APPROVED_AT, [RECLAIMABLE_PATH],
    )
    result = approval.validate_approval(wrong_id, plan, fresh_pre_action(),
                                        inventory(), now=NOW)
    check("wrong plan id rejected",
          result.authorized is False and "plan_id_mismatch" in result.rejections,
          str(result.rejections))

    wrong_identity = approval.make_approval(
        plan["plan_id"], "0" * 64, "operator-fixture",
        "note", APPROVED_AT, [RECLAIMABLE_PATH],
    )
    result = approval.validate_approval(wrong_identity, plan, fresh_pre_action(),
                                        inventory(), now=NOW)
    check("wrong plan identity rejected",
          result.authorized is False and "plan_identity_mismatch" in result.rejections,
          str(result.rejections))

    protected_path = approval.make_approval(
        plan["plan_id"], plan["plan_identity"], "operator-fixture",
        "note", APPROVED_AT, [PROTECTED_PATH],
    )
    result = approval.validate_approval(protected_path, plan,
                                        fresh_pre_action(PROTECTED_PATH),
                                        inventory(), now=NOW)
    check("protected path cannot be approved",
          result.authorized is False
          and any(r.startswith("path_not_reclaimable") for r in result.rejections),
          str(result.rejections))

    unknown_path = approval.make_approval(
        plan["plan_id"], plan["plan_identity"], "operator-fixture",
        "note", APPROVED_AT, ["/fixtures/approval/not-in-plan"],
    )
    result = approval.validate_approval(unknown_path, plan, {}, inventory(), now=NOW)
    check("path not in plan rejected",
          result.authorized is False
          and any(r.startswith("path_not_in_plan") for r in result.rejections),
          str(result.rejections))


def test_stale_approval_rejected() -> None:
    print("=== T3: stale approval and stale pre-action evidence are rejected ===")
    plan = build_plan()

    stale_obs = fresh_pre_action(observed_at="2026-08-25T17:00:00Z")
    result = approval.validate_approval(valid_approval(plan), plan, stale_obs,
                                        inventory(), now=NOW)
    check("60-minute-old pre-action observation rejected",
          result.authorized is False
          and any(r.startswith("stale_pre_action_observation") for r in result.rejections),
          str(result.rejections))

    result = approval.validate_approval(valid_approval(plan), plan, {},
                                        inventory(), now=NOW)
    check("missing pre-action observation rejected",
          result.authorized is False
          and any(r.startswith("missing_pre_action_observation") for r in result.rejections),
          str(result.rejections))

    result = approval.validate_approval(
        valid_approval(plan), plan, fresh_pre_action(), inventory(),
        now="2026-08-26T18:30:00Z",
    )
    check("plan older than 24h is stale",
          result.authorized is False and "stale_plan" in result.rejections,
          str(result.rejections))

    predating = approval.make_approval(
        plan["plan_id"], plan["plan_identity"], "operator-fixture",
        "note", "2026-08-25T16:00:00Z", [RECLAIMABLE_PATH],
    )
    result = approval.validate_approval(predating, plan, fresh_pre_action(),
                                        inventory(), now=NOW)
    check("approval predating the plan rejected",
          result.authorized is False and "approval_predates_plan" in result.rejections,
          str(result.rejections))


def test_pre_action_state_change_rejected() -> None:
    print("=== T4: fresh observation showing new activity blocks approval ===")
    plan = build_plan()
    changed = observations.correlate(
        observations.load_observations([
            git_obs(RECLAIMABLE_PATH, PRE_ACTION_AT),
            orca_live_obs(RECLAIMABLE_PATH, PRE_ACTION_AT),
        ])
    )
    result = approval.validate_approval(valid_approval(plan), plan, changed,
                                        inventory(), now=NOW)
    check("state change to PROTECTED rejected",
          result.authorized is False
          and any(r.startswith("pre_action_state_changed")
                  and r.endswith("PROTECTED") for r in result.rejections),
          str(result.rejections))
    check("no path authorized after state change", result.approved_paths == ())


def test_approval_record_roundtrip_and_secrets() -> None:
    print("=== T5: approval records persist with exact plan identity ===")
    plan = build_plan()
    record = valid_approval(plan)
    with tempfile.TemporaryDirectory(prefix="lifecycle-approval-") as tmp:
        path = approval.record_approval(record, Path(tmp))
        check("record written to scoped dir", path.is_file()
              and path.parent == Path(tmp))
        loaded = approval.load_approval(path)
        check("round-trip preserves exact plan identity",
              loaded.plan_identity == plan["plan_identity"]
              and loaded.plan_id == plan["plan_id"]
              and loaded.paths == (RECLAIMABLE_PATH,))
        document = json.loads(path.read_text(encoding="utf-8"))
        document["token"] = "abc123"
        poisoned = path.with_name("poisoned.json")
        poisoned.write_text(json.dumps(document), encoding="utf-8")
        try:
            approval.load_approval(poisoned)
            check("credential-shaped record rejected", False, "no error raised")
        except approval.ApprovalError as exc:
            check("credential-shaped record rejected",
                  "credential-shaped" in str(exc), str(exc))

    base_kwargs = dict(
        plan_id=plan["plan_id"], plan_identity=plan["plan_identity"],
        operator="operator-fixture", approval_note="note",
        approved_at=APPROVED_AT, paths=[RECLAIMABLE_PATH],
    )
    for name, override in [
        ("missing note", dict(approval_note="")),
        ("missing operator", dict(operator="")),
        ("missing paths", dict(paths=[])),
    ]:
        try:
            approval.make_approval(**{**base_kwargs, **override})
            check(f"rejected: {name}", False, "no error raised")
        except approval.ApprovalError:
            check(f"rejected: {name}", True)


def test_module_is_read_only() -> None:
    print("=== T6: approval module never invokes mutation surfaces ===")
    source = inspect.getsource(approval)
    for forbidden in ("import subprocess", "subprocess.", "os.system", "Popen"):
        check(f"no mutation surface: {forbidden!r}", forbidden not in source)


def main() -> int:
    test_valid_approval_authorizes()
    test_mismatched_approval_rejected()
    test_stale_approval_rejected()
    test_pre_action_state_change_rejected()
    test_approval_record_roundtrip_and_secrets()
    test_module_is_read_only()
    print(f"\n=== RESULTS: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
