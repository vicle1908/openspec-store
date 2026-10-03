# shb-observability-telemetry Specification Delta

## MODIFIED Requirements

### Requirement: Centralized Telemetry and Dashboard Service
The `shb-observability` package SHALL collect OpenTelemetry traces, metrics, and structured logs across SHB agent runs and backend services using `opentelemetry-api>=1.45.0`, propagating standard W3C `traceparent` headers across client requests, recording tool execution counters (`shb_agent_tool_calls_total`), and presenting aggregate operational health metrics via a dedicated dashboard.

#### Scenario: Telemetry ingestion and query
- **WHEN** an SHB service emits OTLP traces or structured logs to the collector endpoint
- **THEN** the collector ingests the spans, stores them in the local telemetry store, and renders them in the observability dashboard

#### Scenario: Distributed trace context propagation
- **WHEN** an agent executes a tool call requiring outbound HTTP banking communication
- **THEN** the request client SHALL inject the active OpenTelemetry trace context and `traceparent` header into the request

#### Scenario: Telemetry ingestion and metric recording
- **WHEN** an SHB service emits OTLP traces or tool execution metrics
- **THEN** the collector ingests the spans, updates metric counters, and renders them in the observability dashboard
