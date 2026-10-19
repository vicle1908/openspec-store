# Tasks: remediate-tcc-provenance-and-inventory-degradation

## 1. Streamline Central TCC Provenance Verifier (`platform/openspec-store`)

- [x] 1.1 Remove unused `ROLE_POLICY_DESCRIPTIONS` (`L67-88`), collapse `TCCTargetSpec` into `TCCRecordAudit`, unify the duplicate `binaries` vs `None` resolution loops in `build_required_targets()`, and extract `_create_static_code()` and `_tcc_result()` in `/Users/androidteam/Developer/platform/openspec-store/scripts/tcc_provenance.py`, verifying `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/tcc_provenance.py --json` returns `status: "CLEAN"` across all 9 workstation identities and `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/test-version-authority-governance.py` passes (`34/34` tests).

## 2. Reconcile Scheduler Inventory Validation & Error Helpers (`shb/shb-schedule`)

- [x] 2.1 Deduplicate error-result dictionaries in `verify_tcc_provenance()` via `_tcc_error_result()` and update `step_integrity_and_store_validation()` in `/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` so uncovered `target_misalignment` entries (`updater_dispatch == "none"`, such as `prime-agent`) that are `state: "aligned"` in `manifest_reconciliation` do not trigger false-`DEGRADED` status while true manifest drift, unaligned target misalignment, conflicts, or unknown tools still return `DEGRADED`.
- [x] 2.2 Add unit tests in `/Users/androidteam/Developer/shb/shb-schedule/tests/test_workstation_update_workflow.py` covering both (a) `SUCCESS` when `manifest_reconciliation` is `aligned` and `authority_reconciliation` has only uncovered `prime-agent` `target_misalignment`, and (b) `DEGRADED` when `manifest_reconciliation` has drift or `authority_reconciliation` has unaligned `target_misalignment` / `unknown_count` / `conflict_count`, and verify both `uv run --no-sync --directory /Users/androidteam/Developer/shb/shb-schedule pytest tests/test_workstation_update_workflow.py -q` and live `step_integrity_and_store_validation()` pass with `status == "SUCCESS"` and `errors == []`.

## Workflow follow-up

- Record value-blind verification evidence in `evidence.md` inside the change directory before archiving.
- Sync delta specs and archive the change via `openspec archive remediate-tcc-provenance-and-inventory-degradation --store openspec-store`.
