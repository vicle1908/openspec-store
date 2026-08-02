## Why

The Sprint 16 Google Spreadsheet (`SPREADSHEET_ID=1pqFsRRLQ9OsCOf9siuZwJ--azT4s2qdO4hpXH954usg`, link in `~/.tdt/.env`) is the working surface for the planning team — it holds the member mapping, the team activity grids, and the buckets the daily-reports pipeline parses. The team has no single reference for **which Jira labels, custom fields, priorities, components, fix versions, resolutions, and issue types are actually being used in the current cycle**, nor what each of those things means.

Today the only way to know "is there a Severity custom field and what is it called?" is to click through every project in the Jira UI. When a new team member joins or a label gets added, there is no canonical doc to point at. The catalog must live **in the same workbook** as the other sprint references so the team finds it next to the mapping they already use, and it must be **enriched by both Jira API metadata and observed ticket usage** so it answers both "what is this?" and "is anyone using it?".

## What Changes

- **Add a new tab** named `Jira Catalog` in the existing Sprint 16 spreadsheet. Its gid is appended to `SHEET_LINKS` in `~/.tdt/.env` after the tab is created. The tab uses a fixed 16-column schema (A=Kind, B=Name, C=Field ID, D=Type, E=Description, F=Purpose, G=Owner, H=Notes, I=Allowed Values, J=Usage Count, K=First Seen, L=Last Seen, M=Jira Updated, N=Status, O=Source Project, P=Issue Keys). Column P lists the issue keys that carry each label or tracked custom field.
- **Add a `jira_daily_reports.catalog` package** that pulls, joins, diffs, and writes catalog rows:
  - `collector.py` — paginated JQL (cursor via `client._jql_paginated`) for tickets updated in the last 90 days; pulls Jira metadata from `/rest/api/3/field`, `/rest/api/3/priority/search`, `/rest/api/3/resolution/search`, `/rest/api/3/label`, `/rest/api/3/project/{key}/component`, `/rest/api/3/project/{key}/version`, `/rest/api/3/issuetype/project` — all via `PatchedJira` from `tdt_core.clients.jira`.
  - `joiner.py` — joins "used in tickets" with "documented by Jira" into one row per (kind, name).
  - `differ.py` — diffs the joined snapshot against the live tab; classifies each row as `new` / `changed` / `unchanged` / `removed` and **never overwrites human-edited columns**.
  - `writer.py` — `tdt-sheets` (`SheetsClient` + `ServiceAccountAuth.from_env()`) writes the delta.
- **Add a `catalog` subcommand** to `jira-daily-reports`'s CLI: `uv run jira-daily-reports catalog build | refresh | show | diff`. The catalog is a sibling of the existing `planning` subcommand family.
- **Add a DBOS scheduled workflow** `jira-catalog-refresh` that runs daily at 03:00 UTC inside the central `tdt-scheduler` Docker service (per the binding `centralized-scheduling-module` contract). Registration goes into the scheduler's `schedule.py` shape, not into the receiver.
- **Add three env knobs** to `~/.tdt/.env` (defaults in parentheses):
  - `JIRA_CATALOG_TAB_NAME` (`"Jira Catalog"`) — the tab name to create or update.
  - `JIRA_CATALOG_LOOKBACK_DAYS` (`90`) — sliding window for "currently used".
  - `JIRA_CATALOG_PROJECTS` (`"AM,AU,COM,FUN,GAMI,PWM,RMD,SR,STABI,TJ,QA"`) — comma-separated list of project keys to mine.
- **No new Python dependencies** — uses existing `tdt_core.clients.jira` (PatchedJira), `tdt-sheets` (`SheetsClient`), `dbos` (via `tdt-core[scheduler]`), and stdlib. No raw SDK or `requests` calls.

## Capabilities

### New Capabilities

- `jira-catalog-tab-data-model`: the column schema, the row shape, and the (kind, name) primary key contract for the catalog tab.
- `jira-catalog-collection-and-joiner`: the contract for pulling usage data from JQL and metadata from Jira's `/rest/api/3/*` endpoints, and the rules for joining them.
- `jira-catalog-diff-and-writer`: the contract for diffing the live tab against a new snapshot, preserving human-edited columns, and writing deltas via `tdt-sheets`.
- `jira-catalog-scheduling`: the contract for the DBOS scheduled workflow and the CLI subcommand family (`build`, `refresh`, `show`, `diff`).

### Modified Capabilities

*(None — the new subcommand is additive and does not change the requirements of the existing `jira-daily-reports` spec.)*

## Impact

- **Code**:
  - `jira-daily-reports/src/jira_daily_reports/catalog/__init__.py` — new package.
  - `jira-daily-reports/src/jira_daily_reports/catalog/collector.py` — JQL + metadata pull.
  - `jira-daily-reports/src/jira_daily_reports/catalog/joiner.py` — usage + metadata join.
  - `jira-daily-reports/src/jira_daily_reports/catalog/differ.py` — diff classifier.
  - `jira-daily-reports/src/jira_daily_reports/catalog/writer.py` — `tdt-sheets` writer.
  - `jira-daily-reports/src/jira_daily_reports/catalog/cli.py` — `typer` subcommand group.
  - `jira-daily-reports/src/jira_daily_reports/cli.py` — register the new subcommand group.
  - `jira-daily-reports/src/jira_daily_reports/schedule.py` — register `jira-catalog-refresh` as a DBOS scheduled workflow following the same pattern as the 14 existing reports.
  - `jira-daily-reports/tests/catalog/` — unit tests for each module (target: 30+ tests, mirroring `tests/test_planning_sheet_fields.py`).
  - `jira-daily-reports/pyproject.toml` — add `[project.scripts]` entry if a thin CLI is needed (else reuse the existing `jira-daily-reports` script).
- **APIs**: no new public APIs. The catalog is a CLI + a tab; the only "API surface" is the tab column schema in `jira-catalog-tab-data-model`.
- **Dependencies**: none new. `tdt_core.clients.jira`, `tdt-sheets` (`SheetsClient`, `ServiceAccountAuth.from_env()`), `tdt-core[scheduler]` (`dbos`), and `typer` are all already in the repo or its declared dependencies.
- **Operations**: one new DBOS scheduled workflow (`jira-catalog-refresh`, daily 03:00 UTC) registered in the central `tdt-scheduler` Docker service. The catalog tab is created on first run via `tdt-sheets`'s `add_worksheet`; the resulting gid is appended to `SHEET_LINKS` in `~/.tdt/.env` by a one-shot bootstrap step in the writer.
- **Out of scope (non-goals)**:
  - Cataloging other Jira projects outside the configured list (no multi-tenant support).
  - Real-time incremental updates (only daily batch + on-demand `build` / `refresh`).
  - Editing Jira metadata from the sheet (read-only catalog — the team owns labels/fields in Jira).
  - Replacing the existing `planning_sheet_fields.py` reader; the catalog is a new tab, not a replacement for the team activity grid.
  - Building a custom UI — the catalog renders in Google Sheets like the existing tabs.
  - Cataloging **attachments**, **worklogs**, **comments**, or any ticket-content field — only labels, custom fields, and system fields.
  - Mirroring the catalog to a second workbook; the Sprint 16 sheet is the single source of truth.

## Non-Goals

- No redesign of how the team activity grids or mapping tab are read; the catalog is an additive read+write tab.
- No move off Google Sheets; the team uses the workbook daily and a catalog in Markdown or a database is not useful to them.
- No automated alert when a label stops being used — the `Last Seen` column already exposes staleness, and the team can filter on it.
- No retroactive backfill beyond the 90-day lookback window (configurable per env var, but the change does not ship a one-time full-history backfill).
