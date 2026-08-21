## ADDED Requirements

### Requirement: Observability initialization at composition root

The agent-docs-sync CLI composition root SHALL call `init_observability(service_name="agent-docs-sync")` before dispatching any subcommand. The `agent_docs_sync.observability` module SHALL export `get_tracer` and `get_meter` without performing initialization as a side effect.

#### Scenario: CLI entry point initializes observability

- **WHEN** the `docs-sync` CLI is invoked
- **THEN** `init_observability(service_name="agent-docs-sync")` SHALL be called exactly once before agent construction

#### Scenario: Module import does not initialize telemetry

- **WHEN** `agent_docs_sync.observability` is imported
- **THEN** no OTel tracer provider, meter provider, or exporter SHALL be configured as a side effect

### Requirement: Consumer observability conformance

Each consumer CLI entry point SHALL initialize observability exactly once at its composition root. Consumer observability initialization SHALL follow the same idempotency and lifecycle guarantees defined in the `agent-observability-contract` capability.

#### Scenario: Consumer CLI initializes before agent construction

- **WHEN** a consumer CLI command executes
- **THEN** `init_observability(service_name=<consumer-name>)` SHALL be called before the first agent is built

#### Scenario: Consumer startup activation test exists

- **WHEN** a consumer CLI is instrumented with the observability lifecycle
- **THEN** a test SHALL exist proving observability activation before agent construction
