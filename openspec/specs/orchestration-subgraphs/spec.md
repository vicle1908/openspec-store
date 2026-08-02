# Orchestration — Subgraphs

## Purpose

Nested graph composition for reusable workflow components via LangGraph subgraph patterns.

## Requirements

### Requirement: Subgraph node kind

`NodeKind` SHALL include a `SUBGRAPH` value for classifying workflow nodes that contain nested graphs.

#### Scenario: SUBGRAPH kind is available
- **WHEN** `NodeKind` is imported from `agent_core.orchestration.types`
- **THEN** `NodeKind.SUBGRAPH` SHALL be a valid enum value with string value `"subgraph"`

### Requirement: StateMapping dataclass

The system SHALL provide a `StateMapping` dataclass in `agent_core/orchestration/types.py` with:
- `input: dict[str, str]` — maps parent state keys to child subgraph state keys
- `output: dict[str, str]` — maps child subgraph state keys back to parent state keys

#### Scenario: StateMapping construction
- **WHEN** `StateMapping(input={"context": "data"}, output={"result": "results"})` is created
- **THEN** `mapping.input` SHALL be `{"context": "data"}`
- **AND** `mapping.output` SHALL be `{"result": "results"}`

### Requirement: NodeDescriptor subgraph fields

`NodeDescriptor` SHALL have two optional fields:
- `subgraph_engine: WorkflowEngine | None` — the compiled subgraph to embed
- `state_mapping: StateMapping | None` — how to translate state between parent and child

#### Scenario: Subgraph node creation
- **WHEN** a `NodeDescriptor` is created with `kind=NodeKind.SUBGRAPH`
- **THEN** `subgraph_engine` MUST be provided (validated at build time)
- **AND** `state_mapping` SHOULD be provided when state schemas differ (validated at build time)

### Requirement: WorkflowBuilder subgraph registration

`WorkflowBuilder.add_node()` SHALL accept a `NodeDescriptor` with `kind=NodeKind.SUBGRAPH` and validate that `subgraph_engine` is provided.

#### Scenario: Valid subgraph registration
- **WHEN** `builder.add_node(NodeDescriptor(name="review", kind=NodeKind.SUBGRAPH, subgraph_engine=review_engine, state_mapping=StateMapping(...)))` is called
- **THEN** the node SHALL be registered without error

#### Scenario: Missing subgraph_engine raises error
- **WHEN** `builder.add_node(NodeDescriptor(name="review", kind=NodeKind.SUBGRAPH))` is called without `subgraph_engine`
- **THEN** a `ValueError` SHALL be raised at `build()` time

### Requirement: Subgraph state translation (different schemas)

When parent and subgraph have different state schemas, the engine SHALL use `StateMapping` to translate between them. This follows the official LangGraph "Call a subgraph inside a node" pattern.

#### Scenario: Subgraph execution with state mapping
- **WHEN** a subgraph node with `state_mapping=StateMapping(input={"context": "data"}, output={"result": "results"})` executes
- **AND** parent state has `{"context": {"key": "value"}, "results": {}}`
- **THEN** the subgraph SHALL receive `{"data": {"key": "value"}}`
- **AND** the subgraph's output `{"result": "processed"}` SHALL be mapped to parent `{"results": "processed"}`

#### Scenario: Subgraph error propagation
- **WHEN** the subgraph raises an exception during execution
- **THEN** the workflow's `error` state field SHALL be set to the error message
- **AND** `completed` SHALL be set to `False`

### Requirement: Subgraph shared state (same schemas)

When parent and subgraph share state keys, the engine SHALL pass the compiled subgraph directly to LangGraph's `StateGraph.add_node()` without a wrapper. This follows the official LangGraph "Add a subgraph as a node" pattern.

#### Scenario: Shared state subgraph
- **WHEN** a subgraph node is created WITHOUT `state_mapping` (state_mapping=None)
- **AND** the parent and subgraph share the same state schema
- **THEN** the compiled subgraph SHALL be passed directly to `StateGraph.add_node()`
- **AND** the subgraph SHALL read from and write to the same state channels as the parent

### Requirement: Backward compatibility

Existing flat graphs with `NodeKind.AGENT`, `NodeKind.TOOL`, etc. and `dict`-returning handlers SHALL continue to work without modification.

#### Scenario: Existing graph still compiles
- **WHEN** a `WorkflowBuilder` with only non-SUBGRAPH nodes is built
- **THEN** the resulting `WorkflowEngine` SHALL compile and execute identically to the current implementation
