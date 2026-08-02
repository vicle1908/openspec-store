# Tasks — Sprint Spreadsheet as Single Source of Truth

## 1. tdt-core: Jira create/search primitives
- [x] 1.1 Add `search_filters(name)` to `PatchedJira` (`GET /rest/api/3/filter/search?filterName=`)
- [x] 1.2 Add `create_filter(name, jql, share_authenticated)` (`POST /rest/api/3/filter`)
- [x] 1.3 Add `search_boards(name)` (`GET /rest/agile/1.0/board?name=`)
- [x] 1.4 Add `create_board(name, filter_id, type="kanban")` (`POST /rest/agile/1.0/board`)
- [x] 1.5 Unit tests for the four methods (mock transport)

## 2. tdt-core: SprintScope resolver
- [x] 2.1 Add `SprintScope` dataclass (spreadsheet_id, sprint_number, sprint_dates, filter_id, board_id, filter_name, board_name)
- [x] 2.2 Add `resolve_sprint_scope(jira, spreadsheet_id, issue_keys, dry_run, filter_id_override, board_id_override)` find-or-create
- [x] 2.3 Resolve filter/board from spreadsheet title; treat explicit ids as optional fallback cache only
- [x] 2.4 Board-create failure → fall back to override id, log, do not abort
- [x] 2.5 Unit tests: find-existing, create-missing, dry-run, override, board fallback

## 3. KBS: wire resolver into sync
- [x] 3.1 In `cli.sync`, after JQL build, call `resolve_sprint_scope` instead of using static `cfg.filter_id`
- [x] 3.2 Use resolved filter_id for `update_filter`, resolved board_id for `verify_count`
- [x] 3.3 Make `WorkflowConfig.filter_id/board_id` optional (default `None`) and keep KBS env loading spreadsheet-first (`SPREADSHEET_ID` only for sprint scope). Tests made hermetic against ambient env values.
- [x] 3.4 Surface resolved ids in `SyncResult` + console URLs
- [x] 3.5 Tests: sync reuses resolved override + refreshes JQL; dry-run makes no writes; `JIRA_*` precedence (resolver create/dry-run branches unit-tested in tdt-core test_sprint_scope.py)

## 4. jira-daily-reports + epic-report: consume resolved scope
- [x] 4.1 `sprint_report_sheet` resolves filter/board via spreadsheet scope first; Jira ids are fallback cache only
- [x] 4.2 Derive `SPRINT_NUMBER` from workbook title when unset
- [x] 4.3 epic-report: spreadsheet_url remains the only required output config (verified — epic-report consumes spreadsheet_url + JiraConfig only; no filter/board coupling)
- [x] 4.4 Tests cover derive-from-sheet path (TestSprintScopeResolution in test_sprint_report_sheet.py)

## 5. ~/.tdt config → Sprint 16, spreadsheet-first
- [x] 5.1 `.env`: `SPREADSHEET_ID` → Sprint 16 id/link; filter/board cache vars optional; drop hard `SPRINT_NUMBER`
- [x] 5.2 `config.toml`: add `sprint_sheets.sprint_16`; point primary at S16; mark filter/board derived
- [x] 5.3 `config.yaml`: `sprint_report.spreadsheet_url` → S16
- [x] 5.4 `epic-report-config.toml`: `spreadsheet_url` → S16

## 6. Scheduling alignment
- [x] 6.1 Correct `run-sprint-sheet.sh` header comment (`0 18 * * *` → `0 * * * *` per `schedule.py`)
- [x] 6.2 Confirm DBOS `sprint-sheet` cadence unchanged; note resolver runs inside it

## 7. Docs + skills
- [x] 7.1 `kanban-board-from-spreadsheet` SKILL: document spreadsheet-as-SSOT + find-or-create
- [x] 7.2 `jira-daily-reports` SKILL + `.env.example`: filter/board optional, derived from sheet
- [x] 7.3 Repo READMEs (kbs, jira-daily-reports, tdt-core) note resolver
- [x] 7.4 Update `~/.tdt/config.toml` header comment to describe SSOT model

## 8. Verify
- [x] 8.1 `openspec validate jira-sprint-spreadsheet-ssot --type change --strict`
- [x] 8.2 tdt-core + kbs + jira-daily-reports: ruff + mypy + pytest (src AND tests)
- [x] 8.3 `kbs sync --spreadsheet <S16 id-or-url> --dry-run` shows intended filter/board resolve
- [x] 8.4 Confirm config loads (JiraConfig.from_env, WorkflowConfig.from_env)
