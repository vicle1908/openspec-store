## Why

Post-archive verification of the Jira epic reporting changes found that several archived completion claims were broader than their evidence: explicit empty-data dashboard tests are missing, spreadsheet filtering and health semantics are incomplete, and capacity calculations lack the time and role data required by the intended behavior. The completed archives remain useful historical records, but this debt needs an active, testable owner so canonical requirements are not weakened or silently treated as complete.

## What Changes

- Add explicit automated coverage for empty subtasks, zero bugs, zero sprints, and empty dashboard input, including the zero-item progress path.
- Reconcile resource-overload, timeline-risk, configuration-default, and dashboard status semantics against current implementation and canonical capability intent.
- Complete spreadsheet filtering and align health-tier thresholds and labels with a documented contract.
- Extend capacity input models only where authoritative worklog, estimate, blocked-time, and role data are available; otherwise expose an explicit unavailable state rather than a proxy labeled as effective utilization.
- Add role-aware capacity grouping when role data is present.
- Update architecture and verification documentation to distinguish automated tests from manual live Jira smoke checks and to record the `tdt-sheets` integration.
- Preserve the archived changes and reference this change from their reconciliation notes.

## Non-Goals

- Reopening or rewriting the historical change directories as active changes.
- Adding external dependencies or changing credential storage.
- Treating live Jira credentials as a mandatory unit-test prerequisite.
- Weakening canonical requirements to match incomplete implementation.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `epic-data-collection`: Require explicit empty optional-collection test coverage and safe downstream handling.
- `risk-analysis`: Clarify configurable overload and timeline threshold semantics and test the effective defaults.
- `status-aggregation`: Reconcile dashboard-specific statuses with the canonical completion model.
- `cli-interface`: Require automated empty-input behavior and documented manual live verification evidence.
- `spreadsheet-export-enhancement`: Define filtering, health-tier semantics, truthful capacity utilization, and optional role grouping.

## Impact

- `jira-epic-report`: collectors, risk/status analyzers, dashboard and spreadsheet reporters, configuration, tests, and architecture/verification documentation.
- `tdt-meta`: canonical OpenSpec deltas and archive reconciliation notes.
- `tdt-sheets`: no API change is assumed; public APIs remain preferred for authenticated reads and writes.
- No mobile repositories or public command names are changed.
