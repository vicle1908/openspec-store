## 1. BudgetTracker Hook Rewire

- [x] 1.1 Enhance `_normalize_ctx()` in `_ai/hooks.py` to flatten `deps.extra` into the top-level hook context dict
- [x] 1.2 Add `"budget_id": budget_id` to `deps.extra` dict in `agent_base/agent.py`
- [x] 1.3 Create `budget_enforcement` hook pack in `agent_base/hooks/builtins.py`
- [x] 1.4 Add token-to-USD cost estimation in the after_model hook
- [x] 1.5 Register `"budget_enforcement"` in `register_pack()` dispatch
- [x] 1.6 Fix latent bug in `cost_tracker` — `_normalize_ctx` flattening fixes `ctx.get("agent_name")` for MODEL_REQUEST hooks
- [x] 1.7 Add tests for budget_enforcement hook pack (3 tests: registers hooks, state tracking, register_pack)
- [x] 1.8 Verify: `uv run pytest tests/agent_base/ tests/llm_gateway/ -x` passes

## 2. CLI Extraction

- [x] 2.1 Create `cli/utils.py` with global state, `_print_result`, profile helpers, `_run_agent_prompt`
- [x] 2.2 Create `cli/schedules.py` — extract `schedules_app` + 5 commands + 6 helpers
- [x] 2.3 Create `cli/skills.py` — extract `skills_app` + 3 commands
- [x] 2.4 Create `cli/init_cmd.py` — extract `init` command + 6 helpers
- [x] 2.5 Create `cli/agent_cmd.py` — extract `review`, `propose`, `explore`, `repl` commands
- [x] 2.6 Renamed `cli/eval.py` → `cli/eval_cmd.py`, registered as `eval_app` sub-app
- [x] 2.7 Rewrite `cli/app.py` as thin wiring file with re-exports for test compat
- [x] 2.8 Updated `cli/__init__.py` exports (unchanged)
- [x] 2.9 Verify: `uv run ruff check src/agent_core/cli/` passes
- [x] 2.10 Verify: `uv run pytest tests/cli/ -x` passes (24/24 tests pass)
- [x] 2.11 Verify: `agent-core --help` shows all commands

## 3. Memory Lifecycle Integration

- [x] 3.1 Create `MemoryCapability` class in `_ai/capability.py` (minimal capability pattern)
- [x] 3.2 Session ID obtained from `ctx.deps.extra["run_id"]` at call time (not for_run)
- [x] 3.3 Implemented `get_toolset()` — memory_store, memory_retrieve, memory_recall, memory_list_keys tools
- [x] 3.4 Implemented `get_instructions()` — injects ContextMemory context into system prompt
- [x] 3.5 Conversation capture deferred (requires after_run hook wiring — future work)
- [x] 3.6 Memory wired via `memory` param on AgentRuntime, not harness config
- [x] 3.7 Accept optional `memory` param in `BaseAgent.__init__()`, pass to AgentRuntime
- [x] 3.8 Removed EXPERIMENTAL annotation from `memory/__init__.py`
- [x] 3.9 Add tests for MemoryCapability (8 tests: create, tools, instructions, store/retrieve/list_keys)
- [x] 3.10 Verify: `uv run pytest tests/memory/ tests/agent_base/ -x` passes

## 4. Tool Resilience Decorator

- [x] 4.1 Created `@resilient_tool` decorator in `resilience/decorators.py`
- [x] 4.2 Implemented retry with `retry_with_jitter` from `resilience/`
- [x] 4.3 Implemented per-tool circuit breaker using `CircuitBreaker` + `CircuitBreakerRegistry`
- [x] 4.4 Added configurable `retryable` predicate (default: ConnectionError, TimeoutError, OSError)
- [x] 4.5 Add tests for resilient_tool decorator (5 tests: success, retry, max retries, non-retryable, custom predicate)
- [x] 4.6 Verify: `uv run pytest tests/resilience/ -x` passes

## 5. Final Verification

- [x] 5.1 Run `uv run ruff check src/` — zero new errors (pre-existing test_streaming issues only)
- [x] 5.2 Run `uv run pytest tests/` — 130+ tests pass in all modified areas
- [x] 5.3 Verify no phantom imports: `uv run python -c "import agent_core"` succeeds
- [x] 5.4 Verify resilience utility: `from agent_core.resilience import resilient_tool, CircuitBreaker` succeeds
- [x] 5.5 Verify memory integration: `from agent_core.memory import Memory` succeeds
