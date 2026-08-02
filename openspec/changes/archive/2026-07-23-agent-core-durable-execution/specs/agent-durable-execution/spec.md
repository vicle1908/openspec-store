## ADDED Requirements

### Requirement: Durable execution configuration

The system SHALL support durable execution via a `durable_execution` config key in `harness_config`.

#### Scenario: DBOS backend (default)
- **WHEN** `harness_config={"durable_execution": {"backend": "dbos"}}` is provided
- **THEN** the agent SHALL use `DBOSDurability()` capability
- **AND** `DBOSDurability` SHALL be added to the agent's capabilities list

#### Scenario: Default backend
- **WHEN** `harness_config={"durable_execution": {}}` is provided without `backend`
- **THEN** the system SHALL default to `"dbos"`

#### Scenario: No durable execution
- **WHEN** `harness_config` does not contain `durable_execution`
- **THEN** no durable execution capability SHALL be added (backward compatible)

### Requirement: Optional Temporal support

The system SHALL support Temporal as an optional durable execution backend.

#### Scenario: Temporal backend
- **WHEN** `harness_config={"durable_execution": {"backend": "temporal"}}` is provided
- **AND** `temporalio` package is installed
- **THEN** the agent SHALL use `TemporalDurability()` capability

#### Scenario: Missing temporal dependency
- **WHEN** `harness_config={"durable_execution": {"backend": "temporal"}}` is provided
- **AND** `temporalio` package is NOT installed
- **THEN** the system SHALL raise `ImportError` with message: "Install temporalio: pip install pydantic-ai[temporal]"

### Requirement: Optional Prefect support

The system SHALL support Prefect as an optional durable execution backend.

#### Scenario: Prefect backend
- **WHEN** `harness_config={"durable_execution": {"backend": "prefect"}}` is provided
- **AND** `prefect` package is installed
- **THEN** the agent SHALL use `PrefectDurability()` capability

#### Scenario: Missing prefect dependency
- **WHEN** `harness_config={"durable_execution": {"backend": "prefect"}}` is provided
- **AND** `prefect` package is NOT installed
- **THEN** the system SHALL raise `ImportError` with message: "Install prefect: pip install pydantic-ai[prefect]"

### Requirement: Durable execution documentation

`harness-integration.md` SHALL document durable execution capabilities.

#### Scenario: Durable execution section
- **WHEN** a developer reads `harness-integration.md`
- **THEN** it SHALL have a durable execution section with:
  - Config schema for `durable_execution.backend`
  - Example for DBOS (default)
  - Example for Temporal (optional)
  - Example for Prefect (optional)
  - Note about DBOS requiring `@DBOS.workflow` context
