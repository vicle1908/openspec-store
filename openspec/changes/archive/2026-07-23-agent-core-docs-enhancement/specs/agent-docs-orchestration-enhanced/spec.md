## ADDED Requirements

### Requirement: Subgraph documentation

`orchestration.md` SHALL document subgraph composition with both shared-state and wrapper patterns.

#### Scenario: Shared-state subgraph
- **WHEN** a developer reads `orchestration.md`
- **THEN** it SHALL show how to create a subgraph with `NodeDescriptor(kind=NodeKind.SUBGRAPH, subgraph_engine=engine)` and no `state_mapping`

#### Scenario: Wrapper subgraph with state mapping
- **WHEN** a developer reads `orchestration.md`
- **THEN** it SHALL show `StateMapping(input={...}, output={...})` for translating state between parent and child

#### Scenario: Subgraph validation
- **WHEN** a developer creates a SUBGRAPH node without `subgraph_engine`
- **THEN** the docs SHALL explain that `ValueError` is raised at `build()` time

### Requirement: Command API documentation

`orchestration.md` SHALL document the Command API for dynamic in-node routing.

#### Scenario: CommandResult usage
- **WHEN** a developer reads `orchestration.md`
- **THEN** it SHALL show `CommandResult(goto="target_node", update={...})` for dynamic routing

#### Scenario: CommandResult without update
- **WHEN** a developer reads `orchestration.md`
- **THEN** it SHALL show `CommandResult(goto="next_step")` for routing without state update

#### Scenario: Backward compatibility note
- **WHEN** a developer reads the Command API section
- **THEN** it SHALL note that dict-returning handlers continue to work unchanged

### Requirement: Per-node features documentation

`orchestration.md` SHALL document per-node retry, cache, error_handler, metadata, and timeout.

#### Scenario: Per-node retry_policy
- **WHEN** a developer reads `orchestration.md`
- **THEN** it SHALL show `NodeDescriptor(retry_policy=RetryPolicy(...))` usage

#### Scenario: Per-node timeout validation
- **WHEN** a developer reads `orchestration.md`
- **THEN** it SHALL note that timeout requires async handlers (sync raises `ValueError`)

#### Scenario: Per-node metadata and error_handler
- **WHEN** a developer reads `orchestration.md`
- **THEN** it SHALL show `metadata={...}` and `error_handler=callable` usage

### Requirement: Streaming docs match implementation

`streaming.md` SHALL document the actual `run_stream()` async generator API.

#### Scenario: run_stream yields StreamChunk
- **WHEN** a developer reads `streaming.md`
- **THEN** it SHALL show `async for chunk in runtime.run_stream(...)` with `StreamChunk(text=..., output=..., done=True)`

#### Scenario: StreamChunk type documented
- **WHEN** a developer reads `streaming.md`
- **THEN** it SHALL document `StreamChunk` fields: `text`, `output`, `tool_call`, `done`

#### Scenario: Approval gate in streaming
- **WHEN** a developer reads `streaming.md`
- **THEN** it SHALL show how approval requests appear as `StreamChunk(tool_call={...})`
