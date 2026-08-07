# Proposal: Remove Deprecated Legacy Code

## Why

After the pydantic-settings migration, several deprecated patterns remain:
1. `load_sprint_config()` bridge in `env.py` — injects config.toml values into os.environ, marked DEPRECATED
2. `config.toml` references in active code — stale paths to non-existent config format
3. Duplicate `_env_int`/`_env_bool`/`_env_float` helpers across 5 repos (11 definitions)
4. Stale docstrings referencing config.toml

## What Changes

### tdt-core
- Remove deprecated `load_sprint_config()` call from `env.py:142-153`
- Remove `load_sprint_config` from `__init__.py` exports
- Remove `get_sprint_config` from `__init__.py` exports (no external consumers)
- Remove `get_current_sprint_section` from `__init__.py` exports (no external consumers)
- Keep `config.py` module (still needed for backward compat with tests)
- Keep `config_ownership.py` (still used by scheduler/settings.py and cli.py)
- Keep `migrate_config.py` (still needed for TOML→YAML migration)
- Update docstrings to reference config.yaml instead of config.toml

### No external repo changes needed
- No external repos import `load_sprint_config`, `get_sprint_config`, or `get_current_sprint_section`

## Compatibility

- Remove deprecated exports from `tdt_core.__init__`
- Remove deprecated bridge call from `env.py`
- Keep all active migration code intact
- No breaking changes for production code
