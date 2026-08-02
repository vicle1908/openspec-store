## Why

Agent-core's orchestration layer currently supports flat, single-level workflow graphs with static conditional routing (`EdgeCondition` enum + optional `condition_fn`). Two LangGraph features — **subgraphs** (nested graph composition) and the **Command API** (in-node dynamic routing) — would unlock significantly more powerful workflow patterns without adding new dependencies.

- **Subgraphs** enable reusable, composable workflow components (e.g., a review subgraph invoked from multiple pipelines). Currently, duplicating a workflow pattern requires copy-pasting node/edge definitions.
- **Command API** enables nodes to make runtime routing decisions (skip ahead, loop back, jump to error handler) without pre-declaring every conditional edge at graph build time.

Both features are supported natively by **LangGraph 1.2.9** (upgraded from 1.2.2) — verified via live API inspection. Additionally, LangGraph 1.2.9 brings per-node `RetryPolicy`, `CachePolicy`, `error_handler`, `metadata`, and async-only `timeout` — all wirable through `NodeDescriptor`. The gap is purely in agent-core's `WorkflowBuilder`/`WorkflowEngine` API surface.

## What Changes

- **Subgraph support**: Add `NodeKind.SUBGRAPH` enum value. Extend `NodeDescriptor` with optional `subgraph_engine` and `state_mapping` fields. Add `StateMapping` dataclass for explicit parent↔child state translation. Wire subgraph compilation in `WorkflowEngine._compile()`.
- **Command API bridge**: Add `CommandResult` dataclass as a framework-agnostic return type for dynamic routing. Update `NodeHandler` type alias to accept `CommandResult`. Wrap handlers in `_compile()` to translate `CommandResult` → LangGraph `Command`.
- **Dependencies**: `langgraph>=1.2.9` (upgraded from 1.2.2). No other new dependencies.

## Capabilities

### New Capabilities
- `orchestration-subgraphs`: Nested graph composition with state mapping
- `orchestration-command-api`: In-node dynamic routing via `CommandResult` return type bridged to LangGraph `Command`

### Modified Capabilities
- `agent-runtime` (existing): `NodeHandler` type alias broadened to accept `CommandResult`

## Impact

- **Code**: `agent_core/orchestration/types.py`, `agent_core/orchestration/graph.py`, `agent_core/orchestration/__init__.py`
- **Tests**: New test cases in `tests/orchestration/test_orchestration.py`
- **Dependencies**: None — uses existing `langgraph` package
- **Backward compat**: Fully backward-compatible — existing flat graphs and `dict`-returning handlers work unchanged
- **Non-goals**: Visual workflow debugging (LangGraph Studio), runtime graph modification, per-node timeout wiring
