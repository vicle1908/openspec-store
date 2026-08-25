## MODIFIED Requirements

### Requirement: Latest Langfuse dependency deviations pass behavioral acceptance

The gate SHALL run Langfuse `4.16.0` with Redis `8.10.1-alpine` and ClickHouse `26.7.5.10-alpine`. The web and worker Compose services SHALL each contain the fixed literal `REDIS_SOCKET_TIMEOUT_MS: "0"`, and the gate SHALL retain migration, strict worker queue-readiness, external composite readiness, representative queue work, v4 trace ingestion, analytics, restart classification, and bounded clean and fault/recovery evidence. On the measured 8-vCPU Docker Desktop baseline, LGTM SHALL be limited to 1.0 CPU, ClickHouse SHALL be limited to 1.5 CPUs, and ClickHouse health SHALL use a bounded local HTTP `/ping`.

#### Scenario: Langfuse latest-image cohort passes

- **WHEN** web, worker, Redis, ClickHouse, MinIO, and PostgreSQL converge on the approved image versions
- **THEN** Redis SHALL be running with existing Docker health `healthy`, and the worker strict endpoint SHALL return HTTP 200 with queue consumption enabled and `stuck: false`
- **AND** the external composite SHALL report ready only when the same-worker-network authenticated Redis probe succeeds and the existing worker container health is not unhealthy
- **AND** a v4 trace SHALL ingest, representative background queue work SHALL complete, and the required migration and analytics queries SHALL return
- **AND** the clean acceptance window SHALL contain zero Redis-version, command, BullMQ, socket-timeout, and unplanned-restart errors

#### Scenario: Fixed timeout policy is paired and non-overridable by planning inputs

- **WHEN** the Langfuse and full Compose profiles are rendered and their configuration sources are inspected
- **THEN** both web and worker SHALL contain the exact fixed Compose literal `REDIS_SOCKET_TIMEOUT_MS: "0"`
- **AND** no env template, tools configuration, or operator input SHALL be required or accepted as the source of that setting
- **AND** invented timeout variables and the legacy ingestion route SHALL be absent
- **AND** `LANGFUSE_BULLMQ_SKIP_REDIS_VERSION_CHECK` SHALL remain exactly `false`

#### Scenario: Redis interruption recovery is bounded

- **WHEN** a separately identified controlled Redis interruption lasting 60–120 seconds is followed by Redis restoration
- **THEN** the external composite SHALL report non-ready while the same-worker-network authenticated probe fails, even if the strict worker endpoint remains HTTP 200 because of recent activity
- **AND** composite readiness SHALL recover within the declared 120-second recovery budget only after three consecutive successful composite evaluations
- **AND** representative post-recovery queue work SHALL complete
- **AND** expected transient fault-interval errors SHALL be classified separately from the zero-error clean and post-recovery windows, with no unplanned restart or unbounded reconnect cadence accepted

#### Scenario: Deviation evidence is health-only

- **WHEN** containers are running or Docker health is green but composite readiness, queue work, ingestion, migration, analytics, or clean/fault evidence is missing
- **THEN** compatibility acceptance SHALL fail as incomplete

#### Scenario: Local resource pressure would starve readiness timers

- **WHEN** LGTM and ClickHouse background work contend with Langfuse worker, Redis, and verifier timers on the measured 8-vCPU Docker Desktop baseline
- **THEN** the selected Compose model SHALL enforce the measured 1.0/1.5 CPU limits for LGTM/ClickHouse
- **AND** ClickHouse health SHALL use a bounded lightweight local HTTP `/ping`
- **AND** promotion SHALL still require behavioral evidence rather than resource limits or health alone

#### Scenario: Worker liveness or queue readiness fails

- **WHEN** the worker process is running but its strict endpoint fails, reports stuck consumption, or the same-worker-network Redis probe fails
- **THEN** external composite readiness SHALL fail closed and the Langfuse or full profile SHALL remain not ready
- **AND** process liveness or a recent activity timestamp MUST NOT be promoted to behavioral acceptance

### Requirement: Langfuse OTLP fan-out remains exact and independently evidenced

The acceptance gate SHALL use the v4 route `/api/public/otel/v1/traces` with header `x-langfuse-ingestion-version: "4"`, SHALL prove exactly one unique trace event in each of `default.events_core` and `default.events_full`, and SHALL retain independent Collector, Tempo, and MLflow fan-out evidence. No legacy route, placeholder credential, or credential value SHALL be committed or recorded.

#### Scenario: Exact event and fan-out evidence passes

- **WHEN** one uniquely identified trace is sent through the selected Collector route
- **THEN** exactly one matching event SHALL be present in `default.events_core` and exactly one matching event SHALL be present in `default.events_full`
- **AND** Collector acceptance/export counters, Tempo receipt/HTTP evidence, and MLflow span receipt SHALL agree with the same run-scoped trace identity

#### Scenario: Event or fan-out evidence is incomplete

- **WHEN** the v4 route/header is configured but either event table or any required Collector, Tempo, or MLflow fan-out evidence is absent or mismatched
- **THEN** the acceptance gate SHALL remain blocked
