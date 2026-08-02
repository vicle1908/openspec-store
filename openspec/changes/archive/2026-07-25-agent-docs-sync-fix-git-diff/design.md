## Context

The `git_diff.py` tool uses an outdated pattern that doesn't follow agent-core standards. All other tools (8/9) use the correct BaseTool pattern.

## Current vs Required

```
┌─────────────────────────────────────────────────────────┐
│  CURRENT (Wrong)                                         │
└─────────────────────────────────────────────────────────┘

  class ToolMetadata:  # Custom, not agent-core's
      name: str
      description: str
      parameters: dict
      requires_approval: bool
      source: str

  class GitDiffTool:   # No BaseTool inheritance
      metadata = ToolMetadata(...)
      
      async def execute(self, base_ref, file_pattern, repo_root):
          return {...}  # Returns dict, not ToolResult


┌─────────────────────────────────────────────────────────┐
│  REQUIRED (Correct)                                      │
└─────────────────────────────────────────────────────────┘

  from agent_core.tool_registry import BaseTool, ToolMetadata, ToolResult

  class GitDiffArgs(BaseModel):
      base_ref: str = "HEAD~1"
      file_pattern: str = "*"
      repo_root: str = "."

  class GitDiffTool(BaseTool[GitDiffArgs]):
      args_schema = GitDiffArgs
      
      @property
      def metadata(self) -> ToolMetadata:
          return ToolMetadata(name="git_diff", ...)
      
      async def execute(self, args: GitDiffArgs) -> ToolResult:
          # implementation
          return ToolResult(success=True, output=...)
```

## Design Decisions

### Decision 1: Use BaseTool pattern

Follow the same pattern as all other tools in agent-docs-sync.

### Decision 2: Use agent-core ToolMetadata

Use `agent_core.tool_registry.ToolMetadata` instead of custom class.

### Decision 3: Return ToolResult

All tools must return `ToolResult` for consistency with agent-core's tool collection bridge.

## Testing Strategy

| Test Type | Scope |
|-----------|-------|
| Unit | GitDiffTool with new interface |
| Integration | ToolRegistry registration |
| E2E | CLI check command |
