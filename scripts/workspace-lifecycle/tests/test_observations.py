#!/usr/bin/env python3
"""Observation tests for workspace-lifecycle-gated-cleanup task 1.1.

Verification contract: the fixture inventory covers each authority (OpenSpec,
Git, Orca, runtime, index) and correlation preserves conflicting observations
rather than selecting the less restrictive state.

Usage: python3 openspec-store/scripts/workspace-lifecycle/tests/test_observations.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import observations  # noqa: E402

FIXTURE = (
    Path(__file__).resolve().parent / "fixtures" / "authority-observations.fixture.json"
)

CONFLICT_PATH = "/fixtures/lifecycle/repo-alpha-worktrees/feature-merged"
MULTI_AUTHORITY_PATH = "/fixtures/lifecycle/repo-alpha"

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


def raw_fixture() -> list:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_fixture_covers_each_authority() -> None:
    print("=== T1: fixture inventory covers each authority ===")
    loaded = observations.load_observations(raw_fixture())
    covered = {obs.authority for obs in loaded}
    check(
        "all five authorities covered",
        covered == set(observations.AUTHORITIES),
        str(sorted(covered)),
    )
    check("observations load without loss", len(loaded) == len(raw_fixture()))


def test_observation_contract_fields() -> None:
    print("=== T2: observations carry the task 1.1 contract fields ===")
    loaded = observations.load_observations(raw_fixture())
    for obs in loaded:
        if not Path(obs.canonical_path).is_absolute():
            check(f"absolute canonical path ({obs.subject})", False, obs.canonical_path)
            return
        if not obs.subject:
            check("subject identity present", False, repr(obs))
            return
        observations.parse_observed_at(obs.observed_at)
    check("canonical path, subject, timestamp valid for all observations", True)

    git_obs = [obs for obs in loaded if obs.authority == "git"]
    check(
        "git observations carry repo/worktree identity and revision",
        all(
            obs.facts.get("repo_identity")
            and obs.facts.get("worktree_id")
            and (obs.facts.get("branch") or obs.facts.get("detached"))
            and obs.revision
            for obs in git_obs
        ),
    )
    openspec_obs = [obs for obs in loaded if obs.authority == "openspec"]
    check(
        "openspec observations carry change identity and task activity",
        all(obs.facts.get("change") and "incomplete_tasks" in obs.facts for obs in openspec_obs),
    )
    orca_obs = [obs for obs in loaded if obs.authority == "orca"]
    check(
        "orca observations carry workspace identity and activity state",
        all(
            obs.facts.get("workspace_id")
            and "agent_state" in obs.facts
            and "terminal_state" in obs.facts
            for obs in orca_obs
        ),
    )


def test_correlation_groups_by_canonical_path() -> None:
    print("=== T3: correlation groups observations by canonical path ===")
    loaded = observations.load_observations(raw_fixture())
    records = observations.correlate(loaded)
    conflict_record = records[CONFLICT_PATH]
    check(
        "conflicting path correlates git and orca records",
        conflict_record.authorities == {"git", "orca"},
        str(conflict_record.authorities),
    )
    check(
        "both observations retained on the conflicting path",
        len(conflict_record.observations) == 2,
        str(len(conflict_record.observations)),
    )
    multi = records[MULTI_AUTHORITY_PATH]
    check(
        "shared repo path correlates git and index records",
        multi.authorities == {"git", "index"},
        str(multi.authorities),
    )


def test_conflicting_observations_preserved() -> None:
    print("=== T4: conflicting observations are preserved, not softened ===")
    loaded = observations.load_observations(raw_fixture())
    records = observations.correlate(loaded)
    record = records[CONFLICT_PATH]
    git_obs = record.by_authority("git")[0]
    orca_obs = record.by_authority("orca")[0]
    check(
        "git still reports merged and clean",
        git_obs.facts.get("merged_into_target") is True
        and git_obs.facts.get("dirty") is False,
    )
    check(
        "orca still reports live terminal and working agent",
        orca_obs.facts.get("live_terminal") is True
        and orca_obs.facts.get("agent_state") == "working"
        and orca_obs.facts.get("host_activity") is True,
    )
    pairs = record.conflicting_pairs()
    check(
        "conflict detected between reclaimable-leaning git and active orca",
        any(
            left.authority == "git" and right.authority == "orca"
            for left, right in pairs
        ),
        str([(left.authority, right.authority) for left, right in pairs]),
    )
    check(
        "no observation was dropped or rewritten",
        [obs.observed_at for obs in record.observations]
        == ["2026-08-25T12:00:01Z", "2026-08-25T12:00:02Z"],
    )


def test_malformed_observations_rejected() -> None:
    print("=== T5: malformed observations are rejected ===")
    base = raw_fixture()[2]

    def variant(**overrides) -> dict:
        raw = json.loads(json.dumps(base))
        raw.update(overrides)
        return raw

    cases = [
        ("unknown authority", variant(authority="docker")),
        ("relative canonical path", variant(canonical_path="relative/path")),
        ("missing canonical path", variant(canonical_path="")),
        ("missing subject", variant(subject="")),
        ("invalid observed_at", variant(observed_at="not-a-timestamp")),
        ("missing facts", {k: v for k, v in base.items() if k != "facts"}),
    ]
    for name, raw in cases:
        try:
            observations.validate_observation(raw)
            check(f"rejected: {name}", False, "no error raised")
        except observations.ObservationError:
            check(f"rejected: {name}", True)


def main() -> int:
    test_fixture_covers_each_authority()
    test_observation_contract_fields()
    test_correlation_groups_by_canonical_path()
    test_conflicting_observations_preserved()
    test_malformed_observations_rejected()
    print(f"\n=== RESULTS: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
