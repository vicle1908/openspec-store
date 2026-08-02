## Context

agent-core serves as a shared framework for the TDT ecosystem. After the legacy cleanup, the codebase is lean (~20K lines) with several integration gaps:

- BudgetTracker: set_budget() called from BaseAgent.run() but check_and_record()/pre_check() never reached
- Memory module: fully implemented, not wired into agent lifecycle
- CLI: 729-line monolith with extractable sections
- agent-docs-sync: hand-rolled retry, no caching, sequential pipeline

## Goals / Non-Goals

**Goals:**
- Fix BudgetTracker enforcement (bug fix)
- Wire Memory into agent lifecycle (feature)
- Modularize CLI (architecture)
- Enable tool-level resilience for consumers (feature)

**Non-Goals:**
- Changing BaseAgent's public API
- Breaking agent-docs-sync's existing behavior
- Adding external dependencies
- Modifying orchestration module

## Decisions

### D1: BudgetTracker — hook pack pattern (not middleware)

**Decision:** Create `budget_enforcement` hook pack in `builtins.py` using existing `HookPoint.MODEL_REQUEST` hooks.

**Rationale:** The HookAdapter already routes `before_model_request`/`after_model_request` to `HookPoint.MODEL_REQUEST`. The existing `cost_tracker` hook pack demonstrates the pattern. BudgetTracker just needs `pre_check()` called before and `check_and_record()` called after each LLM request.

**Validated constraints (from deep research):**
- `budget_id` is nested in `deps.extra["budget_id"]` — the HookAdapter's `_normalize_ctx` flattens RunContext to a dict but does NOT flatten `deps.extra`. The hook must access `ctx["deps"].extra["budget_id"]` or the `_normalize_ctx` must be enhanced to flatten `deps.extra` into the top-level dict.
- `cost_usd` does NOT exist on pydantic-ai's `RequestUsage` or `RunUsage` objects. Cost must be estimated from token counts using a pricing table (same approach as existing `cost_tracker` hook).
- The existing `cost_tracker` hook has a latent bug: `ctx.get("agent_name")` returns `None` for MODEL_REQUEST hooks. This should be fixed as part of this work.

**Alternatives considered:**
- pydantic-ai AbstractCapability → rejected; overkill for a 2-method integration
- Direct wiring in AgentRuntime → rejected; breaks separation of concerns

### D2: Memory — duck-typed capability via memory= param (simplified from AbstractCapability)

**Decision:** Create `MemoryCapability` as a duck-typed capability class with `get_instructions()` and `get_toolset()` methods, wired via `memory=` parameter on `AgentRuntime.__init__()`.

**Rationale:** The original design proposed `AbstractCapability` subclass + harness_config integration. The actual implementation uses a simpler duck-typed approach: `MemoryCapability` wraps the `Memory` facade and contributes tools + instructions via an inner `_MemCap` class. The `memory=` parameter on `AgentRuntime`/`BaseAgent` is more explicit than config-driven factory. Conversation capture (after_run) is handled directly in `AgentRuntime.run()` after the agent completes.

**Validated:** agent-docs-sync (sole consumer) does not import memory/ — zero breaking changes. The `memory=` parameter defaults to `None`, preserving existing behavior.

**Alternatives considered:**
- AbstractCapability subclass → rejected; overkill for a simple tools+instructions contribution
- Hook pack → rejected; can't contribute tools or instructions
- harness_config integration → rejected; `memory=` param is more explicit and simpler

### D3: CLI — Typer sub-app extraction (not monolith rewrite)

**Decision:** Extract commands into separate modules using Typer's `add_typer()` pattern. Keep `app.py` as a thin wiring file.

**Rationale:** The codebase already uses `add_typer()` for skills and schedules sub-apps. The extraction follows established patterns. Tests use `CliRunner` against `app` — as long as `app.py` re-exports, no test changes needed.

**Alternatives considered:**
- Click-based rewrite → rejected; Typer works fine
- Single-file with clear sections → rejected; 729 lines is too large

### D4: Tool resilience — decorator pattern (not class hierarchy)

**Decision:** Provide `@resilient_tool(max_retries, retryable)` decorator that wraps tool execution with retry and circuit breaker.

**Rationale:** agent-docs-sync's hand-rolled retry in `hooks.py` hardcodes tool names and exception types. A decorator is simpler, composable, and follows the existing `retry_with_jitter` pattern.

## Risks / Trade-offs

- **[Risk] BudgetTracker cost_usd may not be available from pydantic-ai** → Mitigation: pydantic-ai's `RunUsage` doesn't directly provide USD cost. The hook will need to estimate from token counts using model pricing (like cost_tracker already does). Budget enforcement will be approximate, not exact.

- **[Risk] MemoryCapability adds latency** → Mitigation: Memory operations are async and optional. ContextMemory is in-process (fast). PostgresMemory has 5-second timeout with graceful degradation. VectorMemory is not wired by default.

- **[Risk] CLI extraction breaks tests** → Mitigation: Tests import `app` from `app.py`. As long as `app.py` re-exports all commands, tests work unchanged. Verify with `pytest tests/cli/` after extraction.

- **[Trade-off] BudgetTracker approximate vs exact enforcement** → Acceptable because pydantic-ai's token-based `UsageLimits` provides exact token enforcement. BudgetTracker adds a USD-layer approximation on top.
