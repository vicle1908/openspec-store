# Tasks: Simplify TDT Home Config Loading

## Task 1: Remove migration shims from tdt-core/paths.py
- [ ] Remove `_unsafe_legacy_migration()`, `legacy_xdg_share_path()`, `legacy_top_level_state_path()`
- [ ] Remove `migrate_legacy_state_file()`, `migrate_legacy_state_dir()`, `merge_jsonl_observations()`, `migrate_legacy_top_level_jsonl()`
- [ ] Remove migration section from module docstring
- [ ] Remove migration symbols from `__all__`

## Task 2: Remove ensure_env_loaded from tdt-core/env.py
- [ ] Delete `ensure_env_loaded()` function
- [ ] Update `_do_load()` and `get_profile()` docstrings

## Task 3: Make config.toml authoritative in tdt-core/config.py
- [ ] Change all `os.environ.setdefault()` to `os.environ[key] = value`
- [ ] Remove Python < 3.11 tomli fallback
- [ ] Update module and function docstrings

## Task 4: Remove migration callers from jira-daily-reports
- [ ] Remove `migrate_legacy_state_file` import and call from cli.py

## Task 5: Remove migration callers from webhook-receiver
- [ ] Remove `migrate_legacy_state_dir` from impact.py
- [ ] Remove `migrate_legacy_top_level_jsonl` and `migrate_legacy_state_file` from scan_recent_mr.py

## Task 6: Delete rollback/recovery specs
- [ ] Delete `tdt-home-live-cutover` spec
- [ ] Delete `tdt-home-provider-rollout` spec

## Task 7: Update tdt-env-loader-tdt-home spec
- [ ] Remove migration shim requirements
- [ ] Remove rollback/recovery scenarios
- [ ] Add authoritative config.toml injection requirement
- [ ] Remove backward-compat language

## Task 8: Update tdt-home-migration-engine spec
- [ ] Simplify to plan+execute only (remove recovery/rollback)

## Task 9: Run tests and fix failures
- [ ] Run tdt-core test suite
- [ ] Run jira-daily-reports test suite
- [ ] Run webhook-receiver test suite
- [ ] Fix any test failures from removed functions

## Task 10: Commit all changes
- [ ] Commit tdt-core changes
- [ ] Commit jira-daily-reports changes
- [ ] Commit webhook-receiver changes
- [ ] Commit openspec-store changes
