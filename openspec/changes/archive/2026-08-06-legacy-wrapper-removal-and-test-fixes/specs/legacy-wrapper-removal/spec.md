# Delta Spec: Legacy Wrapper Removal

## Purpose

Define the removal of legacy wrapper functions and updates to test infrastructure.

## ADDED Requirements

### Requirement: Legacy Wrapper Functions

The ecosystem SHALL NOT contain legacy wrapper functions that duplicate os.environ functionality.

#### Scenario: get_env() removed

- **GIVEN** a consumer calls `get_env()` from tdt_core.env
- **WHEN** they upgrade to the new version
- **THEN** they MUST use `os.environ.get()` directly
- **AND** the function MUST NOT exist in the public API

#### Scenario: get_int_env() removed

- **GIVEN** a consumer calls `get_int_env()` from tdt_core.env
- **WHEN** they upgrade to the new version
- **THEN** they MUST use `os.environ.get()` with int conversion
- **AND** the function MUST NOT exist in the public API

### Requirement: Test Infrastructure

Test infrastructure SHALL support async tests and environment-dependent tests gracefully.

#### Scenario: Async tests with asyncio_mode

- **GIVEN** a test file contains `async def test_*` functions
- **WHEN** pytest is configured with `asyncio_mode = "auto"`
- **THEN** tests MUST run without explicit `@pytest.mark.asyncio` decorators
- **AND** all async tests MUST pass

#### Scenario: Hardcoded paths in tests

- **GIVEN** a test contains a hardcoded path to a developer machine
- **WHEN** the test runs on a different machine
- **THEN** the test MUST skip gracefully with `pytest.skip()`
- **AND** the path MUST be configurable via environment variable

### Requirement: Environment Loading Consistency

All services SHALL use consistent environment loading patterns.

#### Scenario: Services use consistent patterns

- **GIVEN** a service needs to load configuration
- **WHEN** it initializes
- **THEN** it MUST load secrets from `~/.tdt/.env` via dotenv
- **AND** it MUST load config from `~/.tdt/config.yaml` via TDTSettings.load()
- **AND** it MUST access env vars via `os.environ.get()`
