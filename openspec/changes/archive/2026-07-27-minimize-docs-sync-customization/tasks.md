## 1. agent-core: Extend build_agent() with flavors parameter

- [x] 1.1 Add `flavors: list[Flavor] | None = None` parameter to `build_agent()` in `agent-core/src/agent_core/sdk/agents.py`
- [x] 1.2 Make `config` parameter optional (default None), add ValueError when both config and flavors are None
- [x] 1.3 When `flavors` is provided, use it instead of creating Flavor from config
- [x] 1.4 Add `flavors` to `__all__` export list in `agent-core/src/agent_core/sdk/__init__.py`
- [x] 1.5 Add test for `build_agent` with pre-built flavors in `agent-core/tests/sdk/test_agents.py`
- [x] 1.6 Add test for `build_agent` with both config and flavors (flavors take precedence)
- [x] 1.7 Add test for `build_agent` with neither config nor flavors (raises ValueError)
- [x] 1.8 Run `uv run pytest tests/sdk/ -x` to verify

## 2. agent-docs-sync: Fix non-SDK imports (9 occurrences)

- [x] 2.1 Fix `agent.py`: Change `from agent_core.agent_base.hooks import HookPhase, HookPoint` to `from agent_core.sdk import HookPhase, HookPoint`
- [x] 2.2 Fix `agent.py`: Change `from agent_core.llm_gateway import LLMGateway` to `from agent_core.sdk import LLMGateway`
- [x] 2.3 Fix `discovery.py`: Change `from agent_core.agent_base import BaseAgent` to `from agent_core.sdk import BaseAgent`
- [x] 2.4 Fix `discovery.py`: Change `from agent_core.llm_gateway import LLMGateway` to `from agent_core.sdk import LLMGateway`
- [x] 2.5 Fix `generation.py`: Change `from agent_core.agent_base import BaseAgent` to `from agent_core.sdk import BaseAgent`
- [x] 2.6 Fix `generation.py`: Change `from agent_core.agent_base.hooks import HookPhase, HookPoint` to `from agent_core.sdk import HookPhase, HookPoint`
- [x] 2.7 Fix `generation.py`: Change `from agent_core.llm_gateway import LiteLLMGateway` to `from agent_core.sdk import LiteLLMGateway`
- [x] 2.8 Fix `validation.py`: Change `from agent_core.agent_base import BaseAgent` to `from agent_core.sdk import BaseAgent`
- [x] 2.9 Fix `validation.py`: Change `from agent_core.llm_gateway import LLMGateway` to `from agent_core.sdk import LLMGateway`
- [x] 2.10 Run `uv run ruff check src/` to verify no import errors

## 3. agent-docs-sync: Adopt build_toolkit() in agent builders

- [x] 3.1 Refactor `agent.py:build_doc_sync_agent()` to use `build_toolkit(tools=[...])` instead of manual ToolRegistry + register
- [x] 3.2 Refactor `agents/discovery.py:build_discovery_agent()` to use `build_toolkit(tools=[...])`
- [x] 3.3 Refactor `agents/generation.py:build_generation_agent()` to use `build_toolkit(tools=[...])`
- [x] 3.4 Refactor `agents/validation.py:build_validation_agent()` to use `build_toolkit(tools=[...])`
- [x] 3.5 Run `uv run pytest tests/ -x` to verify all agents build correctly

## 4. agent-docs-sync: Add @resilient_tool to external-call tools

- [x] 4.1 Add `@resilient_tool(max_retries=2, failure_threshold=3)` to `CheckLinksTool` in `tools/check_links.py`
- [x] 4.2 Add `@resilient_tool(max_retries=1, failure_threshold=5)` to `GitDiffTool` in `tools/git_diff.py`
- [x] 4.3 Add `@resilient_tool(max_retries=1, failure_threshold=5)` to `StateTool` in `tools/state.py`
- [x] 4.4 Remove `on_tool_error` hook registration from `agent.py` (keep function in hooks.py for backward compat)
- [x] 4.5 Run `uv run pytest tests/ -x` to verify tools still work

## 5. agent-docs-sync: Adopt AgentRequest for typed task passing

- [x] 5.1 Update `workflows/full_pipeline.py:generate_handler()` to use `AgentRequest` instead of string task (follow code_reviewer pattern)
- [x] 5.2 Update `cli.py:update()` command to use `AgentRequest` when calling agent.run()
- [x] 5.3 Run `uv run pytest tests/ -x` to verify

## 6. agent-docs-sync: Refactor agent.py to use build_agent()

- [x] 6.1 Refactor `agent.py:build_doc_sync_agent()` to use `build_agent()` with pre-built hooks and flavors
- [x] 6.2 Ensure mode-based flavor selection still works (check/generate/full_sync)
- [x] 6.3 Run `uv run pytest tests/ -x` to verify

## 7. Verification

- [x] 7.1 Run full test suite in agent-core: `cd agent-core && uv run pytest -x`
- [x] 7.2 Run full test suite in agent-docs-sync: `cd agent-docs-sync && uv run pytest -x`
- [x] 7.3 Run lint in both repos: `uv run ruff check src/`
- [x] 7.4 Verify no non-SDK imports remain: `grep -rn "from agent_core\.\(agent_base\|llm_gateway\|resilience\|tool_registry\|memory\|foundation\)" src/ | grep -v sdk`
