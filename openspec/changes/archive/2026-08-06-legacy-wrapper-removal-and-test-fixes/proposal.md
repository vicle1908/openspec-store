# Proposal: Legacy Wrapper Removal and Test Fixes

## Why

After the pydantic-settings migration, several issues remained:
1. **Legacy wrapper functions** still existed in tdt-core/env.py (get_env, get_int_env, etc.)
2. **Dead code** in webhook-receiver (_load_tdt_env method)
3. **Test failures** caused by:
   - Hardcoded paths to specific developer machines
   - Missing asyncio_mode config for async tests
   - Mock references to removed functions
4. **Inconsistent environment loading** across services

## What Changes

### tdt-core
- Remove `get_env()`, `get_int_env()`, `get_bool_env()`, `get_float_env()`, `get_path_env()` from env.py
- Keep `load_tdt_env()` for environment loading
- Update tests to use `os.environ.get()` directly

### jira-skill
- Add `asyncio_mode = "auto"` to pyproject.toml
- Remove `mock.patch("jira_skill.env.load_tdt_env")` from test_audit.py
- Remove `monkeypatch.setattr("jira_skill.cli.load_tdt_env", ...)` from test_cli.py

### jira-daily-reports
- Add warning logging to `_env_int()` for invalid values
- Update test expectations

### webhook-receiver
- Remove dead `_load_tdt_env()` method
- Fix hardcoded path in test_validate_impact_pipeline.py

### jira-kanban-from-spreadsheet
- Update error message to not reference removed functions

### code-daily-scan
- Replace hardcoded path with env var + skip
- Add `pytest.skip()` when iOS repo not available

## Compatibility

- No breaking changes for production code
- Tests updated to match new patterns
- Backward-compatible with existing .env files
