## Context

The orchestration module in agent-core uses a dict-based `WorkflowState` dataclass that is manually serialized to/from dicts for LangGraph's `StateGraph`. The current implementation:

```
WorkflowState (dataclass)
  → to_dict() → dict
  → StateGraph(dict) ← LangGraph
  → from_dict() ← LangGraph
```

This works but provides no type safety, no merge semantics for list fields, and relies on manual serialization. LangGraph natively supports `TypedDict` with `Annotated` reducers as state schemas.

## Goals / Non-Goals

**Goals:**
- Replace `WorkflowState` dataclass with TypedDict using `Annotated` reducers
- Enable LangGraph's built-in state channel management (no manual serialize/deserialize)
- Add Mypy strict-mode type checking for all state fields
- Maintain full backward compatibility with existing node handlers

**Non-Goals:**
- Adding new state fields beyond what exists today
- Changing the checkpointing backend (PostgresSaver stays)
- Adding Pydantic BaseModel validation at runtime (TypedDict + Mypy is sufficient)
- Changing the public `WorkflowResult` API

## Decisions

### Decision 1: TypedDict with Annotated reducers (not Pydantic BaseModel)

**Choice:** `TypedDict` with `Annotated[list, operator.add]` for list fields

**Rationale:**
- LangGraph's recommended pattern in official docs
- Zero runtime overhead (type hints only, no validation at runtime)
- Mypy strict catches schema drift at type-check time
- Pydantic BaseModel would add validation overhead on every state transition with no benefit — state channels are simple value types

**Alternatives considered:**
- Pydantic BaseModel: Overkill. Adds runtime validation cost, slower serialization, and doesn't integrate with LangGraph's reducer system as cleanly.
- Plain dict (status quo): No type safety, no merge semantics.

### Decision 2: Annotated reducers for messages and results

**Choice:** Use `Annotated[list, operator.add]` for `messages` and `results` fields

**Rationale:**
- When a node returns `{"messages": ["new_msg"]}`, LangGraph appends to the list instead of replacing
- This matches the current manual pattern where handlers append to lists
- `current_node`, `iteration`, `error`, `completed` use last-write-wins (default)

### Decision 3: Keep WorkflowResult as dataclass

**Choice:** `WorkflowResult` remains a dataclass (not TypedDict)

**Rationale:**
- `WorkflowResult` is the public API return type — it's not LangGraph state
- Dataclass gives better ergonomics (attribute access, defaults)
- No need to change the public contract

## Risks / Trade-offs

**[Risk] Node handler signatures change** → All existing handlers must accept `WorkflowState` (TypedDict) instead of `dict[str, Any]`. This is a mechanical change but touches every handler. Mitigation: grep for all `NodeHandler` usages and update in one pass.

**[Risk] Checkpoint compatibility** → Existing checkpoints in Postgres use dict-based state. New TypedDict state will serialize differently. Mitigation: PostgresSaver handles any dict-like state; old checkpoints will deserialize as dicts and be wrapped into TypedDict on resume. No data loss.

**[Risk] LangGraph version compatibility** → TypedDict state requires LangGraph >= 1.0 (already met — current dep is `>=1.2.1`).

## Migration Plan

1. Define `WorkflowStateTypedDict` as TypedDict with reducers in `types.py`
2. Update `NodeHandler` type alias to accept `WorkflowStateTypedDict`
3. Update all node handler functions to use typed state
4. Update `WorkflowBuilder._compile()` to pass `state_schema=WorkflowStateTypedDict`
5. Remove `to_dict()`/`from_dict()` methods (LangGraph handles serialization)
6. Update tests to use typed state
7. Keep old `WorkflowState` dataclass as deprecated alias for one release cycle

## Open Questions

- Should we add a `state_validate()` helper that runs Pydantic validation on state for debugging? (Low priority — Mypy catches most issues)
