# Tasks — sprint-switch-config-consolidation

## Implementation

### Phase 1: Config bridge (`tdt-core`)

- [x] 1. Create `tdt-core/src/tdt_core/config.py` with `load_sprint_config()`, `get_sprint_config()`, `_load_toml()` helper. Reads `~/.tdt/config.toml`, injects sprint-critical values into `os.environ` via `setdefault`. Graceful no-op when `current_sprint` is absent.
- [x] 2. Update `tdt-core/src/tdt_core/env.py` — call `load_sprint_config()` after `load_dotenv()` in `load_tdt_env()`. Import is lazy to avoid circular deps.
- [x] 3. Update `tdt-core/src/tdt_core/__init__.py` — export `config` module.

### Phase 2: Sprint-switch CLI (`jira-daily-reports`)

- [x] 4. Create `jira-daily-reports/src/jira_daily_reports/sprint_switch.py` — core logic: `parse_input()`, `read_workbook_title()`, `update_config_toml()`, `update_dotenv()`, `update_config_yaml()`, `delete_stale_freshness()`, `run_bootstrap()`, `print_summary()`. All functions are pure/testable; CLI layer is thin.
- [x] 5. Add `sprint-switch` command to `jira-daily-reports/src/jira_daily_reports/cli.py` — Typer command with `<spreadsheet>` arg and `--dry-run` flag. Delegates to `sprint_switch.py`.
- [x] 6. Implement `update_config_toml()` — read TOML, set `current_sprint`, add new `[sprint_sheets.sprint_N]`, archive previous, update `[google_sheets]` and `[jira]` sections. Write back preserving comments.
- [x] 7. Implement `update_dotenv()` — read `.env` lines, replace `SPREADSHEET_ID`, remove `SHEET_LINKS` line entirely, update `JIRA_DEFAULT_FILTER_IDS`, update sprint comment on line 1. Preserve all other lines exactly.
- [x] 8. Implement `update_config_yaml()` — update `sprint_report.spreadsheet_url` in `~/.tdt/config.yaml`. Preserve all other keys.
- [x] 9. Implement `delete_stale_freshness()` — find and delete `~/.tdt/state/jira-daily-reports/freshness/<old_id>.json`.
- [x] 10. Implement `run_bootstrap()` — invoke `sprint-bootstrap --spreadsheet <id> --live` via subprocess, capture output, parse resolved filter_id/board_id from output.
- [x] 11. Implement `print_summary()` — display sprint number, dates, filter ID, board ID, spreadsheet URL.

### Phase 3: Config migration (`~/.tdt`)

- [x] 12. Populate `~/.tdt/config.toml` with new schema — add `current_sprint`, `[sprint]`, `[person_capacity]`, `[dev_performance]`, `[report_freshness]` sections with current values.
- [x] 13. Remove migrated vars from `~/.tdt/.env` — `SPREADSHEET_ID`, `SHEET_LINKS`, `JIRA_DEFAULT_FILTER_IDS`, `JIRA_PROJECT_KEY`, `PERSON_CAPACITY_*`, `DEV_PERFORMANCE_*`, `REPORT_FRESHNESS_*`. Keep credentials and runtime-only vars.
- [x] 14. Delete stale `.env` backup files: `.env.backup.20260527_085942`, `.env.bak`, `.env.bak.sprint16_20260608_210442`, `.env.bak2`.
- [x] 15. Archive stale config.toml sprint entries — keep only sprint 18 (archived) + sprint 19 (current). Remove sprint 14–17.
- [x] 16. Remove hardcoded `PERSON_CAPACITY_MAPPING_SHEET_NAME` from `agent-core/compose.yaml`.

### Phase 4: Legacy cleanup — SHEET_LINKS removal

**Key discovery:** `tdt_sheets.resolve_gid(backend, spreadsheet_id, sheet_name)` already exists with built-in metadata caching. No performance regression.

- [x] 17. **Delete** `jira-daily-reports/src/jira_daily_reports/_env_quoting.py` — entire module.
- [x] 18. **Refactor** `tdt_sheet.py:_resolve_sheet_links()` — replace SHEET_LINKS env parsing with `resolve_gid()` from `tdt_sheets.utils`. Keep in-memory cache.
- [x] 19. **Delete** `catalog/writer.py:_persist_gid_to_sheet_links()` and `_resolve_gid_from_env()`.
- [x] 20. **Refactor** `catalog/writer.py:resolve_tab_gid()` — use `resolve_gid()` from tdt_sheets (already has get_metadata fallback + bootstrap).
- [x] 21. **Delete** `dev_performance/sheet_writer.py:persist_gid_to_sheet_links()` and `resolve_gid_from_env()`.
- [x] 22. **Refactor** `dev_performance/sheet_writer.py` — use `resolve_gid()` from tdt_sheets.
- [x] 23. **Fix latent bug in kbs** `config.py:92` — `v.split(",")` should be `v.split(";")` or removed entirely (kbs should use API-based tab resolution).
- [x] 24. **Remove kbs `sheet_links` config field** — extra tabs resolved via API, not env var.
- [x] 25. Update all imports that referenced `_env_quoting` — remove dead imports.

### Phase 5: Legacy cleanup — dead code removal

- [x] 26. **Remove** `migrate_legacy_state_file("jira-daily-reports", "freshness.json")` and `migrate_legacy_state_dir("jira-daily-reports", "freshness", ...)` from `tdt_sheet.py`. Migration complete.
- [x] 27. **Remove** all `migrate_legacy_state_*` calls from `webhook-receiver/settings.py`. Migration complete.
- [x] 28. Update `jira-daily-reports/src/jira_daily_reports/dbos_scheduling.py` — replace hardcoded fallback with `get_sprint_config()` from `tdt_core.config`.
- [x] 29. Simplify `config.py:require_jira_filter_id()` — read from `config.toml [jira] default_filter_ids` via `get_sprint_config()` instead of multi-level env fallback.
- [x] 30. Simplify `config.py:workspace_timezone_name()` — read from `config.toml [person_capacity] timezone` via `get_sprint_config()`.

### Phase 6: Tests

- [x] 31. Add `tdt-core/tests/test_config.py` — unit tests for `load_sprint_config()`: with/without `current_sprint`, graceful fallback, `setdefault` behavior.
- [x] 32. Add `jira-daily-reports/tests/test_sprint_switch.py` — unit tests for `parse_input()`, `read_workbook_title()` parsing, `update_config_toml()` TOML mutations, `update_dotenv()` line edits, `update_config_yaml()`.
- [x] 33. Add test for dynamic tab ID discovery — mock Sheets API, verify tab resolution without SHEET_LINKS.
- [x] 34. Integration test: `sprint-switch --dry-run` with mock spreadsheet title — verify config.toml and .env changes printed without side effects.

### Phase 7: Validation

- [x] 35. Run `ruff check . --fix && ruff format .` in `tdt-core/` and `jira-daily-reports/`.
- [x] 36. Run `mypy tdt-core/ --strict` and `mypy jira-daily-reports/ --strict`.
- [x] 37. Run `pytest -x` in `tdt-core/tests/` and `jira-daily-reports/tests/`.
- [x] 38. Run `openspec validate --strict sprint-switch-config-consolidation`.
- [x] 39. Verify all `os.getenv("SPREADSHEET_ID")` consumers work with bridge — run `sprint-sheet --output terminal` and `dev-performance --dry-run`.
- [x] 40. Verify SHEET_LINKS removal — run `catalog-refresh` and `dev-performance` to confirm dynamic tab discovery works.

### Phase 8: Documentation

- [x] 41. Update `tdt-meta/docs/superpowers/specs/2026-07-21-sprint-switch-design.md` — cross-link to OpenSpec change.
- [x] 42. Add "Sprint Rotation" section to `tdt-meta/docs/workflows/` with step-by-step runbook for operators.
