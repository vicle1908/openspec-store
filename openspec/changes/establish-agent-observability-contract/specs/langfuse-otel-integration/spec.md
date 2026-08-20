## MODIFIED Requirements

### Requirement: Langfuse OTel integration SHALL use get_client()

`configure_tracing()` SHALL call `langfuse.get_client()` to initialize Langfuse's built-in OTel integration. The returned `Langfuse` instance automatically registers as an OTel span processor on the global `TracerProvider`. There is NO separate `langfuse.opentelemetry` module — OTel support is built into the `Langfuse` class.

Langfuse trace ingestion SHALL use exactly one configured route mode: `direct` (Langfuse SDK span processor via `get_client()`), `collector` (OTel Collector exporter), or `disabled`. The selected mode SHALL be determined at configuration time and SHALL NOT change at runtime. The default mode SHALL be `direct` unless deployment validation proves Collector ingestion is authoritative.

#### Scenario: Langfuse receives agent traces via OTel

- **WHEN** Langfuse env vars are set (LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST) and an agent run completes
- **THEN** the trace SHALL appear in Langfuse with nested spans for agent run, model requests, and tool executions

#### Scenario: Langfuse not configured — graceful degradation

- **WHEN** Langfuse env vars are not set
- **THEN** `get_client()` SHALL return a Langfuse instance and no error SHALL be raised (tracing_enabled=False internally)

#### Scenario: Langfuse auth check

- **WHEN** Langfuse is configured but authentication fails
- **THEN** `langfuse.auth_check()` SHALL return False and a warning SHALL be logged

#### Scenario: Direct mode active

- **WHEN** Langfuse is configured with mode `direct`
- **THEN** traces SHALL reach Langfuse via the Langfuse SDK span processor registered during initialization
- **AND** the `LangfuseClient` wrapper SHALL NOT duplicate trace ingestion

#### Scenario: Collector mode active

- **WHEN** Langfuse is configured with mode `collector`
- **THEN** traces SHALL reach Langfuse exclusively through the OTel Collector
- **AND** the direct SDK span processor SHALL NOT be registered for ingestion

#### Scenario: Disabled mode

- **WHEN** Langfuse is configured with mode `disabled`
- **THEN** no Langfuse trace export SHALL occur
- **AND** the application SHALL function normally

### Requirement: Langfuse agent graph view SHALL be available

With pydantic-ai's `Instrumentation` capability creating OTel spans, Langfuse SHALL display agent runs as node/edge graphs showing the hierarchy of agent run → model requests → tool executions.

#### Scenario: Agent graph renders in Langfuse UI

- **WHEN** an agent completes a multi-step run with tool calls
- **THEN** Langfuse SHALL display a graph view with the agent run as root node, model requests and tool executions as child nodes

### Requirement: Existing LangfuseClient.score_trace() SHALL be preserved

The manual `LangfuseClient` wrapper SHALL be retained for backward compatibility with hook-based scoring and shall remain available in all enabled Langfuse modes (`direct` and `collector`). Trace ingestion moves to the configured mode, but manual score recording via `score_trace()` continues to work independently.

#### Scenario: Hook-based scoring still works

- **WHEN** `langfuse_hooks` in `builtins.py` calls `score_trace()`
- **THEN** the score SHALL be recorded on the trace in Langfuse

#### Scenario: Scoring in collector mode

- **WHEN** `LangfuseClient.score_trace()` is called in `collector` mode
- **THEN** the score SHALL be recorded on the existing trace in Langfuse

### Requirement: propagate_attributes SHALL be available for metadata

The `langfuse.propagate_attributes` context manager SHALL be available for attaching `user_id`, `session_id`, `tags`, and `metadata` to traces.

#### Scenario: Custom metadata attached to trace

- **WHEN** `propagate_attributes(user_id=..., session_id=...)` is used within an agent run
- **THEN** the Langfuse trace SHALL include the specified user_id and session_id

## ADDED Requirements

### Requirement: Langfuse duplicate prevention

The system SHALL NOT allow the same trace to reach Langfuse via two different routes simultaneously. When `direct` mode is active, the Collector SHALL NOT export the same traces to Langfuse. When `collector` mode is active, the SDK span processor SHALL NOT ingest traces.

#### Scenario: Only one route active

- **WHEN** Langfuse is configured in any enabled mode
- **THEN** exactly one trace-ingestion path SHALL be active
- **AND** no duplicate trace records SHALL appear in Langfuse

### Requirement: Langfuse backend failure isolation

When Langfuse is unreachable, the failure SHALL NOT prevent span export to other backends or application shutdown. The flush attempt SHALL be bounded by the configured timeout.

#### Scenario: Langfuse unavailable does not block other exports

- **WHEN** Langfuse endpoint is unreachable during span export
- **THEN** spans SHALL still be exported to other configured backends
- **AND** the process SHALL exit normally within the shutdown timeout
