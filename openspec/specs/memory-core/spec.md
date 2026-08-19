## Purpose

Defines the memory framework architecture, persistence ownership matrix, bounded artifact storage, memory layer usage patterns, and operational behaviors (cleanup, observability, fallbacks) for the agent harness memory system.

## Requirements

### Requirement: Memory Initialization

The harness SHALL use `create_consumer_memory` from agent-core's SDK for memory initialization.

#### Scenario: Memory creation

- **WHEN** the harness starts
- **THEN** it SHALL call `create_consumer_memory` with appropriate parameters
- **AND** the memory SHALL include ContextMemory (in-process bounded buffer), ScratchMemory (filesystem), and PostgresMemory (JSONB storage if available)

#### Scenario: Postgres unavailable

- **WHEN** Postgres is unavailable
- **THEN** `create_consumer_memory` SHALL return Memory with `long_term=None`
- **AND** the harness SHALL log a warning and continue with scratch-only memory

#### Scenario: Memory initialization failure

- **WHEN** memory creation fails
- **THEN** the harness SHALL raise `ConfigError` with clear message and SHALL NOT start

### Requirement: Memory Layer Usage

Each memory layer SHALL be used for specific purposes.

#### Scenario: ContextMemory usage

- **WHEN** the harness needs to store conversation context
- **THEN** it SHALL use `layer="context"` for LLM conversation history, inter-stage communication, and human approval context

#### Scenario: ScratchMemory usage

- **WHEN** the harness needs to store per-ticket artifacts
- **THEN** it SHALL use `layer="scratch"` for stage artifacts, trace chains, intermediate computation results, and temporary validation results

#### Scenario: PostgresMemory usage

- **WHEN** the harness needs to store cross-ticket patterns
- **THEN** it SHALL use `layer="long_term"` for design decisions, API patterns, lessons learned, gate history, and validation failure patterns

### Requirement: Session Naming Conventions

The harness SHALL use consistent session naming for memory scoping.

#### Scenario: Per-ticket session

- **WHEN** storing per-ticket data
- **THEN** the session SHALL be `harness:{ticket_id}`

#### Scenario: Per-stage session

- **WHEN** storing stage-specific data
- **THEN** the session SHALL be `harness:{ticket_id}:{stage}`

#### Scenario: Cross-ticket session

- **WHEN** storing cross-ticket patterns
- **THEN** the session SHALL be `harness:patterns:{category}`

#### Scenario: Agent session

- **WHEN** storing agent conversation context
- **THEN** the session SHALL be `harness:{ticket_id}:agent:{stage}`

### Requirement: TTL Strategies

Different data types SHALL have appropriate TTL values.

#### Scenario: Artifact TTL

- **WHEN** storing stage artifacts
- **THEN** scratch layer SHALL have no TTL and long_term layer SHALL have TTL of 90 days

#### Scenario: Pattern TTL

- **WHEN** storing design patterns
- **THEN** long_term layer SHALL have TTL of 30 days

#### Scenario: Decision TTL

- **WHEN** storing gate decisions
- **THEN** long_term layer SHALL have TTL of 365 days

#### Scenario: No TTL

- **WHEN** storing critical patterns
- **THEN** long_term layer SHALL have no TTL

### Requirement: Memory Retrieval Patterns

The harness SHALL use consistent retrieval patterns.

#### Scenario: Direct retrieval

- **WHEN** a stage needs a specific artifact
- **THEN** the harness SHALL use direct retrieval by session and key

#### Scenario: Fallback retrieval

- **WHEN** scratch retrieval returns None
- **THEN** the harness SHALL fall back to long_term

#### Scenario: List keys

- **WHEN** a stage needs to know what's stored
- **THEN** the harness SHALL use list_keys for the appropriate layer

### Requirement: Memory Cleanup

The harness SHALL clean up memory appropriately.

#### Scenario: Workflow completion cleanup

- **WHEN** a workflow completes
- **THEN** the harness SHALL NOT auto-cleanup scratch (for debugging)
- **AND** the harness SHALL log a completion message

#### Scenario: Manual cleanup

- **WHEN** a user runs `harness cleanup <ticket_id>`
- **THEN** the harness SHALL call `scratch.clear_task()` for the ticket

#### Scenario: TTL-based cleanup

- **WHEN** long_term entries expire
- **THEN** PostgresMemory SHALL auto-expire via the `expires_at` column without manual intervention

### Requirement: MemoryCapability Integration

The harness SHALL wire MemoryCapability into stage agents for agent-level memory tools.

#### Scenario: Agent memory tools

- **WHEN** building a stage agent via `build_agent`
- **THEN** the `memory` parameter SHALL be passed and the agent SHALL have access to memory_store, memory_retrieve, memory_recall, and memory_list_keys tools

#### Scenario: Agent memory usage

- **WHEN** an agent needs to store intermediate results
- **THEN** the agent SHALL use memory_store and memory_retrieve tools

### Requirement: Memory Observability

The harness SHALL track memory operations for observability.

#### Scenario: Memory operation logging

- **WHEN** a memory operation occurs
- **THEN** the harness SHALL log operation details including session, key, layer, and result status

#### Scenario: Memory metrics

- **WHEN** a workflow completes
- **THEN** the harness SHALL record memory_store_count, memory_retrieve_count, memory_hit_rate, and memory_layer_usage

### Requirement: Fallback Behaviors

The harness SHALL handle memory failures gracefully.

#### Scenario: Scratch write failure

- **WHEN** scratch write fails (disk full, permissions)
- **THEN** the harness SHALL log a warning, continue without scratch persistence, and the artifact SHALL still be in state dict (in-memory)

#### Scenario: Postgres write failure

- **WHEN** Postgres write fails
- **THEN** the harness SHALL log a warning, continue without long_term persistence, and the artifact SHALL still be in scratch if available

#### Scenario: Postgres read failure

- **WHEN** Postgres read fails
- **THEN** the harness SHALL fall back to scratch, and if scratch also fails, the stage SHALL proceed without prior context

### Requirement: Memory Schema

The harness SHALL define consistent schemas for stored values.

#### Scenario: Artifact schema

- **WHEN** storing an artifact
- **THEN** the value SHALL include artifact_type, data, and metadata fields (ticket_id, stage, timestamp, version)

#### Scenario: Pattern schema

- **WHEN** storing a pattern
- **THEN** the value SHALL include pattern_type, description, example_ticket, success, and metadata fields

#### Scenario: Decision schema

- **WHEN** storing a gate decision
- **THEN** the value SHALL include decision_type, stage, decision, approver, rationale, and metadata fields

### Requirement: Persistence ownership matrix

The harness SHALL assign each state category to one persistence authority.

#### Scenario: Workflow state

- **WHEN** node state, routing, or pending interrupts require recovery
- **THEN** the LangGraph checkpointer SHALL own that state

#### Scenario: Agent step state

- **WHEN** an agent run requires step continuation or forking
- **THEN** Harness StepPersistence with a public StepStore SHALL own it

#### Scenario: Semantic memory

- **WHEN** approved cross-ticket patterns or decisions are recalled
- **THEN** the official Harness Memory capability over an authorized MemoryStore SHALL own retrieval/injection

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

Stage agents requiring semantic memory SHALL receive the public Harness Memory capability through typed composition.

#### Scenario: TDT memory backend

- **WHEN** a TDT tenant-aware backend is selected
- **THEN** a public MemoryStore adapter SHALL preserve tenant, workspace, ticket, and run namespaces
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
