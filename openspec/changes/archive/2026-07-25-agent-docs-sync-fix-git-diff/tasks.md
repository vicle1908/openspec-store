## 1. Refactor GitDiffTool

- [x] 1.1 Create GitDiffArgs Pydantic BaseModel
- [x] 1.2 Import BaseTool, ToolMetadata, ToolResult from agent-core
- [x] 1.3 Refactor GitDiffTool to inherit from BaseTool[GitDiffArgs]
- [x] 1.4 Add args_schema class attribute
- [x] 1.5 Add metadata property returning ToolMetadata
- [x] 1.6 Update execute() to use args-based signature
- [x] 1.7 Return ToolResult instead of dict
