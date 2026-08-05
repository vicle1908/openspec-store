# Delta Spec: tdt-env-loader-tdt-home (MODIFIED)

## Purpose

Modify the canonical `TDT_HOME` configuration loading to support pydantic-settings as an alternative.

## MODIFIED Requirements

### Requirement: `load_tdt_env()` honours `TDT_HOME` when set

The environment loader SHALL evaluate the effective `TDT_HOME` value at load time and use that root for the home environment file. **NEW**: Callers MAY use `TDTSettings.load()` as an alternative to `load_tdt_env()` for typed config access.

#### Scenario: TDTSettings loads from same root

- **GIVEN** `TDT_HOME` names an absolute directory
- **WHEN** `TDTSettings.load()` is called
- **THEN** it SHALL read `$TDT_HOME/config.yaml` using the same root resolution as `tdt_root()`

### Requirement: `config.toml` injection is deprecated

The environment loader SHALL NOT inject `config.toml` values into `os.environ` by default. **NEW**: `load_sprint_config()` SHALL emit a deprecation warning.

#### Scenario: Deprecated function warns

- **WHEN** `load_sprint_config()` is called
- **THEN** it SHALL emit a `DeprecationWarning`
- **AND** it SHALL inject values into `os.environ` for backward compatibility
