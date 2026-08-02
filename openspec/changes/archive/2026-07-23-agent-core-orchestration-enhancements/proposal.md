## Why

Agent-core's orchestration layer currently supports flat, single-level workflow graphs with static conditional routing. Two LangGraph features — **subgraphs** (nested graph composition) and the **Command API** (in-node dynamic routing) — would unlock significantly more powerful workflow patterns without adding new dependencies. Subgraphs enable reusable, composable workflow components (e.g., a review subgraph used in multiple pipelines). The Command API enables nodes to make runtime routing decisions without pre-declaring all conditional edges at graph build time. Both are already supported natively by the installed LangGraph v1.2.x — the gap is purely in agent-core's `WorkflowBuilder`/`WorkflowEngine` API surface.

## What Changes

- **Subgraph support**: Add `NodeKind.SUBGRAPH` to the node classification enum. Extend `WorkflowBuilder` with a `compose()` method that accepts a compiled `WorkflowEngine` as a nested subgraph node, with explicit state mapping between parent and child schemas.
- **Command API bridge**: Add `CommandResult` return type for node handlers. Detect `CommandResult` returns in `WorkflowEngine._compile()` and translate them to LangGraph's native `Command(goto=..., update=...)` for dynamic in-node routing.
- **State mapping types**: Add `StateMapping` dataclass to describe how parent state fields map to/from subgraph state fields.
- **No new dependencies**: Both features use LangGraph APIs already available in the installed v1.2.x.

## Capabilities

### New Capabilities
- `orchestration-subgraphs`: Nested graph composition with state mapping — `WorkflowBuilder.compose()`, `NodeKind.SUBGRAPH`, `StateMapping` types
- `orchestration-command-api`: In-node dynamic routing via `CommandResult` return type bridged to LangGraph `Command`

### Modified Capabilities
- `agent-runtime` (existing): `NodeHandler` type alias updated to accept `CommandResult` as a valid return type alongside `dict[str, Any]`

## Impact

- **Code changes**: `agent_core/orchestration/types.py` (new types), `agent_core/orchestration/graph.py` (builder/engine modifications), `agent_core/orchestration/__init__.py` (exports)
- **Tests**: New test cases in `tests/orchestration/test_orchestration.py` for subgraph composition and Command routing
- **Dependencies**: None — uses existing `langgraph` package
- **Backward compatibility**: Fully backward-compatible — existing flat graphs and `dict`-returning handlers work unchanged
- **Non-goals**: Visual workflow debugging (LangGraph Studio), dynamic graph modification at runtime, per-node timeout wiring (separate concern)
