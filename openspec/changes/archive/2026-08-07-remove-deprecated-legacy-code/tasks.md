# Tasks

## Phase 1: Remove Deprecated Bridge ✅
- [x] Remove `load_sprint_config()` call from `env.py:142-153`
- [x] Update env.py docstring to remove reference to config.toml injection

## Phase 2: Remove Deprecated Exports ✅
- [x] Remove `load_sprint_config` from `__init__.py` exports
- [x] Remove `get_sprint_config` from `__init__.py` exports
- [x] Remove `get_current_sprint_section` from `__init__.py` exports
- [x] Verify no external imports break

## Phase 3: Update Docstrings ✅
- [x] Update `config.py` docstring to reference config.yaml
- [x] Update `config_models.py` docstring to reference config.yaml
- [x] Update `scheduler/settings.py` docstring to reference config.yaml

## Phase 4: Validation ✅
- [x] Run full test suite in tdt-core — all pass
- [x] Run downstream tests (jira-daily-reports, jira-skill) — all pass
- [x] Commit all changes
- [x] Archive OpenSpec change
