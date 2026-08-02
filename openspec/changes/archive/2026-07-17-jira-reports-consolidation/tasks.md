# TDT Ecosystem - Tasks

**Status:** ✅ Phases 1-4 + 6 + 7 Implemented (Phase 5 deferred)  
**Date:** 2026-05-27  
**CI:** GitLab CI (git.ecomedic.vn) — configured and pushed  
**Workflow:** Local-first development, push to GitLab when ready

**Archive reconciliation (2026-07-17):** Optional email and Slack delivery code is complete and activates only when configured. Later `jira-epic-report` spreadsheet health, filtering, time-based capacity utilization, and role-grouping semantics are tracked separately by `jira-epic-report-archive-gap-closure`; they do not reopen this consolidation change's completed extraction and delivery scope.

---

## Phase 1: Extract tdt-core (1 day) — ✅ COMPLETE

### Task 1.1: Scaffold tdt-core project — ✅
### Task 1.2: Move env loading to tdt-core — ✅
### Task 1.3: Move JiraConfig to tdt-core — ✅ (includes PatchedJira for search/jql)
### Task 1.3b: Extract PatchedJira to module level — ✅ (2026-05-22)

- PatchedJira promoted from nested class inside `create_client()` to module-level export
- `from tdt_core.clients.jira import PatchedJira` now works directly
- Methods: `jql()`, `add_comment_adf()`, `get_issue_changelog()`, `delete_comment()`
- `jira-epic-report/epic_report/jira_client.py` → thin re-export from tdt-core (67 LOC removed)
### Task 1.4: Move GitlabConfig to tdt-core — ✅
### Task 1.5: Add shared domain models — ✅
### Task 1.6: Verify all consumers still work — ✅

---

## Phase 2: Create jira-daily-reports (1-2 days) — ✅ COMPLETE

### Task 2.1: Scaffold project — ✅
### Task 2.2: Migrate critical reports (3) — ✅ (standup, blocked, missing_info)
### Task 2.3: Migrate medium-priority reports (4) — ✅ (wip, velocity, platform, priority)
### Task 2.4: Migrate low-priority reports (2) — ✅ (code_review, sprint_health)
### Task 2.5: Add delivery mechanisms — ✅ Complete

- ✅ `delivery/file.py` — markdown file output
- ✅ `delivery/terminal.py` — rich terminal output
- ✅ `delivery/email.py` — implemented and wired; no-op when `SMTP_HOST` is absent
- ✅ `delivery/slack.py` — implemented and wired; no-op when `SLACK_WEBHOOK_URL` is absent

### Task 2.6: Add cron integration — ✅ Complete

- `schedule.py` module with `SCHEDULES` dict (9 reports × cron expressions)
- `generate_crontab()` generates full crontab block
- `install_crontab()` appends to system crontab (replaces old block)
- CLI: `jira-daily-reports schedule` (show) / `--install` (install to crontab)
- 7 tests covering generation, project flags, header/footer

### Task 2.7: Sprint Report Sheet (Target vs Actual) — ✅ Complete

- `reports/sprint_report_sheet.py` — SprintReportSheetReport class (321 lines)
  - Reads Jira issues via filter, computes status/priority/platform/type/WIP metrics
  - Compares actual status against spreadsheet Target Status using workflow rank
  - Produces `ReportResult` with full summary dict + per-issue verdict data
  - `build_sheet_rows()` generates Google Sheets rows with `=HYPERLINK()` formulas
  - `format_markdown()` for terminal/file output
- `delivery/sheet.py` — Google Sheets delivery mechanism (133 lines)
  - `read_bucket_targets()` — reads Target Status from 3 bucket sheets via gws batchGet
  - `ensure_sheet()` — creates tab if missing via batchUpdate
  - `clear_and_write()` — idempotent overwrite via values clear + update
  - `write_sheet()` — orchestrates full flow, returns sheet URL
- CLI: `jira-daily-reports sprint-sheet` (default: sheet output)
  - `--output sheet` (default) — writes to Google Sheet
  - `--output terminal` — rich terminal rendering
  - `--output markdown` — markdown file output
- Hyperlinks: Filter, Board, and all issue keys are clickable
- Target validation: only recognized workflow statuses accepted (junk filtered)
- Workflow order: To Do → In Progress → Code Review → Deploy in Dev → SIT → Test Done → Done
- Verdict logic: ✅ Met (actual ≥ target) | ❌ Behind | 🚫 Rejected | — (no target)
- Audit logging: writes to `~/.tdt/logs/jira-reports.log` (same format as bash scripts)
- Legacy bash script kept at `.agents/skills/jira-daily-reports/scripts/sprint_report_to_sheet.py`
- Skill SKILL.md updated to reference Python CLI as primary

### Task 2.8: Native Jira Dashboard Generator — ✅ Complete

- `delivery/jira_dashboard.py` — programmatic dashboard builder (183 lines)
  - `GADGET_URIS` dict — 11 verified gadget URIs from Cloud instance
  - `build_default_layout()` — 8-gadget layout covering 6 of 10 custom reports
  - `find_or_create_dashboard()` — idempotent find-by-name with fallback create
  - `remove_all_gadgets()` + `add_gadget()` — overwrite semantics with per-property config
  - `build_dashboard()` — orchestrator returning (dashboard_id, gadget_count)
- CLI: `jira-daily-reports dashboard` (--name, --filter-id)
- 12 unit tests (mocked Jira client) — all passing
- Coverage map: ~80% of custom reports mirrored in native Jira UI
- Resilient: per-gadget errors logged but don't abort the run
- Hybrid recommendation: Python CLI for automation/alerting, Jira Dashboard for visual exploration

### Task 2.9: Cycle Time + WIP Age Enhancement Reports — ✅ Complete

Closes coverage gaps identified in 2026-05-22 research session: native Jira reports
provide aggregate Resolution Time + Average Time in Status, but neither surfaces
per-issue cycle time or per-ticket stuck-time alerts.

- `reports/cycle_time.py` — CycleTimeReport (104 lines)
  - Reads `created` + `resolutiondate` for all Done tickets via filter
  - Computes per-project avg/median/p95 cycle time
  - Skips tickets without resolution date (counted in summary)
- `reports/wip_age.py` — WipAgeReport (107 lines)
  - JQL filter for active statuses (In Progress, Code Review, SIT, Deploy in Dev, Test Done)
  - Days since last `updated` per ticket
  - Threshold flags: 🔴 >7d, 🟡 >3d, 🟢 ≤3d
  - Sorted by age descending — stuck work surfaces first
- CLI: `jira-daily-reports cycle-time` + `wip-age`
- Schedule: cycle-time Fri 6 PM, wip-age Daily 5 PM
- run-all integration: both run in batch
- 6 unit tests (mocked Jira) — all passing
- Live data validation: 14 critical 🔴 items found (>7 days stuck), previously
  invisible in basic `wip` report

### Task 2.10: Output Format Consistency — ✅ Complete

Closes the divergence between terminal and markdown rendering paths.

- `delivery/terminal.py` rewritten — renders `report.format_markdown()` via Rich Markdown
  - Previous version had hardcoded generic key/summary/status table (ignored per-report metrics)
  - All metrics, flags, breakdowns now appear identically in terminal and `.md` file
- `delivery/json_out.py` — new (51 lines)
  - `to_dict()` / `to_json()` / `write_json()` with emoji preservation
  - Serializes full `result.summary` for machine consumption
- CLI: `--output json` added to all 11 report commands
- 9 unit tests — all passing
- Single source of truth: each report's `format_markdown()` (text) + `result.summary` (data)
- Output guarantee: Numbers match across terminal / markdown / JSON / sheet

### Task 2.11: Sprint Sheet Metadata Enrichment (Estimation/Start/End/Logwork/Summary) — ✅ Complete

Closes current gap where sprint-sheet focuses on target-vs-actual but lacks
estimation/time-tracking/date completeness detail per work item.

- [x] Add sprint metadata block (sprint start date, sprint end date) to sheet + markdown output
- [x] Add per-work-item estimation column(s):
  - [x] estimation value
  - [x] estimation source/field marker
  - [x] missing-estimation flag
- [x] Add per-work-item start date + end date columns with fallback mapping
- [x] Add per-work-item logwork columns:
  - [x] total logged work
  - [x] worklog count or compact worklog summary
  - [x] missing-logwork flag
- [x] Add sprint-level summarization section:
  - [x] total estimation
  - [x] total logged work
  - [x] completeness coverage (% with estimation/start/end/logwork)
  - [x] risk summary (behind target, overdue/missing fields)
  - [x] short narrative summary for stakeholders
- [x] Ensure implementation uses `atlassian-python-api` via `tdt-core` (no acli fallback in Python path)
- [x] Validate live retrieval on filter `15113` + board `1067` before release
- [x] Confirm graceful fallback when sprint metadata, board-estimation, or worklogs are absent
- [x] Distinguish `missing` vs `unavailable` in enriched per-item output
- [x] Add tests for field normalization and summary aggregation

### Task 2.12: Centralize sprint-sheet work-item retrieval/normalization — ✅ Complete

- [x] Make `src/jira_daily_reports/work_item_fields.py` the canonical helper module for:
  - [x] board capability extraction
  - [x] date-field discovery
  - [x] sprint metadata retrieval
  - [x] estimation normalization
  - [x] date normalization
  - [x] worklog normalization
- [x] Update `reports/sprint_report_sheet.py` to consume shared helpers instead of re-implementing them inline
- [x] Add direct unit tests for shared helper behavior (`tests/test_work_item_fields.py`)
- [x] Update README/spec docs to document centralized work-item field logic

---

## Phase 3: Wire jira-epic-report to tdt-core (0.5 day) — ✅ COMPLETE

### Task 3.1: Replace env loading — ✅
### Task 3.2: Optionally adopt JiraConfig — ✅

---

## Phase 4: Migrate webhook-receiver to python-gitlab (1 day) — ✅ COMPLETE

### Task 4.1: Replace GitLabClient with python-gitlab — ✅
### Task 4.2: Update error handling — ✅
### Task 4.3: Update tests — ✅
### Task 4.4: Remove glab dependency — ⚠️ Partial (code done, Dockerfile kept for debugging)

---

## Phase 5: ops-automation-suite adoption — 🔲 DEFERRED

### Task 5.1: Depend on tdt-core from start — Not started (project early stage)

---

## Phase 6: GitLab CI/CD Pipeline — ✅ COMPLETE

### Task 6.1: Create .gitlab-ci.yml template — ✅

**Status:** ✅ Done (2026-05-27)

All 5 projects use a consistent CI template with:
- `stages: check, test` with uv setup (Python 3.14, uv 0.11.15)
- Cache for `.uv-cache` and `.venv` per job/branch
- `lint`: `uv run ruff check .` + `uv run ruff format --check .`
- `typecheck`: `uv run mypy` (allow_failure varies by project maturity)
- `test`: `uv run pytest` with JUnit XML artifacts and coverage regex

### Task 6.2: Add .gitlab-ci.yml to each project — ✅

All 5 projects configured and committed:
- [x] tdt-core (commit `4d736aa`)
- [x] jira-skill (commit `01ab2c2`)
- [x] jira-daily-reports (commit `ce1f29f`)
- [x] jira-epic-report (commit `808661d`)
- [x] webhook-receiver (commit `4a4561d`)

### Task 6.3: Configure GitLab runners — ✅

**Status:** ✅ Verified (2026-05-27)

Shared runners confirmed available on git.ecomedic.vn.
All CI configs target shared runners (no custom runner tags needed).

---

## Phase 7: Bash → Python Skill Migration — ✅ COMPLETE

### Task 7.1: Align kbs with bash kanban skill — ✅

**Status:** ✅ Done (2026-05-22)  
**Repo:** `tdt/jira-kanban-from-spreadsheet/` (commits `bc222c4`, `16e5da3`)

Feature parity reached with `.agents/skills/kanban-board-from-spreadsheet/`:
- ORDER BY Rank ASC default in JQL builder
- Filter share permissions (`{"type":"authenticated"}`)
- Sprint dates in filter name (`Sprint 14 (11 May - 22 May)`)
- Board/Filter URLs printed after sync
- Platform labels from Side column (iOS/AOS/API/Web)
- Priority field updates (case-insensitive normalization)
- Time estimate (hours × 3600 → `timeoriginalestimate`)
- Rate limiting (0.15s between Jira API calls)
- Dynamic bucket sheet discovery (`discover_bucket_sheets`)
- 102 tests pass, live verified against filter 15113

### Task 7.2: Update bash skill SKILL.md files to delegate to Python — ✅

**Status:** ✅ Done (2026-05-22)

Skill files updated with Python-first delegation blocks:
- ✅ `.agents/skills/kanban-board-from-spreadsheet/SKILL.md` — full Python kbs section + Quick Reference table mapping each step to `kbs` command
- ✅ `.agents/skills/jira-jql-builder/SKILL.md` — migration note (JQL generation now in `kbs.jira.jql_builder`)
- ✅ `.agents/skills/jira-daily-reports/SKILL.md` — migration notice (already in place from Phase 2)
- ✅ `.agents/skills/jira-comprehensive-management/SKILL.md` — migration note pointing to 5 Python repos
- ✅ `.agents/skills/jira-integration/SKILL.md` — migration note pointing to webhook-receiver, tdt-core, jira-skill

`config/claude/skills/` mirror automatically synced (legacy cloud, identical file sizes).

### Task 7.3: Document remaining skills as legacy/reference — ✅

**Status:** ✅ Done

Skills retained as reference (not deprecated, not the primary path):
- `gws-sheets`, `gws-sheets-read`, `gws-sheets-append` — Google Workspace CLI auth/usage docs (still useful for kbs `GwsCliBackend`)
- `acli` — Atlassian CLI reference (still used in interactive workflows)
- `jira-jql-builder` — JQL pattern catalog (Python embeds the patterns; skill keeps the docs)
- `jira-comprehensive-management` — workflow reference
- `jira-integration` — branch-naming conventions, smart-commits guide

### Bash → Python migration summary

| Bash Skill | Primary Python Implementation | Status |
|---|---|---|
| `kanban-board-from-spreadsheet` | `tdt/jira-kanban-from-spreadsheet/` (`kbs` CLI) | ✅ Migrated |
| `jira-daily-reports` | `tdt/jira-daily-reports/` | ✅ Migrated |
| `jira-jql-builder` | `tdt/jira-kanban-from-spreadsheet/src/kbs/jira/jql_builder.py` | ✅ Embedded |
| `gws-sheets*` | `tdt/jira-kanban-from-spreadsheet/src/kbs/sheets/reader.py` (`GwsCliBackend`) | ✅ Embedded |
| `jira-comprehensive-management` | `tdt-core` + `jira-skill` + `jira-epic-report` + `jira-daily-reports` | ✅ Migrated |
| `jira-integration` | `tdt-core` (clients) + `webhook-receiver` (events) | ✅ Migrated |
| `acli` | _kept as reference; Python uses atlassian-python-api via tdt-core_ | Reference only |

---

## Success Criteria

- [x] `tdt-core` passes its own test suite (17/17)
- [x] All 4 existing projects pass their tests after wiring
- [x] New `jira-daily-reports` project has 9 reports with tests (31 tests)
- [x] webhook-receiver uses python-gitlab (no glab for API calls)
- [x] A new tool can authenticate to Jira+GitLab in 3 lines of code
- [x] Zero duplication of `~/.tdt/.env` loading logic
- [x] GitLab CI pipeline configured for all projects (5/5 `.gitlab-ci.yml` written)
- [x] Optional Email/Slack delivery for daily reports — implemented as environment-gated no-op when unconfigured and verified by `tests/test_delivery_notifications.py` on 2026-07-17
