# Spec Delta: shb-planning-harness

## Purpose
Modernizes the `shb-agent-harness` workflow execution from linear procedural loops to a stateful LangGraph (`langgraph>=1.2.12`) `StateGraph` with conditional edge routing, durable persistence (`MemorySaver` / `PostgresSaver`), and human-in-the-loop approval gating.

## MODIFIED Requirements

### Requirement: Multi-Stage Ticket Planning Workflow
The `shb-agent-harness` system SHALL execute structured multi-stage planning pipelines using a compiled LangGraph (`langgraph>=1.2.12`) `StateGraph` over `HarnessState`, managing node transitions, conditional branch evaluations, and stage artifacts.

#### Scenario: Ticket analysis and design execution
- **WHEN** an engineering ticket instruction is submitted to the harness
- **THEN** the harness compiles and executes the state graph sequentially through the registered stages, recording stage deliverables in the state dictionary

#### Scenario: Conditional branch bypassing non-applicable stages
- **WHEN** the classification stage identifies a ticket as internal refactoring with no API surface modifications
- **THEN** conditional routing in the state graph SHALL route execution directly to design, bypassing `ApiContractStage`

## ADDED Requirements

### Requirement: StateGraph Workflow and Conditional Branching
The planning harness SHALL define workflow transitions as explicit graph nodes and edges using `StateGraph(HarnessState)`, supporting deterministic decision routing and stage reducers.

#### Scenario: Dynamic graph compilation
- **WHEN** the harness engine initializes for a given ticket
- **THEN** it SHALL assemble a typed `StateGraph` registering all 12 stages as nodes and compile the runnable graph

#### Scenario: Routing error fail-safe
- **WHEN** a conditional edge evaluation fails or returns an unrecognized branch name
- **THEN** the state graph SHALL fail safely to the default sequential pipeline and log an error event

### Requirement: Durable Persistence and State Checkpointing
The planning harness SHALL persist workflow execution state at each node boundary using LangGraph checkpointers (`MemorySaver` for ephemeral CLI and tests, `PostgresSaver` for persistent execution).

#### Scenario: State checkpoint persistence across stages
- **WHEN** any stage node finishes execution
- **THEN** the checkpointer SHALL save the updated `HarnessState` snapshot keyed by ticket ID (`thread_id`)

#### Scenario: Resumption of interrupted ticket workflow
- **WHEN** an operator requests resumption of an interrupted ticket run via CLI
- **THEN** the harness SHALL reload the latest checkpoint from storage and continue execution from the next pending stage without re-running completed stages

### Requirement: Human-in-the-Loop Milestone Approval Gating
The planning harness SHALL support pausing execution at designated governance milestones (`API_CONTRACT` and `PLAN_REVIEW`) via LangGraph `interrupt()`, requiring operator approval before proceeding to implementation planning or code generation.

#### Scenario: Workflow interruption for plan review approval
- **WHEN** execution reaches `PlanReviewStage`
- **THEN** the graph SHALL pause execution, emit an `ApprovalRequired` event with ticket details, and suspend until reviewed

#### Scenario: Workflow continuation upon operator approval
- **WHEN** an operator submits an approval command for a suspended ticket thread
- **THEN** the harness graph SHALL resume execution from the checkpoint into subsequent phases
