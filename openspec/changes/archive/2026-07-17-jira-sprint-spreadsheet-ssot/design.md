# Design — Sprint Spreadsheet as Single Source of Truth

## Context

Per-sprint config used to require hand-editing several env values. Current design
keeps the spreadsheet id/URL as the only sprint-specific input. The reporting
filter/board used to require manual Jira creation each sprint. KBS already parses sprint number + dates from the
workbook title and builds JQL from bucket tabs, but it only `update_filter`
(assumes existing) and `verify_count` (assumes existing) — neither creates.

Sprint 16 workbook exists (`1pqFsRRLQ9OsCOf9siuZwJ--azT4s2qdO4hpXH954usg`,
title `Sprint 16 - (08 Jun - 19 Jun)`) but its Jira filter/board do not. That is
the recurring manual gap this change removes.

## Goals

- One required input per sprint: the spreadsheet id/URL.
- Derive sprint number, dates, JQL from the workbook (mostly exists).
- Find-or-create the reporting filter + board by name; return resolved ids.
- Keep dry-run the default; only write to Jira on `--live`.
- No change to report calculations or sheet layout.

## Decisions

### Decision 1: Resolver lives in tdt-core
A `SprintScope` resolver in `tdt_core` (alongside `JiraConfig`/`PatchedJira`) is
shared by KBS, jira-daily-reports, and jira-epic-report, so all consumers derive
scope identically. Avoids duplicating find-or-create in three repos.

### Decision 2: Find-or-create by sprint name
Filter name `Sprint N (<dates>)`, board name `Sprint N Board`, both derived from
the workbook title. Lookups: `GET /rest/api/3/filter/search?filterName=` and
`GET /rest/agile/1.0/board?name=`. Matching is exact on the normalized name.
This preserves the existing per-sprint naming pattern, so existing filters resolve without creating duplicates.

### Decision 3: New PatchedJira methods
Add `search_filters`, `create_filter`, `search_boards`, `create_board` to
`PatchedJira`, following the existing `search_dashboards`/`create_dashboard`
precedent. `update_filter`/`get_filter` already exist on the base client.
Board creation uses `POST /rest/agile/1.0/board` with `filterId` + `type=kanban`
to match the existing kanban boards.

### Decision 4: Spreadsheet id/URL is the sprint scope input
`SPREADSHEET_ID` + workbook title are authoritative. Jira filter/board ids are
resolved from the workbook title and may be supplied only as explicit fallback
cache values in rare cases. `SPRINT_NUMBER` is no longer required (derived).

### Decision 5: Creation gated behind existing dry-run boundary
KBS already defaults to `--dry-run`. The create arm only fires on `--live`. The
resolver takes an explicit `dry_run: bool`; in dry-run it reports the intended
create/update and returns the existing id (or a sentinel) without writing.

### Decision 6: Scheduling unchanged in cadence, corrected in docs
DBOS `sprint-sheet` stays hourly (`0 * * * *`). The stale `run-sprint-sheet.sh`
header comment (`0 18 * * *`) is corrected to match `schedule.py`. No new
schedule is added; the resolver runs inside the existing sprint-sheet/sync flow.

## Risks

- Creating Jira filters/boards is a write to shared Jira. Mitigated by:
  exact-name find-first (no duplicates), live-only gating, dry-run default,
  and logging resolved ids.
- Board creation API permissions may differ from filter creation. If board
  create fails, the resolver SHALL surface the error and fall back to a
  explicitly configured board id if present, rather than aborting the report.
