# Spec Delta: SHB Observability and Telemetry

## Purpose

Establishes full-stack observability, OpenTelemetry instrumentation, centralized telemetry dashboards, and health polling services for Saigon - Hanoi Bank (SHB) microservices.

## ADDED Requirements

### Requirement: Centralized Telemetry and Dashboard Service
The `shb-observability` package SHALL collect OpenTelemetry traces, metrics, and structured logs across SHB agent runs and backend services, presenting aggregate operational health metrics via a dedicated dashboard.

#### Scenario: Telemetry ingestion and query
- **WHEN** an SHB service emits OTLP traces or structured logs to the collector endpoint
- **THEN** the collector ingests the spans, stores them in the local telemetry store, and renders them in the observability dashboard

### Requirement: Automated Health Polling and Service Watchdog
The system SHALL periodically poll health check endpoints of all active SHB microservices and agent runtimes, recording uptime status and triggering alerts on consecutive failures.

#### Scenario: Service outage detection
- **WHEN** a monitored banking service endpoint fails consecutive health checks
- **THEN** the health poller marks the service degraded and emits a structured incident payload for alerting

### Requirement: Command-Line Interface Entrypoints
The package SHALL provide executable command-line interfaces named `shb-observability-dashboard` and `shb-observability-poller` for manual diagnostics and continuous execution.

#### Scenario: Health poller invocation
- **WHEN** an operator runs `shb-observability-poller --interval 60`
- **THEN** the CLI runs continuous polling cycles across configured endpoints and outputs live statuses
