# Proposal: remediate-tcc-provenance-and-inventory-degradation

## Why

The daily workstation maintenance step `step_integrity_and_store_validation()` falsely marks every normal run `DEGRADED` because it treats `authority_reconciliation` `target_misalignment` on uncovered local-dev bundles (`prime-agent`) as an authority conflict even when `manifest_reconciliation` is `aligned`, and `scripts/tcc_provenance.py` carries ~175 lines of duplicated target-resolution loops, unused role tables, and repeated error-dictionary literals.

In `inventory-workstation-toolchain.py`, `prime-agent` (`/opt/homebrew/lib/prime-agent`) is intentionally reported with `drift_status: "target_misalignment"` (`updater_dispatch: "none"`) in `authority_reconciliation` so `workstation-daily-update.sh` adds it to `DENY_ROSTER_NPM` and prevents `npm update -g` from touching it, while `manifest_reconciliation` classifies `prime-agent` as `state: "aligned"` (`owner: "local-dev"`, `drift_count: 0`). Because `shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` (`L888-909`) unconditionally sets `authority_conflicts = True` whenever `authority_reconciliation.drift_count > 0` or `target_misalignment_count > 0`, `step_integrity_and_store_validation()` returns `"status": "DEGRADED"` on every healthy workstation run, which in turn causes `workstation-daily-update.sh` (`L496-502`) to think the primary `shb-schedule` run failed and re-run the entire 12-stage update pipeline a second time. Simultaneously, `ponytail-review` identified 5 lean/duplication defects across `scripts/tcc_provenance.py` and `workstation_update.py` (`ROLE_POLICY_DESCRIPTIONS` dead table, duplicate `binaries` vs `None` resolution loops in `build_required_targets()`, duplicate `CFURL`/`SecStaticCode` setup, 10 repeated 8-line error-return dictionaries, and redundant `TCCTargetSpec`/`TCCRecordAudit` dataclasses).

## What Changes

- **Eliminate False-`DEGRADED` Toolchain Inventory Aggregation (`workstation-toolchain-inventory`)**:
  - Update `step_integrity_and_store_validation()` in `/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` to evaluate `manifest_reconciliation` alongside `authority_reconciliation`:
    - Flag `DEGRADED` on any `authority_reconciliation` conflict (`conflict_count > 0` or `"conflict"` in status), any unclassified tool (`unknown_count > 0`), any `manifest_reconciliation` drift/missing/unsanctioned/unknown count (`> 0` or status not in `("aligned", "reconciled", "clean", "ok")`), or any `target_misalignment` item that is not reconciled as `aligned` in `manifest_reconciliation`.
    - When `manifest_reconciliation` is `aligned` (`drift_count == 0`, `missing_count == 0`, `unsanctioned_count == 0`, `unknown_count == 0`) and `authority_reconciliation` has `conflict_count == 0` and `unknown_count == 0` (with only uncovered `updater_dispatch == "none"` `target_misalignment` items that are `aligned` in `manifest_reconciliation`), `step_integrity_and_store_validation()` SHALL return `status: "SUCCESS"`.
- **Streamline `scripts/tcc_provenance.py` and `verify_tcc_provenance()` (`workstation-remote-and-agent-permissions`)**:
  - Delete unused `ROLE_POLICY_DESCRIPTIONS` (`tcc_provenance.py:L67-88`).
  - Unify the two duplicate target-resolution branches in `build_required_targets()` (`tcc_provenance.py:L378-572`) into a single loop by defaulting the input list to `[*CANONICAL_TCC_CLIS, *([SHARED_PYTHON_AUTOMATION_BINARY] if include_py else [])]` when `binaries is None`.
  - Extract a shared `_create_static_code(target_p)` helper used by both `evaluate_csreq_against_path()` and `copy_designated_csreq_blob()`, and a shared `_tcc_result(status, reason=..., errors=...)` helper in `tcc_provenance.py` and `workstation_update.py` to replace the 10 copy-pasted error dictionaries.
  - Collapse `TCCTargetSpec` and `TCCRecordAudit` so target resolution and SQLite audit use a single record structure without field-by-field re-copying.

## Non-Goals

- **No weakening of TCC or `csreq` validation**: All 9 required identities, role-scoped services (`kTCCServiceAccessibility`, `kTCCServiceScreenCapture`, `kTCCServiceSystemPolicyAllFiles`), native `Security.framework` `SecStaticCodeCheckValidity` checks, and fail-closed `DRIFT`/`ERROR` exits remain 100% intact.
- **No change to `TestProductionPrimeAgentProvenance`**: `inventory-workstation-toolchain.py` continues to report `prime-agent` as `target_misalignment` (`updater_dispatch: "none"`) in `authority_reconciliation` so `workstation-daily-update.sh` keeps gating it out of `npm update -g`.
- **No removal of `copy_designated_csreq_blob()`**: Because both `shb/shb-schedule/tests/test_workstation_update_workflow.py` and `platform/openspec-store/scripts/test-version-authority-governance.py` call `tcc_provenance.copy_designated_csreq_blob()`, it remains in `tcc_provenance.py` (streamlined via shared `_create_static_code()`).

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `workstation-toolchain-inventory`: Refine `step_integrity_and_store_validation()` inventory reconciliation so `manifest_reconciliation`-aligned local-dev tools (`prime-agent`) do not trigger false `DEGRADED` status and duplicate fallback runs, while true manifest drift, conflicts, or unknown tools fail closed.
- `workstation-remote-and-agent-permissions`: Simplify and deduplicate `scripts/tcc_provenance.py` and `workstation_update.py` (`verify_tcc_provenance()`) while preserving all native `csreq` and fail-closed verification contracts.

## Impact

- **Ownership Boundaries**:
  - **Central OpenSpec Store (`/Users/androidteam/Developer/platform/openspec-store`)**: Owns `scripts/tcc_provenance.py` and `scripts/test-version-authority-governance.py`.
  - **SHB Scheduler Repository (`/Users/androidteam/Developer/shb/shb-schedule`)**: Owns `src/shb_schedule/workflows/workstation_update.py` and `tests/test_workstation_update_workflow.py`.
