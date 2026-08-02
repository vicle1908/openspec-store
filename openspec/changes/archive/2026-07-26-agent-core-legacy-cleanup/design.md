## Context

agent-core is a Python 3.14 SDK providing agent primitives: LLM gateway routing, agent run loops, tool registries, skill systems, and scheduler bootstrapping. It serves as a **shared framework** — other repos in the TDT ecosystem import its public API.

### External Consumer Map (validated via cross-repo audit of 40+ repos)

```
agent-docs-sync (SOLE HARD CONSUMER)
├── agent_base     → BaseAgent, HookRegistry, Flavor, otel_metrics, structured_audit
├── tool_registry  → ToolRegistry, BaseTool, ToolMetadata, ToolResult (15+ files)
├── llm_gateway    → LLMGateway (type), LiteLLMGateway (construct + is_available)
├── orchestration  → WorkflowBuilder, WorkflowEngine, EdgeDescriptor, NodeDescriptor, NodeKind, EdgeCondition
└── foundation     → configure_logging, GatewayError

agent-docs-sync future needs (from code analysis):
├── Has dead fallback_enabled/fallback_on_error config → needs CircuitBreaker + FallbackChain
├── Has no LLM retry (custom hook only) → needs retry_with_jitter
└── Has zero memory usage → if needed, implement at point of use

code-daily-scan (PHANTOM — pyproject.toml dep, zero imports)
tdt-core (SOFT — dynamic import of scheduler_setup, ImportError suppressed)
~40 other repos (ZERO references)
```

### Dead Code State
- `memory/` module: fully implemented but zero production imports, zero external consumers. Well-structured but needs ABC improvements and agent lifecycle wiring.
- `resilience/` module: CircuitBreaker/FallbackChain/retry_with_jitter have HIGH standalone value; DegradationManager is agent-loop-specific dead code; ResilienceSettings parsed but never consumed
- `llm_gateway/` raw HTTP methods: `complete()` and `stream()` dead (pydantic-ai provides full replacements); `BudgetTracker` set but never enforced (only called from dead path) — BUT fills unique USD cost ceiling gap that pydantic-ai doesn't cover; `is_available()` dead but part of public API
- pydantic-ai replaces: complete() → Agent.run(), stream() → Agent.run_stream(), LLMResponse → ModelResponse, LLMUsage → RunUsage, manual OTel → InstrumentedModel
- pydantic-ai does NOT replace: BudgetTracker (USD cost ceilings, cross-agent budgets, thread-safe enforcement)
- `src/reports/` tracked generated output in git
- Stale constants in verification scripts (EXPECTED_MANIFESTS=3, actual=4)
- Stale test count in AGENTS.md (481, actual=441)

## Goals / Non-Goals

**Goals:**
- Remove ~1,500 lines of confirmed dead code
- Preserve high-value resilience patterns (CircuitBreaker, FallbackChain, retry_with_jitter) as standalone utility
- Shrink `LLMGateway` ABC to its minimal useful surface (`get_model()`, `is_available()`, `close()`)
- Fix stale documentation and script constants
- Clean up generated output tracked in git

**Non-Goals:**
- Wiring resilience patterns into the gateway (separate change if desired)
- Re-implementing BudgetTracker for pydantic-ai (separate change if budget enforcement is needed)
- Refactoring `cli/app.py` into sub-modules (separate change)
- Modifying `orchestration/` beyond docstring annotation
- Implementing agent memory (if needed, implement at point of use)

## Decisions

### D1: Enhance `memory/` module to match best practices

**Decision:** Delete the entire `memory/` directory and its tests.

**Rationale:** Deep analysis reveals zero standalone value across all components:
- `MemoryBackend` ABC: 4-method session-scoped key-value interface — too narrow for reuse
- `ContextMemory`: 30-line `defaultdict(deque)` — trivially inlineable
- `ScratchMemory`: 20-line JSON file wrapper — trivially inlineable
- `PostgresMemory` + `FeedbackStore`: depend on unused `agent_memory` schema
- `VectorMemory`: depends on unused pgvector schema
- `Memory` facade: routes to backends nobody uses, never instantiated outside tests
- `FeedbackEntry`: 13 fields for a self-learning system that was never built
- `MemoryBackendError`: defined but never raised

Zero external consumers across all repos. Zero future consumer value preserved — if memory is ever needed, implement at point of use in a few lines.

**Alternatives considered:**
- Keep MemoryBackend ABC → rejected; too narrow (session-scoped key-value only)
- Keep ContextMemory as utility → rejected; 30 lines that any consumer would inline
- Mark as experimental → rejected; zero imports, annotation adds noise

### D2: Restructure `resilience/` — preserve high-value patterns

**Decision:** Restructure the module to keep general-purpose patterns, remove agent-loop-specific code.

**Preserve (~200 lines):**
- `CircuitBreaker`, `CircuitBreakerRegistry`, `BreakerConfig`, `BreakerState` — textbook state machine, zero coupling
- `FallbackChain`, `FallbackEntry` — generic async chain executor parameterized on `fn`
- `retry_with_jitter` — zero dependencies, general-purpose async retry with exponential backoff

**Remove (~175 lines):**
- `DegradationManager`, `DegradationConfig`, `DegradationLevel` — `effective_max_iterations` is agent-loop-specific, `MINIMAL` level is dead, `psutil` dependency for no realized benefit
- `is_transient` — hardcoded `GatewayError.code` checks, subsumed by `retryable` parameter
- `ResilienceSettings` from `foundation/settings.py` — parsed but never consumed

**Decouple exceptions:**
- `CircuitBreakerOpenError` → extend `RuntimeError` instead of `GatewayError`
- `FallbackChainError` → extend `RuntimeError` instead of `GatewayError`

**Rationale:** agent-docs-sync has dead `fallback_enabled`/`fallback_on_error` config and no LLM retry. These patterns are directly usable for future provider fallback and retry integration. The DegradationManager, by contrast, answers "should I reduce the agent's iteration count?" — a question that never became a real integration point.

**Alternatives considered:**
- Remove entirely → rejected; loses high-value patterns that future consumers need
- Keep DegradationManager → rejected; agent-loop-specific, dead MINIMAL level, psutil dependency
- Move to separate package → out of scope; keep in agent-core for now

### D3: Remove legacy `LLMGateway` methods, rewire BudgetTracker

**Decision:** Remove `complete()`, `stream()`, `LLMResponse`, `LLMDelta` from the gateway. **Rewire** `BudgetTracker` into pydantic-ai's hooks system.

**Rationale:**
- `complete()`/`stream()`: zero callers across all 40+ repos. pydantic-ai provides full replacements (`Agent.run()`, `Agent.run_stream()`, `RunUsage`, `InstrumentedModel`).
- `BudgetTracker`: Currently broken (only called from dead path), but fills a UNIQUE gap — pydantic-ai's `UsageLimits` tracks tokens/requests but has NO USD cost ceiling enforcement. BudgetTracker's `set_budget()`/`check_and_record()` with thread-safe atomicity is valuable. Rewire as a `before_model_request`/`after_model_request` hook.
- `is_available()`: dead but part of public API — keep for interface stability.

**Preserved:** `get_model()`, `is_available()`, `close()`, `create_gateway()`, `BifrostGateway`, `LiteLLMGateway`, `BudgetTracker` (rewired).

**Alternatives considered:**
- Remove BudgetTracker → rejected; it provides unique USD cost ceiling that pydantic-ai doesn't have
- Keep in dead path → rejected; rewire into hooks for actual enforcement
- Remove is_available() → rejected; agent-docs-sync references the gateway type

### D4: Remove `deployments/scheduler/pyproject.toml`

**Decision:** Delete the file.

**Rationale:** Byte-for-byte identical to the main `pyproject.toml`. The scheduler Dockerfile copies from the main one. Leftover from before the Dockerfile was restructured.

### D5: Update stale constants in-place

**Decision:** Update `EXPECTED_MANIFESTS` from 3 to 4 in both verification scripts. Update test count in `AGENTS.md`.

**Rationale:** Simple constant corrections, not architectural changes.

### D6: httpx dependency analysis

**Decision:** After removing gateway raw methods and memory module, check if `httpx` is still imported anywhere. If only `tool_registry/builtins/http_request.py` uses it, keep the dependency. If unused, remove from `pyproject.toml` and run `uv lock`.

**Rationale:** `httpx` is used by `tool_registry/builtins/http_request.py` (builtin HTTP tool) — likely still needed. Verify during implementation.

## Risks / Trade-offs

- **[Risk] Future consumers lose memory capability** → Mitigation: Memory patterns have zero standalone value (too narrow, too coupled to unused schemas). If memory is needed, implement at point of use — the patterns are simple enough (30-line deque, 20-line JSON I/O) that reimplementing is cheaper than maintaining dead infrastructure.

- **[Risk] Future consumers lose DegradationManager** → Mitigation: The degradation concept (CPU/error rate → reduced capabilities) is reusable, but the specific API was designed for an agent loop iteration cap that never materialized. If needed, redesign against actual integration points.

- **[Risk] BudgetTracker removal limits future budget enforcement** → Mitigation: BudgetTracker was broken (set but never enforced). Reimplementation as pydantic-ai middleware/hooks would be the correct approach for budget enforcement in the pydantic-ai agent loop.

- **[Risk] External consumers of `complete()`/`stream()`** → Mitigation: **Validated safe.** Cross-repo audit of 40+ repos confirms zero external callers.

- **[Risk] Tests break after removal** → Mitigation: Update test files for restructured modules. Run full test suite before commit.

- **[Risk] `agent-docs-sync` breaks** → Mitigation: Not possible — its imports are all preserved. Resilience patterns are preserved as utility for future use.
