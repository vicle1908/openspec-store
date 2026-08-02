# agent-core pydantic-ai v2.9 Migration — Proposal

## Why

`agent-core` declares `pydantic-ai>=1.103.0,<2` as a dependency but implements its own agent runtime — custom ReAct loop, gateway, tool registry, and hooks — from scratch. Pydantic-ai v2.9 is now stable (released 2026-07-10) and ships production-grade primitives that subsume all of our custom code: `Agent`, `@agent.tool()`, `RunContext`, `AgentDepsT`, the model system, hooks, capabilities, and streaming UI adapters.

Migrating to v2.9 gives us:
- **Durable execution** and fault-tolerant agent runs for free
- **Native MCP** and UI adapter integrations (AG-UI, Vercel AI) without bespoke adapters
- **pydantic-graph** for complex orchestration graphs
- **Built-in evals** framework for systematic agent testing
- **Active maintenance** from the Pydantic team vs our hand-rolled loop

The migration is bounded: only `agent-core` changes; consumer repos (`ai-review`, `code-daily-scan`, CLI, examples) require **zero changes** because the public API (`BaseAgent`, `Flavor`, `HookRegistry`, `AgentRequest`, `AgentResult`) is preserved as a frozen contract.

## What Changes

- **`pyproject.toml`**: Bump `pydantic-ai>=2.9.0,<3`
- **New `_ai/` internal package**: All pydantic-ai v2 types confined here — `AgentRuntime`, model adapters, tool adapter, hook adapter
- **`llm_gateway/gateway.py`**: Bifrost/LiteLLM implementations delegate to `_ai/models.py`; expose `get_model()` for `BaseAgent`
- **`agent_base/agent.py`**: Custom `_react_loop()` deleted; `BaseAgent` wraps `AgentRuntime`
- **`tool_registry/`**: Full replacement — 7 built-in tools re-implemented as `@agent.tool()`; thin `ToolRegistryFacade` retained for compatibility
- **`agent_base/hooks/`**: `HookRegistry` facade wires to pydantic-ai v2 hooks via `HookAdapter`
- **`Flavor` system**: Facade maps to `agent.instructions` + tool allowlists
- **`memory/`**, **`orchestration/`**, **`resilience/`**, **`foundation/`**: Unchanged

## Problem

`agent-core` has accumulated a significant maintenance burden maintaining functionality that pydantic-ai v2 solves natively. The custom ReAct loop lacks durable execution, structured streaming, tool call introspection, and the observability primitives that pydantic-ai ships with. Every new pydantic-ai v2 feature (MCP adapters, UI streams, evals) requires bespoke integration work instead of being available by default.

Additionally, the v1 `pydantic-ai` constraint (`<2`) means we are stuck on a deprecated API surface. Pydantic-ai v2 was released in 2025 and is now at v2.9 — we are running ancient code by AI framework standards.

## Change

Replace the internal agent runtime of `agent-core` with pydantic-ai v2.9 primitives, confined to a private `_ai/` package. The public API contract is unchanged so all consumers and examples work without modification.

## Scope

**In scope:**
- `agent-core/src/agent_core/` — migration of agent, gateway, tools, hooks
- `agent-core/pyproject.toml` — dependency update
- `agent-core/examples/` — update examples to exercise new internals
- `agent-core/tests/` — update tests for new internal layer
- `tdt-meta/openspec/changes/agent-core-pydantic-ai-v2-migration/` — change artifacts

**Out of scope:**
- `ai-review/`, `code-daily-scan/`, `webhook-receiver/`, CLI repos — zero changes required
- `agent-core/memory/`, `orchestration/`, `resilience/`, `foundation/` — independent layers
- `poems-mobile3-ios/`, `poems-mobile3-android/`, `mcp-router/` — non-Python repos
- Any changes to `tdt-core/` SDK

## Non-goals

- No consumer API migration. `BaseAgent`, `Flavor`, `HookRegistry` stay as-is.
- No removal of built-in tools. All 7 survive, re-implemented as `@agent.tool()`.
- No migration of `memory/` or `orchestration/` to pydantic-ai equivalents (pydantic-graph, memory). These are future work.
- No adoption of pydantic-ai MCP adapters, UI adapters, or evals in this change. These require separate design.

## Success criteria

1. `ruff check . --fix && ruff format .` passes
2. `mypy src/agent_core --strict` passes
3. `pytest` passes with existing coverage threshold maintained
4. No `from pydantic_ai import` at runtime outside `src/agent_core/_ai/` (enforced by ruff `TC002`)
5. `examples/minimal_agent.py` runs successfully end-to-end
6. `examples/flavor_composition.py` runs successfully end-to-end
7. `ai-review/` test suite passes with zero code changes
8. `code-daily-scan/` test suite passes with zero code changes
9. OpenSpec change validates with `openspec validate --strict`
10. CHANGELOG entry added to `agent-core/CHANGELOG.md`

## Design

See `design.md` and the full design spec at `tdt-meta/docs/superpowers/specs/2026-07-13-agent-core-pydantic-ai-v2-migration.md`.

## Repos touched

- `agent-core/` — primary migration target
- `tdt-meta/` — OpenSpec change artifacts + design spec document

## Integration with TDT patterns

- Uses `tdt_core.env.load_tdt_env()` for any settings accessed during migration
- Follows OpenSpec v1.4.1 conventions: kebab-case name, `proposal.md` + `design.md` + `specs/` + `tasks.md`, RFC 2119 requirements
- Binds to existing patterns: `_ai/` internal package follows the same isolation principle as other TDT internal layers
- No changes to `~/.tdt/` configuration or Docker compose

## Deployment

- No Docker changes
- No DBOS scheduled workflow changes
- Only source code and dependency changes in `agent-core/`
- Rollback: revert the commit; all consumers are unaffected

## Timeline

~20–30 hours of focused work across 5–6 sessions. Each phase (scaffold, agent runtime, tools, hooks, consumer smoke) is independently verifiable.

`★ Insight ─────────────────────────────────────`
Key architectural findings from codebase research:
1. Examples call `LLMGateway()` with no args — this would raise `TypeError` (ABC with no implementation). The correct usage is `create_gateway()` or `BifrostGateway(...)`. `_ai/models.py` needs `create_model_from_env()` for the env-based path.
2. There are 7 built-in tools, not 6 — ShellTool is the 7th (registered as `shell_execute`).
3. `approval_gate` uses `requires_approval=True` on `@agent.tool()` — pydantic-ai v2 has this built-in. Simpler than `AbstractCapability`.
4. The `pydantic_ai.Hooks` capability uses decorator registration (`@hooks.on.before_model_request`), which is a different pattern than our `HookRegistry.register(point, phase, fn)`. Hooks must be registered BEFORE `AgentRuntime` is constructed.
5. `BudgetTracker` is a thread-safe singleton that wraps every gateway call — this pattern stays. pydantic-ai's `UsageLimits` is per-run and doesn't cover cost ceilings.
6. `AgentThought` is publicly exported in `agent_base/__init__.py` — it stays. Never part of `AgentResult` contract.
7. `HookError` is publicly exported in `foundation/__init__.py` — it stays.
8. `BaseAgent.run(output_schema=...)` is a consumer-facing parameter. Maps to pydantic-ai `Agent`'s `output_type` parameter.
9. Custom tool registration (`registry.register(CustomTool())`) is used by `examples/custom_tool.py`. `BaseAgent.__init__()` must collect ALL tools from `ToolRegistry` at construction.
10. `FlavorToolPolicy.require_approval` maps to `@agent.tool(requires_approval=True)` for listed tool names.
`─────────────────────────────────────────────────`

## Open questions

1. **TC002 enforcement → RESOLVED**: Add `"src/agent_core/_ai/*" = ["TC002"]` to `[tool.ruff.lint.per-file-ignores]` in `pyproject.toml`. No separate `ruff.toml`.
2. **Memory integration → OUT OF SCOPE**: Future work. Memory managed independently by consumer repos.
3. **Evals → OUT OF SCOPE**: Future work. `pydantic_evals` integration noted for later.
4. **LLMGateway() no-arg → RESOLVED**: Both examples call `LLMGateway()` (the ABC) with no args. This raises `TypeError` at runtime today. This is a pre-existing example bug, NOT introduced by migration. Migration does NOT fix this. Correct usage is `create_gateway()` or `BifrostGateway(...)`.
5. **`iterations` in AgentResult → RESOLVED**: Computed from `result.usage.requests` on pydantic-ai `RunResult`.
6. **`AgentThought` stays → RESOLVED**: Publicly exported in `agent_base/__init__.py.__all__`. Used internally by `_react_loop()` but never in `AgentResult` contract. Stays.
7. **`HookError` stays → RESOLVED**: Publicly exported in `foundation/__init__.py.__all__`. Not touched by this migration.
8. **Approval gate → RESOLVED**: Use `@agent.tool(requires_approval=True)` — pydantic-ai v2 native. Existing `approval_gate()` function stays with updated implementation.
9. **Hook registration order → RESOLVED**: Decorator-based (`@hooks.on.*`) must precede `Agent` construction. Execution order: (1) `HookRegistry`, (2) `HookAdapter`, (3) `AgentRuntime`.
10. **`output_schema` → RESOLVED**: `BaseAgent.run(output_schema=...)` maps to pydantic-ai `Agent`'s `output_type` parameter.
11. **Custom tool registration → RESOLVED**: `BaseAgent.__init__()` reads `registry.list_tools()` to collect ALL tools (builtins + consumer-registered) for `AgentRuntime`. `ToolRegistry.register()` itself is NOT modified.
12. **`FlavorToolPolicy.require_approval` → RESOLVED**: Maps to `@agent.tool(requires_approval=True)` for listed tool names.
