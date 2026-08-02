## 1. Tool Refactoring

- [x] 1.1 Create ReadDocArgs Pydantic BaseModel
- [x] 1.2 Refactor ReadDocTool to implement BaseTool[ReadDocArgs]
- [x] 1.3 Create WriteDocArgs Pydantic BaseModel
- [x] 1.4 Refactor WriteDocTool to implement BaseTool[WriteDocArgs]
- [x] 1.5 Create CheckLinksArgs Pydantic BaseModel
- [x] 1.6 Refactor CheckLinksTool to implement BaseTool[CheckLinksArgs]
- [x] 1.7 Create ParseSourceArgs Pydantic BaseModel
- [x] 1.8 Refactor ParseSourceTool to implement BaseTool[ParseSourceArgs]
- [x] 1.9 Create SyncSpecArgs Pydantic BaseModel
- [x] 1.10 Refactor SyncSpecTool to implement BaseTool[SyncSpecArgs]

## 2. Tool Registration

- [x] 2.1 Update tools/__init__.py to export BaseTool subclasses
- [x] 2.2 Verify ToolRegistry.register() works with all tools
- [x] 2.3 Test tool_collection.py bridge generates correct adapters

## 3. Skill Implementation

- [x] 3.1 Create .agents/skills/doc-sync/ directory
- [x] 3.2 Create SKILL.md with domain knowledge
- [x] 3.3 Define allowed_tools in skill
- [x] 3.4 Test skill matching with doc sync tasks

## 4. Harness Integration

- [x] 4.1 Add pydantic-ai-harness dependency
- [x] 4.2 Configure ContextCompaction for large docs
- [x] 4.3 Add Guardrails for doc output validation
- [x] 4.4 Test harness capabilities

## 5. Unit Testing

- [x] 5.1 Unit tests for ReadDocTool.execute()
- [x] 5.2 Unit tests for WriteDocTool.execute()
- [x] 5.3 Unit tests for CheckLinksTool.execute()
- [x] 5.4 Unit tests for ParseSourceTool.execute()
- [x] 5.5 Unit tests for SyncSpecTool.execute()
- [x] 5.6 Test ToolResult contract (success/failure cases)

## 6. Integration Testing

- [x] 6.1 Test ToolRegistry.register() with all tools
- [x] 6.2 Test tool_collection.py generates correct adapters
- [x] 6.3 Test BaseAgent with registered tools
- [x] 6.4 Test tool execution through agent

## 7. Real Agent Verification

- [x] 7.1 Create test script that triggers agent with read_doc tool
- [x] 7.2 Verify agent can read markdown files using ReadDocTool
- [x] 7.3 Create test script that triggers agent with check_links tool
- [x] 7.4 Verify agent can validate links using CheckLinksTool
- [x] 7.5 Create test script that triggers agent with parse_source tool
- [x] 7.6 Verify agent can parse Python files using ParseSourceTool
- [x] 7.7 Test agent with multiple tools in single run
- [x] 7.8 Verify ToolResult flows correctly through agent loop
- [x] 7.9 Test approval flow for WriteDocTool (requires_approval=True)
- [x] 7.10 Verify skill matching activates doc-sync skill

## 8. E2E Verification

- [x] 8.1 Run `docs-sync check` with refactored tools
- [x] 8.2 Run `docs-sync validate` with refactored tools
- [x] 8.3 Run `docs-sync sync` with agent and tools
- [x] 8.4 Verify all CLI commands work with new tool interface
- [x] 8.5 Performance test: parallel validation with new tools
