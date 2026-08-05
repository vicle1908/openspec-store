# Design: Fix TDT Config Precedence Drift

## Changes

### 1. `~/.tdt/config.toml` header comment

**Before:**
```
# Priority: env vars > TOML values (env vars override via load_sprint_config bridge)
```

**After:**
```
# Priority: TOML values are authoritative for injected keys (sprint, Jira, person capacity).
# Process env vars set before load_tdt_env() are not overwritten.
```

### 2. `tdt-core/src/tdt_core/config_ownership.py` module docstring

**Before:**
```
That keeps the legacy TOML compatibility path observable without silently choosing a source.
```

**After:**
```
That keeps the scheduler source precedence explicit: YAML is canonical for
duplicates, and conflicts fail closed.
```

## Rationale

These are documentation-only changes that align operator-facing and
developer-facing text with the current implementation. No behavior changes.
