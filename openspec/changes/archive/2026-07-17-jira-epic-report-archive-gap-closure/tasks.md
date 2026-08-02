## 1. Characterization and Edge Coverage

- [x] 1.1 In `jira-epic-report`, add fixture-backed collector and dashboard tests for no subtasks, no bugs, and no sprint assignments.
- [x] 1.2 Add an empty-items CLI test that asserts the documented message, non-success exit, and absence of output artifacts.
- [x] 1.3 Add a direct reporter test for zero total items and prevent division by zero without masking invalid non-empty data.
- [x] 1.4 Document the manual live Jira dashboard smoke procedure and preserve date, epic scope, formats, and outcome separately from automated test results.

## 2. Risk and Status Semantics

- [x] 2.1 Characterize current resource-overload weight and trigger boundaries, timeline-risk boundaries, and project overrides.
- [x] 2.2 Select and document authoritative defaults, then make analyzer and configuration output consume the same values.
- [x] 2.3 Consolidate completion weights or add an explicit normalization layer for dashboard-only statuses.
- [x] 2.4 Add boundary and cross-format consistency tests for all reconciled risk and status semantics.

## 3. Spreadsheet Health and Filtering

- [ ] 3.1 Characterize current health tiers and decide the canonical boundaries and labels recorded in the delta spec.
- [ ] 3.2 Align all managed spreadsheet tabs to the chosen health contract and add exact-boundary tests.
- [ ] 3.3 Add managed filters for issue key, status, assignee, blocker state, and impact tier through the authenticated `tdt-sheets` integration.
- [ ] 3.4 Verify filter creation failures propagate and unknown or protected stakeholder tabs remain unchanged.

## 4. Capacity Data and Role Grouping

- [ ] 4.1 Identify authoritative Jira or planning sources for logged effort, planned estimate, blocked time, and role; document unavailable fields by project.
- [ ] 4.2 Extend normalized models and collection only for supported authoritative inputs.
- [ ] 4.3 Calculate bounded Effective Utilization when all required time inputs exist; otherwise render an explicit unavailable state.
- [ ] 4.4 Rename any item-count proxy so it cannot be mistaken for time utilization.
- [ ] 4.5 Add optional role grouping with an ungrouped fallback and tests proving every person appears exactly once.

## 5. Documentation and Verification

- [ ] 5.1 Update `jira-epic-report` architecture documents to record `tdt-core` client creation and the authenticated `tdt-sheets` integration boundary.
- [ ] 5.2 Reconcile stale command, package-layout, and test-count statements without replacing historical dated evidence.
- [ ] 5.3 Run `ruff check . --fix`, `ruff format .`, strict mypy, and the focused and full pytest suites in `jira-epic-report`.
- [ ] 5.4 Run strict OpenSpec validation and update the archived reconciliation notes with this change's final outcome.
- [ ] 5.5 If spreadsheet validation regresses managed workbooks, roll back the affected reporter change while retaining characterization tests and failure evidence.
