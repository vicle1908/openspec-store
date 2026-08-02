## Why

agent-core has accumulated dead code, legacy API surface, and stale documentation through rapid iteration on the pydantic-ai v2.9 migration, observability integration, and scheduler deployment. Three modules (`memory/`, `resilience/`, legacy `llm_gateway` methods) were built as prepared capabilities that were never wired into the agent runtime. Stale constants in verification scripts and outdated documentation create confusion for operators. This cleanup reduces cognitive load, removes ~1,200 lines of dead code, and eliminates legacy API surface that no production code path uses.

agent-core serves as a shared framework — `agent-docs-sync` imports 6 subpackages (`agent_base`, `tool_registry`, `llm_gateway`, `orchestration`, `foundation`). All proposed removals have been validated against this consumer: zero external callers of `complete()`/`stream()`, zero external imports of `memory/` or `resilience/`. A cross-repo dependency audit across 40+ repos confirms no breaking changes.

## What Changes

### Memory Module Enhancement (Not Removal)
The `memory/` module is well-structured internally and aligns with industry best practices (LangChain BaseStore, CrewAI Memory, pydantic-ai-harness Memory capability). agent-docs-sync is a strong candidate for memory integration — it already has a primitive KV store (`.docs-sync-state.yaml`) showing intent toward caching. However, the module needs targeted improvements to match best practices and serve consumers:
- Widen `MemoryBackend` ABC: add `delete()`, `count()`, `search()` methods
- Add unified `recall(query)` to Memory facade — consumers shouldn't need to know layers
- Fix `PostgresMemory` rowcount bug and `EmbeddingProvider` URL bug
- Add embedding caching to avoid redundant API calls
- Fix `ContextMemory` key-as-role abuse — accept `role`/`content` directly
- Add metadata filtering and distance threshold to `VectorMemory`
- Add `EXPERIMENTAL` annotation noting module needs agent lifecycle wiring

### Dead Code Removal
- Remove `llm_gateway/` raw HTTP methods `complete()` and `stream()` from `LLMGateway` ABC and implementations — all production code paths now flow through `get_model()` → pydantic-ai `Agent`. Remove associated types: `LLMResponse`, `LLMDelta`. pydantic-ai provides full replacements: `Agent.run()` for completions, `Agent.run_stream()` for streaming, `RunUsage` for usage tracking, `InstrumentedModel` for OTel. Validated: `agent-docs-sync` (sole external consumer) never calls these methods — it only uses `is_available()` and type-annotates `LLMGateway`

### BudgetTracker Rewiring (Not Removal)
- **Rewire** `BudgetTracker` from the dead HTTP path into pydantic-ai's hooks system — it fills a unique gap that pydantic-ai doesn't cover: USD cost ceiling enforcement. pydantic-ai's `UsageLimits` tracks token/request counts but has no monetary budget enforcement. BudgetTracker's `set_budget()`/`check_and_record()` pattern with thread-safe atomicity is unique and valuable.
- Wire BudgetTracker as a `before_model_request` / `after_model_request` hook in pydantic-ai
- Fix the data flow: propagate pydantic-ai's `RunUsage` to `AgentResult` (currently dropped by `_to_result()`)

### Resilience Restructuring (Preserve High-Value Patterns)
- **Preserve as standalone utility**: `CircuitBreaker`, `CircuitBreakerRegistry`, `BreakerConfig`, `BreakerState`, `FallbackChain`, `FallbackEntry`, `retry_with_jitter` — these are general-purpose, zero-coupling patterns with high standalone value. `agent-docs-sync` has dead fallback config and no LLM retry, making these directly useful for future integration.
- **Remove**: `DegradationManager`, `DegradationConfig`, `DegradationLevel` — agent-loop-specific (`effective_max_iterations`), dead `MINIMAL` level, `psutil` dependency for no realized benefit
- **Remove**: `is_transient` — tied to `GatewayError.code` values, subsumed by `retryable` parameter on `retry_with_jitter`
- **Remove**: `ResilienceSettings` from `foundation/settings.py` — parsed but never consumed
- **Decouple exceptions**: Make `CircuitBreakerOpenError` and `FallbackChainError` extend `RuntimeError` instead of `GatewayError` for full independence

### Stale Documentation & Scripts
- Update `AGENTS.md` test count from 481 to 441
- Remove or update stale `opentelemetry-sdk` vs `pydantic-ai` version conflict warning in `AGENTS.md` line 201
- Update `EXPECTED_MANIFESTS` from 3 to 4 in `scripts/verify_scheduler.py:30` and `scripts/post_deploy_verify.py:24`
- Update `examples/durable_pipeline.py` to use `get_engine()` singleton pattern instead of standalone `SchedulerEngine` instance

### Generated Output Hygiene
- Add `src/reports/` to `.gitignore` and `git rm --cached` the tracked `.url` files
- Remove `deployments/scheduler/pyproject.toml` — exact duplicate of main `pyproject.toml`, not referenced by scheduler Dockerfile

### Module Status Annotation
- Add docstring annotation to `orchestration/` module — note that it is used externally by `agent-docs-sync` but not wired into `BaseAgent`'s own run loop (NOT dead code)

## Capabilities

### New Capabilities
- `agent-core-dead-code-cleanup`: Removal of legacy API surface, stale artifacts, and dead gateway methods from agent-core
- `agent-core-resilience-utility`: Preserve high-value resilience patterns (CircuitBreaker, FallbackChain, retry_with_jitter) as a standalone, decoupled utility module
- `agent-core-memory-enhancement`: Improve memory module to match industry best practices — widen ABC, add unified recall, fix bugs, add embedding caching

### Modified Capabilities
- `gateway`: Remove legacy `complete()`, `stream()`, `BudgetTracker`, `LLMResponse`, `LLMDelta` from `LLMGateway` interface — scope reduction to `get_model()`, `is_available()`, `close()`
- `vector-memory-search`: Enhance existing requirements — add metadata filtering, distance threshold, cross-session search; fix EmbeddingProvider URL bug

## Impact

### Cross-Repo Compatibility (validated)
- **agent-docs-sync** (sole hard consumer): Uses `agent_base`, `tool_registry`, `llm_gateway`, `orchestration`, `foundation`. None of the proposed removals affect its imports. It never calls `complete()`/`stream()`, never imports `memory/` or `resilience/`.
- **code-daily-scan**: Declares `agent-core` in pyproject.toml but has zero actual imports (phantom dependency). No impact.
- **tdt-core**: Dynamic import of `agent_core.scheduler_setup` with `ImportError` suppression. No impact.
- **~40 other repos**: Zero references to agent-core.

### Code Changes
- **Removal**: ~430 lines across `resilience/` DegradationManager + is_transient (~80), `llm_gateway` legacy methods + types + BudgetTracker (~350)
- **Restructuring**: `resilience/` reduced from 376 to ~200 lines — CircuitBreaker, FallbackChain, retry_with_jitter preserved as standalone utility with decoupled exceptions
- **Memory enhancement**: ~100 lines of improvements — ABC widening, facade recall, bug fixes, embedding caching
- **API surface**: `LLMGateway` ABC retains `get_model()`, `is_available()`, `close()`. Removes `complete()`, `stream()`, `LLMResponse`, `LLMDelta`, `BudgetTracker`. No external callers exist.
- **Dependencies**: `psutil` may become unused after DegradationManager removal (verify); `httpx` stays (used by `tool_registry/builtins/http_request.py` and `memory/embedding.py`)
- **Tests**: `tests/resilience/test_engine.py` updated to cover preserved patterns only; `tests/llm_gateway/test_gateway.py` simplified; `tests/memory/` updated with new ABC methods
- **Docs**: `docs/llm-gateway.md`, `docs/architecture.md`, `docs/resilience.md`, `docs/memory.md` updated
- **Scripts**: Two verification scripts updated with correct manifest count
- **Git**: `src/reports/epics/*.url` files untracked

### Future Consumer Value
- **Resilience utility**: `agent-docs-sync` has dead `fallback_enabled`/`fallback_on_error` config and no LLM retry. The preserved CircuitBreaker + FallbackChain + retry_with_jitter patterns are directly usable for future LLM provider fallback and retry integration.
- **Memory module**: `agent-docs-sync` is a strong candidate for memory integration — it already has a primitive KV store (`.docs-sync-state.yaml`) showing intent toward caching. Enhanced memory patterns (key-value with TTL, unified recall, vector search) would enable incremental pipelines that skip unchanged work. Industry consensus: memory is a first-class capability in all major agent frameworks.

### Non-Goals
- Wiring resilience patterns into the gateway (tracked separately if desired)
- Wiring memory into the agent lifecycle (tracked as separate change — requires `_ai/capability.py` integration)
- Re-implementing BudgetTracker for pydantic-ai (separate change if budget enforcement is needed)
- Refactoring `cli/app.py` into sub-modules (separate change)
- Modifying the `orchestration/` module beyond docstring annotation
- Changing the `LLMGateway` ABC's preserved interface (`get_model()`, `is_available()`, `close()`)
- Affecting `agent-docs-sync` or any other external consumer's code
