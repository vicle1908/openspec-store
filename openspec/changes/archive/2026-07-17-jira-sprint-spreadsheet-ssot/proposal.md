## Why

Rolling the TDT toolchain to a new sprint currently means hand-editing Jira
`filter_id` / `board_id` / `SPREADSHEET_ID` / `SPRINT_NUMBER` across four files
in `~/.tdt` (`.env`, `config.toml`, `config.yaml`, `epic-report-config.toml`),
plus manually creating a Sprint N filter and board in Jira. Sprint 16 exposed
the gap: the sheet exists, but no Jira filter/board do, and nothing creates
them. The values drift, and a wrong `filter_id` makes reports silently query
the wrong sprint.

The sprint workbook already encodes everything we need: its title carries the
sprint number and date range (`Sprint 16 - (08 Jun - 19 Jun)`), and its bucket
tabs carry the issue keys. We should treat the spreadsheet as the single source
of truth and derive — or create — the Jira filter and board from it, instead of
storing per-sprint Jira IDs in hand-maintained config.

## What Changes

- Treat the sprint **spreadsheet** as the single source of truth. The only
  required per-sprint config is the spreadsheet id/URL.
- Derive `sprint_number` and `sprint_dates` from the workbook title (already
  parsed by KBS) and reuse them everywhere reporting needs a sprint label.
- Add **find-or-create** resolution for the per-sprint reporting filter and
  board: look up `Sprint N (<dates>)` by name, create it if absent, and return
  the resolved ids. Creation is a Jira write, gated behind the existing
  `--live` flag; dry-run stays the default and never writes.
- Make `JIRA_FILTER_ID` / `JIRA_BOARD_ID` optional **cache/override** values,
  not the source. When absent, they are resolved from the spreadsheet.
- Point `~/.tdt` config at the Sprint 16 workbook and reduce per-sprint config
  to the spreadsheet id; keep stable infra (KBS planning filter/board,
  scheduler DSN, ports) as-is.
- Align scheduling docs/comments with the real DBOS cadence (the
  `run-sprint-sheet.sh` header still cites a stale `0 18 * * *`).
- Align docs and skills (`kanban-board-from-spreadsheet`, `jira-daily-reports`)
  to the spreadsheet-as-truth model.

## Capabilities

### New Capabilities
- `sprint-spreadsheet-ssot`: Resolve the active sprint's number, dates, JQL,
  reporting filter, and board from the sprint spreadsheet, creating the Jira
  filter/board on demand when they do not yet exist.

### Modified Capabilities
- `kanban-board-from-spreadsheet`: sync flow resolves filter/board from the
  workbook (find-or-create) instead of requiring pre-existing ids.
- `jira-daily-reports`: sprint-sheet and related reports resolve sprint scope
  from the spreadsheet when Jira ids are not explicitly configured; report
  calculations and sheet layout are unchanged.

## Impact

- `tdt-core`: add filter create + board search/create client methods and a
  sprint-resolution helper consumed by the reporting apps.
- `jira-kanban-from-spreadsheet`: sync resolves/creates filter+board from the
  workbook; `.env`-supplied ids become optional overrides.
- `jira-daily-reports` / `jira-epic-report`: consume resolved sprint scope;
  no change to report content contract.
- `~/.tdt`: per-sprint config reduced to the spreadsheet id (Sprint 16);
  scheduling comments corrected.
- `tdt-meta`: this OpenSpec change, plus skill/doc updates for the SSOT model.
