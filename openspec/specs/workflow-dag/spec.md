## Purpose

This specification defines requirements for Workflow Dag.

## Requirements

### Requirement: Prerequisite framework contract

`agent-harness` implementation SHALL begin only after `stabilize-agent-framework-integration` and `converge-agent-framework-upstream` are complete and their strict validation and contract suites pass.

#### Scenario: Prerequisite incomplete

- **WHEN** either prerequisite change is incomplete or failing verification
- **THEN** implementation SHALL stop before repository source is created
- **AND** the failed prerequisite SHALL be reported

### Requirement: Exact typed 12-stage workflow

The harness SHALL implement exactly these planning stages in order: `intake`, `context`, `clarify`, `spec`, `impact`, `design`, `api_contract`, `implementation_plan`, `coding_plan`, `plan_review`, `test_plan`, and `verification`.

#### Scenario: Normal progression

- **WHEN** each stage completes without a gate, validation failure, or blocked dependency
- **THEN** the graph SHALL progress through all 12 stages in order
- **AND** verification SHALL produce the terminal workflow result

#### Scenario: Planning-only scope

- **WHEN** `coding_plan`, `plan_review`, or `test_plan` runs
- **THEN** it SHALL produce planning/review artifacts
- **AND** it SHALL not edit source, execute tests, create branches, commits, merge requests, deployments, or canonical OpenSpec changes

### Requirement: Native typed LangGraph state

The workflow SHALL use a typed consumer-owned state schema with explicit reducers for accumulated trace and revision fields.

#### Scenario: Typed stage update

- **WHEN** a stage returns an update
- **THEN** every updated field SHALL conform to the declared state schema
- **AND** an invalid artifact or transition SHALL identify its stage and field

#### Scenario: Concurrent accumulation

- **WHEN** parallel read-only context queries append evidence or trace entries
- **THEN** declared reducers SHALL combine them deterministically
- **AND** no generic mutable `results` dictionary SHALL be required

### Requirement: Native command routing

Backtrack, skip, blocked, and abort transitions SHALL use native LangGraph `Command`.

#### Scenario: Revision backtrack

- **WHEN** validation requests a revision from an earlier stage
- **THEN** the node SHALL return `Command(update=..., goto=<stage>)`
- **AND** the revision count and reason SHALL be recorded

#### Scenario: Invalid route

- **WHEN** a command names an unknown stage
- **THEN** graph validation or execution SHALL fail
- **AND** no custom `CommandResult` adapter SHALL be involved

### Requirement: Durable asynchronous execution

Durable workflow execution SHALL use the asynchronous graph API and a live async checkpointer context.

#### Scenario: Durable run

- **WHEN** durable mode starts a workflow
- **THEN** the runner SHALL enter `AsyncPostgresSaver.from_conn_string()`
- **AND** it SHALL compile and execute the graph with a stable run-specific `thread_id` before leaving that context

#### Scenario: Restart resume

- **WHEN** a process restarts after a completed stage or pending interrupt
- **THEN** a new runner SHALL resume the same thread from its checkpoint
- **AND** completed side effects SHALL not repeat

#### Scenario: Non-durable run

- **WHEN** durable mode is disabled
- **THEN** the graph SHALL still execute through `ainvoke` or `astream`
- **AND** the result SHALL not claim restart durability

### Requirement: Public integration boundary

The harness SHALL use `agent_core.sdk` for TDT agent composition/policy and public upstream modules for concrete Pydantic AI, Harness, and LangGraph types.

#### Scenario: Agent construction

- **WHEN** a stage agent is created
- **THEN** it SHALL receive official capabilities and toolsets through the public agent-core SDK
- **AND** it SHALL not import `agent_core._ai` or inspect private framework attributes

#### Scenario: Workflow construction

- **WHEN** the workflow graph is created
- **THEN** it SHALL use public LangGraph `StateGraph`, `Command`, and `interrupt`
- **AND** it SHALL not depend on dict-only `WorkflowBuilder` semantics
