## Why

Three recurring warnings appear on every `jira-sprint-sheet` run (and on the
daily `jira-catalog-refresh` / `jira-run-all` chains). They are non-fatal, but
they dilute the scheduler's log signal and one of them silently drops a
production env var.

| Warning | Where it appears | Why it matters |
|---|---|---|
| `worklog_invalid_timezone tz=Asia/Saigon — falling back to UTC` | `jira-daily-reports/src/jira_daily_reports/person_worklog_source.py:70` | `Asia/Saigon` is an obsolete IANA alias (rejected by `zoneinfo` since tzdata 2018c). The test fixture in `jira-daily-reports/tests/conftest.py` sets `PERSON_CAPACITY_TIMEZONE=Asia/Saigon`, so the warning fires on every pytest collection. The `SprintReportSheetReport` code path in production only emits the warning if the operator overrides the env, but the spec/operator gap is real: the spec mandates a UTC fallback, while the codebase already has the canonical zone in mind. |
| `catalog.diff.primary_key_remap kind=Custom Field field_id=… old_name=… new_name=…` (x ~280 / refresh) | `jira-daily-reports/src/jira_daily_reports/catalog/differ.py:75–81` | One warning per colliding `(Kind, Name)` row, on every refresh. The behaviour is correct (the spec mandates the alternate-key match), but the volume drowns out other diagnostics. The string itself is not named in any spec. |
| `python-dotenv could not parse statement starting at line 80` | `dotenv/main.py:32–39`, surfaced by `tdt_core.env.load_tdt_env()` at `tdt-core/src/tdt_core/env.py:42,46,51`. Source line: `~/.tdt/.env:80` — a malformed `SHEET_LINKS="…";Jira Catalog|…` value. | The warning itself is **spec-compliant** (the `deployable-env-loading` baseline mandates that the warning is emitted). The bug is that the entire `SHEET_LINKS` value is silently dropped — there is no diagnostic that tells the operator which env var was lost. |

The fix is two small code changes (alias map in `_parse_report_timezone`, dedupe
in `Differ`) plus one diagnostic-enhancement change in `tdt_core.env`, plus
a one-line operator repair in `~/.tdt/.env`. The umbrella change is
spec-first, with the new baseline capability (`ops-scheduler-warning-hygiene`)
capturing the contract and the existing in-flight changes
(`jira-person-capacity-worklog-mode`, `jira-catalog-tab`) gaining the
narrow scenarios that operationalize the umbrella.

## What Changes

- **Add a new capability** `ops-scheduler-warning-hygiene` that names the
  three contract changes below.
- **TZ alias resolution (lightweight).** Add a static alias map
  `_REPORT_TZ_ALIASES` in `person_worklog_source.py` and use it inside
  `_parse_report_timezone(name)`. `Asia/Saigon` resolves to
  `Asia/Ho_Chi_Minh` and no warning is emitted; the existing
  `worklog_invalid_timezone` warning text is preserved for genuinely
  unrecognised names.
- **Catalog remap warning dedupe.** Accumulate per-pair `(Kind, Name)`
  field_ids during the differ walk, emit at most one
  `catalog.diff.primary_key_remap` warning per pair, expose the full set
  on `CatalogDelta.primary_key_remap_collisions`, and print a single
  summary line at the end of the catalog CLI run.
- **Env-loader diagnostic preservation.** Wrap `python-dotenv.load_dotenv`
  with a `LogCaptureHandler` on the `dotenv` logger. Expose the captured
  records on `tdt_core.env` as `last_load_diagnostics`, each containing
  `key_attempted`, `line`, and `source`. The WARN log itself is preserved
  (the `deployable-env-loading` baseline still holds) but the operator
  can now see which env var was lost.
- **Operator action: repair `~/.tdt/.env` line 80.** Either escape the
  inner `"` characters, or split the `SHEET_LINKS` value onto multiple
  lines. Tracked in `tasks.md`.

## Capabilities

### New Capabilities

- `ops-scheduler-warning-hygiene`: the umbrella capability that defines
  the three contract changes — alias-resolving timezone parser, deduped
  catalog-remap warnings, and enriched env-loader diagnostics.

### Modified Capabilities

- `person-capacity-worklog-mode` (in-flight in
  `openspec/changes/jira-person-capacity-worklog-mode/`): append one
  scenario "A documented IANA alias resolves without warning" to the
  existing "Invalid timezone falls back to UTC with warning" requirement.
- `jira-catalog-diff-and-writer` (in-flight in
  `openspec/changes/jira-catalog-tab/`): append one requirement
  "The differ MUST dedupe primary-key-remap warnings per `(Kind, Name)`
  pair" and one scenario.

## Impact

- **Code**:
  - `jira-daily-reports/src/jira_daily_reports/person_worklog_source.py` —
    add `_REPORT_TZ_ALIASES` constant; widen `_parse_report_timezone` to
    use it before falling back to UTC. No public API change.
  - `jira-daily-reports/src/jira_daily_reports/catalog/differ.py` —
    restructure the per-`new_row` warning emission so collisions are
    collected into `primary_key_remap_collisions` first, then one warning
    per `(Kind, Name)` pair is emitted at the end. Classification
    (`appended` / `updated` / `removed`) is unchanged.
  - `jira-daily-reports/src/jira_daily_reports/catalog/models.py` —
    add `primary_key_remap_collisions: dict[tuple[str,str], list[str]]`
    field to `CatalogDelta`.
  - `jira-daily-reports/src/jira_daily_reports/jira_daily_reports/cli.py`
    (catalog subcommand) — one summary print line.
  - `tdt-core/src/tdt_core/env.py` — add private `_LogCaptureHandler`
    class, wire it into `load_tdt_env()`, expose
    `last_load_diagnostics`. The existing `WARN` log is preserved
    (baseline compatibility).

- **Tests**:
  - `jira-daily-reports/tests/test_person_worklog_source_v145.py` —
    add `test_parse_report_timezone_resolves_documented_aliases` that
    asserts `Asia/Saigon` is accepted silently and resolves to
    `Asia/Ho_Chi_Minh`.
  - `jira-daily-reports/tests/catalog/test_differ.py` — add
    `test_primary_key_remap_warnings_deduped_per_pair` that asserts 5
    colliding snapshot rows produce 1 warning entry and
    `len(delta.primary_key_remap_collisions) == 1`.
  - `tdt-core/tests/test_env_loader.py` — add
    `test_load_tdt_env_captures_malformed_line_diagnostic` that writes
    a temp `.env` with the exact `SHEET_LINKS="…";…` malformed line and
    asserts the captured record has `key_attempted == "SHEET_LINKS"`
    and `line == 80`.

- **Spec**:
  - `openspec/changes/ops-fix-three-scheduler-warnings/specs/ops-scheduler-warning-hygiene/spec.md` — new.
  - `openspec/changes/jira-person-capacity-worklog-mode/specs/person-capacity-worklog-mode/spec.md` — append alias scenario.
  - `openspec/changes/jira-catalog-tab/specs/jira-catalog-diff-and-writer/spec.md` — append dedupe requirement + scenario.

- **Operator**:
  - `~/.tdt/.env` line 80 — escape the inner `"` (replace
    `"<url>"` with `\"<url>\"` and wrap the whole value in single
    quotes, or split the value into multiple `SHEET_LINKS_<i>` keys).
    Tracked in `tasks.md` as an operator action, not a code change.

## Out of Scope

- Changing the differ's primary-key rule itself — the spec-mandated
  `(Kind, Name)` rule stays.
- Removing the `worklog_invalid_timezone` warning text — the spec still
  requires it for genuinely invalid tz names.
- Silencing `python-dotenv` warnings entirely — the `deployable-env-loading`
  baseline requires the warning; this change only enriches the
  diagnostic payload.
- Any change to `SprintReportSheetReport` or the rest of `jira-sprint-sheet`
  — only `_parse_report_timezone` is touched.
- Migrating `Asia/Saigon` consumers in `tests/conftest.py` — the alias
  map handles them transparently, so we leave the test fixture unchanged
  and assert that the warning no longer fires.
