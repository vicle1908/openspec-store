## Purpose

This specification defines requirements for Typed Orchestration State.

## Requirements

### Requirement: Typed state is the default workflow contract

New `agent-core` workflows SHALL declare a typed LangGraph state schema and explicit reducers for concurrently updated fields. Dict-only state SHALL remain available only through the compatibility adapter during the migration window.

#### Scenario: Typed workflow

- **WHEN** a workflow is built through the supported API
- **THEN** its node inputs and updates SHALL be checked against the declared state schema

#### Scenario: Concurrent updates

- **WHEN** parallel nodes update an accumulated field
- **THEN** the declared reducer SHALL merge those values deterministically

#### Scenario: Invalid update

- **WHEN** a node returns a value incompatible with the state schema
- **THEN** execution SHALL fail with the node and field name

### Requirement: Consumer-owned domain state

Consumers SHALL own their domain state types while `agent-core` provides reusable protocol and lifecycle helpers.

#### Scenario: docs-sync state

- **WHEN** `agent-docs-sync` defines discovery, audit, generation, validation, and report state
- **THEN** those fields SHALL be declared in a consumer-owned typed schema
- **AND** `agent-core` SHALL not require a generic mutable `results` dictionary

#### Scenario: agent-harness state

- **WHEN** `agent-harness` is implemented
- **THEN** it SHALL define typed artifact and traceability fields directly
- **AND** it SHALL not be forced to serialize typed artifacts into an untyped wrapper for every node

### Requirement: Managed async checkpointer boundary

`agent-core` SHALL own the shared TDT async checkpointer boundary for DSN resolution, first-use schema provisioning, and saver resource lifetime, while consumers SHALL own their graph and thread identifiers.

#### Scenario: First-use provisioning

- **WHEN** a Postgres checkpoint database has not been provisioned
- **THEN** the shared boundary SHALL invoke the public `AsyncPostgresSaver.setup()` contract before the saver is used
- **AND** schema migration failure SHALL stop execution before a graph node runs

#### Scenario: Runtime operation

- **WHEN** a consumer runs, streams, inspects, or resumes a workflow
- **THEN** it SHALL compile or inspect the graph with an opened saver from the shared boundary
- **AND** the saver context SHALL remain open for the complete operation

#### Scenario: Public status inspection

- **WHEN** a consumer reads workflow status or history
- **THEN** it SHALL use public compiled-graph `aget_state` or `aget_state_history` APIs with the stable thread configuration
- **AND** it SHALL not query private saver internals

#### Scenario: Native interrupt resume

- **WHEN** a persisted workflow exposes a native interrupt ID
- **THEN** an authorized decision SHALL resume with `Command(resume={pending_interrupt.id: decision})`
- **AND** a missing or mismatched interrupt ID SHALL fail without advancing the checkpoint
