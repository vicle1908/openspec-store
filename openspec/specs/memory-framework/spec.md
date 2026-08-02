## Purpose

This specification defines requirements for Memory Framework.

## Requirements

### Requirement: Memory Initialization

The harness SHALL use `create_consumer_memory` from agent-core's SDK for memory initialization.

#### Scenario: Memory creation
- **WHEN** the harness starts
- **THEN** it SHALL call:
  ```python
  from agent_core.sdk import create_consumer_memory

  memory = await create_consumer_memory(
      consumer_name="agent-harness",
      enable_postgres=True,
      enable_vector=False,  # future enhancement
      context_max_messages=50,
  )
  ```
- **THEN** the memory SHALL include:
  - `ContextMemory` — in-process bounded buffer (50 messages)
  - `ScratchMemory` — filesystem at `~/.tdt/agent-harness/scratch/`
  - `PostgresMemory` — JSONB storage (if Postgres available)

#### Scenario: Postgres unavailable
- **WHEN** Postgres is unavailable
- **THEN** `create_consumer_memory` SHALL return Memory with `long_term=None`
- **THEN** the harness SHALL log a warning: "long_term_memory_unavailable consumer=agent-harness"
- **THEN** the harness SHALL continue with scratch-only memory

#### Scenario: Memory initialization failure
- **WHEN** memory creation fails
- **THEN** the harness SHALL raise `ConfigError` with clear message
- **THEN** the harness SHALL NOT start

### Requirement: Memory Layer Usage

Each memory layer SHALL be used for specific purposes.

#### Scenario: ContextMemory usage
- **WHEN** the harness needs to store conversation context
- **THEN** it SHALL use `layer="context"`:
  ```python
  await memory.store(session, "user", "Review auth.py", layer="context")
  ```
- **THEN** context SHALL be used for:
  - LLM conversation history per stage agent
  - Inter-stage communication (what was discussed)
  - Human approval conversation context

#### Scenario: ScratchMemory usage
- **WHEN** the harness needs to store per-ticket artifacts
- **THEN** it SHALL use `layer="scratch"`:
  ```python
  await memory.store(session, "clarify", artifact.model_dump(), layer="scratch")
  ```
- **THEN** scratch SHALL be used for:
  - Stage artifacts (TicketArtifact, ContextArtifact, etc.)
  - Trace chain (trace.jsonl)
  - Intermediate computation results
  - Temporary validation results

#### Scenario: PostgresMemory usage
- **WHEN** the harness needs to store cross-ticket patterns
- **THEN** it SHALL use `layer="long_term"`:
  ```python
  await memory.store(session, "api_pattern:attendance", pattern, layer="long_term", ttl_seconds=86400*30)
  ```
- **THEN** long_term SHALL be used for:
  - Design decisions and rationale
  - API patterns used across tickets
  - Lessons learned from past workflows
  - Gate approval/rejection history
  - Validation failure patterns

### Requirement: Session Naming Conventions

The harness SHALL use consistent session naming for memory scoping.

#### Scenario: Per-ticket session
- **WHEN** storing per-ticket data
- **THEN** the session SHALL be: `harness:{ticket_id}`
  - Example: `harness:TICKET-123`

#### Scenario: Per-stage session
- **WHEN** storing stage-specific data
- **THEN** the session SHALL be: `harness:{ticket_id}:{stage}`
  - Example: `harness:TICKET-123:clarify`

#### Scenario: Cross-ticket session
- **WHEN** storing cross-ticket patterns
- **THEN** the session SHALL be: `harness:patterns:{category}`
  - Example: `harness:patterns:api_design`
  - Example: `harness:patterns:gate_decisions`

#### Scenario: Agent session
- **WHEN** storing agent conversation context
- **THEN** the session SHALL be: `harness:{ticket_id}:agent:{stage}`
  - Example: `harness:TICKET-123:agent:clarify`

### Requirement: TTL Strategies

Different data types SHALL have appropriate TTL values.

#### Scenario: Artifact TTL
- **WHEN** storing stage artifacts
- **THEN** scratch layer SHALL have no TTL (filesystem cleanup)
- **THEN** long_term layer SHALL have TTL of 90 days:
  ```python
  await memory.store(session, key, value, layer="long_term", ttl_seconds=86400*90)
  ```

#### Scenario: Pattern TTL
- **WHEN** storing design patterns
- **THEN** long_term layer SHALL have TTL of 30 days:
  ```python
  await memory.store(session, key, value, layer="long_term", ttl_seconds=86400*30)
  ```

#### Scenario: Decision TTL
- **WHEN** storing gate decisions
- **THEN** long_term layer SHALL have TTL of 365 days:
  ```python
  await memory.store(session, key, value, layer="long_term", ttl_seconds=86400*365)
  ```

#### Scenario: No TTL
- **WHEN** storing critical patterns
- **THEN** long_term layer SHALL have no TTL:
  ```python
  await memory.store(session, key, value, layer="long_term", ttl_seconds=None)
  ```

### Requirement: Memory Retrieval Patterns

The harness SHALL use consistent retrieval patterns.

#### Scenario: Direct retrieval
- **WHEN** a stage needs a specific artifact
- **THEN** the harness SHALL use direct retrieval:
  ```python
  artifact = await memory.retrieve(f"harness:{ticket_id}", "clarify", layer="scratch")
  ```

#### Scenario: Fallback retrieval
- **WHEN** scratch retrieval returns None
- **THEN** the harness SHALL fall back to long_term:
  ```python
  artifact = await memory.retrieve(f"harness:{ticket_id}", "clarify", layer="scratch")
  if artifact is None:
      artifact = await memory.retrieve("harness:patterns:api_design", "clarify_pattern", layer="long_term")
  ```

#### Scenario: List keys
- **WHEN** a stage needs to know what's stored
- **THEN** the harness SHALL use list_keys:
  ```python
  keys = await memory.list_keys(f"harness:{ticket_id}", layer="scratch")
  ```

### Requirement: Memory Cleanup

The harness SHALL clean up memory appropriately.

#### Scenario: Workflow completion cleanup
- **WHEN** a workflow completes
- **THEN** the harness SHALL NOT auto-cleanup scratch (for debugging)
- **THEN** the harness SHALL log: "Workflow {ticket_id} completed, scratch retained"

#### Scenario: Manual cleanup
- **WHEN** a user runs `harness cleanup <ticket_id>`
- **THEN** the harness SHALL call `scratch.clear_task(f"harness:{ticket_id}")`
- **THEN** the harness SHALL log: "Scratch cleaned for {ticket_id}"

#### Scenario: TTL-based cleanup
- **WHEN** long_term entries expire
- **THEN** PostgresMemory SHALL auto-expire via `expires_at` column
- **THEN** the harness SHALL NOT need manual cleanup

### Requirement: MemoryCapability Integration

The harness SHALL wire MemoryCapability into stage agents for agent-level memory tools.

#### Scenario: Agent memory tools
- **WHEN** building a stage agent via `build_agent`
- **THEN** the `memory` parameter SHALL be passed:
  ```python
  agent = build_agent(
      config=config,
      tools=registry,
      memory=memory,  # MemoryCapability auto-wired
  )
  ```
- **THEN** the agent SHALL have access to:
  - `memory_store` — store values in memory
  - `memory_retrieve` — retrieve values from memory
  - `memory_recall` — search memory by query
  - `memory_list_keys` — list stored keys

#### Scenario: Agent memory usage
- **WHEN** an agent needs to store intermediate results
- **THEN** the agent SHALL use `memory_store` tool:
  ```
  memory_store(key="partial_analysis", value="...", layer="scratch")
  ```
- **THEN** the agent SHALL use `memory_retrieve` tool:
  ```
  memory_retrieve(key="partial_analysis", layer="scratch")
  ```

### Requirement: Memory Observability

The harness SHALL track memory operations for observability.

#### Scenario: Memory operation logging
- **WHEN** a memory operation occurs
- **THEN** the harness SHALL log:
  ```python
  logger.info("memory.store", session=session, key=key, layer=layer, size=len(value))
  logger.info("memory.retrieve", session=session, key=key, layer=layer, found=result is not None)
  ```

#### Scenario: Memory metrics
- **WHEN** a workflow completes
- **THEN** the harness SHALL record:
  - `memory_store_count` — number of store operations
  - `memory_retrieve_count` — number of retrieve operations
  - `memory_hit_rate` — retrieve hits / total retrieves
  - `memory_layer_usage` — breakdown by layer (context/scratch/long_term)

### Requirement: Fallback Behaviors

The harness SHALL handle memory failures gracefully.

#### Scenario: Scratch write failure
- **WHEN** scratch write fails (disk full, permissions)
- **THEN** the harness SHALL log a warning
- **THEN** the harness SHALL continue without scratch persistence
- **THEN** the artifact SHALL still be in state dict (in-memory)

#### Scenario: Postgres write failure
- **WHEN** Postgres write fails
- **THEN** the harness SHALL log a warning
- **THEN** the harness SHALL continue without long_term persistence
- **THEN** the artifact SHALL still be in scratch (if available)

#### Scenario: Postgres read failure
- **WHEN** Postgres read fails
- **THEN** the harness SHALL fall back to scratch
- **THEN** if scratch also fails, the harness SHALL log a warning
- **THEN** the stage SHALL proceed without prior context

### Requirement: Memory Schema

The harness SHALL define consistent schemas for stored values.

#### Scenario: Artifact schema
- **WHEN** storing an artifact
- **THEN** the value SHALL be:
  ```json
  {
    "artifact_type": "TicketArtifact",
    "data": {...artifact.model_dump()},
    "metadata": {
      "ticket_id": "TICKET-123",
      "stage": "intake",
      "timestamp": "2026-07-27T10:30:00Z",
      "version": 1
    }
  }
  ```

#### Scenario: Pattern schema
- **WHEN** storing a pattern
- **THEN** the value SHALL be:
  ```json
  {
    "pattern_type": "api_design",
    "description": "REST endpoint with service layer",
    "example_ticket": "TICKET-123",
    "success": true,
    "metadata": {
      "service": "attendance",
      "timestamp": "2026-07-27T10:30:00Z"
    }
  }
  ```

#### Scenario: Decision schema
- **WHEN** storing a gate decision
- **THEN** the value SHALL be:
  ```json
  {
    "decision_type": "gate_approval",
    "stage": "requirement",
    "decision": "approved",
    "approver": "product_owner",
    "rationale": "Requirements are clear and complete",
    "metadata": {
      "ticket_id": "TICKET-123",
      "timestamp": "2026-07-27T10:30:00Z"
    }
  }
  ```
