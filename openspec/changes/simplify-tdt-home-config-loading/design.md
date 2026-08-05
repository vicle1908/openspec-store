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
- Module docstring paragraph about migration shims (lines 19-25)
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
- `load_sprint_config()`: change all `os.environ.setdefault()` to `os.environ[key] = value`
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

## Testing

- `tdt-core` tests: update test_config.py tests that assert `setdefault`
  behavior; update test_paths.py tests that reference migration shims
- `jira-daily-reports` tests: update any test that mocks migration calls
- `webhook-receiver` tests: update any test that mocks migration calls
- Run full test suites for all 3 affected repos
