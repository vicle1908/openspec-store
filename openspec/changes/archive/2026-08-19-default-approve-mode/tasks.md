## 1. Configuration Layer

- [x] 1.1 Add `auto_approve_tools: tuple[str, ...] = ()` field to `DocsSyncConfig` in `agent-docs-sync/config.py`
- [x] 1.2 Add `auto_approve_tools` to `config.yaml` with default value `[]` (empty, secure by default)
- [x] 1.3 Add unit tests for config parsing of `auto_approve_tools`

## 2. Agent Construction Chain

- [x] 2.1 Add `auto_approve_tools: tuple[str, ...] = ()` parameter to `build_generation_agent()` in `agent-docs-sync/agents/generation.py`
- [x] 2.2 Pass `auto_approve_tools` from config to `build_generation_agent()` call
- [x] 2.3 Add `auto_approve_tools: tuple[str, ...] = ()` parameter to `build_doc_sync_agent()` in `agent-docs-sync/agent.py`
- [x] 2.4 Pass `auto_approve_tools` through to `build_agent()` call
- [x] 2.5 Add `auto_approve_tools: tuple[str, ...] = ()` parameter to `build_agent()` in `agent-core/sdk/agents.py`
- [x] 2.6 Pass `auto_approve_tools` to `AgentRuntime` constructor

## 3. Agent Runtime

- [x] 3.1 Add `auto_approve_tools: tuple[str, ...] = ()` parameter to `AgentRuntime.__init__()` in `agent-core/_ai/agent.py`
- [x] 3.2 Add `auto_approve_tools` as first-class field in `AgentRuntimeDeps` (type safety)
- [x] 3.3 Add unit tests for AgentRuntime with auto_approve_tools

## 4. Tool Execution

- [x] 4.1 In `agent-core/_ai/tools.py`, retrieve `auto_approve_tools` from `ctx.deps.auto_approve_tools` (first-class field)
- [x] 4.2 Check if `tool_name in auto_approve_tools` before raising `ApprovalRequired`
- [x] 4.3 Add unit tests for tool execution with auto-approval

## 5. Integration Testing

- [x] 5.1 Run existing test suite to verify no regressions
- [x] 5.2 Run `uv run docs-sync sync --full` with `auto_approve_tools: [write_doc]`
- [x] 5.3 Verify files are written to `docs/`
- [x] 5.4 Verify audit trail in `writes.sqlite3` and `lifecycle.sqlite3`
- [x] 5.5 Verify security constraints (scope, limits) still enforced

## 6. Documentation

- [x] 6.1 Update `config.yaml` comments to document `auto_approve_tools`
- [x] 6.2 Add security warning in config about auto-approval implications
