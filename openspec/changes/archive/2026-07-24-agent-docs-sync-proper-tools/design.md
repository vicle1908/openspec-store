## Context

agent-docs-sync has 6 tools that don't follow agent-core standards. The tools use custom `ToolMetadata` dataclasses instead of agent-core's `ToolMetadata`, don't implement `BaseTool[Args]`, and return `dict` instead of `ToolResult`.

## Goals / Non-Goals

**Goals:**
- Refactor all tools to implement `BaseTool[Args]` interface
- Add Pydantic `args_schema` for argument validation
- Use agent-core's `ToolMetadata` and `ToolResult`
- Add doc-sync skill for domain knowledge
- Integrate pydantic-ai-harness capabilities

**Non-Goals:**
- Changing tool functionality (only refactoring interface)
- Adding new tools (existing 6 are sufficient)
- Modifying agent-core (use as-is)

## Decisions

### Decision 1: BaseTool Pattern (from agent-core)

```python
from pydantic import BaseModel, Field
from agent_core.tool_registry import BaseTool, ToolMetadata, ToolResult

class ReadDocArgs(BaseModel):
    path: str = Field(description="Path to markdown file")
    section: str | None = Field(default=None, description="Section header")

class ReadDocTool(BaseTool[ReadDocArgs]):
    args_schema = ReadDocArgs
    
    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="read_doc",
            description="Read markdown documentation",
            source="local",
        )
    
    async def execute(self, args: ReadDocArgs) -> ToolResult:
        # Implementation
        return ToolResult(success=True, output=content)
```

### Decision 2: Hybrid Tool Strategy

```
Custom Tools (BaseTool pattern):
├─ ReadDocTool — Parse markdown, extract sections
├─ WriteDocTool — Update docs (requires_approval=True)
├─ CheckLinksTool — Validate links
├─ ParseSourceTool — Extract API from Python
└─ SyncSpecTool — Merge delta specs

Built-in Tools (from agent-core):
├─ read_file — General file reading
├─ write_file — General file writing
├─ shell_execute — Command execution
└─ git_diff — Git operations
```

### Decision 3: Add doc-sync Skill

```yaml
# .agents/skills/doc-sync/SKILL.md
name: doc-sync
description: Documentation synchronization for TDT repos
allowed_tools:
  - read_doc
  - write_doc
  - check_links
  - parse_source
  - sync_spec
  - read_file
  - write_file
  - git_diff
```

### Decision 4: Integrate pydantic-ai-harness

Use harness capabilities for:
- `ContextCompaction` — Handle large doc contexts
- `Guardrails` — Validate doc outputs
- `Budget` — Track LLM costs

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Tool Implementation Pattern                             │
└─────────────────────────────────────────────────────────┘

  Pydantic BaseModel (args_schema)
         │
         ▼
  BaseTool[Args] subclass
         │
         ├─ metadata: ToolMetadata (agent-core)
         ├─ execute(args) -> ToolResult
         │
         ▼
  ToolRegistry.register()
         │
         ▼
  tool_collection.py bridge
         │
         ▼
  pydantic-ai Agent(tools=...)
```

## File Structure

```
agent-docs-sync/
├── src/agent_docs_sync/
│   ├── tools/
│   │   ├── read_doc.py        # BaseTool[ReadDocArgs]
│   │   ├── write_doc.py       # BaseTool[WriteDocArgs]
│   │   ├── check_links.py     # BaseTool[CheckLinksArgs]
│   │   ├── parse_source.py    # BaseTool[ParseSourceArgs]
│   │   └── sync_spec.py       # BaseTool[SyncSpecArgs]
│   └── skills/
│       └── doc-sync/
│           └── SKILL.md       # Domain knowledge
```

## Testing Strategy

| Test Type | Scope |
|-----------|-------|
| Unit | Each tool's execute() method |
| Integration | ToolRegistry registration |
| E2E | Agent with tools |
