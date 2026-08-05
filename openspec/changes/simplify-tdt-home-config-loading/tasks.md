# Tasks: Simplify TDT Home Config Loading

## Task 1: Remove migration shims from tdt-core/paths.py
- [x] Remove `_unsafe_legacy_migration()`, `legacy_xdg_share_path()`, `legacy_top_level_state_path()`
- [x] Remove `migrate_legacy_state_file()`, `migrate_legacy_state_dir()`, `merge_jsonl_observations()`, `migrate_legacy_top_level_jsonl()`
- [x] Remove migration section from module docstring
- [x] Remove migration symbols from `__all__`

## Task 2: Remove ensure_env_loaded from tdt-core/env.py
- [x] Delete `ensure_env_loaded()` function
- [x] Update `_do_load()` and `get_profile()` docstrings

## Task 3: Make config.toml authoritative in tdt-core/config.py
- [x] Change all `os.environ.setdefault()` to `os.environ[key] = value`
- [x] Remove Python < 3.11 tomli fallback
- [x] Update module and function docstrings
- [x] Add `_inject_env()` secret guardrail using `classify_secret_key`

## Task 4: Remove migration callers from jira-daily-reports
- [x] Remove `migrate_legacy_state_file` import and call from cli.py

## Task 5: Remove migration callers from webhook-receiver
- [x] Remove `migrate_legacy_state_dir` from impact.py
- [x] Remove `migrate_legacy_top_level_jsonl` and `migrate_legacy_state_file` from scan_recent_mr.py
- [x] Remove `migrate_legacy_top_level_jsonl` from selftest.py
- [x] Remove `migrate_legacy_state_file` from tailscale_health.py
- [x] Create missing `webhook_receiver/utils/` package (logging.py + health.py)

## Task 6: Replace ensure_env_loaded in jira-skill
- [x] Replace `ensure_env_loaded` with `load_tdt_env` in env.py
- [x] Replace `ensure_env_loaded` with `load_tdt_env` in config.py

## Task 7: Delete rollback/recovery specs
- [x] Delete `tdt-home-live-cutover` spec
- [x] Delete `tdt-home-provider-rollout` spec

## Task 8: Update tdt-env-loader-tdt-home spec
- [x] Remove migration shim requirements
- [x] Remove rollback scenario
- [x] Add authoritative config.toml injection requirement

## Task 9: Update tdt-home-migration-engine spec
- [x] Simplify to plan+execute only (remove recovery/rollback)

## Task 10: Update sprint-switch spec
- [x] Mark migration requirement as fulfilled

## Task 11: Run tests and fix failures
- [x] Run tdt-core test suite — all pass (519 tests)
- [x] Update test_config.py for authoritative config behavior
- [x] Update test_paths.py to remove legacy migration tests
- [x] Update test_paths_typed.py to remove legacy migration tests
- [x] Update test_clients.py for isolated TDT_HOME

## Task 12: Commit all changes
- [x] Commit tdt-core changes
- [x] Commit jira-daily-reports changes
- [x] Commit webhook-receiver changes
- [x] Commit jira-skill changes
- [x] Commit openspec-store changes
