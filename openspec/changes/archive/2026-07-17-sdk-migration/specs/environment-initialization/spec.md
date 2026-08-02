# environment-initialization Specification

## Purpose

Define the canonical pattern for environment variable initialization in jira-skill and related Python packages. All environment loading MUST happen once at application startup, not scattered across individual functions.

## ADDED Requirements

### Requirement: Single environment initialization at entry point
All CLI applications SHALL call `load_tdt_env()` exactly once at the application entry point, not in individual command functions.

#### Scenario: Typer callback for environment loading
- **WHEN** creating a Typer CLI application
- **THEN** use a `@app.callback()` decorator to load environment variables
- **AND** remove all `load_tdt_env()` calls from individual command functions

#### Scenario: Ensure idempotent env loading
- **WHEN** `load_tdt_env()` is called multiple times
- **THEN** subsequent calls SHALL be no-ops (caching behavior)
- **AND** the function SHALL NOT reload the `.env` file

### Requirement: Use Typer callback for CLI apps
CLI applications using Typer SHALL use a callback decorator to initialize environment once.

#### Scenario: Proper Typer callback pattern
- **WHEN** defining a Typer CLI application
- **THEN** add a callback function that calls `load_tdt_env()`
- **AND** this callback runs before every command

```python
from typer import Typer
from tdt_core.env import load_tdt_env

app = Typer()

@app.callback()
def ensure_env() -> None:
    """Load environment variables before running any command."""
    load_tdt_env()
```

### Requirement: Factory methods handle their own initialization
Factory methods like `JiraClientFactory.from_env()` SHALL call `ensure_env_loaded()` internally, so explicit env loading is not required before factory calls.

#### Scenario: Factory handles env loading
- **WHEN** calling `JiraClientFactory.from_env()`
- **THEN** the factory SHALL internally call `ensure_env_loaded()`
- **AND** explicit `load_tdt_env()` calls are not required before factory usage

### Requirement: Helper functions do not need env loading
Helper functions and module-level code SHALL NOT call `load_tdt_env()`. Environment loading is the responsibility of the application entry point.

#### Scenario: Helper functions remain env-agnostic
- **WHEN** creating helper functions that may be called from multiple contexts
- **THEN** do NOT call `load_tdt_env()` in the helper
- **AND** document that callers are responsible for env initialization

## Implementation Notes

- `load_tdt_env()` is idempotent and caches loaded values
- `JiraClientFactory.from_env()` internally calls `ensure_env_loaded()`
- For non-CLI code, call `load_tdt_env()` at module import time if the module requires env vars
- The pattern `ensure_env_loaded()` from `jira_skill.env` is used in some places

### Exception: Lazy Initialization in Library Modules

Library modules that may be called programmatically (not just from CLI) MAY use lazy initialization:

```python
def _ensure_client() -> bool:
    """Lazy initialization - loads env if needed."""
    if self.client:
        return True
    load_tdt_env()  # Acceptable in library modules with programmatic use
    self.client = SheetsClient(...)
    return True
```

This is acceptable for modules like `filter_registry.py` that can be used both from CLI and as libraries.

## Files Affected

| File | Change | Status |
|------|--------|--------|
| `jira_skill/cli.py` | Consolidated 8 `load_tdt_env()` calls to 1 in callback | ✅ Complete |
| `jira_skill/analysis/filter_registry.py` | Lazy init in `_ensure_client()` | ✅ Acceptable (library module) |
