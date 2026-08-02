## ADDED Requirements

### Requirement: MemoryCapability class
A `MemoryCapability` SHALL be implemented as a pydantic-ai `AbstractCapability` subclass.

#### Scenario: Capability contributes memory tools
- **WHEN** `MemoryCapability.get_native_tools()` is called
- **THEN** it SHALL return native tools: `memory_store`, `memory_retrieve`, `memory_recall`, `memory_list_keys`
- **AND** each tool SHALL delegate to the `Memory` facade methods
- **AND** each tool SHALL receive `session` from `ctx.deps.extra.get("run_id")` or `ctx.deps.correlation_id`

#### Scenario: Capability injects context instructions
- **WHEN** `MemoryCapability.get_instructions()` is called
- **THEN** it SHALL call `ContextMemory.get_context_for_llm(session)` for the current session
- **AND** return formatted context as a system prompt addition

#### Scenario: Capability captures conversation
- **WHEN** the agent run completes
- **THEN** `MemoryCapability.after_run()` SHALL capture the conversation history into `ContextMemory` for the session

### Requirement: Memory wired via harness config
Memory integration SHALL be configurable via the harness config dictionary.

#### Scenario: Memory enabled
- **WHEN** `harness_config` contains `"memory": {"enabled": true}`
- **THEN** `MemoryCapability` SHALL be added to the capabilities list
- **AND** the `Memory` facade SHALL be constructed with `ContextMemory()` (in-process, max 50 messages) and `ScratchMemory(scratch_dir=...)` (filesystem-backed)
- **AND** optional backends (PostgresMemory, FeedbackStore) SHALL be configured from additional config keys

#### Scenario: Memory disabled by default
- **WHEN** `harness_config` does not contain a `"memory"` key
- **THEN** `MemoryCapability` SHALL NOT be added
- **AND** agent behavior SHALL be unchanged

### Requirement: BaseAgent accepts optional memory
`BaseAgent` SHALL accept an optional `memory` parameter.

#### Scenario: Memory passed to AgentRuntime
- **WHEN** `BaseAgent(gateway=..., memory=Memory(...))` is constructed
- **THEN** the `Memory` instance SHALL be passed to `AgentRuntime` via harness config

#### Scenario: No memory parameter
- **WHEN** `BaseAgent(gateway=...)` is constructed without memory
- **THEN** agent behavior SHALL be unchanged (no memory integration)
