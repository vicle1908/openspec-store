## Context

agent-core's orchestration layer (`agent_core/orchestration/`) provides `WorkflowBuilder` and `WorkflowEngine` that compile to LangGraph `StateGraph`. After upgrading to **LangGraph 1.2.9** (from 1.2.2) and **Pydantic AI 2.16.0** (via harness 0.10.0), the following new APIs are available.

**LangGraph 1.2.9 new/confirmed APIs** (all verified via live execution):
- `StateGraph.add_node(name, handler, *, retry_policy, cache_policy, error_handler, metadata, timeout, destinations, defer, input_schema)` — per-node config
- `StateGraph.compile(checkpointer, cache, store, interrupt_before, interrupt_after, transformers, name, debug)` — enhanced compilation
- `Command(goto, update, resume, graph)` + `Command.PARENT` — in-node routing with parent graph access
- `Send(node, arg)` — map-reduce fan-out with `Annotated[list, operator.add]` reducers
- `RetryPolicy(initial_interval, backoff_factor, max_interval, max_attempts, jitter, retry_on)` — per-node retry
- `CachePolicy(key_func, ttl)` — node-level caching
- `add_sequence([("name", handler), ...])` — sequential node addition
- `set_node_defaults(retry_policy, cache_policy, error_handler, timeout)` — graph-wide defaults
- **Per-node timeout**: async-only constraint (sync nodes cannot be safely cancelled)

**Key constraint discovered**: Per-node `timeout` only works for async nodes. Sync handlers will raise `ValueError` at compile time. Our `NodeHandler` type must support both sync and async.

**Official docs verified**: `https://docs.langchain.com/oss/python/langgraph/use-subgraphs` — two subgraph patterns confirmed (shared state + wrapper function).

## Goals / Non-Goals

**Goals:**
- Enable reusable workflow components via subgraph composition (both shared-state and wrapper-function patterns)
- Enable dynamic in-node routing via Command API (including `Command.PARENT` for parent graph access)
- Expose LangGraph 1.2.9 per-node features: `retry_policy`, `cache_policy`, `error_handler`, `metadata`, `timeout`
- Enable map-reduce fan-out via `Send` + `Annotated` reducers
- Maintain full backward compatibility

**Non-Goals:**
- Visual workflow debugging (LangGraph Studio)
- Runtime graph modification (graphs immutable after `build()`)
- Sync node timeout (LangGraph constraint — async only)

## Decisions

### Decision 1: Extend NodeDescriptor with 1.2.9 per-node config

Add fields to `NodeDescriptor` that map directly to `add_node()` params:
- `retry_policy: RetryPolicy | None` — per-node retry
- `cache_policy: CachePolicy | None` — per-node caching
- `error_handler: NodeHandler | None` — per-node error handler
- `metadata: dict[str, Any] | None` — per-node metadata
- `timeout: float | None` — per-node timeout (async only, validated at build time)

**Rationale**: These are direct 1.2.9 features that enhance workflow reliability and observability. Exposing them via `NodeDescriptor` keeps the declarative builder pattern consistent.

### Decision 2: Subgraph patterns — both shared-state and wrapper-function

The official LangGraph docs define two patterns:
1. **Shared state** (Pattern 1): Parent and subgraph share state keys → compiled graph passed directly to `add_node`
2. **Wrapper function** (Pattern 2): Different state schemas → wrapper function transforms state

Our spec supports both:
- `state_mapping=None` → Pattern 1 (shared state, compiled graph as node)
- `state_mapping=StateMapping(...)` → Pattern 2 (wrapper function with state translation)

### Decision 3: CommandResult with Command.PARENT support

`CommandResult` SHALL support `goto=Command.PARENT` for routing back to the parent graph from a subgraph node.

### Decision 4: async-first NodeHandler

`NodeHandler` SHALL support both sync and async handlers. The engine will detect async handlers and use `await` appropriately. Per-node timeout will only be applied to async handlers (LangGraph constraint).

## Risks / Trade-offs

- **Per-node timeout async-only** → Validate at build time; document constraint
- **CachePolicy key_func** → Default key function is sufficient for most cases; custom key_func available for advanced use
- **RetryPolicy retry_on** → Default catches all exceptions; custom filter available
- **NodeDescriptor field proliferation** → Many optional fields; mitigated by defaults
- **Command(update=...) with StateGraph(dict)** → `StateGraph(dict)` uses a single `__root__` channel; `Command(update={"key": val})` writes to individual channels that don't exist, so updates are silently ignored. Workaround: use typed state (TypedDict with `Annotated` reducers) for `Command` updates to take effect. The routing (`goto`) works correctly regardless.
