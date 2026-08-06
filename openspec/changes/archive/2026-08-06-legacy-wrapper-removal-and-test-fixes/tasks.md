# Tasks

## Phase 1: tdt-core Cleanup ✅
- [x] Remove `get_env()` from env.py
- [x] Remove `get_int_env()` from env.py
- [x] Remove `get_bool_env()` from env.py
- [x] Remove `get_float_env()` from env.py
- [x] Remove `get_path_env()` from env.py
- [x] Remove deprecated exports from __init__.py
- [x] Update tests to use os.environ.get()
- [x] Verify all tests pass

## Phase 2: jira-skill Test Fixes ✅
- [x] Add `asyncio_mode = "auto"` to pyproject.toml
- [x] Remove `mock.patch("jira_skill.env.load_tdt_env")` from test_audit.py
- [x] Remove `monkeypatch.setattr("jira_skill.cli.load_tdt_env", ...)` from test_cli.py
- [x] Add stub `load_tdt_env()` to env.py for backward compatibility
- [x] Verify all tests pass

## Phase 3: jira-daily-reports Test Fixes ✅
- [x] Add warning logging to `_env_int()` for invalid values
- [x] Update test expectations
- [x] Verify all tests pass

## Phase 4: webhook-receiver Fixes ✅
- [x] Remove dead `_load_tdt_env()` method
- [x] Fix hardcoded path in test_validate_impact_pipeline.py
- [x] Verify all tests pass

## Phase 5: jira-kanban-from-spreadsheet Fixes ✅
- [x] Update error message to not reference removed functions
- [x] Verify all tests pass

## Phase 6: code-daily-scan Fixes ✅
- [x] Replace hardcoded path with env var
- [x] Add `pytest.skip()` when iOS repo not available
- [x] Verify all tests pass

## Phase 7: Validation ✅
- [x] Run full test suite across all repos
- [x] Verify no regressions
- [x] Commit all changes
- [x] Archive OpenSpec change
