## ADDED Requirements

### Requirement: CommandResult dataclass

The system SHALL provide a `CommandResult` dataclass in `agent_core/orchestration/types.py` with:
- `goto: str` — name of the target node to route to
- `update: dict[str, Any] | None` — optional state update to apply before routing

#### Scenario: CommandResult construction
- **WHEN** `CommandResult(goto="error_handler", update={"error": "failed"})` is created
- **THEN** `result.goto` SHALL be `"error_handler"`
- **AND** `result.update` SHALL be `{"error": "failed"}`

#### Scenario: CommandResult without update
- **WHEN** `CommandResult(goto="next_step")` is created
- **THEN** `result.update` SHALL be `None`

### Requirement: NodeHandler type broadening

`NodeHandler` type alias SHALL be updated to `Callable[[WorkflowState], dict[str, Any] | CommandResult]`.

#### Scenario: Handler returns dict
- **WHEN** a handler returns `{"results": {"key": "value"}}`
- **THEN** the engine SHALL treat it as a state update (current behavior, unchanged)

#### Scenario: Handler returns CommandResult
- **WHEN** a handler returns `CommandResult(goto="target_node")`
- **THEN** the engine SHALL route execution to `target_node`

### Requirement: Handler wrapping in WorkflowEngine

`WorkflowEngine._compile()` SHALL wrap each node handler to detect `CommandResult` returns and translate them to LangGraph `Command(goto=..., update=...)`.

#### Scenario: Dynamic routing via CommandResult
- **WHEN** a node handler returns `CommandResult(goto="branch_b", update={"value": 42})`
- **THEN** the engine SHALL invoke `Command(goto="branch_b", update={"value": 42})`
- **AND** LangGraph SHALL route to the `branch_b` node with the state update applied

#### Scenario: State update without routing
- **WHEN** a handler returns `CommandResult(goto="same_node", update={"counter": 1})`
- **THEN** the engine SHALL route back to the same node with the update applied

### Requirement: Compile-time validation

The engine SHALL validate that all `CommandResult.goto` targets reference nodes registered in the graph.

#### Scenario: Invalid goto target
- **WHEN** a handler returns `CommandResult(goto="nonexistent_node")`
- **THEN** LangGraph SHALL raise an error at runtime when the route is taken

### Requirement: Backward compatibility

Handlers returning `dict[str, Any]` SHALL continue to work without modification.

#### Scenario: Existing dict handler
- **WHEN** a handler returns `{"results": {"key": "value"}}`
- **THEN** the engine SHALL process it as a state update (no Command created)
