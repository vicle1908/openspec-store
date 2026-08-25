#!/usr/bin/env python3
"""Manifest tests for workspace-lifecycle-gated-cleanup task 2.1.

Verification contract: schema validation rejects missing identity, stale
evidence, and credential-shaped fields. Also covers redaction, proposed
owner actions, stable plan identity, and previously-skipped history.

Usage: python3 openspec-store/scripts/workspace-lifecycle/tests/test_manifest.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import classify  # noqa: E402
import manifest  # noqa: E402
import observations  # noqa: E402
import retention  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
AUTHORITY_FIXTURE = FIXTURES / "authority-observations.fixture.json"
RETENTION_FIXTURE = FIXTURES / "retention-inventory.protected-and-candidate.json"

GENERATED_AT = "2026-08-25T14:00:00Z"

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


def correlated_records() -> dict:
    raw = json.loads(AUTHORITY_FIXTURE.read_text(encoding="utf-8"))
    return observations.correlate(observations.load_observations(raw))


def build_valid_manifest(generated_at: str = GENERATED_AT) -> dict:
    records = correlated_records()
    inventory = retention.load_inventory(RETENTION_FIXTURE)
    entries = []
    for path in sorted(records):
        record = records[path]
        result = classify.classify_path(record, inventory)
        entries.append(
            manifest.build_entry(
                path, record.observations, result.classification,
                result.blockers, result.evidence, generated_at,
            )
        )
    return manifest.build_manifest("plan-fixture-0001", entries, generated_at, inventory)


def test_valid_manifest_builds_and_validates() -> None:
    print("=== T1: valid manifest builds and validates ===")
    document = build_valid_manifest()
    check("manifest identity and mode", document["manifest"] == manifest.MANIFEST_NAME
          and document["mode"] == "dry-run")
    check("plan id and plan identity present",
          bool(document["plan_id"] and document["plan_identity"]))
    check("retention policy identity recorded",
          document["retention_policy"]["available"] is True
          and document["retention_policy"]["policy_identity"] == "sha256:fixture-identity-0001")
    entry = document["entries"][0]
    for key in ("canonical_path", "identity", "observations", "classification",
                "blockers", "evidence", "evidence_timestamps", "proposed_owner_action"):
        if key not in entry:
            check(f"entry carries {key}", False, str(sorted(entry)))
            return
    check("entry carries all contract fields", True)
    check("evidence timestamps bracket observations",
          bool(entry["evidence_timestamps"]["generated_at"] == GENERATED_AT))


def test_missing_identity_rejected() -> None:
    print("=== T2: missing identity is rejected ===")
    records = correlated_records()
    record = next(iter(records.values()))
    try:
        manifest.build_manifest("", [], GENERATED_AT)
        check("missing plan id rejected", False, "no error raised")
    except manifest.ManifestError as exc:
        check("missing plan id rejected", "plan id" in str(exc), str(exc))
    try:
        manifest.build_entry("relative/path", record.observations, "PROTECTED", [], [], GENERATED_AT)
        check("non-absolute path identity rejected", False, "no error raised")
    except manifest.ManifestError as exc:
        check("non-absolute path identity rejected", "canonical path" in str(exc), str(exc))

    document = build_valid_manifest()
    document["entries"][0]["observations"][0].pop("subject")
    try:
        manifest.validate_manifest(document)
        check("missing observation subject rejected", False, "no error raised")
    except manifest.ManifestError as exc:
        check("missing observation subject rejected", "subject identity" in str(exc), str(exc))

    document = build_valid_manifest()
    document["entries"][0].pop("canonical_path")
    try:
        manifest.validate_manifest(document)
        check("missing entry path identity rejected", False, "no error raised")
    except manifest.ManifestError as exc:
        check("missing entry path identity rejected", "path identity" in str(exc), str(exc))


def test_stale_evidence_rejected() -> None:
    print("=== T3: stale evidence is rejected ===")
    records = correlated_records()
    record = next(iter(records.values()))
    stale_obs = observations.Observation(
        authority="git", canonical_path=record.canonical_path, subject="stale",
        observed_at="2026-08-24T10:00:00Z", facts={"revision": "s"},
    )
    entry = manifest.build_entry(
        record.canonical_path, [stale_obs], "REVIEW_REQUIRED", ["stale"], [], GENERATED_AT
    )
    try:
        manifest.build_manifest("plan-stale", [entry], GENERATED_AT)
        check("stale observation rejected", False, "no error raised")
    except manifest.ManifestError as exc:
        check("stale observation rejected", "stale" in str(exc), str(exc))

    document = build_valid_manifest()
    document["entries"][0]["observations"][0].pop("observed_at")
    try:
        manifest.validate_manifest(document)
        check("missing evidence timestamp rejected", False, "no error raised")
    except manifest.ManifestError as exc:
        check("missing evidence timestamp rejected", "evidence timestamp" in str(exc), str(exc))

    document = build_valid_manifest()
    document["entries"][0]["observations"][0]["observed_at"] = "2026-08-25T15:00:00Z"
    try:
        manifest.validate_manifest(document)
        check("future evidence timestamp rejected", False, "no error raised")
    except manifest.ManifestError as exc:
        check("future evidence timestamp rejected", "future" in str(exc), str(exc))


def test_credential_fields_rejected_and_redacted() -> None:
    print("=== T4: credential-shaped fields rejected; secrets redacted at build ===")
    document = build_valid_manifest()
    document["entries"][0]["observations"][0]["facts"]["token"] = "abc123"
    try:
        manifest.validate_manifest(document)
        check("credential field rejected", False, "no error raised")
    except manifest.ManifestError as exc:
        check("credential field rejected", "credential-shaped" in str(exc), str(exc))

    document = build_valid_manifest()
    document["entries"][1]["identity"]["request_body"] = "{}"
    try:
        manifest.validate_manifest(document)
        check("request body field rejected", False, "no error raised")
    except manifest.ManifestError as exc:
        check("request body field rejected", "credential-shaped" in str(exc), str(exc))

    secret_obs = observations.Observation(
        authority="runtime", canonical_path="/fixtures/lifecycle/svc",
        subject="svc-owner", observed_at="2026-08-25T13:30:00Z",
        facts={"owner": "svc-owner", "endpoint": "http://127.0.0.1:8080",
               "token": "abc123", "request_body": "{\"x\":1}",
               "nested": {"api_key": "k", "kind": "process"}},
    )
    redacted = manifest.redact_observation(secret_obs)
    check("owner and endpoint metadata retained",
          redacted["facts"].get("owner") == "svc-owner"
          and redacted["facts"].get("endpoint") == "http://127.0.0.1:8080")
    check("token and request body stripped",
          "token" not in redacted["facts"] and "request_body" not in redacted["facts"])
    check("nested secret stripped, nested metadata kept",
          "api_key" not in redacted["facts"]["nested"]
          and redacted["facts"]["nested"].get("kind") == "process")


def test_proposed_owner_actions() -> None:
    print("=== T5: proposed owner actions name the owning authority ===")
    document = build_valid_manifest()
    by_path = {e["canonical_path"]: e for e in document["entries"]}

    conflict = by_path["/fixtures/lifecycle/repo-alpha-worktrees/feature-merged"]
    check("orca-managed protected path -> no action",
          conflict["classification"] == "PROTECTED"
          and conflict["proposed_owner_action"]["action"] == "none")

    runtime_unknown = by_path["/fixtures/lifecycle/mystery-db"]
    check("review-required path -> operator review",
          runtime_unknown["classification"] == "REVIEW_REQUIRED"
          and runtime_unknown["proposed_owner_action"] ==
          {"owner": "operator", "action": "review",
           "note": "operator review required before any lifecycle action"})

    git_obs = observations.load_observations([{
        "authority": "git",
        "canonical_path": "/fixtures/lifecycle/reclaimable-wt",
        "subject": "reclaimable-wt",
        "observed_at": "2026-08-25T13:00:00Z",
        "facts": {"repo_identity": "/fixtures/lifecycle/repo/.git",
                  "worktree_id": "wt-r", "branch": "reclaimable-wt",
                  "detached": True, "revision": "abab0000000000000000000000000000000000ab",
                  "dirty": False, "unpushed": False, "ancestor_of_target": True},
    }])
    inventory = retention.load_inventory(RETENTION_FIXTURE)
    record = observations.correlate(git_obs)["/fixtures/lifecycle/reclaimable-wt"]
    result = classify.classify_path(record, inventory)
    entry = manifest.build_entry(record.canonical_path, record.observations,
                                 result.classification, result.blockers,
                                 result.evidence, GENERATED_AT)
    check("reclaimable git worktree -> git-owned retirement review proposal",
          result.classification == "RECLAIMABLE"
          and entry["proposed_owner_action"]["owner"] == "git"
          and entry["proposed_owner_action"]["action"] == "propose_retirement_review")

    all_actions = json.dumps([e["proposed_owner_action"] for e in document["entries"]])
    check("no action vocabulary contains deletion",
          "delete" not in all_actions and "remove" not in all_actions
          and "prune" not in all_actions)


def test_plan_identity_stable() -> None:
    print("=== T6: plan identity is deterministic and generation-time independent ===")
    first = build_valid_manifest()
    second = build_valid_manifest()
    check("same entries -> same plan identity",
          first["plan_identity"] == second["plan_identity"])
    later = build_valid_manifest(generated_at="2026-08-25T15:00:00Z")
    check("generated_at excluded from plan identity",
          later["plan_identity"] == first["plan_identity"])
    mutated = json.loads(json.dumps(first))
    mutated["entries"][0]["classification"] = "RECLAIMABLE"
    check("changed classification -> different plan identity",
          manifest.plan_identity(mutated["entries"]) != first["plan_identity"])


def test_previously_skipped_history() -> None:
    print("=== T7: later runs distinguish new from previously skipped candidates ===")
    prior = build_valid_manifest()
    current = build_valid_manifest()
    updated = manifest.mark_previously_skipped(current, prior)
    skipped_paths = [e["canonical_path"] for e in updated["entries"]
                     if e["previously_skipped"]]
    prior_skipped = [e["canonical_path"] for e in prior["entries"]
                     if e["classification"] in ("PROTECTED", "REVIEW_REQUIRED")]
    check("previously skipped paths flagged", sorted(skipped_paths) == sorted(prior_skipped),
          f"{len(skipped_paths)} vs {len(prior_skipped)}")
    check("at least one previously skipped path exists", len(skipped_paths) > 0)


def main() -> int:
    test_valid_manifest_builds_and_validates()
    test_missing_identity_rejected()
    test_stale_evidence_rejected()
    test_credential_fields_rejected_and_redacted()
    test_proposed_owner_actions()
    test_plan_identity_stable()
    test_previously_skipped_history()
    print(f"\n=== RESULTS: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
