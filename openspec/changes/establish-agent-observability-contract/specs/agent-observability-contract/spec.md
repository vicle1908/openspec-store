## ADDED Requirements

### Requirement: Composition-root initialization

Every supported process entry point SHALL initialize the observability stack exactly once at its composition root. Library imports SHALL NOT initialize global telemetry. The initialization path SHALL be explicit and verifiable per entry point.

#### Scenario: CLI entry point initializes observability

- **WHEN** an agent-core CLI command executes
- **THEN** `init_observability(service_name="agent-core")` SHALL be called once before any agent construction
- **AND** the command name SHALL be recorded as an attribute on the root span (not as `service.name`)

#### Scenario: Consumer CLI entry point initializes observability

- **WHEN** a consumer CLI (e.g., `docs-sync`) executes
- **THEN** its composition root SHALL call `init_observability()` or `configure_tracing()` exactly once

#### Scenario: Library import does not initialize telemetry

- **WHEN** `agent_core.foundation`, `agent_core.sdk`, or `agent_core.observability` is imported
- **THEN** no OTel tracer provider, meter provider, or exporter SHALL be configured as a side effect

#### Scenario: Scheduler/worker entry point initializes observability

- **WHEN** a DBOS scheduler or Temporal worker process starts
- **THEN** observability SHALL be initialized at the process composition root before any workflow or agent registration

#### Scenario: Unconfigured telemetry degrades safely

- **WHEN** `init_observability()` is called with no OTel endpoint configured
- **THEN** a no-op tracer provider SHALL be used
- **AND** no error SHALL be raised
- **AND** the application SHALL function normally

### Requirement: Idempotent initialization

Repeated calls to `init_observability()` or `configure_tracing()` SHALL NOT add duplicate processors, exporters, or instrumentation registrations. The observable state after a second call SHALL be identical to the state after the first.

#### Scenario: Initialization called twice

- **WHEN** `init_observability()` is called twice in one process with the same service name
- **THEN** only one tracer provider, meter provider, instrumentation registration, and exporter pipeline SHALL be active
- **AND** duplicate spans SHALL NOT be emitted

#### Scenario: Initialization called with different service names

- **WHEN** `init_observability(service_name="a")` is called, then `init_observability(service_name="b")`
- **THEN** the first provider SHALL be retained
- **AND** a warning SHALL be logged indicating the conflicting service name
- **AND** no duplicate processors SHALL be added

### Requirement: Lifecycle completion

Short-lived processes (CLI commands, scripts) SHALL flush all pending spans, logs, and metric data before exiting. Long-running services SHALL shut down cleanly with the same guarantees. Backend failure SHALL NOT prevent application shutdown.

#### Scenario: CLI flush before exit

- **WHEN** an agent-core CLI command completes
- **THEN** all pending OTel spans SHALL be flushed and exported before process exit
- **AND** the flush SHALL complete within the configured shutdown timeout

#### Scenario: Scheduler worker shutdown

- **WHEN** a scheduler worker process receives SIGTERM
- **THEN** all pending spans and logs SHALL be flushed before process exit
- **AND** the flush SHALL complete within a configurable timeout (default 10 seconds)

#### Scenario: Backend failure does not block shutdown

- **WHEN** Langfuse or MLflow is unavailable during flush
- **THEN** the flush attempt SHALL be bounded by the configured timeout
- **AND** the process SHALL exit normally
- **AND** a warning SHALL be logged

### Requirement: Canonical correlation attributes

The system SHALL use the following authoritative attribute names. Backend-specific specs MAY extend these but SHALL NOT redefine them.

| Attribute | OTel Attribute | Description |
|-----------|---------------|-------------|
| Agent identity | `gen_ai.agent.name` | Human-readable agent name |
| Agent ID | `gen_ai.agent.id` | Unique agent identifier |
| Conversation/session | `gen_ai.conversation.id` | Thread or conversation identifier |
| Workflow | `agent_core.workflow.id` | Workflow/orchestration identifier |
| Run | `agent_core.run.id` | Unique run identifier |
| Budget | `agent_core.budget.id` | Budget or cost-control identifier |
-| Tool name | `gen_ai.tool.name` | Canonical tool name for agent tool executions |
| Tool success | `agent_core.tool.success` | Boolean: tool call succeeded |
| Tool duration | `agent_core.tool.duration_ms` | Tool execution wall-clock time |
| Operation name | `gen_ai.operation.name` | One of: `invoke_agent`, `chat`, `execute_tool`, `invoke_workflow` |

#### Scenario: Standard attributes present on all spans

- **WHEN** an agent run produces spans
- **THEN** each span SHALL carry `gen_ai.agent.name` and `gen_ai.agent.id`
- **AND** the root `invoke_agent` span SHALL carry `agent_core.run.id` and `agent_core.workflow.id` when applicable

#### Scenario: Extension attributes coexist with standard

- **WHEN** a tool execution span is emitted
- **THEN** it SHALL carry `gen_ai.tool.name` (standard) and MAY additionally carry `agent_core.tool.name`, `agent_core.tool.success`, and `agent_core.tool.duration_ms` (extension)

### Requirement: Trace-log correlation

Structured log entries produced during an active OTel span SHALL include the current `trace_id` and `span_id`. This enables linking log entries to specific traces in Langfuse, Grafana, and other backends.

#### Scenario: Log entry includes trace context

- **WHEN** `structlog.info("tool_executed", ...)` is called inside an active OTel span
- **THEN** the JSON log output SHALL include `trace_id` and `span_id` fields
- **AND** these fields SHALL match the active span's trace and span identifiers

#### Scenario: Log entry outside active span

- **WHEN** `structlog.info("startup")` is called before any span is started
- **THEN** `trace_id` and `span_id` SHALL be omitted or set to empty strings
- **AND** no error SHALL be raised

### Requirement: Evaluation-to-trace linkage

Evaluation records stored in `agent_memory.eval_metrics` SHALL include optional `trace_id` and `span_id` columns. When a trace is active during evaluation, these fields SHALL be populated.

#### Scenario: Evaluation with active trace

- **WHEN** an evaluation runs while an OTel span is active
- **THEN** `EvalRecord.trace_id` SHALL be set to the active trace ID
- **AND** `EvalRecord.trace_id` and `span_id` SHALL be populated from `EvaluationReport.trace_id` and `EvaluationReport.span_id`

#### Scenario: Evaluation without active trace

- **WHEN** an evaluation runs outside any OTel span context
- **THEN** `EvalRecord.trace_id` SHALL be `None`
- **AND** `EvalRecord.span_id` SHALL be `None`
- **AND** the evaluation SHALL still be recorded successfully

### Requirement: Privacy defaults

Content capture (prompts, completions, tool arguments, tool results) SHALL be OFF by default. Known credential patterns—API keys, tokens, and passwords—SHALL be redacted before export when `capture_sensitive_payloads` is True. Generalized PII classification is follow-up scope. Binary content SHALL be excluded by default.

#### Scenario: Default privacy settings

- **WHEN** no privacy-related environment variables are set
- **THEN** `include_content` SHALL be `False`
- **AND** `capture_sensitive_payloads` SHALL be `False`
- **AND** `include_binary_content` SHALL be `False`
- **AND** `include_model_request_parameters` SHALL be `True`

#### Scenario: Content capture with minimum secret redaction

- **WHEN** `capture_sensitive_payloads=true` is set
- **THEN** prompts and tool arguments MAY appear in span attributes
- **AND** minimum secret redaction (API keys, tokens, passwords) SHALL be applied before export
- **AND** generalized PII classification and tenant-specific redaction are follow-up scope

#### Scenario: Content capture enabled

- **WHEN** `OTEL_INCLUDE_CONTENT=true` is set
- **THEN** prompt and completion text SHALL appear in span attributes
- **AND** `capture_sensitive_payloads` settings SHALL still apply for redaction

### Requirement: Exporter topology and duplicate prevention

Each backend (Langfuse, MLflow) SHALL have exactly one authoritative ingestion route. The system SHALL NOT allow the same trace to reach a backend via two different routes simultaneously.

#### Scenario: Langfuse trace ingestion route is explicit

- **WHEN** Langfuse is configured
- **THEN** exactly one trace-ingestion route SHALL be active (direct SDK span processing or Collector export)
- **AND** the selected route SHALL be validated at startup
- **AND** manual scoring via `LangfuseClient.score_trace()` SHALL remain available independently

#### Scenario: MLflow trace ingestion route is explicit

- **WHEN** MLflow is configured
- **THEN** exactly one trace-ingestion route SHALL be active (autolog SDK or Collector export)
- **AND** the selected route SHALL be validated at startup
- **AND** no duplicate trace records SHALL be produced

#### Scenario: Backend failure isolation

- **WHEN** the Langfuse exporter fails
- **THEN** MLflow traces SHALL NOT be affected
- **AND** application traces SHALL still be exported to OTel Collector
- **AND** a warning SHALL be logged

### Requirement: Extensibility for future span types

The canonical attribute schema and lifecycle contract SHALL be designed to accommodate future span types including but not limited to: memory R/W spans, MCP tool-call spans, DBOS workflow spans, agent handoff spans, and skill resolution spans. Adding new span types SHALL NOT require changing this contract's lifecycle or correlation requirements.

#### Scenario: Future span type conforms to contract

- **WHEN** a new span type (e.g., `memory.read`) is added to agent-core
- **THEN** it SHALL carry the canonical correlation attributes
- **AND** it SHALL be flushed through the same exporter pipeline
- **AND** it SHALL NOT require changes to `init_observability()` or the lifecycle contract

Note: Memory, MCP, DBOS, and handoff span instrumentation are explicit non-goals for this change. Cross-language propagation validation is deferred to a separate change.

### Requirement: Conformance evidence classifications

Every observability capability SHALL be classified across the following evidence levels. No deployment-readiness claim SHALL be made without backend evidence.

| Level | Definition |
|-------|-----------|
| **Specified** | Requirement exists in an OpenSpec spec |
| **Implemented** | Code exists in source |
| **Unit-tested** | Automated test covers the behavior |
| **Integration-tested** | Test exercises the real integration path |
| **Runtime-validated** | Verified against running process with real backend |
| **Deployment-validated** | Verified in target deployment environment |

#### Scenario: Capability without runtime validation

- **WHEN** a capability is specified, implemented, and unit-tested
- **THEN** its evidence level SHALL be reported as "unit-tested"
- **AND** it SHALL NOT be reported as "deployment-validated"
