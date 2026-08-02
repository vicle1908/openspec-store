## ADDED Requirements

### Requirement: ADR-001: Consumer Pattern Over Framework Extension — agent-harness SHALL use SDK primitives only

agent-harness MUST import only from `agent_core.sdk` and MUST NOT import from internal modules.

#### Scenario: SDK-only integration
- **WHEN** agent-harness imports from agent-core
- **THEN** it SHALL import only from `agent_core.sdk`
- **AND** it MUST NOT import from `agent_core._ai`, `agent_core.foundation._internal`, or other internal modules

**Status**: Accepted
**Date**: 2026-07-27
**Deciders**: TDT Team

#### Context

agent-core provides a comprehensive SDK with `ConsumerConfig`, `build_agent`, `build_toolkit`, `create_consumer_memory`, `init_observability`, and `discover_repos`. The question is whether agent-harness should use these SDK primitives or import from internal modules directly.

#### Decision

agent-harness SHALL use agent-core's SDK as the sole integration point. agent-harness MUST NOT import from `agent_core.*` internal modules.

#### Rationale

- SDK provides stable API surface — internal modules may change
- `ConsumerConfig` composes framework settings + consumer-specific fields
- `build_agent` auto-registers Tier 0 hooks (otel_metrics, structured_audit)
- `create_consumer_memory` handles memory initialization with correct paths
- `init_observability` configures OTel + logging in one call

#### Consequences

- ✅ Stable API — won't break on agent-core internal refactors
- ✅ Auto-registered hooks — no manual hook setup needed
- ✅ Consistent patterns — same as agent-docs-sync and other consumers
- ❌ Slightly more verbose — must use SDK wrappers instead of direct access
- ❌ Limited to SDK-provided functionality — can't access internal extensions

#### Agent-Readable Summary

```
Decision: consumer_pattern
Choice: sdk_primitives_only
Rationale: stable_api, auto_hooks, consistent_patterns
Consequences: verbose_but_stable
```

### Requirement: ADR-002: Typed Artifacts Over Raw Dicts — artifacts SHALL use typed Pydantic models

Stage artifacts MUST be typed Pydantic models with the common ArtifactEnvelope provenance fields.

#### Scenario: Artifact type safety
- **WHEN** a stage produces an artifact
- **THEN** the artifact SHALL be a typed Pydantic model
- **AND** unknown fields SHALL cause validation failure

**Status**: Accepted
**Date**: 2026-07-27
**Deciders**: TDT Team

#### Context

LangGraph's `StateGraph(dict)` uses plain dicts for state. The question is whether stage artifacts should be typed Pydantic models or raw dicts.

#### Decision

Artifacts SHALL use typed Pydantic models, stored as dicts in state via `model_dump()`/`model_validate()`. Each stage artifact MUST have a distinct typed model with the common `ArtifactEnvelope` provenance fields.

#### Rationale

- Pydantic models provide IDE completion and type checking
- `model_dump()` serializes to dict for LangGraph state compatibility
- `model_validate()` deserializes from dict when reading from state
- JSON schema generation enables API contract validation
- Field validators catch malformed data early

#### Consequences

- ✅ Type safety — IDE knows available fields
- ✅ Validation — Pydantic catches malformed data
- ✅ Schema generation — JSON schema for API contracts
- ❌ Serialization overhead — convert between model and dict
- ❌ More code — must define model classes for each artifact

#### Agent-Readable Summary

```
Decision: typed_artifacts
Choice: pydantic_models_with_dict_storage
Rationale: type_safety, validation, schema_generation
Consequences: serialization_overhead, more_code
```

### Requirement: ADR-003: Native Interrupt Gates — gate nodes SHALL use LangGraph interrupt

Gate nodes MUST use native LangGraph interrupt() with typed GateRequest payloads and MUST resume via Command(resume=GateDecision(...)).

#### Scenario: Gate interrupt and resume
- **WHEN** a configured gate stage is reached
- **THEN** the node SHALL interrupt with a typed GateRequest
- **AND** the workflow SHALL resume via Command(resume=GateDecision(...)) on the same thread_id

**Status**: Accepted
**Date**: 2026-07-27
**Deciders**: TDT Team

#### Context

agent-core's WorkflowBuilder supports `NodeKind.HUMAN` for nodes that require external input. The question is whether approval gates should use this or be implemented as wrapper functions.

#### Decision

Gate nodes SHALL use native LangGraph `interrupt()` with typed `GateRequest` payloads. The workflow MUST resume via `Command(resume=GateDecision(...))` using the same `thread_id`.

#### Rationale

- `NodeKind.HUMAN` is designed for exactly this use case
- LangGraph knows to pause and wait for external input
- `PostgresSaver` preserves state during approval wait
- `CommandResult(goto=...)` handles backtrack on rejection
- `StreamApprovalHandler` manages stream pause/resume

#### Consequences

- ✅ Explicit in DAG — gates are visible in workflow visualization
- ✅ Native LangGraph support — no custom pause/resume logic
- ✅ Checkpoint integration — state preserved during wait
- ❌ Requires external approval mechanism (CLI/webhook)
- ❌ More complex than simple wrapper function

#### Agent-Readable Summary

```
Decision: gate_mechanism
Choice: nodekind_human_with_approval_gate
Rationale: explicit_dag, native_support, checkpoint_integration
Consequences: requires_external_mechanism
```

### Requirement: ADR-004: Tool Resilience — tool wrappers SHALL use circuit breaker and retry

External tool wrappers MUST use circuit breaker, retry with jitter, and fallback chain patterns. Tool errors MUST NOT be silently swallowed.

#### Scenario: Tool failure handling
- **WHEN** an external tool call fails
- **THEN** the harness SHALL record the failure as evidence with reduced confidence
- **AND** it SHALL NOT silently swallow the error

**Status**: Accepted
**Date**: 2026-07-27
**Deciders**: TDT Team

#### Context

External tools (GitNexus, Graphify, Jira, GitLab) may fail due to network issues, rate limits, or service unavailability. The question is how to handle these failures.

#### Decision

External tool wrappers SHALL use circuit breaker, retry with jitter, and fallback chain patterns for resilience. Tool calls MUST NOT fail silently — errors SHALL propagate as evidence with reduced confidence.

#### Rationale

- `CircuitBreaker` prevents cascading failures on repeated failures
- `retry_with_jitter` handles transient failures with exponential backoff
- `FallbackChain` provides graceful degradation
- `@resilient_tool` decorator wraps tools with circuit breaker + retry
- All primitives are proven in agent-core's LLM gateway

#### Consequences

- ✅ Fault tolerance — tools recover from transient failures
- ✅ Fast failure — circuit breaker prevents wasted retries
- ✅ Graceful degradation — fallback chain provides alternatives
- ❌ Complexity — must configure breaker thresholds per tool
- ❌ State management — circuit breaker state must be shared

#### Agent-Readable Summary

```
Decision: tool_resilience
Choice: circuit_breaker_with_retry_and_fallback
Rationale: fault_tolerance, fast_failure, graceful_degradation
Consequences: complexity, state_management
```

### Requirement: ADR-005: Three-Tier Validation — artifacts SHALL pass existence, semantic, structural tiers

Every stage artifact MUST pass through existence, semantic, and structural validation tiers before being marked verified.

#### Scenario: Validation pipeline execution
- **WHEN** a stage produces an artifact
- **THEN** the validation pipeline SHALL run all three tiers
- **AND** the artifact SHALL not be marked verified unless all tiers pass above the confidence threshold

**Status**: Accepted
**Date**: 2026-07-27
**Deciders**: TDT Team

#### Context

AI agents may hallucinate APIs, classes, or file paths that don't exist. The question is how to prevent this.

#### Decision

The harness SHALL implement three validation tiers: existence (Tier 1), semantic (Tier 2), and structural (Tier 3). Every stage artifact MUST pass through the validation pipeline before being marked verified.

#### Rationale

- Tier 1 (existence): Fast, no LLM cost — catches obvious hallucinations
- Tier 2 (semantic): LLM-assisted — catches pattern violations
- Tier 3 (structural): Cross-artifact — catches broken trace chains
- Progressive validation — cheap checks first, expensive checks later

#### Consequences

- ✅ Comprehensive coverage — catches hallucinations at multiple levels
- ✅ Cost-efficient — cheap checks first
- ✅ Auditable — each tier produces validation results
- ❌ Latency — three tiers add validation time
- ❌ False positives — Tier 2 may flag valid patterns as violations

#### Agent-Readable Summary

```
Decision: anti_hallucination
Choice: three_tier_validation
Rationale: comprehensive_coverage, cost_efficient, auditable
Consequences: latency, false_positives
```

### Requirement: ADR-006: Memory Isolation — memory namespaces SHALL be isolated by tenant/workspace/ticket

Memory namespaces MUST be isolated by tenant, workspace, and ticket to prevent cross-tenant data leakage.

#### Scenario: Cross-tenant isolation
- **WHEN** two different tenants use the harness
- **THEN** their memory namespaces SHALL be isolated
- **AND** one tenant's data SHALL NOT be visible to the other

**Status**: Accepted
**Date**: 2026-07-27
**Deciders**: TDT Team

#### Context

The harness needs to store per-ticket artifacts and cross-ticket patterns. The question is how to use agent-core's memory system.

#### Decision

The harness SHALL use process-local scratch storage for per-ticket artifacts and durable persistent storage for cross-ticket patterns. Memory namespaces MUST be isolated by tenant/workspace/ticket to prevent cross-tenant leakage.

#### Rationale

- `ScratchMemory` is filesystem-backed, task-scoped — perfect for per-ticket state
- `PostgresMemory` is JSONB-backed, persistent — perfect for cross-ticket patterns
- `Memory` facade routes to the correct layer transparently
- `create_consumer_memory` handles initialization with correct paths

#### Consequences

- ✅ Appropriate storage — filesystem for temp, Postgres for persistent
- ✅ Automatic cleanup — scratch is cleared per task
- ✅ Cross-ticket learning — patterns stored in long-term memory
- ❌ Postgres dependency — long-term memory requires Postgres
- ❌ No vector search — future enhancement

#### Agent-Readable Summary

```
Decision: memory_architecture
Choice: scratch_for_temp_postgres_for_persistent
Rationale: appropriate_storage, automatic_cleanup, cross_ticket_learning
Consequences: postgres_dependency, no_vector_search
```

### Requirement: ADR-007: Trace Linearity — trace entries SHALL record stage, revision, evidence, and validation

Each TraceEntry MUST record stage, revision, event type, timestamps, evidence references, and validation status.

#### Scenario: Trace entry creation
- **WHEN** a stage completes, fails, or is revised
- **THEN** a TraceEntry SHALL be appended with stage, revision, event type, timestamps, and evidence references

**Status**: Accepted
**Date**: 2026-07-27
**Deciders**: TDT Team

#### Context

Artifacts form a dependency chain (ticket → context → requirement → spec → ...). The question is how to represent this chain for traceability.

#### Decision

The harness SHALL use a linear trace chain with explicit input annotations per artifact. Each TraceEntry MUST record the stage, revision, event type, timestamps, evidence references, and validation status.

#### Rationale

- Linear chain is easy to visualize and render in reports
- Input annotations capture the full dependency DAG without complexity
- Each artifact records: source_refs, verification method, confidence level
- TraceEntry schema provides machine-readable trace data

#### Consequences

- ✅ Simple to understand — linear chain is intuitive
- ✅ Easy to render — reports show clear progression
- ✅ Machine-readable — TraceEntry schema for agents
- ❌ Linear approximation — doesn't capture parallel dependencies
- ❌ Verbose — each artifact carries input_artifacts list

#### Agent-Readable Summary

```
Decision: traceability_model
Choice: linear_chain_with_input_annotations
Rationale: simple_understanding, easy_rendering, machine_readable
Consequences: linear_approximation, verbose
```
