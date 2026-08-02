# person-capacity-role-ordering Specification

## ADDED Requirements

### Requirement: Configurable role bucket configuration loading

The `jira_daily_reports.person_capacity.role_config.load_role_config()` function SHALL resolve role configuration from the first available source, in priority order:

1. The file at the path specified by the `PERSON_CAPACITY_ROLE_CONFIG` environment variable, if set and readable
2. `~/.tdt/person_capacity_roles.yaml`, if it exists

When neither source is available, the function SHALL return a `RoleConfig` with an empty `role_order` tuple. The function SHALL log an INFO line indicating that the default empty config is in use.

When the resolved file is malformed (YAML parse error, missing `role_order` key, or `role_order` is not a list), the function SHALL return a `RoleConfig` with an empty `role_order` tuple and log a WARNING with the file path and error details.

#### Scenario: No config file exists
- **WHEN** `PERSON_CAPACITY_ROLE_CONFIG` is unset
- **AND** `~/.tdt/person_capacity_roles.yaml` does not exist
- **THEN** `load_role_config()` SHALL return `RoleConfig(role_order=(), source_path=None)`
- **AND** an INFO log line SHALL be emitted explaining that name-only sort will be used

#### Scenario: PERSON_CAPACITY_ROLE_CONFIG points to a valid file
- **WHEN** `PERSON_CAPACITY_ROLE_CONFIG` is set to an absolute path
- **AND** the file at that path is a readable YAML file with a valid `role_order` list
- **THEN** `load_role_config()` SHALL return a `RoleConfig` whose `role_order` reflects the file contents
- **AND** the file at the default path SHALL NOT be consulted

#### Scenario: Malformed YAML triggers warning and empty config
- **WHEN** the resolved config file contains invalid YAML
- **THEN** `load_role_config()` SHALL return `RoleConfig(role_order=(), source_path=<resolved_path>)`
- **AND** a WARNING log line SHALL be emitted containing the file path and the YAML parse error

#### Scenario: role_order key absent
- **WHEN** the resolved config file parses as YAML but has no `role_order` top-level key
- **THEN** `load_role_config()` SHALL return `RoleConfig(role_order=(), source_path=<resolved_path>)`
- **AND** a WARNING log line SHALL be emitted identifying the missing key

#### Scenario: role_order entries missing required fields
- **WHEN** an entry in `role_order` is missing `bucket` or has empty `bucket`
- **OR** is missing `match_prefix` or has empty `match_prefix`
- **THEN** `load_role_config()` SHALL skip that entry
- **AND** a WARNING log line SHALL identify the offending entry
- **AND** valid entries SHALL still be loaded

#### Scenario: Duplicate bucket labels
- **WHEN** two entries in `role_order` have the same `bucket` label
- **THEN** `load_role_config()` SHALL keep the first occurrence
- **AND** SHALL skip subsequent duplicates
- **AND** SHALL emit a WARNING log line identifying the duplicate

### Requirement: Prefix-based role classification

`classify_role(member_key, config)` SHALL return the `bucket` label of the first `RoleBucket` in `config.role_order` whose `match_prefix` is a case-insensitive prefix of `member_key`. If no bucket matches, the function SHALL return the string `"Other"`.

#### Scenario: Matching prefix
- **WHEN** `config.role_order` contains a bucket with `match_prefix="qa_"`
- **AND** `member_key="QA_Nhung"`
- **THEN** `classify_role` SHALL return `"QA"` (the bucket label from the example config)

#### Scenario: Case-insensitive match
- **WHEN** `match_prefix="qa_"` (lowercase)
- **AND** `member_key="QA-NHUNG"` (uppercase, hyphen variant)
- **THEN** `classify_role` SHALL return the bucket label

#### Scenario: First match wins on overlapping prefixes
- **WHEN** `config.role_order` contains `("qa_", "ios_")` buckets
- **AND** `member_key="QA_ios_something"`
- **THEN** `classify_role` SHALL return `"QA"` (the earlier bucket's label)

#### Scenario: Most-specific prefix ordered first in config
- **WHEN** `role_order` is `[(qa-chennai-auto), (qa-chennai)]`
- **AND** `member_key="qa-chennai-auto-phil"`
- **THEN** `classify_role` SHALL return `"QA Chennai (auto)"`
- **AND** for `member_key="qa-chennai-ram"` the function SHALL return `"QA Chennai (manual)"`
- **AND** the same first-match-wins rule SHALL apply to underscore-separated prefixes (e.g. listing `ios_sy` before `ios_` makes `iOS_SyThanh` go to the more specific bucket)

#### Scenario: Unmatched member_key returns Other
- **WHEN** `member_key="unknown-person"`
- **AND** no bucket matches
- **THEN** `classify_role` SHALL return `"Other"`

#### Scenario: Empty member_key returns Other
- **WHEN** `member_key=""`
- **THEN** `classify_role` SHALL return `"Other"`

#### Scenario: Empty config returns Other
- **WHEN** `config.role_order` is empty
- **AND** `member_key="QA_Nhung"`
- **THEN** `classify_role` SHALL return `"Other"`

### Requirement: Two-pass row sorting with role grouping

`sort_person_rows(rows, config)` SHALL split rows into an active block (`logged_total_seconds > 0`) and an inactive block (`logged_total_seconds == 0`), then sort each block by separating rows into explicit-bucket matches and "Other" (unmatched) rows. Explicit-bucket rows SHALL be sorted by `(role priority, person name casefold ascending)`. "Other" rows SHALL preserve their input order. The final result SHALL concatenate active-explicit + active-other + inactive-explicit + inactive-other and renumber `no` from 1.

When `config.role_order` is empty, the function SHALL preserve the input order of all rows to maintain backward compatibility with the legacy Logged-Total-desc / Worked-Tickets-desc / Person-asc ordering applied upstream in `sprint_report_sheet._build_person_capacity`.

The "Other" rows preserve input order regardless of whether the config is empty or not. This is the safest backward-compatible behavior: operators get role-grouping for the prefixes they explicitly configure; everyone else keeps the existing presentation order.

The function SHALL mutate the `no` field on each input dict.

#### Scenario: Active block precedes inactive block
- **WHEN** rows contain both active (`logged_total_seconds > 0`) and inactive members
- **THEN** the returned list SHALL have all active rows before any inactive row
- **AND** within each block, explicit-bucket rows SHALL be sorted by the configured role priority, then by person name

#### Scenario: Inactive rows are authors with zero worklogs
- **WHEN** a row's `logged_total_seconds == 0` (e.g. an author on leave or in the roster with no time entries this sprint)
- **THEN** that row SHALL be placed in the inactive block
- **AND** SHALL appear after all active rows regardless of role bucket

#### Scenario: Rows renumbered sequentially from 1
- **WHEN** rows are passed with `no=0` placeholders
- **THEN** the returned list SHALL have `no` values `1, 2, 3, ..., N`
- **AND** the input row dicts SHALL be mutated with these values

#### Scenario: Other bucket appended after explicit buckets
- **WHEN** a member's `member_key` matches no prefix
- **THEN** that member's row SHALL appear after all explicit-bucket rows
- **AND** within the "Other" block rows SHALL preserve their input order

#### Scenario: Empty config preserves input order
- **WHEN** `config.role_order` is empty
- **THEN** rows within each block SHALL preserve their input order (no re-sorting)
- **AND** the active block SHALL still precede the inactive block
- **AND** rows SHALL be renumbered 1..N

#### Scenario: Empty input returns empty output
- **WHEN** `rows=[]`
- **THEN** `sort_person_rows` SHALL return `[]`

### Requirement: Sprint report sheet integration with safe fallback

`sprint_report_sheet._build_person_capacity` SHALL apply role-grouped row ordering after the active/inactive split. The wire-in site SHALL be wrapped in a `try/except` block: on any exception raised by the new module, the report SHALL fall back to the prior behavior (active sorted by logged-desc/tickets-desc/person, inactive sorted by person, renumbered 1..N).

The wire-in SHALL NOT change the dict shape passed to the sheet writer; only the row order changes.

#### Scenario: Config present, ordering applied
- **WHEN** `~/.tdt/person_capacity_roles.yaml` is present with the seven buckets (QA, AOS, iOS, Auto, PL, Technical, BA)
- **AND** `_build_person_capacity` produces rows with mixed `member_key` prefixes
- **THEN** the returned `all_rows` SHALL be ordered by role bucket (QA → AOS → iOS → Auto → PL → Technical → BA), then by person name within each bucket
- **AND** active rows SHALL precede inactive rows

#### Scenario: Config absent, prior behavior preserved
- **WHEN** no role config file exists
- **THEN** rows SHALL be ordered as they were before this change (active by hours desc, inactive by person asc)
- **AND** rows SHALL be renumbered 1..N

#### Scenario: Module raises exception, fallback engaged
- **WHEN** `sort_person_rows` raises any exception (e.g. a coding defect)
- **THEN** the report SHALL still complete without crashing
- **AND** rows SHALL be ordered using the prior behavior
- **AND** an ERROR log line SHALL be emitted identifying the exception
