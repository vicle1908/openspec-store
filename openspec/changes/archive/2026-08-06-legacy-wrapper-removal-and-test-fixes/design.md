# Design: Legacy Wrapper Removal and Test Fixes

## Architecture

### 1. Wrapper Function Removal Strategy

**Approach:** Remove wrapper functions that are no longer needed after pydantic-settings migration.

**Files Modified:**
- `tdt-core/src/tdt_core/env.py` - Remove `get_env()`, `get_int_env()`, `get_bool_env()`, `get_float_env()`, `get_path_env()`
- `tdt-core/src/tdt_core/__init__.py` - Remove deprecated exports

**Impact:** Zero production impact - no service code uses these wrappers anymore.

### 2. Test Fix Strategy

**Approach:** Fix pre-existing test failures caused by:
- Hardcoded paths → Replace with env vars + skip
- Missing config → Add required config sections
- Stale mocks → Remove or update

**Files Modified:**
- `jira-skill/pyproject.toml` - Add `asyncio_mode = "auto"`
- `jira-skill/tests/status/test_commands/test_audit.py` - Replace mocks
- `jira-skill/tests/analysis/test_cli.py` - Remove stale mock references
- `webhook-receiver/tests/test_validate_impact_pipeline.py` - Replace hardcoded path
- `code-daily-scan/tests/test_quick_scan.py` - Replace hardcoded path with env var

### 3. Environment Loading Consistency

**Approach:** Ensure all services use consistent patterns:
- `~/.tdt/.env` for secrets (loaded by dotenv)
- `~/.tdt/config.yaml` for config (loaded by TDTSettings.load())
- Direct `os.environ.get()` for env var access

## Trade-offs

### Removed
- Legacy wrapper functions (no longer needed)
- Dead code (no longer called)

### Added
- `asyncio_mode = "auto"` for jira-skill tests
- Env var support for test paths
- Warning logging for invalid env values

### Preserved
- `load_tdt_env()` in tdt-core (still needed for env loading)
- All existing functionality
- Backward compatibility
