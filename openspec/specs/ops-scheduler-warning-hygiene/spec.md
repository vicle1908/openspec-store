# ops-scheduler-warning-hygiene Specification

## Purpose
TBD - created by archiving change ops-fix-three-scheduler-warnings. Update Purpose after archive.
## Requirements
### Requirement: Timezone parser resolves documented IANA aliases without warning

The `_parse_report_timezone` function SHALL consult a static
alias map `_REPORT_TZ_ALIASES` (e.g. `{"Asia/Saigon": "Asia/Ho_Chi_Minh"}`)
before calling `zoneinfo.ZoneInfo(name)`. When `name` matches an
entry in the alias map, the function SHALL return
`zoneinfo.ZoneInfo(canonical)` and SHALL NOT emit the
`worklog_invalid_timezone` warning. When `name` does not match an
alias and `zoneinfo.ZoneInfo(name)` raises, the existing
`worklog_invalid_timezone tz=<name> — falling back to UTC` warning
SHALL still be emitted (preserving the `person-capacity-worklog-mode`
spec contract).

#### Scenario: Asia/Saigon is accepted as a synonym for Asia/Ho_Chi_Minh

- **WHEN** `report_timezone` is `Asia/Saigon` (an obsolete IANA
  alias rejected by modern `zoneinfo` since tzdata 2018c)
- **THEN** `_parse_report_timezone("Asia/Saigon")` SHALL return a
  `zoneinfo.ZoneInfo` equivalent to `Asia/Ho_Chi_Minh`
- **AND** the `worklog_invalid_timezone` warning SHALL NOT be emitted
- **AND** the worklog timestamp bucketing SHALL use
  `Asia/Ho_Chi_Minh` for the whole run

#### Scenario: Unrecognised timezone still warns

- **WHEN** `report_timezone` is `Mars/Olympus_Mons`
- **THEN** `_parse_report_timezone` SHALL return UTC
- **AND** it SHALL log `worklog_invalid_timezone tz=Mars/Olympus_Mons — falling back to UTC`

### Requirement: Catalog differ MUST dedupe primary-key-remap warnings per `(Kind, Name)` pair

The `Differ` SHALL collect
alternate-key collisions into a `dict[tuple[str,str], list[str]]`
keyed by `(Kind, Name)`, where each value is the list of
`field_id`s that collided on that slot. The differ SHALL emit the
`catalog.diff.primary_key_remap` warning at most once per
`(Kind, Name)` pair per refresh. The full collision map SHALL be
exposed on the returned `CatalogDelta` as the new field
`primary_key_remap_collisions: dict[tuple[str, str], list[str]]`.
The differ's row classification (`appended` / `updated` /
`removed`) SHALL NOT change.

The warning text SHALL be one line per pair, formatted as
`catalog.diff.primary_key_remap kind=<K> name=<repr> collisions=<N> field_ids=<sample>`,
where `<sample>` is the first 5 field_ids followed by `...` if
there are more.

#### Scenario: 200 custom-field rows collide on the same live tab slot

- **WHEN** the snapshot contains 200 `Custom Field` rows that each
  collide on a single live `(Kind, Name)` slot
- **THEN** `delta.warnings` SHALL contain at most one entry whose
  message starts with `catalog.diff.primary_key_remap` for that
  `(Kind, Name)` pair
- **AND** `delta.primary_key_remap_collisions[("Custom Field", "Auto Test Coverage")]`
  SHALL contain all 200 field_ids
- **AND** the catalog CLI SHALL print one summary line
  `catalog.diff.primary_key_remap unique_collisions=<M> total_field_ids=<N>`
  at the end of the run

#### Scenario: Differ classification is unchanged

- **WHEN** the dedupe path emits 1 warning instead of 280
- **THEN** `delta.appended`, `delta.updated`, and `delta.removed`
  SHALL be identical to the pre-dedupe values
- **AND** the writer's `tdt-sheets` calls SHALL be byte-identical

### Requirement: Env loader MUST capture malformed-line diagnostics

The `tdt_core.env.load_tdt_env()` SHALL install a private
`_LogCaptureHandler` on the `dotenv` logger for the duration of
the `python-dotenv.load_dotenv(...)` call. The handler SHALL
append each `WARNING` record from the `dotenv` logger to the
module-level list `_last_load_diagnostics`, with each entry
containing at minimum the keys `logger`, `level`, `msg`, `line`,
and `key_attempted`. The captured records SHALL be exposed
read-only via the function `tdt_core.env.last_load_diagnostics()`.

The original `python-dotenv` "could not parse statement starting
at line N" warning SHALL still be emitted at WARN level on the
`dotenv` logger (preserving the `deployable-env-loading` baseline
contract).

#### Scenario: A malformed SHEET_LINKS value produces a captured diagnostic

- **WHEN** `~/.tdt/.env` contains
  `SHEET_LINKS="<url>";Jira Catalog|<url>;…` (literal `";` mid-value)
- **THEN** `tdt_core.env.load_tdt_env()` SHALL log
  `python-dotenv could not parse statement starting at line 80`
  at WARN level
- **AND** `tdt_core.env.last_load_diagnostics()` SHALL return a
  list with one entry whose `key_attempted == "SHEET_LINKS"` and
  `line == 80`

#### Scenario: A clean .env produces an empty diagnostic list

- **WHEN** `~/.tdt/.env` parses without errors
- **THEN** `tdt_core.env.load_tdt_env()` SHALL NOT emit any
  `dotenv` warnings
- **AND** `tdt_core.env.last_load_diagnostics()` SHALL return `[]`

