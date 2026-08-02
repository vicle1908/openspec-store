## ADDED Requirements

### Requirement: Typed workflow state schema
The system SHALL define `WorkflowState` as a `TypedDict` with `Annotated` reducer functions for list fields, replacing the current dataclass.

#### Scenario: State schema is TypedDict
- **WHEN** `WorkflowState` is imported from `agent_core.orchestration.types`
- **THEN** it SHALL be a `TypedDict` with fields: `messages` (list), `context` (dict), `results` (dict), `current_node` (str), `iteration` (int), `error` (str | None), `completed` (bool)

#### Scenario: List fields use Annotated reducers
- **WHEN** a node handler returns `{"messages": ["new_msg"]}`
- **THEN** `messages` SHALL be appended to the existing list via `operator.add` reducer (not replaced)

#### Scenario: Dict fields use last-write-wins
- **WHEN** a node handler returns `{"context": {"key": "value"}}`
- **THEN** `context` SHALL be replaced entirely (no merge — LangGraph default behavior for non-reduced fields)

### Requirement: Mypy strict compatibility
The system SHALL pass `mypy agent_core/orchestration/ --strict` with no errors after the typed state migration.

#### Scenario: Type checking passes
- **WHEN** `mypy agent_core/orchestration/ --strict` is run
- **THEN** zero type errors SHALL be reported

### Requirement: Backward-compatible node handlers
All existing node handler functions SHALL accept `WorkflowState` (TypedDict) and return `dict[str, Any]` partial updates.

#### Scenario: Handler receives typed state
- **WHEN** a node handler is invoked by the workflow engine
- **THEN** the `state` parameter SHALL be typed as `WorkflowState`

#### Scenario: Handler returns partial update
- **WHEN** a node handler returns `{"current_node": "step2"}`
- **THEN** the engine SHALL merge the update into the current state using reducer functions

### Requirement: Checkpoint compatibility
Existing Postgres checkpoints SHALL be resumable after the typed state migration.

#### Scenario: Resume old checkpoint
- **WHEN** a workflow is resumed from a checkpoint created before the migration
- **THEN** the state SHALL be reconstructed correctly and execution SHALL continue
- **NOTE:** PostgresSaver handles any dict-like state; old checkpoints deserialize as dicts and are wrapped into TypedDict on resume

### Requirement: LangGraph StateGraph uses typed schema
The `WorkflowBuilder._compile()` method SHALL pass `state_schema=WorkflowState` to `StateGraph()`.

#### Scenario: Graph compilation uses typed schema
- **WHEN** `WorkflowBuilder.build()` is called
- **THEN** the resulting `StateGraph` SHALL be parameterized with `WorkflowState` as its state schema

#### Scenario: Input/output schema separation (optional)
- **WHEN** `WorkflowBuilder` is extended to support separate input/output schemas
- **THEN** it SHALL use `StateGraph(OverallState, input_schema=InputState, output_schema=OutputState)` pattern

### Requirement: No Pydantic BaseModel for state
The system SHALL use `TypedDict` (not Pydantic BaseModel) for `WorkflowState` to avoid performance overhead.

#### Scenario: Performance choice
- **WHEN** `WorkflowState` is defined
- **THEN** it SHALL be a `TypedDict` with `Annotated` reducers, NOT a Pydantic BaseModel
- **NOTE:** LangGraph docs state "Pydantic is less performant than a TypedDict or dataclass" for state schemas
