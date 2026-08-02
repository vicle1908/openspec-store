## Why

The `git_diff.py` tool in agent-docs-sync uses an outdated pattern that doesn't follow agent-core standards:

1. **Custom ToolMetadata** — Uses a custom `ToolMetadata` class instead of agent-core's
2. **No BaseTool inheritance** — Doesn't inherit from `BaseTool[Args]`
3. **No ToolResult return** — Returns `dict` instead of `ToolResult`
4. **Old execute() signature** — Uses `execute(self, base_ref, ...)` instead of `execute(self, args: GitDiffArgs)`

This causes:
- Inconsistency with other tools (8/9 tools use correct pattern)
- Potential issues with tool registration in ToolRegistry
- Not compatible with agent-core's tool collection bridge

## What Changes

- **Refactor git_diff.py** to follow agent-core BaseTool pattern
- **Use agent-core ToolMetadata** instead of custom class
- **Inherit from BaseTool[GitDiffArgs]**
- **Return ToolResult** instead of dict
- **Update execute() signature** to use args-based approach

## Impact

- **Code changes:** `tools/git_diff.py`
- **No new dependencies** — Uses existing agent-core
- **Breaking changes:** None — internal refactoring
