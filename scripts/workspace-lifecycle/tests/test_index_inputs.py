#!/usr/bin/env python3
"""Index input tests for workspace-lifecycle-gated-cleanup task 1.3.

Verification contract: the approved workspace/index inventory and
knowledge-status.sh --json are consumed as read-only inputs; the dry-run
does not invoke Graphify/GitNexus mutation and skips dirty, watcher-owned,
or non-default targets according to the existing workspace-index-freshness
contracts.

Usage: python3 openspec-store/scripts/workspace-lifecycle/tests/test_index_inputs.py
"""

from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import classify  # noqa: E402
import index_inputs  # noqa: E402
import observations  # noqa: E402
import retention  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
INVENTORY_FIXTURE = FIXTURES / "knowledge-refresh-inventory.fixture.tsv"
STATUS_FIXTURE = FIXTURES / "knowledge-status.fixture.json"
RETENTION_FIXTURE = FIXTURES / "retention-inventory.protected-and-candidate.json"

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


def load_inventory() -> tuple:
    return index_inputs.load_reviewed_inventory(INVENTORY_FIXTURE)


def load_status() -> index_inputs.KnowledgeStatus:
    return index_inputs.parse_knowledge_status(
        json.loads(STATUS_FIXTURE.read_text(encoding="utf-8"))
    )


def entry_by_root(entries: tuple, root: str) -> index_inputs.InventoryEntry:
    return next(e for e in entries if e.canonical_root == root)


def test_reviewed_inventory_loads() -> None:
    print("=== T1: approved repository inventory loads read-only ===")
    entries = load_inventory()
    check("three approved entries parsed", len(entries) == 3, str(len(entries)))
    alpha = entry_by_root(entries, "/fixtures/lifecycle/repo-alpha")
    check(
        "entry carries canonical root, default branch, provider enablement",
        alpha.default_branch == "main"
        and alpha.gitnexus_enabled is True
        and alpha.graphify_enabled is True,
    )
    beta = entry_by_root(entries, "/fixtures/lifecycle/repo-beta")
    check("graphify-disabled entry preserved", beta.graphify_enabled is False)

    bad_dir = Path(__file__).resolve().parent / "fixtures" / "bad-inventory.tsv"
    cases = {
        "wrong field count": "/fixtures/x\tmain\tyes\n",
        "relative root": "relative/root\tmain\tyes\tyes\n",
        "bad enablement flag": "/fixtures/x\tmain\tmaybe\tyes\n",
        "missing default branch": "/fixtures/x\t\tyes\tyes\n",
    }
    for name, content in cases.items():
        bad_dir.write_text(content, encoding="utf-8")
        try:
            index_inputs.load_reviewed_inventory(bad_dir)
            check(f"rejected: {name}", False, "no error raised")
        except index_inputs.IndexInputError:
            check(f"rejected: {name}", True)
    bad_dir.unlink()


def test_knowledge_status_parses() -> None:
    print("=== T2: knowledge-status.sh --json output parses read-only ===")
    status = load_status()
    check(
        "envelope fields present",
        bool(status.generated and status.inventory_digest and status.provider_versions),
    )
    alpha_rows = status.provider_rows("repo-alpha")
    check(
        "provider rows expose indexedSha/headSha/freshness/freshnessRule",
        len(alpha_rows) == 2
        and all(
            row.facts.get("indexedSha")
            and row.facts.get("headSha")
            and row.facts.get("freshness")
            and row.facts.get("freshnessRule") == "commit_equality"
            for row in alpha_rows
        ),
    )
    check("dirty repo detected via Dirty row", status.is_dirty("repo-beta"))
    check("dirty file count exposed", status.dirty_files("repo-beta") == 3)
    check("watcher state detected", status.watcher_active("repo-gamma"))
    check(
        "worktree rows exposed",
        status.worktrees("repo-alpha")
        == [("/fixtures/lifecycle/repo-alpha-worktrees/feature-x", "feature-x")],
    )

    document = json.loads(STATUS_FIXTURE.read_text(encoding="utf-8"))
    broken = json.loads(json.dumps(document))
    broken.pop("repos")
    try:
        index_inputs.parse_knowledge_status(broken)
        check("rejected: missing repos", False, "no error raised")
    except index_inputs.IndexInputError:
        check("rejected: missing repos", True)
    broken = json.loads(json.dumps(document))
    broken["repos"][0]["freshnessRule"] = "timestamp_recency"
    try:
        index_inputs.parse_knowledge_status(broken)
        check("rejected: non-contract freshnessRule", False, "no error raised")
    except index_inputs.IndexInputError:
        check("rejected: non-contract freshnessRule", True)
    broken = json.loads(json.dumps(document))
    broken["repos"][1]["tool"] = "Unknown"
    try:
        index_inputs.parse_knowledge_status(broken)
        check("rejected: unknown tool row", False, "no error raised")
    except index_inputs.IndexInputError:
        check("rejected: unknown tool row", True)


def test_skip_classification_follows_existing_contracts() -> None:
    print("=== T3: dirty, watcher-owned, and non-default targets are skipped ===")
    entries = load_inventory()
    status = load_status()
    alpha = entry_by_root(entries, "/fixtures/lifecycle/repo-alpha")
    beta = entry_by_root(entries, "/fixtures/lifecycle/repo-beta")
    gamma = entry_by_root(entries, "/fixtures/lifecycle/repo-gamma")

    clean_default = index_inputs.classify_index_target(
        alpha, status,
        index_inputs.IndexTarget(path=alpha.canonical_root, provider="gitnexus",
                                 branch="main"),
    )
    check("clean fresh default target eligible", clean_default.eligible is True)

    dirty = index_inputs.classify_index_target(
        beta, status,
        index_inputs.IndexTarget(path=beta.canonical_root, provider="gitnexus",
                                 branch="main"),
    )
    check("dirty target skipped_dirty", dirty.skip_reason == "skipped_dirty", str(dirty))

    watcher = index_inputs.classify_index_target(
        gamma, status,
        index_inputs.IndexTarget(path=gamma.canonical_root, provider="graphify",
                                 branch="main"),
    )
    check("watcher-owned root watcher_active", watcher.skip_reason == "watcher_active", str(watcher))

    detached = index_inputs.classify_index_target(
        alpha, status,
        index_inputs.IndexTarget(path="/fixtures/lifecycle/repo-alpha-worktrees/detached-snap",
                                 provider="gitnexus", detached=True),
    )
    check("detached worktree detached_head", detached.skip_reason == "detached_head", str(detached))

    ephemeral = index_inputs.classify_index_target(
        alpha, status,
        index_inputs.IndexTarget(path="/fixtures/lifecycle/repo-alpha/.claude/worktrees/wt-1",
                                 provider="gitnexus", branch="wt-1"),
    )
    check("ephemeral worktree skipped", ephemeral.skip_reason == "ephemeral_worktree", str(ephemeral))

    stale = index_inputs.classify_index_target(
        alpha, status,
        index_inputs.IndexTarget(path="/fixtures/lifecycle/repo-alpha-worktrees/old-feature",
                                 provider="gitnexus", branch="old-feature",
                                 branch_age_days=45),
    )
    check("stale feature worktree skipped", stale.skip_reason == "stale_worktree", str(stale))

    dispatch_non_default = index_inputs.classify_index_target(
        alpha, status,
        index_inputs.IndexTarget(path="/fixtures/lifecycle/repo-alpha-worktrees/feature-x",
                                 provider="gitnexus", branch="feature-x"),
        context="dispatch",
    )
    check(
        "dispatch on non-default branch skipped",
        dispatch_non_default.skip_reason == "non_default_branch",
        str(dispatch_non_default),
    )

    nightly_feature = index_inputs.classify_index_target(
        alpha, status,
        index_inputs.IndexTarget(path="/fixtures/lifecycle/repo-alpha-worktrees/feature-x",
                                 provider="gitnexus", branch="feature-x",
                                 branch_age_days=2),
        context="nightly",
    )
    check(
        "nightly refresh of fresh non-detached worktree eligible",
        nightly_feature.eligible is True,
        str(nightly_feature),
    )

    uninitialized = index_inputs.classify_index_target(
        alpha, status,
        index_inputs.IndexTarget(path="/fixtures/lifecycle/repo-alpha-worktrees/new-wt",
                                 provider="gitnexus", branch="new-wt",
                                 has_index_state=False),
    )
    check(
        "uninitialized target skipped_uninitialized",
        uninitialized.skip_reason == "skipped_uninitialized",
        str(uninitialized),
    )

    disabled = index_inputs.classify_index_target(
        beta, status,
        index_inputs.IndexTarget(path=beta.canonical_root, provider="graphify",
                                 branch="main"),
    )
    check("disabled provider not a target", disabled.skip_reason == "provider_disabled", str(disabled))

    merge_state = index_inputs.classify_index_target(
        alpha, status,
        index_inputs.IndexTarget(path=alpha.canonical_root, provider="gitnexus",
                                 branch="main", in_merge_state=True),
    )
    check(
        "merge-state target skipped_merge_state",
        merge_state.skip_reason == "skipped_merge_state",
        str(merge_state),
    )


def test_status_feeds_index_observations_and_classification() -> None:
    print("=== T4: status rows become read-only index observations ===")
    entries = load_inventory()
    status = load_status()
    obs = index_inputs.build_index_observations(entries, status)
    check(
        "index observations emitted for provider rows", len(obs) == 4, str(len(obs))
    )
    check(
        "all observations use the index authority",
        all(o.authority == "index" for o in obs),
    )
    gamma_obs = [o for o in obs if o.canonical_path == "/fixtures/lifecycle/repo-gamma"]
    check(
        "watcher-owned root carries watcher_active fact",
        len(gamma_obs) == 1 and gamma_obs[0].facts.get("watcher_active") is True,
    )

    inventory = retention.load_inventory(RETENTION_FIXTURE)
    record = observations.correlate(obs)["/fixtures/lifecycle/repo-gamma"]
    result = classify.classify_path(record, inventory)
    check(
        "watcher-owned root classifies PROTECTED via index authority",
        result.classification == "PROTECTED"
        and any(b.startswith("index_watcher_active") for b in result.blockers),
        f"{result.classification} {result.blockers}",
    )


def test_module_is_read_only_by_construction() -> None:
    print("=== T5: module never invokes mutation surfaces ===")
    source = inspect.getsource(index_inputs)
    for forbidden in ("import subprocess", "subprocess.", "os.system", "Popen"):
        check(f"no mutation surface: {forbidden!r}", forbidden not in source)
    code_only = source.replace(f'"""{index_inputs.__doc__}"""', "", 1)
    for forbidden in ("refresh-knowledge-indexes", "graphify update", "gitnexus analyze"):
        check(f"no index tool invocation: {forbidden!r}", forbidden not in code_only)


def main() -> int:
    test_reviewed_inventory_loads()
    test_knowledge_status_parses()
    test_skip_classification_follows_existing_contracts()
    test_status_feeds_index_observations_and_classification()
    test_module_is_read_only_by_construction()
    print(f"\n=== RESULTS: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
