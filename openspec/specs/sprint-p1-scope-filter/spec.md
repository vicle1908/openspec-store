# sprint-p1-scope-filter Specification

## Purpose

Restrict sprint report ticket extraction to Priority 1 (Highest) when `PRIORITY_1_ONLY=1` is set. Filter is applied at the sheet-reading layer, not in JQL. See `tests/test_priority_1_scope_filter.py` for the test suite (7 tests covering all scenarios below).

## Requirements
### Requirement: Sprint Sheet P1 Scope Filter

The sprint report (`sprint-sheet`) SHALL restrict ticket extraction to **Priority 1 (Highest)** when the `PRIORITY_1_ONLY=1` environment variable is set. The filtering logic MUST be applied at the sheet-reading layer (`read_sprint_ticket_scope()` in `delivery/tdt_sheet.py`), not in the JQL query construction, so that the report processes only the tickets declared as P1 in the sprint workbook. Note: the calling function in `cli.py` is `read_bucket_scope()` which delegates to `read_sprint_ticket_scope()`.

---

##### Scenario: Standard run (no priority filter)

- **GIVEN** `PRIORITY_1_ONLY` is not set or is falsy
- **WHEN** `read_sprint_ticket_scope()` is called
- **THEN** all issue keys from all bucket tabs SHALL be included regardless of their `Priority` column value
- **AND** the `SprintTicketScope.warnings` list SHALL be empty

---

#### Scenario: Priority-filtered run with a Priority column

- **GIVEN** `PRIORITY_1_ONLY=1` is set
- **AND** a bucket tab contains a `Priority` column
- **WHEN** `read_sprint_ticket_scope()` scans a row
- **THEN** a row whose `Priority` cell (case-insensitive) matches `1` or `Highest` SHALL be included
- **AND** a row whose `Priority` cell is any other value SHALL be excluded and counted as skipped
- **AND** a row whose `Priority` cell is empty SHALL be excluded and counted as skipped

---

#### Scenario: Priority-filtered run with no Priority column

- **GIVEN** `PRIORITY_1_ONLY=1` is set
- **AND** a bucket tab has no `Priority` column header
- **WHEN** `read_sprint_ticket_scope()` processes that tab
- **THEN** it SHALL emit a `p1_filter_skip_headerless_tab` WARNING log
- **AND** all issue keys from that tab SHALL be included (the filter cannot be applied)

---

#### Scenario: Priority-filtered run with extra tabs (SHEET_LINKS)

- **GIVEN** `PRIORITY_1_ONLY=1` is set
- **AND** `SHEET_LINKS` resolves to one or more extra tabs
- **WHEN** `read_sprint_ticket_scope()` processes each extra tab
- **THEN** it SHALL apply the same Priority=1 filter logic as the standard bucket tabs
- **AND** it SHALL read up to column Z (not just B) to capture the Priority column when present
- **AND** a headerless extra tab SHALL be included with a `p1_filter_skip_headerless_extra_tab` WARNING log

---

#### Scenario: Scope warnings are surfaced to the operator

- **GIVEN** `PRIORITY_1_ONLY=1` is set
- **AND** `read_sprint_ticket_scope()` excluded N non-P1 tickets
- **WHEN** `sprint-sheet` completes successfully
- **THEN** the CLI SHALL print a yellow warning: `PRIORITY_1_ONLY active: included <M> P1 tickets (skipped <N> non-P1 or unprioritised tickets from bucket sheets)`
- **AND** the same text SHALL be logged at INFO level

---

#### Scenario: Backward compatibility

- **GIVEN** `PRIORITY_1_ONLY` is not set (default)
- **WHEN** `sprint-sheet` runs with no change to invocation
- **THEN** its behavior SHALL be identical to before this change — no tickets are excluded by priority

