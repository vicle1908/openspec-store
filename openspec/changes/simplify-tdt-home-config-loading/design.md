# Design: Simplify TDT Home Config Loading

## Architecture

The TDT home config loading system has three config sources:

```
$TDT_HOME/.env          → credentials (dotenv, loaded first)
$TDT_HOME/config.toml   → sprint config, Jira settings, person capacity (SSOT)
$TDT_HOME/config.yaml   → skills profiles, scheduler config (separate concern)
```

After this change, `config.toml` is authoritative for its domain. No backward
compat bridge, no migration, no rollback.

## Source Changes

### 1. `tdt-core/src/tdt_core/paths.py`

**Remove entirely:**
- Module docstring paragraph about migration shims
- `_unsafe_legacy_migration()` function
- `legacy_xdg_share_path()` function
- `legacy_top_level_state_path()` function
- `migrate_legacy_state_file()` function
- `migrate_legacy_state_dir()` function
- `merge_jsonl_observations()` function
- `migrate_legacy_top_level_jsonl()` function
- Migration shims section header comment
- All removed symbols from `__all__`

**Keep:** All path resolution, validation, `tdt_root()`, typed path helpers,
`ensure_tdt_state_dir()`, `tdt_runtime_path()`.

### 2. `tdt-core/src/tdt_core/env.py`

**Remove:**
- `ensure_env_loaded()` function (zero external callers)

**Update:**
- `_do_load()` comment: "backward compat bridge" → "authoritative config.toml bridge"
- `get_profile()` docstring: remove "Falls back to 'development' for backward compatibility"

**Keep:** `load_tdt_env()`, `EnvironmentIsolation`, all typed env helpers,
diagnostics, profile selection.

### 3. `tdt-core/src/tdt_core/config.py`

**Update:**
- `_load_toml()`: remove Python < 3.11 `tomli` fallback (Python 3.14 only)
- `load_sprint_config()`: change all `os.environ.setdefault()` to `_inject_env()`
- Add `_inject_env()` helper: validates keys against `classify_secret_key()` before
  injecting into `os.environ`; rejects secret-shaped keys
- Module docstring: remove "so existing os.getenv() calls work unchanged"
- `load_sprint_config()` docstring: remove migration period note

**Keep:** `_load_toml()` caching, `get_sprint_config()`,
`get_current_sprint_section()`, `reset_config_cache()`.

### 4. `jira-daily-reports/src/jira_daily_reports/cli.py`

**Remove:**
- `from tdt_core.paths import migrate_legacy_state_file, tdt_state_path` →
  `from tdt_core.paths import tdt_state_path`
- `migrate_legacy_state_file("jira-daily-reports", "reminders.db")` call
- Comment about migration

### 5. `webhook-receiver/src/webhook_receiver/impact.py`

**Remove:**
- `from tdt_core.paths import migrate_legacy_state_dir, tdt_state_path` →
  `from tdt_core.paths import tdt_state_path`
- `_migrated_impact_files = migrate_legacy_state_dir(...)` call and related comments

### 6. `webhook-receiver/src/webhook_receiver/scan_recent_mr.py`

**Remove:**
- `from tdt_core.paths import migrate_legacy_state_file, migrate_legacy_top_level_jsonl, tdt_state_path` →
  `from tdt_core.paths import tdt_state_path`
- `_migrated_obs = migrate_legacy_top_level_jsonl(...)` call
- Comment about JSONL merge
- `migrate_legacy_state_file` import (also used in this file)

### 7. `webhook-receiver/src/webhook_receiver/selftest.py`

**Remove:**
- `from tdt_core.paths import migrate_legacy_top_level_jsonl, tdt_state_path` →
  `from tdt_core.paths import tdt_state_path`
- `_migrated = migrate_legacy_top_level_jsonl(...)` call and comments

### 8. `webhook-receiver/src/webhook_receiver/tailscale_health.py`

**Remove:**
- `from tdt_core.paths import migrate_legacy_state_file, tdt_state_path` →
  `from tdt_core.paths import tdt_state_path`
- Two `migrate_legacy_state_file(...)` calls

### 9. `webhook-receiver/src/webhook_receiver/utils/` (NEW)

**Create:**
- `utils/__init__.py`
- `utils/logging.py` — `get_logger()`, `setup_logging()`, `rotate_log_if_needed()`
- `utils/health.py` — `HealthChecker` class

### 10. `jira-skill/src/jira_skill/env.py`

**Remove:**
- `ensure_env_loaded` from import and `__all__`

### 11. `jira-skill/src/jira_skill/config.py`

**Update:**
- `from .env import ensure_env_loaded` → `from .env import load_tdt_env`
- `ensure_env_loaded()` → `load_tdt_env()`

## OpenSpec Changes

### Delete specs:
- `tdt-home-live-cutover` — rollback/recovery for a cutover that will not run
- `tdt-home-provider-rollout` — staging/rollback for provider release

### Update specs:
- `tdt-env-loader-tdt-home` — remove migration shim requirements, remove
  rollback/recovery scenarios, remove "backward compat" language, add
  authoritative config.toml injection requirement
- `tdt-home-migration-engine` — simplify to plan+execute only (no recovery,
  no rollback, no journal chaining)
- `sprint-switch` — mark migration requirement as fulfilled

## Testing

- `tdt-core` tests: update test_config.py tests that assert `setdefault`
  behavior; update test_paths.py tests that reference migration shims
- `jira-daily-reports` tests: update any test that mocks migration calls
- `webhook-receiver` tests: update any test that mocks migration calls
- Run full test suites for all affected repos

## Gap Analysis & Resolutions

### Resolved by design (no code changes needed)

| Gap | Resolution |
|-----|-----------|
| **YAML `${SCHEDULER_POSTGRES_DSN}` resolution** | `config_ownership.py` validates all `${VAR}` references via `classify_secret_key` + `validate_env_reference`. `postgres_dsn` matches the `dsn` pattern, so the YAML reference IS validated and resolved against `os.environ` after `.env` loading. No code change needed. |
| **config.toml secrets injected as plain env vars** | `_inject_env()` validates all destination environment-variable names against `classify_secret_key()`. Secret-shaped keys are rejected with a warning. Current config.toml keys do not match secret patterns, so this is a guardrail for future safety. |
| **Two config formats without cross-section validation** | `config_ownership.py` validates the `scheduler` section across both TOML and YAML. Other sections (sprint, Jira, person capacity) are TOML-only. No cross-section conflict is possible by design. |

### Fixed in this change

| Issue | Resolution |
|-------|-----------|
| **webhook-receiver missing `utils` package** | Created `src/webhook_receiver/utils/` with `logging.py` (get_logger, setup_logging, rotate_log_if_needed) and `health.py` (HealthChecker). These were dead imports from a deleted module. |
| **webhook-receiver ruff import sorting** | Verified sorted correctly in `api/app.py`. |
| **jira-skill `ensure_env_loaded` import** | Replaced with `load_tdt_env` in `env.py` and `config.py`. |
| **Secret guardrail for config.toml injection** | Added `_inject_env()` to `config.py` — rejects secret-shaped keys from config.toml injection. |

### Documented as future improvement

| Gap | Notes |
|-----|-------|
| **Startup env var inventory validation** | `tdt config doctor` could verify that all env vars required by enabled services are present in the resolved environment. Currently missing vars fail at point-of-use. Not critical — credentials are validated by `config_loader` when accessed. |
