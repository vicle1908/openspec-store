## Context

The Sprint 16 Google Spreadsheet (`SPREADSHEET_ID=1pqFsRRLQ9OsCOf9siuZwJ--azT4s2qdO4hpXH954usg`, link in `~/.tdt/.env`) is the team's day-to-day reference workbook. Two tabs are already wired into the planning pipeline: the **member mapping** tab (parsed by `parse_member_mapping()` in `jira-daily-reports/src/jira_daily_reports/planning_sheet_fields.py`) and the three **team activity** tabs (`Kelvin's Team Activites New`, etc., parsed by `parse_team_activity_tab()`). The catalog tab will live in the same workbook, accessed by the same `SPREADSHEET_ID` and the same `SheetsClient` instance, but reads from a third party — Jira's metadata APIs — and is written by a new pipeline.

The Jira integration point is `PatchedJira` from `tdt_core.clients.jira` (returned by `JiraClientFactory.from_env()`). It already exposes the v3 cursor-paginated JQL (`jql()`) and is the canonical way the team talks to Jira. The Google Sheets integration point is `SheetsClient` from `tdt-sheets` (configured with `ServiceAccountAuth.from_env()`), used by `jira-daily-reports` for every read/write of the Sprint 16 workbook.

The scheduling host is the `tdt-scheduler` Docker service per the binding `centralized-scheduling-module` change. All 14 daily Jira reports already register their workflows there. The new `jira-catalog-refresh` workflow follows the same registration pattern.

`planning_sheet_fields.py` is the closest sibling code: it parses the live sheet with an alias-driven header detector, accumulates `warnings` on the snapshot dataclass, and exposes a `build_planning_snapshot(...)` orchestrator. The catalog uses the **same conventions** (alias lists, snapshot dataclass, warning accumulation) so the two readers feel consistent to the team.

## Goals / Non-Goals

**Goals:**

- A `Jira Catalog` tab in the Sprint 16 workbook that answers "what is this label / field, is it used, when was it last seen, what values does it accept, and which tickets carry it?" for every label, custom field, priority, resolution, component, fix version, and issue type that appears in the configured Jira projects in the last 90 days. The `Issue Keys` column (P) lists the specific tickets that carry each label or tracked custom field.
- A `uv run jira-daily-reports catalog <subcommand>` CLI for `build` (full rebuild), `refresh` (delta from current tab), `show` (print current tab to stdout), and `diff` (show what the next refresh would change).
- A daily DBOS scheduled workflow that calls `refresh` at 03:00 UTC inside the central `tdt-scheduler` service.
- A diff-only writer that **never overwrites a human-edited column** (`Description`, `Purpose`, `Owner`, `Notes`).
- Reuse of every existing helper: `tdt_core.clients.jira.JiraClientFactory`, `PatchedJira.jql()`, `client._jql_paginated`, `tdt_sheets.SheetsClient`, `ServiceAccountAuth.from_env()`, `tdt-core[scheduler]` (`dbos`), and the `planning_sheet_fields.py` snapshot-dataclass + warning-accumulation conventions.

**Non-Goals:**

- Editing Jira metadata from the sheet. The catalog is read-only toward Jira.
- Cataloging projects outside the configured list (the env var `JIRA_CATALOG_PROJECTS` is the only source of project keys; no auto-discovery).
- Real-time incremental updates. The cadence is daily + on-demand; live event-driven updates would require a webhook pipeline that does not exist today.
- Replacing the team activity grid parser. The catalog is a new tab, not a replacement.
- Mirroring to a second workbook.
- Alerting on stale labels. The `Last Seen` column exposes it; the team filters.
- Building a custom UI; the catalog renders in Google Sheets.

## Decisions

### D1. New `jira_daily_reports.catalog` package — not a standalone repo

- **Decision**: Add the catalog as a new sub-package under `jira-daily-reports/src/jira_daily_reports/catalog/`, with a `typer` subcommand group on the existing `jira-daily-reports` CLI.
- **Why**: The catalog reuses `client._jql_paginated`, the `PatchedJira` factory, the `SheetsClient` delivery path, the DBOS scheduled-workflow registration, and the `SheetsClient` exception types. A standalone repo would re-instantiate all of them. The same workbook, same auth, same CLI entry, same scheduler.
- **Alternatives considered**:
  - Standalone `jira-catalog-exporter` repo — rejected: would duplicate `tdt_core.env.load_tdt_env()`, the cursor-paginated JQL pattern, and the `SheetsClient` config, and would add a new deploy target for a 1-job service.
  - One-shot skill with no scheduling — rejected: the user explicitly chose scheduled daily refresh.
  - Inside `tdt-core` — rejected: `tdt-core` is a SDK with no scheduled-workflow host and no Google Sheets client; mixing consumer CLIs in would blur its purpose.

### D2. Single tab, single row per (kind, name) — type-discriminated column

- **Decision**: One tab. The `Kind` column is a discriminator (`Label` / `Custom Field` / `Priority` / `Resolution` / `Component` / `Fix Version` / `Issue Type`). The `Name` column is the value-name; for custom fields an additional `Field ID` column carries the Jira `customfield_NNNNN` ID. Type-specific values (e.g. allowed values for a select field) live in a single `Allowed Values` column (newline-separated) rather than expanding into a sub-table.
- **Why**: One tab = one place the team looks. A discriminator column is the simplest way to keep one row per thing and still let humans filter/sort. A `Field ID` column is the only way the team can later build a JQL that actually targets the field (`cf[12345]`).
- **Alternatives considered**:
  - One tab per kind (7 tabs) — rejected: the team opens one workbook tab at a time and the catalog answers "what does field X mean?" not "what is the priority catalog?". Tabs would multiply without payoff.
  - Separate per-type schemas with type-specific columns — rejected: schema drift across rows is harder to maintain than a single column with structured text.

### D3. Cursor-paginated JQL with the 90-day lookback, never on-the-fly tickets

- **Decision**: The collector runs `client._jql_paginated(jql=f"project IN ({projects}) AND updated >= -{lookback}d", fields="labels,priority,resolution,components,fixVersions,issuetype")` plus the custom field ids from `JIRA_CATALOG_TRACKED_FIELDS`. The `fields` parameter MUST be a **comma-separated string**, not a `list[str]` — `PatchedJira.jql()` accepts both, but `_jql_paginated` coerces to string before calling `jira.jql()`.
- **Why**: A fixed comma-separated field list bounds the response size. Jira's `/rest/api/3/search/jql` with `fields=*all` returns every custom field that has ever appeared — across 11 projects in 90 days that could be thousands of responses. The `JIRA_CATALOG_TRACKED_FIELDS` env var lets the team extend the list without a code change.
- **Note on pagination**: `_jql_paginated` uses `nextPageToken`-based cursor pagination (not offset). The helper deduplicates keys across pages via an in-memory `seen_keys` set and stops on `isLast: true` or a defensive empty-page guard. All of this is handled by the helper — the collector just calls it once.
- **Alternatives considered**:
  - `fields=*all` and aggregate on the client — rejected: response size + time.
  - Per-project tracked fields — deferred: a single global list is enough for v1; per-project overrides can be a follow-up.

### D4. Diff-only writes, with a "human-owned" column set that is never overwritten

- **Decision**: The differ classifies each row as `new` / `changed` / `unchanged` / `removed` by comparing `(Kind, Name)` keys. On `refresh`, the writer:
  1. Inserts `new` rows.
  2. Updates only the **machine-owned** columns on `changed` rows: `Usage Count`, `Last Seen`, `Allowed Values`, `Field ID`, `Jira Updated`, `Status` (sets to `Active` / `Stale` / `Removed`).
  3. Leaves **human-owned** columns untouched on `changed` rows: `Description`, `Purpose`, `Owner`, `Notes`.
  4. Marks `removed` rows with `Status = Removed` and a faint row format (not deleted — humans may want to keep history).
- **Why**: The whole point of "used + documented" is that the team owns the documentation. A `refresh` that overwrites their edits every day is hostile; a `refresh` that respects the columns humans fill in is a partner.
- **Alternatives considered**:
  - Full-tab rebuild on every refresh — rejected: destroys human edits and produces noise in the version history.
  - Append-only with no diff — rejected: stale rows accumulate; the team has no way to know what's still in use.

### D5. `tdt-sheets` is the only path to the workbook; the tab gid is resolved at runtime via `get_metadata()`

- **Decision**: The writer resolves the catalog tab by name using `SheetsClient.get_metadata(spreadsheet_id)` → `SpreadsheetMetadata.sheets` → `get_sheet_by_name(name)`. If the tab does not exist, the writer calls `SheetsClient.ensure_sheet(spreadsheet_id, tab_name)` (which sends a bare `addSheet` request), then re-calls `get_metadata()` to read back the newly created sheet's `gid`, and appends that gid to `SHEET_LINKS` in `~/.tdt/.env` as a one-shot bootstrap. On subsequent runs, the writer reads the gid directly from the `SHEET_LINKS` entry matching the tab name.
- **API corrections**: `SheetsClient` does not have `list_worksheets()`, `add_worksheet(rows=, cols=)`, `append_rows()`, or `set_frozen_rows()`. The writer uses:
  - `get_metadata()` + `get_sheet_by_name()` for lookup.
  - `ensure_sheet()` for creation (no grid properties on first create; the tab gets default dimensions).
  - `read()` with A1 notation (`"Catalog!A1:O2000"`) for reading the live tab.
  - `write()` or `batch_update()` with raw `updateCells` requests for writing appended/updated rows.
  - `clear()` or `batch_update()` with `deleteDimension` requests for clearing rows on `build`.
  - Raw `freezeRange` batch request for freezing the header row.
- **Why**: Using `get_metadata()` + iterating `.sheets` is the correct equivalent of `list_worksheets()` (which doesn't exist). Resolving the gid after creation via a re-call to `get_metadata()` is necessary because `ensure_sheet()` does not return the new sheet's gid.
- **Alternatives considered**:
  - Hard-code the gid — rejected: the first rename or copy breaks the writer silently.
  - Always read by name (never persist the gid) — rejected: `get_metadata()` round-trips to Google's API on every run; persisting the gid avoids the round-trip on all subsequent calls.
  - Add higher-level helpers to `SheetsClient` for `add_worksheet(rows=, cols=)`, `set_frozen_rows`, `append_rows` — deferred to a follow-up. The writer builds raw batch requests using `parse_a1_to_grid_range()` from `tdt_sheets/utils.py` for the grid range construction.

### D6. Scheduling lives in `tdt-scheduler` (Docker), not `jira-daily-reports` process

- **Decision**: The `jira-catalog-refresh` workflow is registered in the central `tdt-scheduler` Docker service (per the binding `centralized-scheduling-module` change). Registration uses `_make_workflow("catalog-refresh", "0 3 * * *", engine=engine)` from `dbos_scheduling.py` — not a `@scheduled_workflow` decorator. The existing `_run_report()` helper already runs `uv run python -m jira_daily_reports <command>` via subprocess in `/workspace/agent-core`, so the registration call is `engine.scheduled_workflow(cron="0 3 * * *", name="jira-catalog-refresh", automatic_backfill=False)(workflow_fn)`.
- **CLI entry point**: The `catalog-refresh` command is a Typer command registered on the existing `app` in `cli.py` (`@app.command("catalog-refresh")`), reached via `python -m jira_daily_reports catalog-refresh`. Do NOT add a separate `catalog/schedule.py` module — registration is a one-line `_make_workflow(...)` call added inside `register_all_schedules()` in `dbos_scheduling.py`.
- **Why**: The binding contract says all movable cron belongs in `tdt-scheduler`. `schedule.py` is only a data dict for documentation; actual DBOS registration lives in `dbos_scheduling.py` and is exposed via `scheduler_setup.py`. Adding `_make_workflow(...)` there follows the exact same pattern as the 14 existing reports.
- **Alternatives considered**:
  - In-process DBOS schedule inside `jira-daily-reports` — rejected: violates the binding contract.
  - macOS crontab — rejected: the user already chose scheduled refresh; crontab is the legacy mechanism.

### D7. Idempotency + crash safety come from DBOS, not from the writer

- **Decision**: The writer is **not** defensive about partial writes. It uses `batch_update` to write machine-owned columns for `changed` rows in one call, and `write()` (A1 notation) to append `new` rows at the next free row (computed from `get_metadata().sheets` row count). If the workflow crashes mid-write, the next `refresh` re-runs the differ, sees the rows are still "new" or "changed", and re-applies the delta. There is no custom crash journal.
- **Why**: DBOS already gives exactly-once execution semantics for the scheduled workflow. Building a second crash journal inside the writer is double bookkeeping.
- **Alternatives considered**:
  - Two-phase write with a journal — rejected: complexity for a problem DBOS already solves.
  - Optimistic concurrency via a `Last Refresh` cell in the tab — deferred: can be added later if duplicate runs ever become a problem in practice.

## Risks / Trade-offs

- **Jira rate limits on a 90-day pull.** A 90-day window across 11 projects with `fields=labels,priority,resolution,components,fixVersions,issuetype` plus a bounded list of custom field IDs could be 20k+ tickets, and the metadata endpoints add another ~10 calls. → Mitigation: run after hours (03:00 UTC); use `client._jql_paginated` with `limit=100` per page; metadata endpoints use server-side pagination and typically complete in 1-2 calls. `JIRA_CATALOG_LOOKBACK_DAYS` is configurable as a safety knob.
- **`tdt-sheets` writer is destructive if mis-targeted.** A wrong `JIRA_CATALOG_TAB_NAME` would clobber a real tab. → Mitigation: the writer requires the tab name match against a pre-flight check; the CLI `build` subcommand takes `--dry-run` and the `diff` subcommand prints the delta before any write.
- **Diffing over a human-edited tab is ambiguous.** If a human renames a `Name` cell, the differ sees it as one row removed and a new row added, and would set `Status = Removed` on the original. → Mitigation: the differ treats `Name` as the primary key but the `Field ID` (when present) is an alternate key for custom fields — a renamed custom field row is `changed`, not `removed`. The differ logs every primary-key re-mapping as a `warning` so the team can spot accidental renames.
- **The DBOS workflow needs the same DBOS install + DSN as the other 14 reports.** This change assumes `tdt-scheduler` is already configured per the binding `centralized-scheduling-module` change. → Mitigation: the `tasks.md` includes a verification step that checks `tdt-scheduler` is up before declaring the schedule registered.
- **Catalog staleness on `last_seen`.** A label used 91 days ago is no longer in the window and shows `Last Seen = (none)`. → Mitigation: 90 days is configurable, and the `Status` column flags `Active` (seen ≤ 30d) / `Stale` (31-89d) / `Removed` (not seen in window) so the team can spot churn at a glance.

## Migration Plan

- **Deploy order**:
  1. Land the code in `jira-daily-reports` (collector → joiner → differ → writer → CLI → schedule registration).
  2. Run `uv run jira-daily-reports catalog build --dry-run` and inspect the projected sheet content.
  3. Run `uv run jira-daily-reports catalog build` to create the tab, bootstrap `SHEET_LINKS`, and write the first snapshot.
  4. Inspect the tab in the Sprint 16 workbook. Confirm column layout, sort order, and the human-owned column set.
  5. Add `_make_workflow("catalog-refresh", "0 3 * * *")` to `dbos_scheduling.py` inside `register_all_schedules()`. Verify it shows up in `tdt-scheduler list`.
  6. Wait 24h and confirm a second run only writes deltas (differ output should be empty or near-empty).
- **Rollback**:
  1. Unregister the workflow from `tdt-scheduler list` / `tdt-scheduler delete jira-catalog-refresh`.
  2. (Optional) The catalog tab is read-only-toward-Jira; deleting it is a manual `tdt-sheets rm-tab` or a Google Sheets UI delete. No data in Jira is touched.
  3. The `SHEET_LINKS` entry is harmless to leave in place if the tab is removed; the next `build` recreates it.
- **No DB migrations.** The DBOS app uses the same logical database (`tdt_jira_daily_reports`) as the other 14 reports. No schema changes.

## Open Questions

- **Should the writer support a `--project <key>` filter for the on-demand `build` subcommand?** Probably yes (so a single PM can regenerate the catalog for their project), but it can ship in a follow-up if v1 is "all configured projects".
- **Should `Jira Catalog` rows be color-coded by `Status` (Active / Stale / Removed)?** Color coding is the most useful UX, but it is `tdt-sheets` API work. v1 ships monochrome; color is a follow-up.
- **Should the catalog be exposed as an MCP resource so agents can `read_sheet("Jira Catalog")`?** Tempting but out of scope; v1 is a workbook tab the team opens in the browser.
