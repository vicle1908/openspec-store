## Why

The orchestration module uses a plain `dict`-based `WorkflowState` that is serialized/deserialized manually via `to_dict()`/`from_dict()`. This provides no type safety, no runtime validation on state channels, and no merge semantics for list fields like `messages` and `results`. LangGraph supports `TypedDict` with `Annotated` reducers out of the box — this is the recommended pattern in the official docs and aligns with the Pydantic AI V2 typed-state conventions already used in agent-core's `_ai` module.

## What Changes

- `WorkflowState` dataclass replaced with a `TypedDict` using `Annotated[list, operator.add]` reducers for `messages` and `results`
- `StateGraph(dict)` upgraded to `StateGraph(WorkflowState)` with typed state schema
- Node handlers receive and return typed dicts instead of untyped dicts
- `to_dict()`/`from_dict()` replaced by direct TypedDict usage (LangGraph handles serialization)
- Checkpointing with `PostgresSaver` continues to work unchanged (TypedDict is compatible)

## Capabilities

### New Capabilities
- `typed-orchestration-state`: Typed state schema for LangGraph workflows with reducer semantics, runtime validation via Mypy strict mode, and backward-compatible migration from dict-based state

### Modified Capabilities
<!-- No existing capabilities are modified -->

## Impact

- **Code:** `agent_core/orchestration/types.py`, `agent_core/orchestration/graph.py`
- **Tests:** `tests/orchestration/test_orchestration.py`, `tests/orchestration/test_checkpointer.py`
- **Dependencies:** None (TypedDict + Annotated are stdlib)
- **Backward compatibility:** Node handler signatures change from `dict` to `WorkflowState` — all existing handlers must be updated but the change is mechanical
