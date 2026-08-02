## Why

`agent-docs-sync` has 44 imports from `agent-core` but 9 bypass the stable SDK surface (importing from internal modules directly). It also has 19 manual `ToolRegistry.register()` calls where `build_toolkit()` could be used, and 4 tools making external calls without the `@resilient_tool` decorator that provides retry + circuit breaker. The `build_agent()` SDK helper is unused by the most complex agent builder (`agent.py`), and `AgentRequest` typed input is available but tasks are passed as plain strings. These gaps increase maintenance burden and miss framework-provided resilience and observability.

## What Changes

- **Fix 9 non-SDK imports** — Redirect to `agent_core.sdk` re-exports (zero risk, all symbols verified available)
- **Adopt `build_toolkit()`** — Replace 19 manual `ToolRegistry.register()` calls with 4 `build_toolkit()` calls across agent builders
- **Add `@resilient_tool`** — Apply to 3 tools making external calls (`check_links`, `git_diff`, `state`) for retry + circuit breaker
- **Extend `build_agent()`** — Add optional `flavors` parameter to support pre-built Flavor objects (backwards-compatible)
- **Refactor `agent.py`** — Use `build_agent()` with pre-built hooks and flavors instead of manual `BaseAgent` construction
- **Adopt `AgentRequest`** — Replace string task passing with typed `AgentRequest` in 3 agent.run() call sites
- **Remove redundant `on_tool_error` hook** — `@resilient_tool` replaces manual retry logic

## Capabilities

### Modified Capabilities
- `sdk-public-api`: `build_agent()` gains optional `flavors` parameter
- `builtin-hooks`: `@resilient_tool` adoption reduces manual retry logic

## Impact

- **agent-core**: `sdk/agents.py` — add `flavors` parameter (additive, backwards-compatible)
- **agent-docs-sync**: `agent.py`, `agents/*.py`, `tools/*.py` — refactor to use SDK helpers
- **Risk**: LOW — all changes are additive or internal refactoring
- **Dependencies**: No new dependencies
- **GitNexus**: `resilient_tool` and `build_toolkit` have 0 upstream callers — safe to modify
