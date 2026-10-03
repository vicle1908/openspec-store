# shb-planning-harness Specification

## Purpose
Provides a multi-stage autonomous planning harness, schema-backed validation, and durable ticket execution workflows for the Saigon - Hanoi Bank (SHB) agent ecosystem.

## Requirements

### Requirement: Multi-Stage Ticket Planning Workflow
The `shb-agent-harness` system SHALL execute structured multi-stage planning pipelines using a compiled LangGraph (`langgraph>=1.2.12`) `StateGraph` over `HarnessState`, managing node transitions, conditional branch evaluations, and stage artifacts.

#### Scenario: Ticket analysis and design execution
- **WHEN** an engineering ticket instruction is submitted to the harness
- **THEN** the harness compiles and executes the state graph sequentially through the registered stages, recording stage deliverables in the state dictionary

#### Scenario: Conditional branch bypassing non-applicable stages
- **WHEN** the classification stage identifies a ticket as internal refactoring with no API surface modifications
- **THEN** conditional routing in the state graph SHALL route execution directly to design, bypassing `ApiContractStage`

### Requirement: Schema-Backed Claim and Evidence Verification
The system SHALL validate stage deliverables against versioned JSON schemas provided by `shb-ai-harness-skills`, asserting evidence completeness before advancing stage transitions.

#### Scenario: Missing evidence rejection
- **WHEN** a stage execution produces a deliverable missing required verification evidence
- **THEN** the harness validation engine SHALL flag the missing claim and prevent stage advancement

### Requirement: Command-Line Interface Entrypoint
The package SHALL provide an executable command-line interface named `shb-harness` allowing engineers to start, inspect, and resume planning workflows across human-in-the-loop governance milestones.

#### Scenario: Workflow status check
- **WHEN** an engineer executes `shb-harness status --ticket-id <id>`
- **THEN** the CLI outputs the current active stage, completed checkpoints, and artifact locations

#### Scenario: Resumption of paused ticket thread
- **WHEN** an engineer executes `shb-harness resume <ticket-id> --action approve`
- **THEN** the CLI SHALL submit the approval command to the compiled state graph and resume pipeline execution

### Requirement: StateGraph Workflow and Conditional Branching
The planning harness SHALL define workflow transitions as explicit graph nodes and edges using `StateGraph(HarnessState)`, supporting deterministic decision routing and stage reducers.

#### Scenario: Dynamic graph compilation
- **WHEN** the harness engine initializes for a given ticket
- **THEN** it SHALL assemble a typed `StateGraph` registering all 12 stages as nodes and compile the runnable graph

#### Scenario: Routing error fail-safe
- **WHEN** a conditional edge evaluation fails or returns an unrecognized branch name
- **THEN** the state graph SHALL fail safely to the default sequential pipeline and log an error event

### Requirement: Durable Persistence and State Checkpointing
The planning harness SHALL persist workflow execution state at each node boundary using LangGraph checkpointers, prioritizing file-backed `SqliteSaver` in `~/.shb/harness.db` for multi-session persistence with graceful fallback to `MemorySaver` for ephemeral test executions.

#### Scenario: State checkpoint persistence across stages
- **WHEN** any stage node finishes execution
- **THEN** the checkpointer SHALL save the updated `HarnessState` snapshot keyed by ticket ID (`thread_id`)

#### Scenario: Resumption of interrupted ticket workflow
- **WHEN** an operator requests resumption of an interrupted ticket run via CLI
- **THEN** the harness SHALL reload the latest checkpoint from storage and continue execution from the next pending stage without re-running completed stages

#### Scenario: SQLite state checkpoint persistence across stages
- **WHEN** any stage node finishes execution in the planning lifecycle
- **THEN** the checkpointer SHALL save the updated `HarnessState` snapshot keyed by ticket ID (`thread_id`) to the SQLite checkpoint database

### Requirement: Human-in-the-Loop Milestone Approval Gating
The planning harness SHALL support pausing execution at designated governance milestones (`API_CONTRACT` and `PLAN_REVIEW`) via LangGraph `interrupt()`, requiring operator approval before proceeding to implementation planning or code generation.

#### Scenario: Workflow interruption for plan review approval
- **WHEN** execution reaches `PlanReviewStage`
- **THEN** the graph SHALL pause execution, emit an `ApprovalRequired` event with ticket details, and suspend until reviewed

#### Scenario: Workflow continuation upon operator approval
- **WHEN** an operator submits an approval command for a suspended ticket thread
- **THEN** the harness graph SHALL resume execution from the checkpoint into subsequent phases
