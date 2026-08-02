## ADDED Requirements

### Requirement: Stage Handler Interaction Pattern

Every stage handler SHALL follow a consistent interaction pattern with the workflow engine, tools, and memory.

#### Scenario: TOOL node interaction
- **WHEN** a TOOL node executes (intake, context, impact, etc.)
- **THEN** the interaction SHALL be:
  ```
  WorkflowEngine → handler(state) → tool_wrapper.execute() → artifact → state update
                   ↑                    ↑                        ↑
                   │                    │                        │
                   │                    ├── GitNexus CLI         │
                   │                    ├── Graphify CLI         │
                   │                    ├── ReadFileTool         │
                   │                    └── GrepSearchTool      │
                   │                                              │
                   └── PostgresSaver checkpoint ←────────────────┘
  ```

#### Scenario: AGENT node interaction
- **WHEN** an AGENT node executes (clarify, spec, design, etc.)
- **THEN** the interaction SHALL be:
  ```
  WorkflowEngine → handler(state) → BaseAgent.run() → artifact → state update
                   ↑                    ↑                ↑
                   │                    │                │
                   │                    ├── LLM Gateway  │
                   │                    ├── Tools (read) │
                   │                    └── Memory       │
                   │                                      │
                   └── PostgresSaver checkpoint ←─────────┘
  ```

#### Scenario: HUMAN node interaction
- **WHEN** a HUMAN node executes (gate stages)
- **THEN** the interaction SHALL be:
  ```
  WorkflowEngine → handler(state) → ApprovalGate → pause
                   ↑                    ↑             │
                   │                    │             │
                   │                    ├── HandleDeferredToolCalls
                   │                    └── StreamApprovalHandler
                   │                                      │
                   │              External approval ←──────┘
                   │                    ↑                   │
                   │                    │                   │
                   └── PostgresSaver checkpoint ←───────────┘
  ```

### Requirement: Tool Wrapper Interaction Pattern

All external tool wrappers SHALL follow a consistent interaction pattern with resilience primitives.

#### Scenario: Resilient tool call
- **WHEN** a tool wrapper is called
- **THEN** the interaction SHALL be:
  ```
  Stage Handler → @resilient_tool → CircuitBreaker.check()
                                    │
                                    ├── [closed] → retry_with_jitter → tool.execute()
                                    │                                  │
                                    │                                  ├── [success] → record_success() → result
                                    │                                  └── [failure] → record_failure() → retry
                                    │
                                    ├── [open] → CircuitBreakerOpenError → FallbackChain
                                    │                                  │
                                    │                                  └── [fallback] → result
                                    │
                                    └── [half_open] → probe → [success] → close circuit
                                                        └── [failure] → open circuit
  ```

### Requirement: Memory Interaction Pattern

All memory operations SHALL follow a consistent interaction pattern via the Memory facade.

#### Scenario: Store artifact
- **WHEN** a stage produces an artifact
- **THEN** the interaction SHALL be:
  ```
  Stage Handler → Memory.store(session, key, value, layer="scratch")
                  │
                  ├── ScratchMemory.store() → ~/.tdt/agent-harness/scratch/workflows/{ticket_id}/{key}
                  │
                  └── (if long_term) PostgresMemory.store() → Postgres JSONB
  ```

#### Scenario: Retrieve artifact
- **WHEN** a stage needs a prior artifact
- **THEN** the interaction SHALL be:
  ```
  Stage Handler → Memory.retrieve(session, key, layer="scratch")
                  │
                  ├── (found) → value
                  │
                  └── (not found) → Memory.retrieve(session, key, layer="long_term")
                                    │
                                    ├── (found) → value
                                    │
                                    └── (not found) → None
  ```

### Requirement: Observability Interaction Pattern

All observability operations SHALL follow a consistent interaction pattern via agent-core's init_observability.

#### Scenario: OTel span per stage
- **WHEN** a stage executes
- **THEN** the interaction SHALL be:
  ```
  Stage Handler → get_tracer("agent_harness.stages").start_as_current_span(stage_name)
                  │
                  ├── span.set_attribute("ticket_id", ticket_id)
                  ├── span.set_attribute("stage_name", stage_name)
                  ├── span.set_attribute("artifact_refs", source_refs)
                  │
                  ├── (success) → span.set_status(OK)
                  └── (failure) → span.set_status(ERROR, error.message)
  ```

#### Scenario: Langfuse scoring
- **WHEN** a workflow completes
- **THEN** the interaction SHALL be:
  ```
  Verification Stage → LangfuseClient.score_trace(trace_id, scores)
                       │
                       ├── CostScorer → cost_efficiency score
                       ├── RegressionScorer → regression score
                       └── (custom) → domain-specific scores
  ```

### Requirement: Gate Interaction Pattern

Gate nodes SHALL follow a consistent interaction pattern for approval/rejection.

#### Scenario: Gate approval flow
- **WHEN** a gate requires approval
- **THEN** the interaction SHALL be:
  ```
  Gate Node → emit approval request via HandleDeferredToolCalls
              │
              ├── ApprovalGate → StreamApprovalHandler.pause()
              │
              ├── PostgresSaver.checkpoint(state)
              │
              ├── (wait for external input)
              │
              ├── (approval received) → StreamApprovalHandler.resume()
              │                         │
              │                         └── continue to next stage
              │
              └── (rejection received) → CommandResult(goto=backtrack_target)
                                         │
                                         └── route back to previous stage
  ```

### Requirement: Validation Interaction Pattern

Validation tiers SHALL follow a consistent interaction pattern.

#### Scenario: Tier 1 validation
- **WHEN** an artifact is generated
- **THEN** the interaction SHALL be:
  ```
  Validator → for each source_ref in artifact.source_refs:
              │
              ├── GitNexus query → exists? → yes: verified_by="gitnexus_query"
              │                      └── no: flag as invalid, retry with context
              │
              └── Graphify query → exists? → yes: verified_by="graphify_query"
                                   └── no: flag as invalid, retry with context
  ```

#### Scenario: Tier 2 validation
- **WHEN** Tier 1 passes
- **THEN** the interaction SHALL be:
  ```
  Validator → LLM Agent.run("Check consistency of {artifact} against codebase patterns")
              │
              ├── (consistent) → validation_result="pass"
              └── (inconsistent) → validation_result="flagged", issues=[...]
  ```

#### Scenario: Tier 3 validation
- **WHEN** Tier 2 passes
- **THEN** the interaction SHALL be:
  ```
  Validator → for each input_artifact in artifact.input_artifacts:
              │
              ├── (exists in state) → check coverage
              │
              └── (missing) → validation_result="fail", backtrack to missing stage
  ```
