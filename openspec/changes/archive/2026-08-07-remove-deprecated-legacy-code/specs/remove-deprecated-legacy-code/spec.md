# Delta Spec: Remove Deprecated Legacy Code

## Purpose

Define the removal of deprecated legacy code that was superseded by pydantic-settings migration.

## REMOVED Requirements

### Requirement: Deprecated Config Bridge

The ecosystem SHALL NOT contain deprecated config.toml injection bridges.

#### Scenario: load_sprint_config() bridge removed

- **GIVEN** `load_tdt_env()` calls `load_sprint_config()` to inject config.toml values
- **WHEN** the bridge is removed
- **THEN** `load_tdt_env()` SHALL only load `.env` files via dotenv
- **AND** config.toml values SHALL NOT be injected into os.environ
- **AND** callers MUST use `TDTSettings.load()` for config access

### Requirement: Deprecated Exports

The public API SHALL NOT contain deprecated function exports.

#### Scenario: load_sprint_config removed from exports

- **GIVEN** `load_sprint_config` is exported from `tdt_core.__init__`
- **WHEN** the export is removed
- **THEN** `from tdt_core import load_sprint_config` SHALL raise ImportError
- **AND** callers MUST use `TDTSettings.load()` instead

#### Scenario: get_sprint_config removed from exports

- **GIVEN** `get_sprint_config` is exported from `tdt_core.__init__`
- **WHEN** the export is removed
- **THEN** `from tdt_core import get_sprint_config` SHALL raise ImportError
- **AND** callers MUST use `TDTSettings.load()` instead

## ADDED Requirements

### Requirement: Clean Public API

The tdt_core public API SHALL only export active, non-deprecated functions.

#### Scenario: No deprecated exports

- **GIVEN** a function is marked deprecated
- **WHEN** all external consumers have migrated
- **THEN** the function SHALL be removed from `__all__` exports
- **AND** the function MAY remain in the module for backward compat
