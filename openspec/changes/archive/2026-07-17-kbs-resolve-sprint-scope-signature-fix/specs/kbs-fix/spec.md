# kbs-fix — Fix kbs CLI resolve_sprint_scope call site

## ADDED Requirements

### Requirement: `kbs sync` pipeline completes without signature errors

The `kbs sync` command SHALL call `resolve_sprint_scope` with only the parameters that `tdt_core.sprint_scope.resolve_sprint_scope` currently accepts. The call SHALL NOT pass `filter_id_override` or `board_id_override` kwargs.

#### Scenario: Sync completes without TypeError

- **WHEN** `kbs sync` is run against a sprint workbook
- **THEN** the call to `resolve_sprint_scope` SHALL use only the current signature parameters: `jira`, `spreadsheet_id`, `title`, `jql`, `dry_run`, `sprint_number_override`, `create_board`
- **AND** it SHALL NOT pass `filter_id_override` or `board_id_override`

#### Scenario: Verify command completes without TypeError

- **WHEN** `kbs verify` is run against a sprint workbook
- **THEN** the call to `resolve_sprint_scope` SHALL use only the current signature parameters
- **AND** it SHALL NOT pass `filter_id_override` or `board_id_override`

#### Scenario: Post-call fallback handles pre-seeded ids

- **WHEN** `cfg.filter_id` or `cfg.board_id` is set (from env or CLI flag) in `sync`
- **THEN** the post-call fallback `scope.filter_id or cfg.filter_id` SHALL use the config value when `scope.filter_id` is `None`
- **AND** the behavior SHALL be semantically equivalent to the removed override-params pattern
- **WHEN** `resolved_filter_id` or `resolved_board_id` is set (from CLI flags) in `verify`
- **THEN** the post-call fallback `scope.filter_id or resolved_filter_id` SHALL use the pre-resolved value when `scope.filter_id` is `None`

### Requirement: Filter and board links in report header are sprint-specific

When the kbs pipeline runs to completion (live mode), the Sprint Report header SHALL show the filter and board created for the current sprint, not an arbitrary pre-existing filter.

#### Scenario: Live kbs sync creates sprint-specific filter

- **WHEN** `kbs sync --live` runs for "Sprint 17 - (22 Jun - 03 July)"
- **THEN** the filter created SHALL be named "Sprint 17 (22 Jun - 03 July)"
- **AND** its JQL SHALL reflect the resolved issue key scope (`key in (...)`)
- **AND** the report header link SHALL point to filter 10357 (or whichever id is actually created)

#### Scenario: Dry-run reports intended filter/board without creating

- **WHEN** `kbs sync --dry-run` runs
- **THEN** no filter or board SHALL be created in Jira
- **AND** the output SHALL report the canonical filter name and board name that would be used

## ADDED Requirements — jdr board guard

### Requirement: kbs-resolved board id is not overwritten by spreadsheet fallback

When `RESOLVED_BOARD_ID` is set (from kbs pipeline handoff), the board id in the report SHALL NOT be overwritten by the spreadsheet fallback search.

#### Scenario: kbs-resolved board id preserved through report init

- **WHEN** `RESOLVED_BOARD_ID=1066` is set in the environment
- **AND** `SprintReportSheetReport` is instantiated
- **THEN** `self.board_id` SHALL be `"1066"` after `_resolve_scope_from_spreadsheet` completes
- **AND** it SHALL NOT be overwritten by a different board id from the Jira search-by-title fallback

#### Scenario: Standalone run still uses spreadsheet fallback

- **WHEN** no `RESOLVED_BOARD_ID` env var is set
- **AND** `_resolve_scope_from_spreadsheet` finds a board by spreadsheet title
- **THEN** `self.board_id` SHALL be set to that board's id
- **AND** this behavior SHALL be unchanged from before this fix
