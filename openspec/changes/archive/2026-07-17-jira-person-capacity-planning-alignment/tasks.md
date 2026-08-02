## 1. Shared Spreadsheet Primitives and Planning Parsing

- [x] 1.1 Audit reusable spreadsheet primitives in `jira-kanban-from-spreadsheet` (`SheetsReader`, header normalization, issue-key validation, JQL builder) and choose extract-vs-local-reuse boundaries
- [x] 1.2 Add or reuse a common helper for Sheets API access, sheet metadata/timezone discovery, header alias lookup, issue-key extraction, and de-duplication
- [x] 1.3 Add `planning_sheet_fields.py` with dataclasses for member mapping, planned rows, planned person aggregates, and reconciliation warnings, using shared helpers from 1.2
- [x] 1.4 Implement parser for the writable mapping sheet (`Person Capacity Mapping`) with fallback to `Dropdown Keys - Do Not Delete -`, reading `MEMBERS`, `EMAIL/Teams ID`, and optional `Jira Account ID` columns by header name
- [x] 1.5 Implement current-sprint team activity parser with header detection for `JIRA ID`, `ASSIGNED TO`, `ORIGINAL ESTIMATE (hour)`, status columns, and date columns
- [x] 1.6 Implement row ownership resolution hierarchy: explicit row member, group member, issue member, unresolved planning bucket
- [x] 1.7 Ignore `TOTAL`, summary, and formula block rows for authoritative planned-capacity totals
- [x] 1.8 Add parser tests for shared helper reuse, mapping rows, missing `EMAIL/Teams ID` values, blank child-row inheritance, group inheritance, summary-row exclusion, and unresolved effort rows

## 2. Snapshot and Reconciliation

- [x] 2.1 Introduce a shared sprint-ticket scope object or equivalent return value around the existing `read_bucket_scope()` result
- [x] 2.2 Pass the shared scope to the existing `set_bucket_keys()` / `set_targets()` path without changing `Sprint Report` behavior
- [x] 2.3 Extend `delivery/sheet.py` to read mapping and team activity tabs after the shared bucket scope is created
- [x] 2.4 Ensure the planning parser receives the shared scope keys as an input filter instead of re-reading bucket tabs or duplicating ticket extraction logic
- [x] 2.5 Filter planned-capacity aggregation to planning rows whose issue keys are present in the shared scope
- [x] 2.6 Add reconciliation logic for bucket-only issues, planning-only issues, unmapped Jira people, mapping rows without `EMAIL/Teams ID`, unresolved planning effort, and formula drift diagnostics
- [x] 2.7 Add tests proving one shared scope feeds both `Sprint Report` and `Person Capacity`, planning-only issue keys are reported but not added to Jira query or planned totals, and bucket-only issue keys remain in the Jira query
- [x] 2.8 Ensure source tabs are never cleared or written by the report path
- [x] 2.9 Add Jira issue-graph expansion for direct blocking/split links from seed issues with dedupe/self-link guards
- [x] 2.10 Add tests covering seed-scope vs direct-fetch-scope behavior, blocking/split link traversal, and reconciliation dedupe

## 3. Person Capacity Merge

- [x] 3.1 Extend `SprintReportSheetReport` to accept planned-capacity data alongside bucket keys and target statuses
- [x] 3.2 Merge planned aggregates, Jira ownership, and Jira worklog activity by workbook `member_key` when mapping is available
- [x] 3.3 Preserve unmapped Jira-only rows and unresolved planning rows with explicit labels
- [x] 3.4 Preserve Jira original-estimate-only ownership behavior and complete-worklog activity behavior
- [x] 3.5 Add tests for mapped Jira assignee merge, mapped worklog author merge, unmapped Jira fallback, and planned-vs-Jira ledger separation

## 4. Output and UX

- [x] 4.1 Update `Person Capacity` rows to include `Member Key`, `Role`, `Planned Issues`, `Planned Tasks`, `Planned Estimate`, `Assigned Tickets`, `Jira Original Estimate`, `Worked Tickets`, and `Logged Total`
- [x] 4.2 Add a reconciliation section to the generated `Person Capacity` tab with counts and samples for warnings
- [x] 4.3 Update CLI sheet-mode summary to mention person-capacity warnings when present
- [x] 4.4 Keep the existing Jira-only layout as fallback when planning data is unavailable
- [x] 4.5 Add sheet-row rendering tests for planning-aligned rows and fallback rows
- [x] 4.6 Refine hyperlink rendering so `Worked Ticket Links` is the canonical clickable multi-ticket field using pure `HYPERLINK(...)` formulas, while `Daily Ticket Details` remains readable diagnostic text
- [x] 4.7 Add tests proving Sprint Report issue cells remain pure hyperlinks, Person Capacity worked ticket cells keep every ticket clickable, and daily detail cells do not become the only hyperlink surface

## 5. Verification and Documentation

- [x] 5.1 Run targeted unit tests for planning parsing, sprint sheet, sheet delivery, and work item field helpers
- [x] 5.2 Run a live read-only verification against spreadsheet `1ZB_CE4xQMOrBbDPe2jxRniMh8adFYC5-EQ4eqSd1ok8` and capture mapping/scope/reconciliation counts
- [x] 5.3 Run a controlled live sheet write only after read-only verification passes, then read back `Person Capacity` to confirm row counts and warning section
- [x] 5.4 Update `jira-daily-reports/README.md` with planned-vs-owned-vs-actual semantics and source tab assumptions
- [x] 5.5 Update `.agents/skills/jira-daily-reports/SKILL.md` with the new runbook and data-quality checks
- [x] 5.6 Run `openspec validate jira-person-capacity-planning-alignment --strict`
