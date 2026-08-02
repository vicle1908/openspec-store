## Why

agent-docs-sync currently uses custom tool implementations that don't follow agent-core standards:

1. **Missing BaseTool interface** — Tools don't inherit from `BaseTool[Args]`
2. **Missing args_schema** — No Pydantic BaseModel for argument validation
3. **Custom ToolMetadata** — Using dataclass instead of agent-core's `ToolMetadata`
4. **Wrong return type** — Returning `dict` instead of `ToolResult`
5. **No skills** — Missing domain knowledge for doc sync operations

These issues prevent proper integration with agent-core's tool collection bridge and pydantic-ai's agent system.

## What Changes

- **Refactor tools** to implement `BaseTool[Args]` interface
- **Add Pydantic args_schema** for each tool
- **Use agent-core ToolMetadata** with proper fields
- **Return ToolResult** from all tool executions
- **Add doc-sync skill** for domain knowledge
- **Integrate pydantic-ai-harness capabilities** (compaction, guardrails)

## Capabilities

### Modified Capabilities

- `agent-docs-sync`: Refactor tools to follow agent-core standards

## Impact

- **Code changes:** `agent-docs-sync/src/agent_docs_sync/tools/*.py`
- **New files:** `agent-docs-sync/src/agent_docs_sync/skills/`
- **Dependencies:** pydantic-ai-harness (already in agent-core)
- **Breaking changes:** None — internal refactoring
