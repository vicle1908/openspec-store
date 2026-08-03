# tdt-env-loader-tdt-home Specification

## Purpose

Define the canonical `TDT_HOME` configuration and environment loading contract for the TDT ecosystem. This capability provides:

1. **Single root resolver** — `tdt_root()` dynamically evaluates `TDT_HOME` at call time; no import-time snapshots.
2. **Typed path helpers** — `tdt_config_path()`, `tdt_credentials_path()`, `tdt_schedules_dir()`, `tdt_logs_dir()`, `tdt_state_path()`, `tdt_runtime_path()` — all backed by `tdt_root()` with component validation.
3. **Governed environment loading** — `load_tdt_env()` with thread-safe one-time initialization, `TDT_ENV_PROFILE` precedence (development/production), and test isolation.
4. **Secret separation** — YAML/TOML config MAY contain environment references (`${VAR_NAME}`) but SHALL NOT contain literal secret values.
5. **Descriptor-relative security kernel** — filesystem operations use `dir_fd` + `O_NOFOLLOW` semantics; no pathname-based fallback.
6. **Journaled migration** — plan/apply/recover/rollback with hash-chained journal, typed attestations, and idempotent recovery.
7. **Runtime diagnostics** — `tdt config doctor` checks layout, permissions, links, config ambiguity, and secret placement.
8. **Cross-repo conformance** — AST-based source audit rejects hard-coded `~/.tdt` construction outside approved sites.

This capability is owned by `tdt-core` and enforced across 15 participating repositories.

## Requirements

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
