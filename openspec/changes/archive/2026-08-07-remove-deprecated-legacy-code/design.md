# Design: Remove Deprecated Legacy Code

## Architecture

### 1. Remove Deprecated Bridge from env.py

**What:** Remove the `load_sprint_config()` call from `env.py:142-153`

**Why:** This bridge injects config.toml values into os.environ. Since `TDTSettings.load()` now handles config.yaml, the bridge is no longer needed.

**Impact:** Zero production impact — no external code calls `load_tdt_env()` expecting config.toml injection.

### 2. Remove Deprecated Exports from __init__.py

**What:** Remove `load_sprint_config`, `get_sprint_config`, `get_current_sprint_section` from `tdt_core.__init__.py`

**Why:** No external consumers import these functions.

**Impact:** Any code importing these will break at import time (desired behavior).

### 3. Keep Active Migration Code

**What:** Keep `config.py`, `config_ownership.py`, `migrate_config.py`

**Why:** These are still needed for:
- `config_ownership.py` — used by `scheduler/settings.py` and `cli.py`
- `migrate_config.py` — needed for TOML→YAML migration
- `config.py` — still has tests, keep for backward compat

### 4. Update Docstrings

**What:** Update docstrings to reference `config.yaml` instead of `config.toml`

**Already Done:** jira-daily-reports docstrings updated

## Trade-offs

### Removed
- Deprecated `load_sprint_config()` bridge call
- Deprecated exports from `__init__.py`
- Stale docstring references

### Preserved
- `config.py` module (backward compat)
- `config_ownership.py` (active use)
- `migrate_config.py` (migration tool)
- All test infrastructure
