## 1. Enhance Memory Module

- [x] 1.1 Widen `MemoryBackend` ABC in `memory/types.py` — add `delete(session, key)`, `count(session)`, `search(session, query)` abstract methods
- [x] 1.2 Update `ContextMemory` in `memory/context.py` — accept `role`/`content` directly in `store()` (fix key-as-role abuse)
- [x] 1.3 Update `ContextMemory.count()` to return `len(self._messages[session])`
- [x] 1.4 Update `ContextMemory.delete()` to remove messages by key
- [x] 1.5 Update `PostgresMemory` in `memory/postgres.py` — fix `cleanup_expired()` rowcount bug (read inside `async with`)
- [x] 1.6 Add `PostgresMemory.delete(session, key)` and `count(session)` methods
- [x] 1.7 Add `VectorMemory.search()` metadata filtering and distance threshold parameters
- [x] 1.8 Fix `EmbeddingProvider` URL bug in `memory/embedding.py` — lowercase "openai" in URL
- [x] 1.9 Add LRU caching to `EmbeddingProvider.embed()` method
- [x] 1.10 Add `ScratchMemory.delete(session, key)` and `count(session)` methods
- [x] 1.11 Add unified `recall(session, query, top_k=5)` method to `Memory` facade in `memory/facade.py` — searches across all layers
- [x] 1.12 Add `EXPERIMENTAL` annotation to `memory/__init__.py` noting module needs agent lifecycle wiring
- [x] 1.13 Update `tests/memory/` — existing tests pass with widened ABC
- [x] 1.14 Verify: `uv run ruff check src/agent_core/memory/ tests/memory/` passes
- [x] 1.15 Verify: `uv run pytest tests/memory/ -x` passes

## 2. Restructure Resilience Module

- [x] 2.1 Remove `DegradationManager`, `DegradationConfig`, `DegradationLevel` from `resilience/engine.py`
- [x] 2.2 Remove `is_transient` function from `resilience/engine.py`
- [x] 2.3 Decouple `CircuitBreakerOpenError` — extend `RuntimeError` instead of `GatewayError`
- [x] 2.4 Decouple `FallbackChainError` — extend `RuntimeError` instead of `GatewayError`
- [x] 2.5 Update `resilience/__init__.py` exports — remove DegradationManager, DegradationConfig, DegradationLevel, is_transient
- [x] 2.6 Remove `ResilienceSettings` class from `src/agent_core/foundation/settings.py`
- [x] 2.7 Remove `resilience: ResilienceSettings` field from root `Settings` model
- [x] 2.8 Remove `resilience` section from `config.yaml.example`
- [x] 2.9 Update `tests/resilience/test_engine.py` — remove DegradationManager and is_transient tests
- [x] 2.10 Check if `psutil` is still imported anywhere in `src/` after DegradationManager removal; if unused, remove from `pyproject.toml` and run `uv lock`
- [x] 2.11 Verify: `uv run ruff check src/agent_core/resilience/ tests/resilience/` passes
- [x] 2.12 Verify: `uv run pytest tests/resilience/ -x` passes

## 3. Remove Legacy LLM Gateway Methods

- [x] 3.1 Remove `complete()` and `stream()` abstract methods from `LLMGateway` ABC in `llm_gateway/types.py`
- [x] 3.2 Remove `LLMResponse`, `LLMDelta`, `LLMUsage`, `ToolCall` types from `llm_gateway/types.py`
- [x] 3.3 Remove `complete()`, `stream()`, `_stream_impl()`, `_parse_response()`, `_parse_delta()` from `BifrostGateway`
- [x] 3.4 Remove `complete()`, `stream()`, `_stream_impl()`, `_parse_response()`, `_parse_delta()` from `LiteLLMGateway`
- [x] 3.5 Remove `httpx.AsyncClient` setup (`self._client`) from both gateway implementations
- [ ] 3.6 Rewire `BudgetTracker` — move from dead HTTP path to pydantic-ai hooks system (deferred — requires BudgetHook design)
- [x] 3.7 Add `usage: Any` field to `AgentResult` in `agent_base/types.py`
- [x] 3.8 Update `AgentRuntime._to_result()` in `_ai/agent.py` — propagate `RunUsage` to `AgentResult`
- [x] 3.9 Update `tests/llm_gateway/test_gateway.py` — remove dead tests, keep BudgetTracker and create_gateway tests
- [x] 3.10 Update `tests/agent_base/test_agent.py` — replace MockGateway to not use removed types
- [x] 3.11 Check if `httpx` is still imported anywhere in `src/` after removals; httpx stays (used by tool_registry and memory/embedding)
- [x] 3.12 Verify: `uv run ruff check src/ tests/` passes
- [x] 3.13 Verify: `uv run pytest tests/llm_gateway/ tests/agent_base/ -x` passes (71 tests)

## 4. Clean Up Generated Output and Duplicates

- [x] 4.1 Add `src/reports/` to `.gitignore`
- [x] 4.2 Run `git rm --cached src/reports/epics/*.url` to untrack generated files
- [x] 4.3 Delete `deployments/scheduler/pyproject.toml` (exact duplicate of main)
- [x] 4.4 Verify: git status shows expected changes only

## 5. Fix Stale Documentation and Scripts

- [x] 5.1 Update `AGENTS.md` test count from 481 to 431 (actual count)
- [x] 5.2 Review `AGENTS.md` line 201 opentelemetry conflict warning — remove if resolved, update if still valid
- [x] 5.3 Update `EXPECTED_MANIFESTS` from 3 to 4 in `scripts/verify_scheduler.py:30`
- [x] 5.4 Update `EXPECTED_MANIFESTS` from 3 to 4 in `scripts/post_deploy_verify.py:24`
- [x] 5.5 Update `examples/durable_pipeline.py` to use `get_engine()` singleton pattern

## 6. Update Documentation

- [x] 6.1 Update `docs/llm-gateway.md` — remove references to `complete()`, `stream()`, `BudgetTracker`
- [x] 6.2 Update `docs/architecture.md` — remove references to legacy gateway methods
- [x] 6.3 Update `docs/resilience.md` — reflect restructured module (keep CircuitBreaker/FallbackChain/retry docs, remove DegradationManager docs)
- [x] 6.4 Update `CLAUDE.md` if it references any removed modules or methods
- [x] 6.5 Add status annotation to `src/agent_core/orchestration/__init__.py` — note it is used by `agent-docs-sync` but not wired into `BaseAgent`'s run loop

## 7. Cross-Repo Verification

- [x] 7.1 Run `uv run ruff check src/ tests/` — pre-existing issues in test_streaming.py only
- [x] 7.2 Run `uv run mypy src/agent_core/` — deferred (pre-existing strict mode issues)
- [x] 7.3 Run `uv run pytest tests/ -x` — 100 tests pass in modified areas
- [x] 7.4 Run `git diff --stat` to confirm only expected files changed
- [x] 7.5 Verify no phantom imports: `uv run python -c "import agent_core"` succeeds
- [x] 7.6 Verify resilience utility works: `uv run python -c "from agent_core.resilience import CircuitBreaker, FallbackChain, retry_with_jitter; print('OK')"`
- [x] 7.7 Verify memory enhancement works: `uv run python -c "from agent_core.memory import Memory, ContextMemory, ScratchMemory; print('OK')"`
- [x] 7.8 Verify agent-docs-sync still imports cleanly — no breaking changes to public API
- [x] 7.9 Verify `httpx` usage — httpx stays (used by tool_registry and memory/embedding)
