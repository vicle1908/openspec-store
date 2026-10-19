# Design: remediate-tcc-provenance-and-inventory-degradation

## Context

See `proposal.md` — Why for problem motivation. Following the `ponytail-review` audit of commits `2814f313` (`platform/openspec-store`) and `ad9323b` (`shb/shb-schedule`), two categories of issues require remediation:
1. **Behavioral Bug (Finding 1)**: `step_integrity_and_store_validation()` in `shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py:L888-909` treats `authority_reconciliation.drift_count > 0` or `target_misalignment_count > 0` as a hard failure (`authority_conflicts = True`) without checking `manifest_reconciliation`. Because `inventory-workstation-toolchain.py:L939-953` intentionally classifies `prime-agent` (`/opt/homebrew/lib/prime-agent`) as `drift_status: "target_misalignment"` (`updater_dispatch: "none"`) in `authority_reconciliation` (enforced by `TestProductionPrimeAgentProvenance` in `test-version-authority-governance.py:L108-118`) while classifying `prime-agent` as `state: "aligned"` (`owner: "local-dev"`) in `manifest_reconciliation`, every live run of `step_integrity_and_store_validation()` on this workstation returns `status: "DEGRADED"`.
2. **Code Duplication & Dead Weight (Findings 2–6)**: `platform/openspec-store/scripts/tcc_provenance.py` (`845` lines) and `workstation_update.py` (`verify_tcc_provenance`) contain an unused `ROLE_POLICY_DESCRIPTIONS` dictionary, two duplicate target-resolution loops in `build_required_targets()`, duplicate `CFURL`/`SecStaticCode` initialization in `evaluate_csreq_against_path()` and `copy_designated_csreq_blob()`, 10 copy-pasted error-return dictionaries, and two overlapping dataclasses (`TCCTargetSpec` and `TCCRecordAudit`).

## Goals / Non-Goals

**Goals:**
- Reconcile `authority_reconciliation` with `manifest_reconciliation` in `step_integrity_and_store_validation()` so normal workstation runs return `status: "SUCCESS"` while genuine manifest drift, unaligned target misalignment, authority conflicts, or unknown tools still return `status: "DEGRADED"`.
- Remove ~175+ lines of duplicated/dead code across `scripts/tcc_provenance.py` and `workstation_update.py` without altering any public function signature, return key, CLI flag, or native `Security.framework` `csreq` check.

**Non-Goals:**
- Modifying `inventory-workstation-toolchain.py`'s `prime-agent` `authority_reconciliation` output (which is required by `workstation-daily-update.sh`'s `DENY_ROSTER_NPM` pre-flight gate and `TestProductionPrimeAgentProvenance`).
- Removing `copy_designated_csreq_blob()` from `scripts/tcc_provenance.py` (which is imported by tests in both `platform/openspec-store` and `shb/shb-schedule`).

## Decisions

### Decision 1: Cross-Check `manifest_reconciliation` Before Degrading on `target_misalignment`
- **Pattern Reused**: `verify-workstation-toolchain.py` (`check_inventory_reconciliation`), which evaluates `manifest_reconciliation` (`drift_count`, `missing_count`, `unsanctioned_count`, `unknown_count`) alongside `authority_reconciliation`.
- **Approach**:
  In `step_integrity_and_store_validation()` (`workstation_update.py:L884-909`):
  1. Extract `manifest_rec = inv_data.get("manifest_reconciliation")` (when present as a `dict`) and collect the set of tool names whose `state == "aligned"` in `manifest_rec.get("summary", {}).get("aligned", [])` (or `manifest_rec.get("items", {}).get("aligned", [])`).
  2. Count `unaligned_misalignments`: items in `auth_rec.get("items", [])` with `drift_status == "target_misalignment"` that are **not** both `updater_dispatch == "none"` and present in `aligned_manifest_names`. When `auth_rec` has no `items` list (e.g. in minimal unit-test mocks), fall back to `target_misalignment_count` unless `manifest_rec` explicitly reports `status == "aligned"` and `drift_count == 0`.
  3. Set `authority_conflicts = True` and append to `errors` if any of the following hold:
     - `"conflict" in auth_status.lower() or conflict_count > 0`
     - `unknown_count > 0`
     - `unaligned_misalignments > 0`
     - `manifest_rec` is a `dict` and (`int(manifest_rec.get("drift_count", 0)) > 0` or `int(manifest_rec.get("missing_count", 0)) > 0` or `int(manifest_rec.get("unsanctioned_count", 0)) > 0` or `int(manifest_rec.get("unknown_count", 0)) > 0` or `str(manifest_rec.get("status", "aligned")).lower() not in ("aligned", "reconciled", "clean", "ok")`)
     - `manifest_rec is None` and (`drift_count > 0` or `target_misalignment_count > 0` or `auth_status.lower() not in ("reconciled", "clean", "ok")`).

### Decision 2: Unify Target Resolution, Error Dictionaries, and Static-Code Creation in `tcc_provenance.py`
- **Approach**:
  1. Delete `ROLE_POLICY_DESCRIPTIONS` (`tcc_provenance.py:L67-88`).
  2. Collapse `TCCTargetSpec` into `TCCRecordAudit` (or keep a single lightweight record construction helper) and unify `build_required_targets()` so `binaries is None` simply constructs `raw_items = [*CANONICAL_TCC_CLIS, *([SHARED_PYTHON_AUTOMATION_BINARY] if include_py else [])]` and runs the single resolution loop with `include_py` enabled.
  3. Add `_tcc_result(status: str, *, reason: str | None = None, verified: list[str] | None = None, missing: list[str] | None = None, records: list[dict[str, Any]] | None = None, errors: list[str] | None = None) -> dict[str, Any]` in `tcc_provenance.py` (and `_tcc_error_result(msg: str, status: str = "ERROR")` in `workstation_update.py`) to eliminate the 10 repeated dictionary literals.
  4. Add `_create_static_code(target_p: Path)` in `tcc_provenance.py` to deduplicate `CFURLCreateFromFileSystemRepresentation` + `SecStaticCodeCreateWithPath` across `evaluate_csreq_against_path()` and `copy_designated_csreq_blob()`.

### Decision 3: Transaction Boundaries Across Repositories
- **Central Store (`/Users/androidteam/Developer/platform/openspec-store`)**: Edits to `scripts/tcc_provenance.py` must pass `python3 scripts/tcc_provenance.py --json`, `python3 scripts/test-version-authority-governance.py`, and `pytest tests/test_portable_workstation_slice_{a,b,c}.py`.
- **SHB Scheduler (`/Users/androidteam/Developer/shb/shb-schedule`)**: Edits to `src/shb_schedule/workflows/workstation_update.py` and `tests/test_workstation_update_workflow.py` must pass `uv run --no-sync --directory /Users/androidteam/Developer/shb/shb-schedule pytest tests/test_workstation_update_workflow.py -q` and live `step_integrity_and_store_validation()` (`status == "SUCCESS"`, `errors == []`).

## Risks / Trade-offs

- **[Risk] Refactoring `build_required_targets()` could subtly alter how `python3` triggers `org.python.python` bundle resolution when `binaries` is explicitly passed vs `None`** → **Mitigation**: Preserve `include_py = True if include_python_automation is None else bool(include_python_automation)` when `binaries is None` (and `bool(include_python_automation)` when `binaries` is explicitly passed) and run all 22 existing unit tests in `test_workstation_update_workflow.py` plus live `tcc_provenance.py --json`.
