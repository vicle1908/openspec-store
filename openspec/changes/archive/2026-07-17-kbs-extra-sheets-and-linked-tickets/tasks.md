## 1. Config inputs (sprint-extra-sheets, sprint-linked-ticket-expansion)

- [x] 1.1 Add `sheet_links: list[str]` to `WorkflowConfig` with `SHEET_LINKS` env (comma-separated URLs)
- [x] 1.2 Add `expand_linked: bool`, `link_expand_project: str = "PUB"`, `excluded_link_types: list[str] = ["Cloners"]` with `EXPAND_LINKED` / `LINK_EXPAND_PROJECT` / `EXCLUDED_LINK_TYPES` env
- [x] 1.3 Document each new field default and note that all new inputs are opt-in in `config/workflow.yaml`
- [x] 1.4 Add `board_mode: str = "kanban"` (`kanban` | `sprint` | `both`) with `BOARD_MODE` env; defaults preserve current behavior

## 2. gid → tab-title resolution (sprint-extra-sheets)

- [x] 2.1 Add `resolve_gids_to_titles(spreadsheet_id, gids)` to `TdtSheetsBackend` using `get_sheet_by_gid`
- [x] 2.2 Add passthrough on `SheetsReader` and the `SheetsBackend` Protocol
- [x] 2.3 Log a warning for gids not found in spreadsheet metadata (skip, do not fail)

## 3. Merge URL-derived tabs into extraction (sprint-extra-sheets)

- [x] 3.1 In `_read_sheets`, parse `cfg.sheet_links` via `tdt_sheets.utils.parse_url` to gids
- [x] 3.2 Resolve gids → titles and append to `sheet_targets` with order-preserving dedup
- [x] 3.3 Add tests proving merged rows from URL-derived tabs flow through existing `parse_rows` + issue-key dedup + per-tab error reporting unchanged

## 4. Linked-ticket expansion (sprint-linked-ticket-expansion)

- [x] 4.1 Create `src/kbs/jira/link_expander.py` with `expand_linked_issues(jira, keys, *, source_project, excluded_link_types)`
- [x] 4.2 Filter source keys to `source_project`; fetch `issuelinks` via chunked `key in (...)` JQL
- [x] 4.3 Collect inward+outward linked keys; skip links whose type name is in `excluded_link_types` (default `Cloners`); allow targets in any project; subtract original keys
- [x] 4.4 Default `DEFAULT_EXCLUDED_LINK_TYPES = frozenset({"Cloners"})`

## 5. CLI wiring (both capabilities)

- [x] 5.1 Hoist `JiraClientFactory.from_env()` before JQL build (reads safe in dry-run)
- [x] 5.2 When `cfg.expand_linked`, expand `issue_keys` before `build_cross_project_jql`, order-preserving dedup
- [x] 5.3 Surface expansion count in console output / `SyncResult`

## 5b. Agile sprint creation (sprint-agile-creation)

- [x] 5b.1 Add to `tdt_core` `PatchedJira`: `search_sprints(board_id, state)`, `create_sprint(name, origin_board_id, start, end, goal=None)`, `move_issues_to_sprint(sprint_id, keys)` (agile v1.0 endpoints)
- [x] 5b.2 Create `src/kbs/jira/sprint_sync.py`: find-or-create scrum board (`create_board(board_type="scrum")`) backed by the resolved filter, distinct name (e.g. `Sprint N Board (Scrum)`)
- [x] 5b.3 Find-or-create the sprint by canonical name on the scrum board; parse start/end from title dates with year inference (current year, roll to next year only if wholly past); create in future state
- [x] 5b.4 On live run, move planned issue keys into the sprint in ≤50-key chunks; dry-run reports intended actions only
- [x] 5b.5 In `cli.py`, after filter resolution, run sprint path when `cfg.board_mode` is `sprint` or `both`; gate all writes behind live mode
- [x] 5b.6 Surface created/resolved sprint + scrum board ids in console / `SyncResult`
- [x] 5b.7 Make board verification compare against the expanded post-link key count, not the pre-expansion sheet-only count

## 5c. End-to-end orchestration + report refresh (sprint-end-to-end-orchestration)

- [x] 5c.1 Add `refresh_reports: bool = False` to `WorkflowConfig` with `REFRESH_REPORTS` env (opt-in)
- [x] 5c.2 Order the `sync` pipeline: read sheets → extract+merge → expand links → build JQL → resolve/update filter → board/sprint per `board_mode` → (live) report refresh
- [x] 5c.3 When `refresh_reports` and live, invoke the `sprint-sheet` write path (generalize `_run_post_sync_reports`, pass the resolved `--spreadsheet`) so `Sprint Report` + `Person Capacity` regenerate from one snapshot
- [x] 5c.4 Hand off the resolved expanded key set explicitly (resolved keys + filter id), NOT via the filter-fallback path (validated unreachable: `write_sheet()` re-reads bucket scope and `run()` prefers `issuekey in (<bucket_keys>)`)
- [x] 5c.5 Classify stages required (fail-stop, non-zero exit) vs non-required (fail-soft, recorded in `SyncResult.errors`): required = spreadsheet resolution, scope extraction, JQL build, filter resolve/update; non-required = per-tab reads, link expansion, board verify, report refresh. Dry-run performs no writes/report regen; final `SyncResult.success` is true only when no required stage failed
- [x] 5c.6 Error when no spreadsheet is resolvable (neither `--spreadsheet` nor `SPREADSHEET_ID`) before any Jira/Sheets call, naming both inputs
- [x] 5c.7 Ensure required-stage failures exit non-zero and are reflected in `SyncResult.errors`, while non-required stage failures remain fail-soft
- [x] 5c.8 Config precedence: defaults < `~/.tdt/.env`/YAML < CLI option overrides. Expose `--board-mode`, `--expand-linked/--no-expand-linked`, `--refresh-reports/--no-refresh-reports` on `kbs sync`; unset options fall through to env/config; `_load_config` re-validates overrides (`model_copy` bypasses validators)

## 5d. jira-daily-reports scope handoff (sprint-end-to-end-orchestration, cross-repo)

- [x] 5d.1 Add optional `resolved_scope` (keys + filter id) to `SprintReportSheetReport` and `delivery/tdt_sheet.write_sheet()`
- [x] 5d.2 In `write_sheet()`, skip the unconditional `read_sprint_ticket_scope()` / `set_bucket_keys()` overwrite when a caller scope is provided
- [x] 5d.3 In `run()`, seed `issuekey in (<resolved_keys>)` from the caller scope when present; preserve bucket-key behavior when absent
- [x] 5d.4 Confirm `_expand_issue_graph` seeds from the resolved keys (widen-only) and never narrows the resolved scope
- [x] 5d.5 Tests: caller scope honored (no bucket re-read), standalone run still bucket-derived, expanded keys present in report rows
- [x] 5d.6 Apply readable sheet formatting after writing `Sprint Report` + `Person Capacity` (sheet-specific widths + wrap text + top alignment)

## 5e. Per-sprint dashboard + report header links (sprint-report-links)

Dashboard creation lives in **jdr** (where `jira_skill.dashboard` + report rendering
already are); kbs has no `jira_skill` dependency and only hands off ids.

- [x] 5e.1 jdr: add `dashboard_name_for(sprint_number)` canonical name (e.g. `Sprint N Dashboard`); reuse `delivery/jira_dashboard.build_dashboard` (shared `jira_skill.dashboard` find-or-create) backed by the resolved filter id
- [x] 5e.2 jdr report path: when a sprint number + resolved filter are present on a live run, find-or-create the per-sprint dashboard after filter resolution; dry-run/standalone reports intended dashboard only and does not create it; failure is fail-soft (logged, link omitted)
- [x] 5e.3 kbs: extend the handoff env in `_run_post_sync_reports` with `RESOLVED_BOARD_ID`, `RESOLVED_SPRINT_ID`, `RESOLVED_PROJECT_KEY` alongside `RESOLVED_FILTER_ID`/`RESOLVED_SCOPE_KEYS`; surface `sprint_id`/`scrum_board_id` already in `SyncResult`
- [x] 5e.4 jdr `SprintReportSheetReport`: read the new resolved ids (env + optional `resolved_scope`); expose `sprint_id`, `dashboard_id` (from find-or-create), `board_id`, `project_key` for rendering; absent ids → blank link (no crash)
- [x] 5e.5 jdr `build_sheet_rows`: render header link rows for Filter, Board, Sprint, Dashboard via `_hyperlink`; each rendered only when its id is present. Sprint URL `{site}/jira/software/c/projects/{project}/boards/{board_id}?sprint={sprint_id}`; dashboard URL `{site}/jira/dashboards/{dashboard_id}`
- [x] 5e.6 Preserve existing Filter/Board rendering exactly when only those ids are present (backward compatible standalone runs); markdown header gains the same links additively
- [x] 5e.7 Tests (kbs): `test_cli.py` handoff env carries `RESOLVED_BOARD_ID`/`RESOLVED_SPRINT_ID`/`RESOLVED_PROJECT_KEY` when sprint resolved
- [x] 5e.8 Tests (jdr): per-sprint dashboard find-or-create on live (dry-run/standalone no-write); `build_sheet_rows` renders all four links when ids present; renders only Filter/Board when sprint/dashboard absent; HYPERLINK formula shape asserted

## 6. Tests

- [x] 6.1 `test_config.py`: new fields + env parsing (canonical + empty defaults)
- [x] 6.2 `tests/sheets/test_reader.py`: `resolve_gids_to_titles` with fake backend (found, missing gid)
- [x] 6.3 `test_cli.py`: `_read_sheets` merges URL-derived tabs and dedups by issue key
- [x] 6.4 `tests/jira/test_link_expander.py` (new): clone exclusion, source-project filter, inward/outward, any-project targets, chunking
- [x] 6.5 `test_cli.py`: sync expands linked keys when `expand_linked` enabled; no-op when disabled
- [x] 6.6 `tests/jira/test_sprint_sync.py` (new): scrum board find-or-create, sprint find-or-create, date/year inference, chunked move, dry-run no-write
- [x] 6.7 `test_cli.py`: `board_mode` selects kanban/sprint/both; sprint path no-ops in dry-run
- [x] 6.8 `test_cli.py`: `refresh_reports` invokes report path only on live run; dry-run regenerates nothing
- [x] 6.9 `test_config.py`: `_load_config` override precedence (CLI > env, unset falls through) + override re-validation rejects invalid `board_mode`; `test_cli.py`: `--board-mode` overrides env
- [x] 6.10 `tests/test_tdt_sheet.py`: formatting requests applied for both report sheets and include wrap/text sizing

## 7. Docs & skill

- [x] 7.1 `README.md` + `OPERATOR_RUNBOOK.md`: document `SHEET_LINKS`, `EXPAND_LINKED`, `LINK_EXPAND_PROJECT`, `BOARD_MODE`, `REFRESH_REPORTS`
- [x] 7.2 `board-from-spreadsheet` SKILL.md: document extra sheets (by URL), linked-ticket expansion (exclude clones, any-project targets), the agile sprint option, and the end-to-end pipeline with report/capacity refresh

## 8. Verify

- [x] 8.1 Hermetic `ruff check`, `mypy`, `pytest` for `jira-kanban-from-spreadsheet` and `jira-daily-reports`
- [x] 8.2 `openspec validate kbs-extra-sheets-and-linked-tickets --type change --strict`
