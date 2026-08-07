## Purpose

This specification defines requirements for Glossary.

## Requirements

### Requirement: Core Terminology

The harness SHALL define and use consistent terminology across all documentation and code.

#### Scenario: Artifact terms
- **WHEN** referring to workflow outputs
- **THEN** the following terms SHALL be used:
  - **Artifact**: A typed Pydantic model produced by a stage (e.g., TicketArtifact)
  - **Stage**: A single step in the 12-stage workflow (e.g., intake, clarify, design)
  - **DAG**: Directed Acyclic Graph — the workflow structure
  - **Trace Chain**: The lineage of artifacts from ticket to verification

#### Scenario: Agent terms
- **WHEN** referring to agent components
- **THEN** the following terms SHALL be used:
  - **BaseAgent**: agent-core's ReAct loop agent (from `agent_core.agent_base`)
  - **Consumer**: A system built on agent-core (e.g., agent-harness)
  - **SDK**: agent-core's public API surface (`agent_core.sdk`)
  - **Flavor**: A named configuration bundle for agent behavior

#### Scenario: Gate terms
- **WHEN** referring to approval mechanisms
- **THEN** the following terms SHALL be used:
  - **Gate**: A checkpoint requiring human approval before proceeding
  - **ApprovalGate**: agent-core's approval mechanism (from `agent_core._ai.capability`)
  - **HandleDeferredToolCalls**: pydantic-ai's deferred tool call handler
  - **StreamApprovalHandler**: agent-core's stream pause/resume handler

#### Scenario: Memory terms
- **WHEN** referring to memory layers
- **THEN** the following terms SHALL be used:
  - **ContextMemory**: In-process bounded message buffer (session-scoped)
  - **ScratchMemory**: Filesystem-backed task-scoped storage
  - **PostgresMemory**: Postgres-backed persistent storage (cross-session)
  - **Memory Facade**: The unified interface routing to context/scratch/long_term

#### Scenario: Resilience terms
- **WHEN** referring to fault tolerance
- **THEN** the following terms SHALL be used:
  - **FallbackModel**: pydantic-ai's built-in model fallback with automatic retry
  - **create_model**: Resolves provider:model_name strings to Model instances
  - **@resilient_tool**: Decorator wrapping tools with error handling

#### Scenario: Validation terms
- **WHEN** referring to anti-hallucination
- **THEN** the following terms SHALL be used:
  - **Tier 1 (Existence)**: Mechanical checks verifying references exist
  - **Tier 2 (Semantic)**: LLM-assisted pattern consistency checks
  - **Tier 3 (Structural)**: Cross-artifact reference checking
  - **Validation Result**: pass/fail/flagged with details

### Requirement: Abbreviation Standards

The harness SHALL use consistent abbreviations across all documentation.

#### Scenario: Common abbreviations
- **WHEN** using abbreviations
- **THEN** the following SHALL be used:
  - **GH**: agent-harness (the harness system)
  - **AC**: agent-core (the framework)
  - **GN**: GitNexus (code intelligence)
  - **GF**: Graphify (graph traversal)
  - **OS**: OpenSpec (spec management)
  - **OTel**: OpenTelemetry (tracing)
  - **LLM**: Large Language Model

### Requirement: Code Naming Conventions

The harness SHALL follow consistent naming conventions in code.

#### Scenario: File naming
- **WHEN** naming files
- **THEN** the following conventions SHALL be used:
  - Stage handlers: `s{NN}_{name}.py` (e.g., `s01_intake.py`, `s06_design.py`)
  - Tool wrappers: `{tool}_client.py` (e.g., `gitnexus_client.py`)
  - Validators: `tier{N}_{type}.py` (e.g., `tier1_existence.py`)
  - Config: `config.py`, `gate_config.py`, `workspace_config.py`

#### Scenario: Class naming
- **WHEN** naming classes
- **THEN** the following conventions SHALL be used:
  - Artifacts: `{Stage}Artifact` (e.g., `TicketArtifact`, `DesignArtifact`)
  - Tools: `{Tool}Client` (e.g., `GitNexusClient`, `GraphifyClient`)
  - Validators: `Tier{N}{Type}Validator` (e.g., `Tier1ExistenceValidator`)
  - Config: `HarnessConfig`, `GateConfig`, `WorkspaceRepoConfig`

#### Scenario: Function naming
- **WHEN** naming functions
- **THEN** the following conventions SHALL be used:
  - Stage handlers: `{stage}_handler` (e.g., `intake_handler`, `clarify_handler`)
  - Tool methods: `{action}_{target}` (e.g., `query_symbols`, `check_existence`)
  - Validators: `validate_{tier}_{check}` (e.g., `validate_tier1_existence`)
