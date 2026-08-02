## 1. Types — Extended NodeDescriptor & New Types

- [x] 1.1 Add `SUBGRAPH = "subgraph"` to `NodeKind` enum in `types.py`
- [x] 1.2 Add `StateMapping` dataclass with `input: dict[str, str]` and `output: dict[str, str]` to `types.py`
- [x] 1.3 Add `CommandResult` dataclass with `goto: str` and `update: dict[str, Any] | None = None` to `types.py`
- [x] 1.4 Extend `NodeDescriptor` with new fields: `subgraph_engine`, `state_mapping`, `retry_policy`, `cache_policy`, `error_handler`, `metadata` (all optional, default None)
- [x] 1.5 Update `NodeHandler` type alias in `graph.py` to `Callable[[WorkflowState], dict[str, Any] | CommandResult]`

## 2. Engine — Subgraph Compilation

- [x] 2.1 Add `_make_subgraph_handler()` private method to `WorkflowEngine` for wrapper-function pattern (state mapping)
- [x] 2.2 Add `_make_shared_state_subgraph_handler()` for shared-state pattern (compiled graph as node)
- [x] 2.3 Update `_compile()` to detect `NodeKind.SUBGRAPH` and dispatch to correct pattern based on `state_mapping`
- [x] 2.4 Add validation in `build()` that SUBGRAPH nodes have `subgraph_engine` set

## 3. Engine — Command API Bridge

- [x] 3.1 Add `_wrap_handler_for_command()` to detect `CommandResult` returns and translate to LangGraph `Command`
- [x] 3.2 Support `CommandResult(goto=Command.PARENT)` for parent graph routing
- [x] 3.3 Update `_compile()` to apply command wrapping to all handlers

## 4. Engine — LangGraph 1.2.9 Per-Node Features

- [x] 4.1 Wire `NodeDescriptor.retry_policy` to `add_node(retry_policy=...)` in `_compile()`
- [x] 4.2 Wire `NodeDescriptor.cache_policy` to `add_node(cache_policy=...)` in `_compile()`
- [x] 4.3 Wire `NodeDescriptor.error_handler` to `add_node(error_handler=...)` in `_compile()`
- [x] 4.4 Wire `NodeDescriptor.metadata` to `add_node(metadata=...)` in `_compile()`
- [x] 4.5 Wire `NodeDescriptor.timeout` to `add_node(timeout=...)` in `_compile()` with async-only validation

## 5. Exports & Public API

- [x] 5.1 Update `__init__.py` to export `StateMapping`, `CommandResult`, updated `NodeKind.SUBGRAPH`
- [x] 5.2 Update `__init__.py` to re-export `RetryPolicy`, `CachePolicy`, `Send` from `langgraph.types`

## 6. Tests

- [x] 6.1 Test `StateMapping` construction and field access
- [x] 6.2 Test `CommandResult` construction with and without `update`
- [x] 6.3 Test subgraph (shared state pattern) compiles and executes
- [x] 6.4 Test subgraph (wrapper pattern) with state mapping roundtrip
- [x] 6.5 Test subgraph error propagation sets `error` state field
- [x] 6.6 Test `CommandResult` handler routes to correct target node
- [x] 6.7 Test `CommandResult` with state update applies update before routing
- [x] 6.8 Test `CommandResult(goto=Command.PARENT)` routes to parent
- [x] 6.9 Test existing dict-returning handlers still work (backward compat)
- [x] 6.10 Test SUBGRAPH node without `subgraph_engine` raises `ValueError`
- [x] 6.11 Test per-node `retry_policy` wired to `add_node`
- [x] 6.12 Test per-node `cache_policy` wired to `add_node`
- [x] 6.13 Test per-node `error_handler` wired to `add_node`
- [x] 6.14 Test per-node `metadata` wired to `add_node`
- [x] 6.15 Test per-node `timeout` on async handler
- [x] 6.16 Test per-node `timeout` on sync handler raises `ValueError`

## 7. Validation

- [x] 7.1 Run `ruff check . --fix && ruff format .` from agent-core root
- [x] 7.2 Run `mypy src/agent_core/ --strict` — zero errors
- [x] 7.3 Run `pytest tests/orchestration/ -x` — all tests pass
- [x] 7.4 Run full `pytest -x` — no regressions (1 pre-existing failure in tests/memory/)
