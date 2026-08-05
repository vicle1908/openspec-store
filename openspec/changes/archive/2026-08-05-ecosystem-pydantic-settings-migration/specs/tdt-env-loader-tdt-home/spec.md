# Delta Spec: tdt-env-loader-tdt-home (MODIFIED + ADDED)

## Purpose

Modify the canonical `TDT_HOME` configuration loading to support pydantic-settings as an alternative.

## MODIFIED Requirements

### Requirement: `load_tdt_env()` honours `TDT_HOME` when set

The environment loader SHALL evaluate the effective `TDT_HOME` value at load time and use that root for the home environment file. Callers MAY use `TDTSettings.load()` as an alternative to `load_tdt_env()` for typed config access.

#### Scenario: Explicit root is selected

- **GIVEN** `TDT_HOME` names an absolute directory
- **WHEN** the loader initializes
- **THEN** it reads only the environment file under that directory before applying any separately governed development override

#### Scenario: Root is unset

- **GIVEN** `TDT_HOME` is absent
- **WHEN** the loader initializes
- **THEN** it uses the default home root and does not raise solely because the optional file is absent

#### Scenario: Root is empty

- **GIVEN** `TDT_HOME` is present but empty
- **WHEN** the loader initializes
- **THEN** it treats the value as unset and uses the default home root

#### Scenario: Root changes after import

- **GIVEN** the module was imported before `TDT_HOME` was changed
- **WHEN** the loader or a path helper is called
- **THEN** the effective value reflects the call-time environment rather than an import-time snapshot

#### Scenario: TDTSettings loads from same root

- **GIVEN** `TDT_HOME` names an absolute directory
- **WHEN** `TDTSettings.load()` is called
- **THEN** it SHALL read `$TDT_HOME/config.yaml` using the same root resolution as `tdt_root()`

## ADDED Requirements

### Requirement: Config.toml injection is deprecated

The environment loader SHALL emit a deprecation warning when injecting `config.toml` values into `os.environ`. `load_sprint_config()` SHALL remain available as a backward-compat shim.

#### Scenario: Deprecated function warns

- **WHEN** `load_sprint_config()` is called
- **THEN** it SHALL emit a `DeprecationWarning`
- **AND** it SHALL inject values into `os.environ` for backward compatibility
