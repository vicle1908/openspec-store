# Proposal: Simplify TDT Home Config Loading

## Summary

Remove all legacy, backward-compatibility, migration, and rollback machinery
from the TDT home config and environment loading system. Keep only the latest
authoritative logic.

## Motivation

The `tdt-core` config/env loading system carries dead weight from a staged
migration that is now complete:

1. **Migration shims** (`migrate_legacy_state_file`, `migrate_legacy_state_dir`,
   `merge_jsonl_observations`, `migrate_legacy_top_level_jsonl`) in `paths.py`
   — all raise `UnsafePathError` immediately. No migration is in progress.
   Dead code with 3 import sites that execute only to error.

2. **Backward-compat bridge** (`load_sprint_config()` using `os.environ.setdefault`)
   — designed so `.env` values override during a transition period. The
   transition is over. `config.toml` is the SSOT for sprint config; `.env` is
   for credentials. The `setdefault` pattern silently hides stale `.env` values.

3. **`ensure_env_loaded()` alias** — dead function, zero external callers.

4. **Live cutover and provider rollout specs** — define rollback and recovery
   mechanisms for a migration that will never run. Removing them eliminates
   a false sense of operational debt.

## What Changes

| Area | Remove | Simplify | Authoritative |
|------|--------|----------|---------------|
| `paths.py` | Migration shims, `_unsafe_legacy_migration`, legacy path helpers | Module docstring | Direct path resolution |
| `env.py` | `ensure_env_loaded()` alias | Docstrings | `load_tdt_env()` is the only entry point |
| `config.py` | Python < 3.11 `tomli` fallback | Docstrings | `config.toml` → `os.environ` direct assign |
| `jira-daily-reports/cli.py` | `migrate_legacy_state_file` call | — | Direct `tdt_state_path()` |
| `webhook-receiver/impact.py` | `migrate_legacy_state_dir` call | — | Direct `tdt_state_path()` |
| `webhook-receiver/scan_recent_mr.py` | `migrate_legacy_top_level_jsonl` call | — | Direct `tdt_state_path()` |
| OpenSpec specs | `tdt-home-live-cutover`, `tdt-home-provider-rollout` | `tdt-home-migration-engine` (plan+execute only) | `tdt-env-loader-tdt-home` (latest logic only) |

## Out of Scope

- `config.yaml` (skills/scheduler config) — separate concern, unchanged
- `.env` loading (credentials) — remains the credential SSOT
- Test isolation (`EnvironmentIsolation`) — legitimate, kept
- Typed env helpers (`get_env`, `get_bool_env`, etc.) — kept
- fs_kernel, config_loader, config_ownership — security/validation, kept

## Risk

Low. All removed code paths either error immediately or have zero callers.
The `setdefault` → direct assign change makes `config.toml` authoritative,
which is the intended final state.
