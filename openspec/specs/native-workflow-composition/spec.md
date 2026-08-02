# Native Workflow Composition Specification

## Purpose

Define direct LangGraph composition and the safety conditions for native workflow topology.

## Requirements

### Requirement: Native graph composition

The harness composition root SHALL build its workflow with native LangGraph `StateGraph`, node, edge, `Command`, interrupt, and checkpointer APIs.

#### Scenario: Build graph

- **WHEN** the harness graph is built
- **THEN** every registered stage SHALL map to an explicit native node
- **AND** every dependency SHALL be inspectable as a native edge

#### Scenario: Invalid topology

- **WHEN** the graph has no entry, has an invalid target, or can reach an unrelated stage from a gate
- **THEN** construction or a topology contract test SHALL fail before production execution

### Requirement: Safe native parallelism

Parallel edges SHALL be added only after read/write, reducer, authority, budget, and fan-in behavior are proven safe.

#### Scenario: Unsafe branch

- **WHEN** candidate branches write the same unreduced field or have order-dependent side effects
- **THEN** the workflow SHALL keep them sequential

#### Scenario: Safe branch

- **WHEN** branch safety is proven
- **THEN** the native graph MAY fan out and fan in
- **AND** an execution-trace test SHALL assert both branch and convergence behavior

### Requirement: No workflow DSL

The change SHALL NOT add a registry-backed `WorkflowComposer` abstraction over LangGraph.

#### Scenario: Stage added

- **WHEN** a new harness stage is introduced
- **THEN** its node and topology SHALL be added to the consumer-owned graph composition root
