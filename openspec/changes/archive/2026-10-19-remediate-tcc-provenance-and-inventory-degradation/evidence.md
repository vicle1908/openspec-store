# Verification Evidence: `remediate-tcc-provenance-and-inventory-degradation`

- **Date**: `2026-10-19`
- **Store**: `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`)
- **Change**: `remediate-tcc-provenance-and-inventory-degradation`
- **Discipline**: Strictly value-blind (SHA-256 digests, line counts, exit codes, and structural metadata only; zero secrets or raw tokens).

---

## 1. Streamline Central TCC Provenance Verifier (`platform/openspec-store`, Task 1.1)

- **Target File**: `/Users/androidteam/Developer/platform/openspec-store/scripts/tcc_provenance.py` (`697` lines, down from `845` lines; `-148` lines)
  - SHA-256: `e7e5d5c89d9e8c89b894662ca03ab6446ad77a7312c90d075d8c7df125cff42c`
- **Changes Applied**:
  - Removed unused `ROLE_POLICY_DESCRIPTIONS` table (`-22` lines).
  - Collapsed `TCCTargetSpec` into `TCCRecordAudit` (`.to_dict()` preserving all 12 record keys).
  - Unified `build_required_targets()` into a single target-resolution loop for both `binaries=None` and explicit `binaries` lists.
  - Extracted shared `_create_static_code()` across `evaluate_csreq_against_path()` and `copy_designated_csreq_blob()`.
  - Added `_tcc_result()` to replace 6 repeated early-exit dictionary literals.
- **Verification**:
  - `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/tcc_provenance.py --json` → Exit Code: `0` (`"status": "CLEAN"`, `"missing_binaries": []`, `"errors": []`, `9/9` workstation identities verified).
  - `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/test-version-authority-governance.py` → Exit Code: `0` (`Ran 34 tests in 6.755s — OK`).

---

## 2. Reconcile Scheduler Inventory Validation & Error Helpers (`shb/shb-schedule`, Tasks 2.1–2.2)

- **Modified Files & SHA-256 Digests**:
  - `/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py`: `d1ad11737876182e1ae66b4efb9e0f6a2f98ac53f8cd7c40a0a63544f94a41d2`
  - `/Users/androidteam/Developer/shb/shb-schedule/tests/test_workstation_update_workflow.py`: `7a9b9c1a247154f7e76ce7ceaa00ffb8207ea092180cee0ae1292ef271654c8c`
- **Changes Applied**:
  - Added `_tcc_error_result()` in `workstation_update.py` (`L712-720`), replacing 4 repeated 8-line error dictionary literals.
  - Updated `step_integrity_and_store_validation()` (`L878-954`) to cross-check `manifest_reconciliation` against `authority_reconciliation` so uncovered `target_misalignment` entries (`updater_dispatch == "none"`, such as `prime-agent`) that are `state: "aligned"` in `manifest_reconciliation` do not trigger false-`DEGRADED` status, while genuine manifest drift, unaligned target misalignment, authority conflicts, or unknown tools return `status: "DEGRADED"`.
- **Verification**:
  - `uv run --no-sync --directory /Users/androidteam/Developer/shb/shb-schedule pytest tests/test_workstation_update_workflow.py -q` → Exit Code: `0` (`37 passed in 38.84s`).
  - Live `step_integrity_and_store_validation()` execution:
    ```json
    {
      "status": "SUCCESS",
      "script_drift": false,
      "openspec_valid": true,
      "snapshot_growth": {
        "status": "SUCCESS",
        "loose_size": "0 B",
        "loose_objects": "0 objects",
        "packed_size": "62.29 MiB",
        "packed_objects": "3105 objects in 1 pack",
        "commit_count": 1035
      },
      "toolchain_inventory": {
        "status": "drift_detected",
        "conflict_count": 0,
        "drift_count": 1,
        "target_misalignment_count": 1,
        "unknown_count": 0
      },
      "agent_cli_coverage": {
        "status": "SUCCESS",
        "undeclared_count": 0,
        "total_installed": 21,
        "declared_covered_count": 8,
        "declared_uncovered_count": 13
      },
      "errors": []
    }
    ```
