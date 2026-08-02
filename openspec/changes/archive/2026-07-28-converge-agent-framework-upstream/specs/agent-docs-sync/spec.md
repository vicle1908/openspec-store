## ADDED Requirements

### Requirement: One canonical docs-sync pipeline

`agent-docs-sync` SHALL expose one supported deterministic pipeline for discover, audit, optional generation, validation, and reporting.

#### Scenario: Public CLI

- **WHEN** `check`, `discover`, `update`, `sync`, `audit`, or `sync-all` is invoked
- **THEN** each command SHALL route to the documented canonical pipeline or one of its explicit deterministic stages

#### Scenario: Agent participation

- **WHEN** generation or adaptive classification requires an LLM
- **THEN** the canonical pipeline SHALL invoke an agent at that bounded stage
- **AND** deterministic scanning, persistence, validation, and report formatting SHALL remain non-agent steps

#### Scenario: Deprecated pipeline

- **WHEN** a caller uses a legacy discovery, sync, full, or dynamic pipeline entry point during the migration window
- **THEN** it SHALL delegate to the canonical implementation or emit a migration error
- **AND** it SHALL not maintain independent behavior

### Requirement: One canonical agent builder

The consumer SHALL own one agent composition builder that receives the gateway, tools/toolsets, capabilities, hooks/policy callbacks, memory, and mode-specific instructions explicitly.

#### Scenario: Supplied registry

- **WHEN** a caller supplies a tool registry or toolset
- **THEN** the builder SHALL use it
- **AND** it SHALL not construct and silently substitute another registry

#### Scenario: Mode-specific policy

- **WHEN** check, generate, or full-sync mode is selected
- **THEN** the builder SHALL derive least-privilege tools and instructions for that mode through run-scoped composition

#### Scenario: Shared observability

- **WHEN** multiple docs-sync agents are built
- **THEN** they SHALL use the same official lifecycle and TDT observability policy
- **AND** hook packs SHALL not be registered repeatedly by every builder

### Requirement: Consumer migration verification

The migration SHALL prove behavioral parity and deletion of redundant implementation paths.

#### Scenario: End-to-end parity

- **WHEN** the canonical pipeline runs against a fixture repository
- **THEN** it SHALL produce the expected discovery, audit, generation decision, validation, and report artifacts

#### Scenario: Dead implementation paths

- **WHEN** migration is complete
- **THEN** deprecated duplicate pipeline and builder modules SHALL have no production callers
- **AND** GitNexus/Graphify analysis SHALL confirm the intended canonical path
