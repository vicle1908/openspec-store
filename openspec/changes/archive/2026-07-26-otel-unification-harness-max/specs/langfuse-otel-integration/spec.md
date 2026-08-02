## ADDED Requirements

### Requirement: Langfuse OTel integration SHALL use get_client()
`configure_tracing()` SHALL call `langfuse.get_client()` to initialize Langfuse's built-in OTel integration. The returned `Langfuse` instance automatically registers as an OTel span processor on the global `TracerProvider`. There is NO separate `langfuse.opentelemetry` module — OTel support is built into the `Langfuse` class.

**Verified API:**
```python
from langfuse import get_client
langfuse = get_client()  # reads LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST from env
```

**Langfuse constructor params (relevant):**
- `tracer_provider: TracerProvider | None = None` — custom provider (default: global)
- `should_export_span: Callable[[ReadableSpan], bool] | None = None` — span filter
- `blocked_instrumentation_scopes: ...` — scope blocklist

#### Scenario: Langfuse receives agent traces via OTel
- **WHEN** Langfuse env vars are set (LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST) and an agent run completes
- **THEN** the trace SHALL appear in Langfuse with nested spans for agent run, model requests, and tool executions

#### Scenario: Langfuse not configured — graceful degradation
- **WHEN** Langfuse env vars are not set
- **THEN** `get_client()` SHALL return a Langfuse instance and no error SHALL be raised (tracing_enabled=False internally)

#### Scenario: Langfuse auth check
- **WHEN** Langfuse is configured but authentication fails
- **THEN** `langfuse.auth_check()` SHALL return False and a warning SHALL be logged

### Requirement: Langfuse agent graph view SHALL be available
With pydantic-ai's `Instrumentation` capability creating OTel spans, Langfuse SHALL display agent runs as node/edge graphs showing the hierarchy of agent run → model requests → tool executions.

#### Scenario: Agent graph renders in Langfuse UI
- **WHEN** an agent completes a multi-step run with tool calls
- **THEN** Langfuse SHALL display a graph view with the agent run as root node, model requests and tool executions as child nodes

### Requirement: Existing LangfuseClient.score_trace() SHALL be preserved
The manual `LangfuseClient` wrapper SHALL be retained for backward compatibility with hook-based scoring. Trace ingestion moves to OTel, but manual score recording via `score_trace()` continues to work.

#### Scenario: Hook-based scoring still works
- **WHEN** `langfuse_hooks` in `builtins.py` calls `score_trace()`
- **THEN** the score SHALL be recorded on the trace in Langfuse

### Requirement: propagate_attributes SHALL be available for metadata
The `langfuse.propagate_attributes` context manager SHALL be available for attaching `user_id`, `session_id`, `tags`, and `metadata` to traces.

**Verified API:**
```python
from langfuse import propagate_attributes
with propagate_attributes(user_id="user-123", session_id="session-abc", tags=["agent"]):
    result = await agent.run(...)
```

#### Scenario: Custom metadata attached to trace
- **WHEN** `propagate_attributes(user_id=..., session_id=...)` is used within an agent run
- **THEN** the Langfuse trace SHALL include the specified user_id and session_id
