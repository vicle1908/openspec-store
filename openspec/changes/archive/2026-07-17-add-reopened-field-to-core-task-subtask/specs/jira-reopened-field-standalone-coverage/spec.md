# Jira Reopened Field Standalone Coverage

## ADDED Requirements

### Requirement: Duplicate scoped Reopened fields SHALL be detected and removed before field-exposure work begins

Before any field-exposure or backfill work starts, the workflow SHALL detect all project-scoped `Reopened` fields and SHALL remove stale ghosts via the supported `DELETE /rest/api/3/field/{fieldId}` endpoint, guarded by a live-state probe.

#### Scenario: Duplicate detection identifies stale ghosts

- **WHEN** the workflow runs duplicate detection against the Jira instance
- **THEN** it SHALL query `GET /rest/api/3/field/search?query=Reopened` to enumerate all fields named `Reopened`
- **AND** for each field with a non-empty `scope.project.id`, it SHALL verify the field's `GET /rest/api/3/field/{id}/context` returns 404 and `JQL cf[{id}] is not EMPTY` returns zero issues
- **AND** it SHALL classify fields that pass both checks as `stale-ghost` and fields that fail either check as `live-field`

#### Scenario: Stale ghosts are deleted via REST

- **WHEN** a field is classified as `stale-ghost`
- **THEN** the workflow SHALL issue `DELETE /rest/api/3/field/{fieldId}` and verify the deleted ID no longer appears in a subsequent `field/search?query=Reopened` call
- **AND** it SHALL classify the deletion as `implemented-and-supported` in the evidence

#### Scenario: Live fields are protected from deletion

- **WHEN** a field is classified as `live-field` (has active context or populated issues)
- **THEN** the workflow SHALL refuse to issue a DELETE and SHALL classify the field as `protected-live-field`
- **AND** the `--force` flag SHALL override this protection only after emitting a warning

### Requirement: Field-exposure plan SHALL capture per-project × per-issue-type evidence against the jira-space-setup-standard taxonomy

The workflow SHALL detect whether `customfield_11523` is present in the `Task` and `Subtask` issue type metadata of each target project, SHALL route into the correct workflow family based on project style, and SHALL emit structured evidence per the established taxonomy.

#### Scenario: Team-managed project enters detection workflow

- **WHEN** the target project is classified as `next-gen`
- **THEN** the workflow SHALL use `GET /rest/api/3/issue/createmeta/{project}/issuetypes/{id}` for each relevant issue type (Task, Subtask) to detect `customfield_11523` presence
- **AND** it SHALL record `customfield_11523_present: true | false` per issue type
- **AND** it SHALL classify any issue type where the field is absent as `unsupported-by-current-api-surface` because no REST write path exists for team-managed field-to-issue-type association

#### Scenario: Classic project enters detection workflow

- **WHEN** the target project is classified as `classic`
- **THEN** the workflow SHALL additionally identify the default screen and tab for the Task issue type via `FieldConfig.get_screens_for_project`
- **AND** it SHALL record the screen ID and tab ID in the evidence for the apply step

#### Scenario: Detection reads back field presence after apply

- **WHEN** the apply step adds `customfield_11523` to a classic project's Task screen
- **THEN** the workflow SHALL verify the field is present in `GET /rest/api/3/screens/{id}/tabs/{id}/fields` before reporting `implemented-and-supported`

### Requirement: Field-exposure plan SHALL produce per-project operator instructions for team-managed projects

For each team-managed project × issue type where the field is absent, the workflow SHALL generate a step-by-step operator instruction covering the Jira UI navigation required to expose the field.

#### Scenario: Operator instruction is generated for a team-managed project

- **WHEN** the field is absent from a team-managed project's Task or Subtask issue type
- **THEN** the workflow SHALL emit an instruction block containing:
  - Project key and Jira URL to the project's Issue Types settings
  - The exact UI navigation path: `Project settings → Issue types → <IssueType> → Layout → Add field → Search "Reopened" → Select the global "Reopened (Number)" field`
  - A confirmation step: verify that only `customfield_11523` (global, not project-scoped) appears in `Jira Admin → Custom fields`

### Requirement: Backfill SHALL derive Reopened count from issue changelog with conservative status allowlists

The backfill workflow SHALL count status transitions matching an operator-defined allowlist from each issue's changelog, SHALL write the count to `customfield_11523` only when the existing value is `None` or `0`, and SHALL surface per-project batch statistics.

#### Scenario: Changelog read counts reopen transitions

- **WHEN** the backfill processes an issue
- **THEN** it SHALL read `GET /rest/api/3/issue/{key}/changelog` using cursor pagination (never `startAt`)
- **AND** it SHALL count `changelog.histories[*].items` where `field == "status"` and `fromStatus in {status-from-allowlist}` and `toStatus in {status-to-allowlist}`
- **AND** the default allowlist SHALL be `fromStatus ∈ {Done, Closed, Resolved}` and `toStatus ∈ {Reopened, Open}`

#### Scenario: Backfill respects no-overwrite guard

- **WHEN** the existing `customfield_11523` value on an issue is non-null and non-zero
- **THEN** the workflow SHALL NOT update that issue unless `--overwrite` is passed

#### Scenario: Backfill is rate-limit safe

- **WHEN** the backfill runs against a project with more than `--batch-size` issues
- **THEN** the workflow SHALL sleep for 24 hours between batches when `--continuous 24h` is passed
- **AND** it SHALL resume from the last processed cursor on restart without reprocessing already-updated issues

### Requirement: Evidence SHALL be written to durable Markdown files per jira-space-setup-standard

Each workflow step SHALL emit a timestamped Markdown evidence file to `output/` with rows per project × issue type, classification per the taxonomy, and a final summary table.

#### Scenario: Evidence file is produced for a workflow run

- **WHEN** a workflow run completes (detection, consolidation, apply, or backfill)
- **THEN** it SHALL write `output/reopened-field-<step>-<timestamp>.md` with:
  - A header row identifying the step, Jira instance, and timestamp
  - Per-row columns: project, style, issue_type, field_present, action_required, classification, status
  - A summary row: `total_projects`, `already_exposed`, `automated_applied`, `manual_required`, `errors`

#### Scenario: Evidence is also printed to console

- **WHEN** a workflow run produces evidence
- **THEN** it SHALL also print a Rich `Table` to the console for immediate readability
- **AND** it SHALL emit `exit 0` on success, `exit 1` on detection failure, and `exit 2` on apply failure
