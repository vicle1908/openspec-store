## 1. Type Definition

- [x] 1.1 Define `WorkflowState` as TypedDict with `Annotated[list, operator.add]` reducers for `messages` in `orchestration/types.py`
- [x] 1.2 Update `NodeHandler` type alias to accept `WorkflowState` instead of `dict[str, Any]`
- [x] 1.3 Add `WorkflowStateDict` type alias for backward compatibility during migration

## 2. Engine Migration

- [x] 2.1 Update `WorkflowBuilder._compile()` to pass `state_schema=WorkflowState` to `StateGraph()`
- [x] 2.2 Remove `WorkflowState.to_dict()` and `from_dict()` methods (LangGraph handles serialization)
- [x] 2.3 Update `WorkflowEngine.run()` to use typed state directly instead of dict conversion
- [x] 2.4 Update `WorkflowEngine.resume()` to reconstruct typed state from checkpoint

## 3. Handler Updates

- [x] 3.1 Audit all existing node handler functions and update signatures to accept `WorkflowState`
- [x] 3.2 Update `_default_handler` to use typed state
- [x] 3.3 Update `_build_router` to use typed state in condition functions

## 4. Tests

- [x] 4.1 Update `tests/orchestration/test_orchestration.py` to use typed state
- [x] 4.2 Update `tests/orchestration/test_checkpointer.py` to verify checkpoint compat
- [x] 4.3 Add test: reducer semantics for `messages` append correctly
- [x] 4.4 Add test: resume from pre-migration checkpoint works

## 5. Validation

- [x] 5.1 Run `mypy agent_core/orchestration/ --strict` and verify zero errors
- [x] 5.2 Run `pytest tests/orchestration/ -x` and verify all tests pass
- [x] 5.3 Run `ruff check agent_core/orchestration/ && ruff format agent_core/orchestration/`
