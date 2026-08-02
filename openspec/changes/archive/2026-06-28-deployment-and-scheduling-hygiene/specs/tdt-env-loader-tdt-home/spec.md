# Capability: tdt-env-loader-tdt-home

## Purpose

`tdt_core.env.load_tdt_env()` is the canonical env-loading utility called
by every Python service in the TDT ecosystem. It currently reads
`Path.home() / ".tdt" / ".env"` only, ignoring the `TDT_HOME` env var.
`agent_core.foundation.settings.TDT_HOME` already implements the
`TDT_HOME` > `Path.home() / ".tdt"` precedence; this change brings
`tdt_core.env` into the same precedence so both loaders are consistent
and so a future launch configuration that overrides `HOME` does not
silently lose credentials.

## ADDED Requirements

### Requirement: `load_tdt_env()` honours `TDT_HOME` when set

The function `tdt_core.env.load_tdt_env()` SHALL resolve the credentials
file at `$TDT_HOME/.env` when `TDT_HOME` is set in the environment, and
fall back to `Path.home() / ".tdt" / ".env"` when `TDT_HOME` is unset or
empty.

#### Scenario: `TDT_HOME` set

- **GIVEN** the environment variable `TDT_HOME=/home/agent/.tdt`
- **WHEN** `load_tdt_env()` is called for the first time in a process
- **THEN** it SHALL read `/home/agent/.tdt/.env` via `python-dotenv`
- **AND** it SHALL NOT read any other `.env` location
- **AND** subsequent calls in the same process SHALL be no-ops
  (the existing idempotency invariant)

#### Scenario: `TDT_HOME` unset

- **GIVEN** `TDT_HOME` is not set in the environment
- **WHEN** `load_tdt_env()` is called
- **THEN** it SHALL read `Path.home() / ".tdt" / ".env"` (existing
  behaviour preserved)
- **AND** the function SHALL NOT raise

#### Scenario: `TDT_HOME` set to empty string

- **GIVEN** `TDT_HOME=""` in the environment
- **WHEN** `load_tdt_env()` is called
- **THEN** it SHALL treat empty string as "unset" and fall back to
  `Path.home() / ".tdt" / ".env"`
- **AND** the function SHALL NOT raise

### Requirement: Tilde expansion is applied

The function SHALL apply `os.path.expanduser` to the value of `TDT_HOME`
before resolving, so that `TDT_HOME=~/foo` works.

#### Scenario: Tilde-prefixed `TDT_HOME`

- **GIVEN** the environment variable `TDT_HOME=~/.tdt` and `$HOME=/Users/lekhanhvinh`
- **WHEN** `load_tdt_env()` is called
- **THEN** it SHALL read `/Users/lekhanhvinh/.tdt/.env`

### Requirement: Local `.env` override behaviour is preserved

The existing "optional local `.env` override in CWD" behaviour SHALL NOT
change. If `TDT_HOME/.env` was loaded, a `Path(".") / ".env"` file (when
present) SHALL still be loaded with `override=True`.

#### Scenario: Local .env exists

- **GIVEN** `~/.tdt/.env` exists
- **AND** the current working directory contains a `.env` file
- **WHEN** `load_tdt_env()` is called
- **THEN** both files SHALL be loaded
- **AND** variables in the local `.env` SHALL override values from
  `~/.tdt/.env` (existing behaviour)

### Requirement: Idempotency is preserved

The existing `_loaded` module-level flag SHALL continue to ensure that
`load_tdt_env()` runs at most once per process.

#### Scenario: Repeated calls

- **GIVEN** `load_tdt_env()` has been called once
- **WHEN** it is called again from the same process
- **THEN** the second call SHALL be a no-op (no file I/O)
- **AND** no exception SHALL be raised
