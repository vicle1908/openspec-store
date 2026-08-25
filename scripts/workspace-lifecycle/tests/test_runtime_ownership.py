#!/usr/bin/env python3
"""Runtime ownership tests for workspace-lifecycle-gated-cleanup task 4.1.

Verification contract: bounded runtime ownership checks cover processes,
LaunchAgents, containers, databases, rollback copies, and index watchers;
unavailable checks are reported as UNKNOWN; unknown runtime ownership
blocks reclaimability without exposing secrets or request bodies.

Usage: python3 openspec-store/scripts/workspace-lifecycle/tests/test_runtime_ownership.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import classify  # noqa: E402
import manifest  # noqa: E402
import observations  # noqa: E402
import retention  # noqa: E402
import runtime  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
RETENTION_FIXTURE = FIXTURES / "retention-inventory.protected-and-candidate.json"

OBSERVED_AT = "2026-08-25T20:00:00Z"
REVISION = "cafe000000000000000000000000000000000021"

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


def quiet_probe(kind: str):
    """Available check that finds no active owner."""
    def probe(path: str):
        return runtime.RuntimeCheckOutcome(kind=kind, available=True,
                                           active=False)
    return probe


def all_quiet_probes() -> dict:
    return {kind: quiet_probe(kind) for kind in runtime.RUNTIME_KINDS}


def git_obs(path: str, **overrides) -> dict:
    """Clean Git observation with preservation proven via ancestry."""
    facts = {
        "repo_identity": f"{path}/.git",
        "worktree_id": f"wt-{Path(path).name}",
        "branch": Path(path).name,
        "detached": False,
        "revision": REVISION,
        "dirty": False,
        "generated_only": False,
        "unpushed": False,
        "merged_into_target": False,
        "ancestor_of_target": True,
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


def record_for(*raw_observations) -> observations.PathRecord:
    loaded = observations.load_observations(list(raw_observations))
    path = loaded[0].canonical_path
    return observations.correlate(loaded)[path]


def retention_inventory() -> retention.RetentionInventory:
    return retention.load_inventory(RETENTION_FIXTURE)


def test_all_six_kinds_covered() -> None:
    print("=== T1: bounded checks cover all six runtime kinds ===")
    path = "/fixtures/runtime/all-kinds"
    emitted = runtime.runtime_observations(path, all_quiet_probes(),
                                           OBSERVED_AT)
    check("one observation per kind", len(emitted) == 6, str(len(emitted)))
    kinds = tuple(obs["facts"]["kind"] for obs in emitted)
    check("kinds match the bounded surface", kinds == runtime.RUNTIME_KINDS,
          str(kinds))
    check("all observations validate against the task 1.1 contract",
          all(isinstance(obs, observations.Observation)
              for obs in observations.load_observations(emitted)))
    check("quiet checks report available and inactive",
          all(obs["facts"]["available"] is True
              and obs["facts"]["active"] is False for obs in emitted))


def test_missing_probe_reports_unknown() -> None:
    print("=== T2: missing probe reports UNKNOWN instead of skipping ===")
    path = "/fixtures/runtime/missing-probes"
    emitted = runtime.runtime_observations(path, {}, OBSERVED_AT)
    check("every kind still observed", len(emitted) == 6, str(len(emitted)))
    check("all unavailable",
          all(obs["facts"]["available"] is False
              and obs["facts"]["active"] is False for obs in emitted))
    check("unknown subjects named per kind",
          all(obs["subject"] == f"{obs['facts']['kind']}-unknown"
              for obs in emitted),
          str([obs["subject"] for obs in emitted]))


def test_failing_probes_fail_closed() -> None:
    print("=== T3: failing, None, and mismatched probes fail closed ===")
    path = "/fixtures/runtime/failing-probes"

    def raising(path_: str):
        raise RuntimeError("probe backend unavailable")

    def none_probe(path_: str):
        return None

    def wrong_kind(path_: str):
        # Registered under "container" but reports a different kind.
        return runtime.RuntimeCheckOutcome(kind="database", available=True,
                                           active=True, owner="wrong")

    def wrong_type(path_: str):
        return {"active": True}

    probes = {
        "process": raising,
        "launchagent": none_probe,
        "container": wrong_kind,
        "database": wrong_type,
    }
    emitted = runtime.runtime_observations(path, probes, OBSERVED_AT)
    by_kind = {obs["facts"]["kind"]: obs for obs in emitted}
    for kind in ("process", "launchagent", "container", "database"):
        check(f"{kind} probe failure degrades to UNKNOWN",
              by_kind[kind]["facts"]["available"] is False
              and by_kind[kind]["facts"]["active"] is False,
              str(by_kind[kind]["facts"]))
    check("scan still covers every kind", len(emitted) == 6)

    try:
        runtime.run_check("filesystem_sweep", path, None)
        check("unknown kind refused", False, "no error raised")
    except ValueError:
        check("unknown kind refused", True)


def test_active_owner_is_protected() -> None:
    print("=== T4: active runtime owner protects the path ===")
    path = "/fixtures/runtime/service-data"

    def active_process(path_: str):
        return runtime.RuntimeCheckOutcome(
            kind="process", available=True, active=True,
            owner="tdt-scheduler", detail={"endpoint": "unix://local"})

    probes = all_quiet_probes()
    probes["process"] = active_process
    raw = runtime.runtime_observations(path, probes, OBSERVED_AT)
    record = record_for(*raw)
    result = classify.classify_path(record, retention_inventory())
    check("active owner classifies PROTECTED",
          result.classification == "PROTECTED", result.classification)
    check("blocker identifies owner without secrets",
          "runtime_owner:process:tdt-scheduler" in result.blockers,
          str(result.blockers))


def test_unknown_runtime_blocks_reclaimability() -> None:
    print("=== T5: unknown runtime ownership blocks reclaimability ===")
    path = "/fixtures/runtime/unknown-owner-wt"
    raw = runtime.runtime_observations(path, {}, OBSERVED_AT)
    record = record_for(git_obs(path), *raw)
    result = classify.classify_path(record, retention_inventory())
    check("git preservation alone cannot win over UNKNOWN runtime",
          result.classification == "REVIEW_REQUIRED",
          result.classification)
    check("blockers name the unavailable checks",
          any(b.startswith("runtime_ownership_unknown:")
              for b in result.blockers),
          str(result.blockers))
    check("all six kinds block",
          sum(1 for b in result.blockers
              if b.startswith("runtime_ownership_unknown:")) == 6,
          str(result.blockers))


def test_quiet_runtime_allows_reclaimability() -> None:
    print("=== T6: available, inactive checks do not block reclaimability ===")
    path = "/fixtures/runtime/quiet-wt"
    raw = runtime.runtime_observations(path, all_quiet_probes(), OBSERVED_AT)
    record = record_for(git_obs(path), *raw)
    result = classify.classify_path(record, retention_inventory())
    check("preserved, clean, unowned path is RECLAIMABLE",
          result.classification == "RECLAIMABLE",
          f"{result.classification} {result.blockers}")


def test_secrets_never_enter_observations() -> None:
    print("=== T7: secrets and request bodies never enter observations ===")
    path = "/fixtures/runtime/secret-probe"

    def leaky_probe(path_: str):
        return runtime.RuntimeCheckOutcome(
            kind="database", available=True, active=True,
            owner="mystery-db",
            detail={
                "endpoint": "postgres://localhost:5432/mystery",
                "api_key": "sk-live-12345",
                "password": "hunter2",
                "request_body": "{\"user\": \"exfiltrate\"}",
                "response_body": "<secret-payload/>",
                "authorization": "Bearer abc.def.ghi",
                "auth_token": "tok-999",
            })

    probes = all_quiet_probes()
    probes["database"] = leaky_probe
    emitted = runtime.runtime_observations(path, probes, OBSERVED_AT)
    db = next(obs for obs in emitted if obs["facts"]["kind"] == "database")
    facts = db["facts"]
    leaked = [key for key in facts
              if manifest._SECRET_FIELD_PATTERN.search(str(key))]
    check("no secret-shaped keys survive redaction", leaked == [],
          str(leaked))
    check("secret values absent from facts",
          not any("hunter2" in str(v) or "sk-live-12345" in str(v)
                  or "exfiltrate" in str(v) or "Bearer" in str(v)
                  for v in facts.values()),
          str(facts))
    check("non-secret owner/endpoint metadata retained",
          facts["owner"] == "mystery-db"
          and facts.get("endpoint") == "postgres://localhost:5432/mystery"
          and facts["active"] is True,
          str(facts))
    check("redaction is idempotent on emitted facts",
          manifest.redact_facts(facts) == facts)

    # The emitted observations must survive manifest secret rejection.
    record = record_for(*emitted)
    result = classify.classify_path(record, retention_inventory())
    entry = manifest.build_entry(path, record.observations,
                                 result.classification, result.blockers,
                                 result.evidence, OBSERVED_AT)
    document = manifest.build_manifest("plan-secret-check", [entry],
                                       OBSERVED_AT, retention_inventory(),
                                       "/fixtures")
    try:
        manifest.validate_manifest(document)
        check("manifest validates with redacted runtime facts", True)
    except manifest.ManifestError as exc:
        check("manifest validates with redacted runtime facts", False,
              str(exc))


def main() -> int:
    test_all_six_kinds_covered()
    test_missing_probe_reports_unknown()
    test_failing_probes_fail_closed()
    test_active_owner_is_protected()
    test_unknown_runtime_blocks_reclaimability()
    test_quiet_runtime_allows_reclaimability()
    test_secrets_never_enter_observations()
    print(f"\n=== RESULTS: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
