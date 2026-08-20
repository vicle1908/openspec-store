## MODIFIED Requirements

### Requirement: Langfuse OTel integration SHALL use get_client()

`configure_tracing()` SHALL call `langfuse.get_client()` to initialize Langfuse's built-in OTel integration. The returned `Langfuse` instance automatically registers as an OTel span processor on the global `TracerProvider`. There is NO separate `langfuse.opentelemetry` module — OTel support is built into the `Langfuse` class.

The `Langfuse` constructor supports filtering controls: `tracing_enabled`, `should_export_span`, `span_exporter`, `tracer_provider`, and `mask_otel_spans`. These are constructor-level controls — `get_client()` does not expose them.

Langfuse trace ingestion SHALL use exactly one mode: `direct` (default, SDK span processor via `get_client()`), `collector` (deferred — conditional on Phase 0 deployment validation), or `disabled`. The mode SHALL be determined at configuration time and SHALL NOT change at runtime.

#### Scenario: Langfuse receives agent traces via OTel

- **WHEN** Langfuse env vars are set (LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST) and an agent run completes
- **THEN** the trace SHALL appear in Langfuse with nested spans for agent run, model requests, and tool executions
- **AND** in `direct` mode, traces reach Langfuse via the SDK span processor registered by `get_client()`

#### Scenario: Langfuse not configured — graceful degradation

- **WHEN** Langfuse env vars are not set
- **THEN** `get_client()` SHALL return a Langfuse instance and no error SHALL be raised (tracing_enabled=False internally)

#### Scenario: Langfuse auth check

- **WHEN** Langfuse is configured but authentication fails
- **THEN** `langfuse.auth_check()` SHALL return False and a warning SHALL be logged

#### Scenario: Collector mode — deferred pending deployment validation

- **WHEN** Langfuse is configured with mode `collector`
- **THEN** trace ingestion via the Collector SHALL be validated in Phase 0 before implementation
- **AND** until validated, `collector` mode SHALL NOT be implemented
- **AND** `direct` mode SHALL be used as fallback

#### Scenario: Disabled mode

- **WHEN** Langfuse is configured with mode `disabled`
- **THEN** `Langfuse` SHALL be constructed with `tracing_enabled=False`
- **AND** no Langfuse trace export SHALL occur
- **AND** the application SHALL function normally

### Requirement: Langfuse agent graph view SHALL be available

With pydantic-ai's `Instrumentation` capability creating OTel spans, Langfuse SHALL display agent runs as node/edge graphs showing the hierarchy of agent run → model requests → tool executions.

#### Scenario: Agent graph renders in Langfuse UI

- **WHEN** an agent completes a multi-step run with tool calls
- **THEN** Langfuse SHALL display a graph view with the agent run as root node, model requests and tool executions as child nodes

### Requirement: Existing LangfuseClient.score_trace() SHALL be preserved

The manual `LangfuseClient` wrapper SHALL be retained for backward compatibility with hook-based scoring. In `direct` mode, the `LangfuseClient` SHALL share the same singleton instance returned by `get_client()` to prevent duplicate span processors. The implementation MUST verify that `LangfuseClient.create()` does not create a second trace-enabled client.

#### Scenario: Hook-based scoring still works

- **WHEN** `langfuse_hooks` in `builtins.py` calls `score_trace()`
- **THEN** the score SHALL be recorded on the trace in Langfuse
- **AND** no duplicate span processors SHALL be registered

### Requirement: propagate_attributes SHALL be available for metadata

The `langfuse.propagate_attributes` context manager SHALL be available for attaching `user_id`, `session_id`, `tags`, and `metadata` to traces.

#### Scenario: Custom metadata attached to trace

- **WHEN** `propagate_attributes(user_id=..., session_id=...)` is used within an agent run
- **THEN** the Langfuse trace SHALL include the specified user_id and session_id

## ADDED Requirements

### Requirement: Langfuse duplicate prevention

The system SHALL NOT allow the same trace to reach Langfuse via two different routes simultaneously. In `direct` mode, the SDK span processor SHALL be the sole trace ingestion path. Manual scoring via `LangfuseClient.score_trace()` SHALL reuse the same underlying Langfuse instance to prevent duplicate processors.

#### Scenario: Only one trace ingestion path active

- **WHEN** Langfuse is configured in `direct` mode
- **THEN** exactly one trace-ingestion path SHALL be active
- **AND** no duplicate trace records SHALL appear in Langfuse

### Requirement: Langfuse backend failure isolation

When Langfuse is unreachable, the failure SHALL NOT prevent span export to other backends or application shutdown. The flush attempt SHALL be bounded by the configured timeout.

#### Scenario: Langfuse unavailable does not block other exports

- **WHEN** Langfuse endpoint is unreachable during span export
- **THEN** spans SHALL still be exported to other configured backends
- **AND** the process SHALL exit normally within the shutdown timeout
