## Purpose

This specification defines requirements for Memory System.

## Requirements

### Requirement: Persistence ownership matrix

The harness SHALL assign each state category to one persistence authority.

#### Scenario: Workflow state

- **WHEN** node state, routing, or pending interrupts require recovery
- **THEN** the LangGraph checkpointer SHALL own that state

#### Scenario: Agent step state

- **WHEN** an agent run requires step continuation or forking
- **THEN** Harness `StepPersistence` with a public `StepStore` SHALL own it

#### Scenario: Semantic memory

- **WHEN** approved cross-ticket patterns or decisions are recalled
- **THEN** the official Harness `Memory` capability over an authorized `MemoryStore` SHALL own retrieval/injection

#### Scenario: Artifact bytes

- **WHEN** a stage writes an artifact or trace file
- **THEN** the bounded harness artifact store SHALL own it
- **AND** workflow or semantic memory SHALL contain only references/digests needed for recovery

### Requirement: Bounded artifact storage

All generated files SHALL remain beneath `$TDT_HOME/agent-harness/artifacts/<ticket-id>/<run-id>/`.

#### Scenario: Artifact write

- **WHEN** a stage persists an artifact
- **THEN** the normalized target SHALL remain inside the run root
- **AND** a new immutable revision and content digest SHALL be recorded

#### Scenario: Path escape

- **WHEN** a target is absolute, traverses with `..`, or escapes through a symlink
- **THEN** the write SHALL be rejected before creating directories or files

### Requirement: Harness memory integration

Stage agents requiring semantic memory SHALL receive the public Harness `Memory` capability through typed composition.

#### Scenario: TDT memory backend

- **WHEN** a TDT tenant-aware backend is selected
- **THEN** a public `MemoryStore` adapter SHALL preserve tenant, workspace, ticket, and run namespaces
- **AND** official injection and search-result limits SHALL apply

#### Scenario: Generic local backend

- **WHEN** TDT-specific backend semantics are unnecessary
- **THEN** a matching public Harness store SHALL be used instead of a custom generic store

### Requirement: Cross-ticket memory admission

Only approved, non-secret decisions and patterns SHALL enter cross-ticket memory.

#### Scenario: Approved pattern

- **WHEN** verification completes and policy approves a reusable pattern
- **THEN** it MAY be stored with tenant/workspace scope, source artifact digest, and retention metadata

#### Scenario: Unapproved or sensitive content

- **WHEN** an artifact is rejected, contains credentials, or lacks admission policy
- **THEN** it SHALL not enter cross-ticket memory

### Requirement: Memory isolation

Memory reads SHALL enforce tenant, workspace, ticket, and authority boundaries.

#### Scenario: Cross-tenant retrieval

- **WHEN** a run requests memory from another tenant or unauthorized workspace
- **THEN** retrieval SHALL return no data
- **AND** the denial SHALL be audited without exposing the protected content
