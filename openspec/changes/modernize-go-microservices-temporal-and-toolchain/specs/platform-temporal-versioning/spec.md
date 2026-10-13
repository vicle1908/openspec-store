## MODIFIED Requirements

### Requirement: Saga compensation order

A saga-style workflow SHALL execute activities in forward order and SHALL execute compensations in INVERSE order on non-retryable failure; the platform's `platformtemporal.NewSaga` helper SHALL enforce this invariant across all service saga implementations. Services MUST NOT maintain ad-hoc slice-based compensation tracking closures.

#### Scenario: Saga compensation enforces inverse-order execution

This scenario is exercised by the cross-service smoke test (`tests/cross-service-smoke/`).

#### Scenario: Platform saga executes compensations in inverse order on terminal failure
- **WHEN** a forward activity in a saga workflow fails with a non-retryable compensation error
- **THEN** `platformtemporal.Saga` executes registered compensations in strict reverse order of completed forward activities

## ADDED Requirements

### Requirement: Strongly consistent Workflow Update handlers

The platform SHALL support and standardize Temporal Workflow Update handlers via `workflow.SetUpdateHandler` for synchronous, strongly-consistent workflow mutations. Workflows exposing interactive mutations MUST validate and apply state changes synchronously within the update handler rather than relying on decoupled asynchronous Signal and Query polling loops.

#### Scenario: Synchronous workflow state update succeeds
- **WHEN** a client submits a valid Workflow Update request to a running workflow
- **THEN** the update validator accepts the request, the handler mutates workflow state synchronously, and the client receives the updated state directly

#### Scenario: Synchronous workflow state update rejected on terminal status
- **WHEN** a client submits a Workflow Update request to a workflow that has already transitioned to a terminal or non-modifiable status
- **THEN** the update handler rejects the update with a non-retryable application error and leaves the workflow state unchanged
