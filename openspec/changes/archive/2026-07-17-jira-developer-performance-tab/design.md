# Developer Performance Tab — Design

## Context

`jira-daily-reports` currently emits a ticket-centric `Sprint Report` tab and a person-centric `Person Capacity` tab (worklog-mode). Engineering leads need a developer-centric **delivery** view: per-(developer, ticket) rows with merged identity columns, per-ticket metrics on the right (status, MR / deploy timestamps, cycle time, reopen count, stale flag, MR links), and a per-developer aggregate footer band (median / p90 cycle time, total assigned / merged / deployed / stale counts).

Existing client factories, the `tdt_sheets.SheetsClient(ServiceAccountAuth.from_env())` write path, the `_jql_paginated` helper from `jira-daily-reports`, and the `tdt_core.clients.gitlab.GitlabClientFactory` are all in place. There is no GitLab deployments cache, so the design must fetch deployments per MR at run time — bounded by `DEV_PERFORMANCE_DEPLOY_ENVIRONMENT` (default `dev`).

Constraints discovered during research:

- Jira↔GitLab remote-link coverage is incomplete in the org; the join MUST fall back to branch-name regex (`{project_key}-{issue_key}.*`).
- The `Dev in Charge` field is `customfield_11520` (verified by `jira-skill/scripts/configure_dev_fields.py`). The design treats this as an env var (`DEV_PERFORMANCE_DEV_IN_CHARGE_FIELD`) defaulting to that ID.
- The org has 11 Jira projects plus a QA project; the JQL `IN (...)` clause must be chunked at 150 accountIds (matches `person-capacity-worklog-mode` precedent `WORKLOG_JQL_CHUNK_SIZE`).
- Hourly cadence → typical cell writes need to be bounded; a SQLite diff cache at `~/.tdt/state/jira-daily-reports/dev_performance_cache.sqlite` keeps writes to changed rows only.
- **Schedules are auto-generated from `_CRON_*` constants**: `agent-core/deployments/scheduler/generators/jira.py` reads them via `inspect.getsource` from `jira_daily_reports.dbos_scheduling`. Adding a new schedule requires touching both the constants + registration in `dbos_scheduling` AND the `_JIRA_CMDS` list in the agent-core generator.
- **`SheetsClient.batch_update()` requires the sheet's numeric gid**, which is resolved via the `SHEET_LINKS` env var (the pattern established by `jira-catalog-tab`).
- `tdt_sheets` already provides `write_with_links` for `=HYPERLINK(...)` formulas and `batch_update` for `mergeCells` requests — no new SDK methods required.

Stakeholders: engineering managers, tech leads, the program's PM.

## Goals / Non-Goals

**Goals:**

- Add a `Developer Performance` tab to the existing sprint-report spreadsheet, written by a new `jira-daily-reports dev-performance` CLI subcommand on a top-of-hour scheduler cadence.
- Render one row per (developer, ticket). Identity columns 1–7 are merged vertically across each developer's tickets; per-ticket metric columns 8–20 are unmerged.
- Compute per-(developer, ticket) metrics: `In Progress At`, `First MR Merged At`, `First Deploy To Dev At`, `In Progress → Deploy`, `Reopen Count`, `Last Status Change (days)`, `Stale?`, `Linked MR(s)`.
- Compute per-developer aggregates in a footer block below the data rows: median + p90 cycle time, median + p90 reopens per ticket, total assigned / merged / deployed / stale.
- Render a reconciliation footer block: `roster_without_tickets`, `unmapped_dev_in_charge`, `missing_first_deploy`, `joined_via_branch_regex`.
- Use a SQLite diff cache keyed by `(developer_account_id, issue_key)` so hourly runs only emit changed rows.
- Stale thresholds configurable via env vars with safe defaults.
- Use the canonical schedule registration pattern: `_CRON_*` constant in `dbos_scheduling.py` + `register_all_schedules` call + `_JIRA_CMDS` entry in the agent-core generator.

**Non-Goals:**

- Replacing or modifying the existing `Person Capacity` (worklog-mode) tab or the `Sprint Report` tab.
- Adding deploy-to-staging or deploy-to-production columns (only `dev` is in scope).
- Wiring into `jira-skill`'s `CapacitySignal` Pydantic model.
- Building a real-time webhook-based cache.
- Modifying any Android / iOS code, or any Python code outside `jira-daily-reports` and `agent-core/deployments/scheduler/generators/jira.py`.
- Adding new methods to `tdt_sheets`; `batch_update` already covers merge_cells.

## Decisions

### 1. One module per concern under `jira_daily_reports/dev_performance/`

```
dev_performance/
├── cli.py             # Typer command entry; orchestration entrypoint
├── source.py          # JiraSource, GitlabSource facades wrapping tdt_core factories
├── join.py            # issue_key ↔ MR resolution (remote-link precedence, branch regex fallback)
├── metrics.py         # pure functions for cycle_time / reopen_count / stale_flag
├── row_builder.py     # per-(dev, ticket) row construction + merge-range generation
├── summary_builder.py # per-developer aggregates for the footer block
├── sheet_writer.py    # tdt_sheets write pipeline (cells + HYPERLINK + mergeCells)
├── diff_cache.py      # SQLite-backed row diff with advisory lock
└── stale_thresholds.py# env-driven per-status threshold config
```

Rationale: matches the existing `person-capacity-worklog-mode` precedent (one submodule per concern) and `catalog/` (which splits `cli.py` / `collector.py` / `joiner.py` / `writer.py` / `differ.py` similarly). Easier to unit-test in isolation.

### 2. Per-(developer, ticket) row grain with merged identity columns

- One row per `(developer, ticket)`. If `Dev in Charge` changed mid-flight, one row per `(developer, ownership-period, ticket)`.
- Sort locked: `Developer ASC, First Deploy To Dev At DESC NULLS LAST, First MR Merged At DESC NULLS LAST, In Progress At DESC NULLS LAST, Jira Ticket ASC`.
- Merge ranges computed in the same pass from sorted rows; columns 1–7 are merged with `mergeType: MERGE_ALL`; columns 8–20 are not merged. (`MERGE_ROWS` was previously used but does NOT merge cells vertically — it merges only within each row, which is why an earlier version produced 100+ trivial per-row merges instead of one merge per developer.)
- Multi-line ticket cells are NOT used — `HYPERLINK(...)` formulas live in per-row `Jira Ticket` and `Linked MR(s)` columns instead.

Alternatives considered:

- **One row per ticket, ticket-list cells on developer rows** — rejected; multi-line cells can't be merged.
- **One row per developer with summary aggregates only** — rejected; loses per-ticket click-through to Jira / GitLab.
- **Two tabs (summary + detail)** — rejected; doubles the surface area and split-brain risk.

### 3. Jira↔GitLab join: remote-link first, branch regex fallback

- **Primary path:** `GET /rest/api/3/issue/{key}/remotelink` — extract `url` fields matching `git.ecomedic.vn`.
- **Fallback path:** when remote-links are empty, scan GitLab projects matching the issue's `project_key` prefix, then `GET /merge_requests?source_branch=~^{KEY}-.*` per project.
- MR deduplication by `id` (GitLab MR IID) — multiple remote-link URLs pointing at the same MR collapse to one entry.
- The fallback path emits a `dev_performance_join_fallback` debug log and increments the `joined_via_branch_regex` reconciliation counter.

Rationale: the org's remote-link coverage is partial. Branch-name regex is reliable because the org enforces `SR-1234/some-description` as the merge-request title pattern.

### 4. Per-status configurable stale thresholds with safe defaults

Env vars (all optional, all with safe defaults):

| Var | Default |
|-----|---------|
| `DEV_PERFORMANCE_STALE_IN_PROGRESS_DAYS` | `3` |
| `DEV_PERFORMANCE_STALE_CODE_REVIEW_DAYS` | `5` |
| `DEV_PERFORMANCE_STALE_IN_QA_DAYS` | `7` |
| `DEV_PERFORMANCE_STALE_DEPLOY_DAYS` | `14` |

Statuses not in the table default to `False` (not stale) and emit a one-time-per-run warning. `DEV_PERFORMANCE_DONE_STATUSES` defaults to `Done,Closed,Resolved,Deployed to Production`.

Rationale: thresholds are inherently opinionated. Surfacing them as env vars means product can tune without code changes, but defaults match the org's sprint cadence.

### 5. SQLite diff cache keyed by `(developer_account_id, issue_key)`

- Cache path: `DEV_PERFORMANCE_CACHE_PATH` (default `~/.tdt/state/jira-daily-reports/dev_performance_cache.sqlite`, computed via `tdt_core.paths.tdt_state_path`).
- Schema: `CREATE TABLE dev_performance_cache (developer_account_id TEXT, issue_key TEXT, row_payload TEXT, written_at TEXT, PRIMARY KEY (...))`.
- Each row stores the full payload (cols 1–20) as JSON.
- On run: load new rows, deep-diff against cache, emit `UPDATE` for changed rows, evict rows older than 25h at run start.
- Concurrent-run protection: `BEGIN IMMEDIATE` advisory lock; second process fails fast with `dev_performance_lock_held`.
- Corrupted cache: drop table, treat as full re-pull, emit `dev_performance_cache_reset reason=corruption`.

Rationale: 30 developers × 14 tickets × 20 cols = 8,400 cell writes per hour without a diff cache. The cache turns most hours into a <500-cell update. The 25h TTL bounds growth while tolerating 1-hour scheduler drift.

### 6. Run cadence and scheduler integration (canonical pattern)

- Cadence: top of every hour (`0 * * * *`), timezone pinned from `workspace_timezone_name()` (matches every other `jira-daily-reports` schedule).
- **Implementation requires three coordinated edits**:
  1. `src/jira_daily_reports/schedule.py` — add `"dev-performance": ("0 * * * *", "Developer performance to sheet (hourly)")` to `SCHEDULES`
  2. `src/jira_daily_reports/dbos_scheduling.py` — add `_CRON_DEV_PERFORMANCE = "0 * * * *"` constant and `_make_workflow("dev-performance", _CRON_DEV_PERFORMANCE, engine=engine); registered.append("jira-dev-performance")` call in `register_all_schedules`
  3. `agent-core/deployments/scheduler/generators/jira.py` — add `("dev-performance", "dev-performance")` to the `_JIRA_CMDS` tuple list
- After the deploy, the manifest generator emits the new entry into `~/.tdt/schedules/jira-daily-reports.yaml` and DBOS picks it up at next container restart (or via the existing `apply_schedules` flow).
- **Test update required**: `tests/test_dbos_scheduling.py::TestScheduleCount::test_expected_count_is_15` currently asserts a 14-item expected list with the class docstring claiming 15 — update to 15 with `"jira-dev-performance"` appended.
- `automatic_backfill` stays `False` (same as every other jira-daily-reports schedule).

Rationale: hourly matches the org's review cadence and keeps the JQL `updated >= NOW()-2h` filter hot against Jira's `updated` index. The `_CRON_*` constant + `_JIRA_CMDS` tuple pattern is the existing precedent for every other report schedule in this repo.

### 7. Sheets write via `tdt_sheets` SDK (not raw API)

- Construct `SheetsClient(ServiceAccountAuth.from_env())` (matches `jira_daily_reports/delivery/tdt_sheet.py` precedent).
- Tab gid is resolved by parsing `SHEET_LINKS` from `~/.tdt/.env` (matches `jira_daily_reports/catalog/writer.py::Writer._resolve_gid_from_env`). When the tab is auto-created, the gid is appended back to `SHEET_LINKS`.
- Cell writes: `SheetsClient.write(spreadsheet_id, range_ref, values)` for header + data rows.
- HYPERLINK formulas: `SheetsClient.write_with_links(spreadsheet_id, tab_name, [(row, col, url, label), ...])` (the `tdt-sheets` SDK writes `=HYPERLINK(...)` formulas).
- Merge ranges: `SheetsClient.batch_update(spreadsheet_id, [{"mergeCells": {"range": {"sheetId": gid, "startRowIndex": ..., "endRowIndex": ..., "startColumnIndex": 0, "endColumnIndex": 7}, "mergeType": "MERGE_ALL"}}, ...])`. Each write also queries the live sheet for any pre-existing merges that don't match the desired ranges and emits `unmergeCells` requests so the sheet converges to the correct state over time.
- Freeze header row + set column widths in the same `batch_update` call (matches `catalog/Writer.write_header` precedent).

Rationale: zero new auth code; identical 3-level credential fallback + mtime cache + token refresh to every other Sheets consumer in this workspace. No new `tdt-sheets` SDK methods required.

### 8. Reused client factories and helpers (no new auth code)

- `tdt_core.clients.jira.JiraClientFactory` → `PatchedJira.jql` (uses `_jql_paginated` from `jira-daily-reports.client`).
- `tdt_core.clients.gitlab.GitlabClientFactory` → GitLab API v4 client.
- `jira_daily_reports.person_worklog_source.load_roster_display_names()` → roster.
- `jira_daily_reports.work_item_fields.format_value()` → ISO datetime + duration formatting.
- `jira_daily_reports.sheet_primitives.find_column_index()` → column lookup helper.
- `tdt_sheets.ServiceAccountAuth.from_env()` + `SheetsClient(...)` → Sheets write path.
- `jira_skill.scripts.configure_dev_fields.DEV_IN_CHARGE_ID` → default value for `DEV_PERFORMANCE_DEV_IN_CHARGE_FIELD`.

Rationale: zero new dependencies; identical auth / retry / cache semantics to existing consumers.

## Risks / Trade-offs

- **[Risk] Remote-link coverage <50% → fallback path is hot** → Branch-name regex is reliable given the org's MR-title convention; fallback failures emit a `joined_via_branch_regex` reconciliation counter so ops can spot drift.
- **[Risk] Dev in Charge field empty on legacy tickets** → Skip + reconciliation row in footer; never block the tab.
- **[Risk] Dev in Charge field ID drifts (customfield_11520 renames)** → `DEV_PERFORMANCE_DEV_IN_CHARGE_FIELD` env var lets ops re-pin without code changes; default matches `jira-skill/scripts/configure_dev_fields.py` constant.
- **[Risk] GitLab `dev` environment not configured on some projects** → `missing_first_deploy` reconciliation row + diagnostic samples.
- **[Risk] Roster churn (member_key changes, new joiners)** → Roster is re-pulled on every run (worklog-mode precedent).
- **[Risk] Sheets API quota exceeded on large teams** → Diff cache reduces typical hourly writes to <500 cells.
- **[Risk] Cache grows unbounded if a developer never reappears** → 25h eviction + manual `--prune-cache` CLI flag for ad-hoc ops.
- **[Risk] Merge ranges shift if sort is unstable** → Sort is locked at row_builder output; merge ranges computed deterministically from sorted rows.
- **[Risk] Schedule manifest generator picks up the new constant without redeploy** → The generator runs at scheduler container start; if `agent-core` is deployed before `jira-daily-reports`, the generator emits `WARNING: source not found` and writes an empty manifest. **Deploy order: `jira-daily-reports` first, then `agent-core`.** Documented in Migration Plan step 1.

## Migration Plan

1. **Deploy `jira-daily-reports`** first (must land before `agent-core` deploy). Includes the new module, the `_CRON_DEV_PERFORMANCE` constant, the `register_all_schedules` entry, the `SCHEDULES` dict entry, and the test update.
2. Run `ruff check src/ tests/ --fix && ruff format .` and `mypy src/jira_daily_reports/dev_performance/ --strict` and `pytest -x tests/dev_performance tests/integration/dev_performance tests/test_dbos_scheduling.py` locally.
3. **Deploy `agent-core`** — picks up the updated `_JIRA_CMDS` tuple list and emits the new schedule into `~/.tdt/schedules/jira-daily-reports.yaml`.
4. Restart the scheduler container (or trigger `apply_schedules` flow) so DBOS picks up the new manifest.
5. First live run is a dry-run: write the `Developer Performance` tab against a copy of the live spreadsheet and verify the row count against `unmapped_dev_in_charge` reconciliation.
6. Flip the schedule from dry-run to live write.

**Rollback:** Disable the `jira_dev_performance` schedule in DBOS. The `Developer Performance` tab is left in place (idempotent — re-running produces the same content). No data on `Sprint Report` or `Person Capacity` is affected by this change. Reverting the generator's `_JIRA_CMDS` tuple list (in `agent-core`) and re-deploying `agent-core` removes the schedule from the regenerated manifest.

## Open Questions

None at write time. All decisions are anchored in either existing precedent (`person-capacity-worklog-mode`, `jira-catalog-tab`, `schedule.py`) or org-confirmed config (deployment environment name, MR-title regex pattern, `Dev in Charge` field ID).