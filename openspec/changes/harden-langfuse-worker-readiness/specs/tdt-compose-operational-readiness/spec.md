## MODIFIED Requirements

### Requirement: Latest Langfuse dependency deviations pass behavioral acceptance

The gate SHALL run Langfuse `4.16.0` with Redis `8.10.1-alpine` and ClickHouse `26.7.5.10-alpine` and SHALL retain service versions, migration results, queue-aware worker readiness, representative queue work, v4 trace ingestion, analytics queries, restarts, and bounded error-log classification.

#### Scenario: Langfuse latest-image cohort passes

- **WHEN** web, worker, Redis, ClickHouse, MinIO, and PostgreSQL converge
- **THEN** Redis SHALL be healthy and the worker queue-readiness endpoint SHALL report consumption enabled and not stuck
- **AND** a trace SHALL ingest through the v4 route, a background queue job SHALL complete, and span-count aggregation, latency-percentile computation, and event-count-over-time queries SHALL return
- **AND** no selected container SHALL restart or emit a Redis, ClickHouse, BullMQ, socket-timeout, or compatibility error during the bounded acceptance window

#### Scenario: Deviation evidence is health-only

- **WHEN** containers are running or Docker-health green but no queue-readiness, queue-work, ingestion, migration, analytics, and error-window evidence is retained
- **THEN** compatibility acceptance SHALL fail as incomplete

#### Scenario: Worker is live but queue readiness fails

- **WHEN** the Langfuse worker process is running but queue consumption is stuck or its bounded readiness endpoint fails
- **THEN** the Langfuse or full profile SHALL remain not ready
- **AND** process liveness SHALL not be promoted as behavioral acceptance
