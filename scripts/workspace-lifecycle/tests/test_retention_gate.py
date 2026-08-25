#!/usr/bin/env python3
"""Retention gate tests for workspace-lifecycle-gated-cleanup task 0.2.

Verification contract: a fixture with a protected retention class is excluded
from lifecycle candidates, and a candidate class remains review-only. Also
covers fail-closed loading (missing identity, secret-shaped fields,
unapproved inventory) and the unavailable-inventory block.

Usage: python3 openspec-store/scripts/workspace-lifecycle/tests/test_retention_gate.py
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import retention  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
GOOD_FIXTURE = FIXTURES / "retention-inventory.protected-and-candidate.json"

PROTECTED_PATH = "/fixtures/retention/reports/archive-readiness-2026-08.md"
CANDIDATE_PATH = "/fixtures/retention/tmp/ephemeral-pytest-cache"
WATCHED_INDEX_PATH = "/fixtures/retention/indexes/watched-graphify-out"
STALE_PATH = "/fixtures/retention/tmp/stale-cache-missing-provenance"
UNLISTED_PATH = "/fixtures/retention/unlisted-worktree"

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


def write_variant(document: dict) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="retention-gate-test-")) / "inventory.json"
    tmp.write_text(json.dumps(document), encoding="utf-8")
    return tmp


def base_document() -> dict:
    return json.loads(GOOD_FIXTURE.read_text(encoding="utf-8"))


def test_protected_class_excluded_from_candidates() -> None:
    print("=== T1: protected retention class is excluded from lifecycle candidates ===")
    inventory = retention.load_inventory(GOOD_FIXTURE)
    candidates = [PROTECTED_PATH, CANDIDATE_PATH, UNLISTED_PATH]
    kept, excluded, review_only = [], [], []
    for path in candidates:
        decision = retention.gate(inventory, path)
        if decision.outcome == retention.EXCLUDED_PROTECTED:
            excluded.append(path)
        elif decision.outcome == retention.REVIEW_ONLY_CANDIDATE:
            review_only.append(path)
        else:
            kept.append(path)
    check("protected path excluded", excluded == [PROTECTED_PATH], str(excluded))
    decision = retention.gate(inventory, PROTECTED_PATH)
    check(
        "exclusion reason records protected class and owner",
        "retained evidence or report" in decision.reason
        and "openspec-store" in decision.reason,
        decision.reason,
    )
    check(
        "protected path never becomes a candidate",
        PROTECTED_PATH not in kept and PROTECTED_PATH not in review_only,
    )


def test_candidate_class_remains_review_only() -> None:
    print("=== T2: candidate class remains review-only ===")
    inventory = retention.load_inventory(GOOD_FIXTURE)
    decision = retention.gate(inventory, CANDIDATE_PATH)
    check(
        "candidate-class entry is review-only",
        decision.outcome == retention.REVIEW_ONLY_CANDIDATE,
        decision.outcome,
    )
    check(
        "review-only is not an approved deletion outcome",
        decision.outcome not in (retention.EXCLUDED_PROTECTED, retention.NOT_GOVERNED)
        or decision.outcome == retention.REVIEW_ONLY_CANDIDATE,
    )
    check(
        "review-only reason names the candidate gate",
        "retention_candidate_review_only" in decision.reason,
        decision.reason,
    )
    check(
        "review-only entry keeps its candidate flag visible",
        decision.entry is not None and decision.entry.candidate is True,
    )


def test_protected_policy_state_excludes_candidate_class() -> None:
    print("=== T3: PROTECTED policy state excludes even a candidate class ===")
    inventory = retention.load_inventory(GOOD_FIXTURE)
    decision = retention.gate(inventory, WATCHED_INDEX_PATH)
    check(
        "candidate class with PROTECTED state is excluded",
        decision.outcome == retention.EXCLUDED_PROTECTED,
        decision.outcome,
    )
    check(
        "reason records watcher ownership",
        "graphify-watcher" in decision.reason,
        decision.reason,
    )


def test_missing_provenance_downgrades_to_review_required() -> None:
    print("=== T4: missing provenance downgrades candidate to REVIEW_REQUIRED ===")
    inventory = retention.load_inventory(GOOD_FIXTURE)
    decision = retention.gate(inventory, STALE_PATH)
    check(
        "unbound provenance is not review-only",
        decision.outcome == retention.REVIEW_REQUIRED,
        decision.outcome,
    )


def test_unavailable_inventory_fails_closed() -> None:
    print("=== T5: unavailable inventory blocks artifact reclaimability ===")
    decision = retention.gate(None, CANDIDATE_PATH)
    check("missing inventory -> UNAVAILABLE", decision.outcome == retention.UNAVAILABLE)
    missing = retention.load_or_unavailable(Path("/nonexistent/retention-inventory.json"))
    check("load_or_unavailable returns None", missing is None)


def test_not_governed_path_passes_through() -> None:
    print("=== T6: path without retention entry is not governed ===")
    inventory = retention.load_inventory(GOOD_FIXTURE)
    decision = retention.gate(inventory, UNLISTED_PATH)
    check("unlisted path -> NOT_GOVERNED", decision.outcome == retention.NOT_GOVERNED)


def test_loader_rejects_missing_policy_identity() -> None:
    print("=== T7: loader rejects missing policy identity ===")
    document = base_document()
    document.pop("policy")
    try:
        retention.load_inventory(write_variant(document))
        check("missing policy rejected", False, "no error raised")
    except retention.RetentionError as exc:
        check("missing policy rejected", "policy identity" in str(exc), str(exc))
    document = base_document()
    document.pop("policy_identity")
    try:
        retention.load_inventory(write_variant(document))
        check("missing policy_identity rejected", False, "no error raised")
    except retention.RetentionError as exc:
        check("missing policy_identity rejected", True, str(exc))


def test_loader_rejects_secret_fields() -> None:
    print("=== T8: loader rejects credential-shaped fields ===")
    document = base_document()
    document["entries"][0]["token"] = "abc123"
    try:
        retention.load_inventory(write_variant(document))
        check("secret field rejected", False, "no error raised")
    except retention.RetentionError as exc:
        check("secret field rejected", "credential-shaped" in str(exc), str(exc))
    document = base_document()
    document["entries"][1]["request_body"] = "{}"
    try:
        retention.load_inventory(write_variant(document))
        check("request body field rejected", False, "no error raised")
    except retention.RetentionError as exc:
        check("request body field rejected", "credential-shaped" in str(exc), str(exc))


def test_loader_rejects_unapproved_inventory() -> None:
    print("=== T9: loader rejects unapproved inventory ===")
    document = base_document()
    document["approval"]["approved"] = False
    try:
        retention.load_inventory(write_variant(document))
        check("unapproved inventory rejected", False, "no error raised")
    except retention.RetentionError as exc:
        check("unapproved inventory rejected", "not approved" in str(exc), str(exc))


def main() -> int:
    test_protected_class_excluded_from_candidates()
    test_candidate_class_remains_review_only()
    test_protected_policy_state_excludes_candidate_class()
    test_missing_provenance_downgrades_to_review_required()
    test_unavailable_inventory_fails_closed()
    test_not_governed_path_passes_through()
    test_loader_rejects_missing_policy_identity()
    test_loader_rejects_secret_fields()
    test_loader_rejects_unapproved_inventory()
    print(f"\n=== RESULTS: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
