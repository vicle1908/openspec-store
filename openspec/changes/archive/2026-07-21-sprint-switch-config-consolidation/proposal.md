# sprint-switch-config-consolidation

## Why

Transitioning to a new sprint (e.g. Sprint 18 → 19) requires editing **5 files across ~10 locations** manually:

1. `~/.tdt/.env` — `SPREADSHEET_ID`, `SHEET_LINKS`, `JIRA_DEFAULT_FILTER_IDS`, comments
2. `~/.tdt/config.toml` — `sprint_spreadsheet_id`, `kanban_from_spreadsheet.spreadsheet_id`, `[jira]` section, new `[sprint_sheets.sprint_N]`
3. `~/.tdt/config.yaml` — `sprint_report.spreadsheet_url`
4. `jira-daily-reports` source — `dbos_scheduling.py` hardcoded fallback
5. Freshness state — stale `<old_spreadsheet_id>.json`

Additionally, `SHEET_LINKS` must be cleared (stale gids cause silent wrong-tab writes), and `sprint-bootstrap` must be run to create the Jira filter/board. There is no single command, no single source of truth, and no validation.

The Sprint 18 → 19 migration on 2026-07-21 took ~15 minutes of manual config editing across 5 files. This is error-prone and does not scale.

## What Changes

### Config consolidation + CLI

- **Add `current_sprint` key to `config.toml`** — single source of truth for the active sprint number. All consumers derive the spreadsheet ID from this.
- **Add `load_sprint_config()` bridge in `tdt_core.config`** — reads `config.toml` and injects values into `os.environ` so existing `os.getenv()` calls work unchanged. Uses `setdefault` so `.env` values still override during migration.
- **Add `sprint-switch` CLI command** — single command that: parses workbook title → updates config.toml → derives .env → clears stale state → runs bootstrap → validates.
- **Migrate sprint-critical vars from `.env` to `config.toml`** — `SPREADSHEET_ID`, `JIRA_DEFAULT_FILTER_IDS`, `PERSON_CAPACITY_*`, `DEV_PERFORMANCE_*`, `REPORT_FRESHNESS_*`. Credentials stay in `.env`.
- **Update `config.yaml`** — `sprint_report.spreadsheet_url` kept in sync by sprint-switch.

### Legacy cleanup

- **Delete SHEET_LINKS gid cache mechanism** — entire `_env_quoting.py` module, `persist_gid_to_sheet_links()` in 2 files, `_resolve_sheet_links()` in tdt_sheet.py. Replace with dynamic tab ID discovery via Sheets API.
- **Delete legacy `.env` backup files** — 4 stale backup files from Sprint 16 era.
- **Remove legacy state migration code** — `migrate_legacy_state_file/dir` calls in tdt_sheet.py and webhook-receiver/settings.py. Migration complete, code is dead.
- **Archive stale config.toml sprint entries** — keep only sprint 18 (archived) + sprint 19 (current). Remove sprint 14–17.
- **Replace hardcoded fallback in `dbos_scheduling.py`** — read from config.toml via `get_sprint_config()`.
- **Simplify `config.py` legacy fallback chains** — read directly from config.toml instead of multi-level env fallback.
- **Move `REPORT_FRESHNESS_COMMAND` to config.toml** — from `.env` shell string to `[report_freshness] command`.
- **Remove Docker compose.yaml hardcoded `PERSON_CAPACITY_MAPPING_SHEET_NAME`** — let config.toml be SSOT.
