# Stage Module Protocol Specification

## Purpose

Define consumer-local stage contracts and whole-graph topology validation.

## Requirements

### Requirement: Consumer-local stage definition

`agent-harness` SHALL define a structural stage contract containing the stage identity, native node callable, typed read/write sets, reducers for concurrent writes, validators, typed official toolsets/capabilities, and optional gate policy.

#### Scenario: Valid stage

- **WHEN** a stage definition is registered at the harness composition root
- **THEN** its node, reads, writes, reducers, validators, toolsets, capabilities, and gate policy SHALL be type-checked
- **AND** it SHALL not require inheritance from a harness or core base class

#### Scenario: String capability or tool name

- **WHEN** a stage supplies an unresolved string as a tool or capability
- **THEN** construction SHALL fail with the stage and field name

### Requirement: Stage contract excludes topology

Graph dependencies, reachability, cycles, and parallelism SHALL be declared by one immutable consumer-local topology plan at the composition root, not by `depends_on` or `parallel` fields on a stage. That plan SHALL contain native node identifiers and SHALL be the single source for both validation and subsequent native `StateGraph` edge/branch wiring. Before graph compilation, the composition root SHALL validate the plan against registered stage read/write sets, reducers, gates, and retry policies without inspecting private LangGraph builder state.

#### Scenario: Independent stages

- **WHEN** two stages are candidates for parallel execution
- **THEN** their read/write sets and reducers SHALL be validated
- **AND** the composition root SHALL add explicit native fan-out/fan-in edges from the same validated topology plan

#### Scenario: Validation and wiring agreement

- **WHEN** graph construction succeeds
- **THEN** every native edge and branch wired into `StateGraph` SHALL come from the validated topology plan
- **AND** a second independently maintained edge list or private builder inspection SHALL NOT be used

#### Scenario: Concurrent scalar writer

- **WHEN** parallel branches can write the same scalar field without an explicit deterministic reducer
- **THEN** graph construction SHALL fail with the branch and field names

#### Scenario: Invalid native edge

- **WHEN** an edge, gate continuation, backtrack target, fan-out, or fan-in references an unregistered stage or unavailable input
- **THEN** graph construction SHALL fail before execution with the invalid endpoint and reason

#### Scenario: Unreachable or unintended terminal stage

- **WHEN** a registered stage is unreachable from the declared entry or a non-terminal path cannot reach an allowed terminal node
- **THEN** graph construction SHALL fail unless that exclusion or terminal behavior is explicitly declared

#### Scenario: Workflow cycle

- **WHEN** native edges form a cycle
- **THEN** graph construction SHALL require an explicit bounded retry or revision policy for that cycle
- **AND** an undeclared or unbounded cycle SHALL be rejected

### Requirement: Inline stage validation

The stage wrapper SHALL validate an artifact immediately after its node returns and before downstream stages consume the update.

#### Scenario: Validation passes

- **WHEN** every validator passes
- **THEN** the state update SHALL be committed and routing SHALL continue

#### Scenario: Validation fails

- **WHEN** a validator fails
- **THEN** the stage SHALL record the bounded error and revision outcome
- **AND** routing SHALL follow the declared retry, block, or human-review policy
