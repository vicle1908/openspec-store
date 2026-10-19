# workstation-toolchain-inventory Spec Delta

## ADDED Requirements

### Requirement: Scheduler integrity validation SHALL reconcile authority and manifest drift without false degradation on aligned local-dev tools

The scheduler integrity validation step SHALL reconcile `authority_reconciliation` against `manifest_reconciliation` so uncovered local-dev tools that are aligned in the workstation manifest do not trigger false-positive degradation, while true manifest drift, authority conflicts, or unknown tools fail closed.

#### Scenario: Aligned manifest with uncovered local-dev bundle passes integrity validation
- **WHEN** `step_integrity_and_store_validation()` evaluates `inventory-workstation-toolchain.py --json` where `manifest_reconciliation` has `status: "aligned"` (`drift_count == 0`, `missing_count == 0`, `unsanctioned_count == 0`, `unknown_count == 0`) and `authority_reconciliation` has `conflict_count == 0` and `unknown_count == 0`
- **THEN** uncovered `target_misalignment` entries (`updater_dispatch == "none"`, such as `prime-agent`) that are `state: "aligned"` in `manifest_reconciliation` SHALL NOT mark `step_integrity_and_store_validation()` as `DEGRADED`
- **AND** `step_integrity_and_store_validation()` SHALL return `status: "SUCCESS"` with `errors: []`

#### Scenario: Unaligned target misalignment, manifest drift, conflict, or unknown tool degrades integrity validation
- **WHEN** `inventory-workstation-toolchain.py --json` reports `conflict_count > 0`, `unknown_count > 0`, `manifest_reconciliation` drift/missing/unsanctioned/unknown counts `> 0`, or a `target_misalignment` item that is not `aligned` in `manifest_reconciliation`
- **THEN** `step_integrity_and_store_validation()` SHALL return `status: "DEGRADED"` and append a diagnostic entry to `errors`
