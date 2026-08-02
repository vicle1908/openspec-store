# State Composition Specification

## Purpose

Define the static checkpoint state, semantic reducers, and compatibility rules for workflow state.

## Requirements

### Requirement: Static typed workflow state

`agent-harness` SHALL declare its checkpointed workflow state statically in source and SHALL NOT generate or merge `TypedDict` classes at runtime.

#### Scenario: Stage extraction

- **WHEN** a stage is moved into its own module
- **THEN** the workflow SHALL continue to use the declared harness state schema
- **AND** the stage SHALL return a typed partial update or native `Command`

### Requirement: Semantic reducers

Every field written by multiple nodes in one superstep SHALL either declare a deterministic, domain-correct reducer or cause graph construction/runtime validation to fail before committing an ambiguous update. Scalar lifecycle fields with no order-independent merge meaning SHALL remain unreduced and SHALL have at most one writer per superstep.

#### Scenario: String collection

- **WHEN** repositories, errors, or gate-history identifiers are accumulated
- **THEN** a string-list or string-set reducer SHALL be used
- **AND** a message reducer SHALL NOT be used

#### Scenario: Sequential Command routing

- **WHEN** a node returns `Command(update=..., goto=...)`
- **THEN** the target SHALL execute in a following graph step and observe the source update
- **AND** source and target writes SHALL NOT require a reducer merely because `goto` was used

#### Scenario: Conflicting scalar writers

- **WHEN** native parallel branches can write `current_stage`, `status`, or another scalar without a proven order-independent merge meaning in one superstep
- **THEN** graph construction SHALL fail with the branch and field names
- **AND** a latest-write-wins reducer SHALL NOT be added solely to suppress the conflict

### Requirement: Checkpoint schema compatibility

Checkpoint state or channel-semantic changes SHALL be versioned and tested against pending-gate and completed-run fixtures. Reverting an unshipped semantic edit to the already-supported schema MAY retain the current version only when fixtures prove the persisted contract is unchanged.

#### Scenario: Incompatible checkpoint

- **WHEN** a runner encounters a checkpoint version it cannot read
- **THEN** it SHALL fail before executing or writing a stage
- **AND** it SHALL preserve the existing checkpoint

#### Scenario: Reducer metadata changes

- **WHEN** reducer metadata for a checkpointed field changes the merge behavior retained by the implementation
- **THEN** the checkpoint schema version SHALL advance with an explicit compatibility policy
- **AND** pending-gate and completed-run fixtures SHALL pass before the new schema writes checkpoints
