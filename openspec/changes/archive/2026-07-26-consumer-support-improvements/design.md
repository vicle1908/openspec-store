## Context

agent-core has one active consumer (agent-docs-sync) and two examples (code_reviewer, minimal_agent). The SDK surface is clean but has gaps discovered during deep exploration:

1. `sdk/memory.py:63` has `except TimeoutError, Exception:` — invalid Python 3 syntax that would crash on non-timeout exceptions during long-term memory creation
2. `VectorMemory` implements `MemoryBackend` but is not wired into the `Memory` facade or `create_consumer_memory()` factory
3. `build_agent()` doesn't accept `flavors` — consumers must construct `Flavor` objects and pass them to `BaseAgent` directly, bypassing the SDK helper
4. `build_toolkit()` creates `ToolRegistry(include_builtins=False)` — consumers who pass a tool list lose builtins unless they manually add them

## Goals / Non-Goals

**Goals:**
- Fix the syntax error (trivial, high-value)
- Wire VectorMemory into the Memory facade (opt-in, backward-compatible)
- Expose Flavor composition through `build_agent()` (reduce consumer boilerplate)
- Add `include_builtins` parameter to `build_toolkit()` (consumer choice)
- Document hooks vs capabilities decision matrix

**Non-Goals:**
- Shared tool library (architecture change, separate proposal)
- Memory.recall() indexing (performance optimization, separate proposal)
- New harness capabilities (separate proposal)

## Decisions

### D1: Fix syntax error directly

**Decision:** Change `except TimeoutError, Exception:` to `except (TimeoutError, Exception):` at `sdk/memory.py:63`.

**Rationale:** This is a clear bug. The current code would raise `SyntaxError` at import time in Python 3 (actually, it's valid Python 2 syntax but invalid in Python 3 — the `except X, Y:` form was removed). However, since the function is `async` and uses `await`, it's already Python 3 only. The fact that it works at all suggests the try/except block is never actually reached in production (long-term memory creation succeeds or fails with ImportError).

### D2: Wire VectorMemory as optional layer

**Decision:** Add `enable_vector: bool = False` and `vector_dsn: str = ""` parameters to `create_consumer_memory()`. When enabled, create a `VectorMemory` instance and add it to the `Memory` facade.

**Rationale:** VectorMemory already implements `MemoryBackend`. Wiring it into the facade is additive — existing consumers are unaffected. The factory pattern already supports optional layers (PostgresMemory is opt-in via `enable_postgres`).

### D3: Add flavors parameter to build_agent()

**Decision:** Add `flavors: list[Flavor] | None = None` parameter to `build_agent()`. When provided, pass them to `BaseAgent(flavors=...)`. When None, build a default Flavor from config (current behavior).

**Rationale:** The current pattern forces consumers to construct Flavor objects manually when they want composition. Adding the parameter preserves backward compatibility (default behavior unchanged) while enabling the common case.

### D4: Add include_builtins to build_toolkit()

**Decision:** Add `include_builtins: bool = True` parameter to `build_toolkit()`. Pass it through to `ToolRegistry(include_builtins=include_builtins)`.

**Rationale:** Currently `build_toolkit()` always creates `ToolRegistry(include_builtins=False)`. Consumers who want builtins must either pass a `ToolRegistry` directly or manually register builtins. Adding the parameter gives consumers explicit control.

## Risks / Trade-offs

- **[Risk] VectorMemory requires pgvector extension** → If consumers enable vector without pgvector installed, it will fail at runtime. **Mitigation:** Wrap creation in try/except with warning, consistent with PostgresMemory pattern.
- **[Risk] Flavors parameter changes build_agent() signature** → Existing callers using positional args could break. **Mitigation:** Parameter is keyword-only (after `*`), so no positional breakage.
- **[Low] Memory.recall() brute-force** → Deferred to future change. Current implementation works for small datasets.
