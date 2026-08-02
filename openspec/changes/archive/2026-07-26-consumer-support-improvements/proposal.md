## Why

Deep exploration of agent-core's feature surface revealed three categories of issues affecting consumer support:

1. **Bugs** — A syntax error in `sdk/memory.py` prevents long-term memory creation from degrading gracefully, and VectorMemory is orphaned from the Memory facade
2. **Consumer UX gaps** — Flavor composition is powerful but not exposed through `build_agent()`, forcing consumers to construct Flavor objects manually
3. **Documentation gaps** — The hooks vs capabilities decision matrix is unclear to consumers, leading to confusion about which to use

These issues don't block current consumers (agent-docs-sync works), but they create friction for new consumers and leave known bugs in production code.

## What Changes

- **Fix syntax error** in `sdk/memory.py:63` — `except TimeoutError, Exception:` → `except (TimeoutError, Exception):`
- **Wire VectorMemory into Memory facade** — add optional vector layer to `Memory` class and `create_consumer_memory()` factory
- **Add Flavor parameter to `build_agent()`** — accept optional `flavors` parameter so consumers can compose flavors without constructing `Flavor` objects manually
- **Add `include_builtins` parameter to `build_toolkit()`** — let consumers opt in to builtins when passing a tool list
- **Document hooks vs capabilities** — add decision matrix to AGENTS.md and SDK docstrings

## Capabilities

### New Capabilities
- `memory-vector-integration`: Wire VectorMemory into Memory facade and create_consumer_memory factory
- `flavor-composition-sdk`: Expose Flavor composition through build_agent() parameter

### Modified Capabilities
- `agent-core-invocation-contract`: Add flavors parameter to build_agent(), add include_builtins to build_toolkit()

## Impact

- **Files modified (4-5)**: `sdk/memory.py`, `memory/facade.py`, `sdk/agents.py`, `sdk/tools.py`, `AGENTS.md`
- **GitNexus blast radius**: LOW — Memory (3 upstream), build_agent (0 upstream), build_toolkit (0 upstream)
- **Dependencies**: Zero new — all libraries already available
- **Breaking changes**: None — all additions are optional parameters with backward-compatible defaults
