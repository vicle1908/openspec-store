# tdt-compose-operational-readiness Specification

## Purpose

Defines the evidence-backed acceptance gate that proves the federated TDT Compose deployment builds, initializes, routes telemetry, persists state, and cleans up safely at exact source and image identities.

## Requirements

### Requirement: Acceptance evidence is run-scoped and identity-bound

Every acceptance run SHALL retain a machine-readable manifest containing the run identity, exact writable-repository HEADs and dirty-state classification, every read-only scheduler build or mount input's absolute path and source identity, Compose files and profiles, rendered services/networks/volumes/ports, image tags and digests, first-party build provenance, required architectures, state-root identity, resource measurements and budgets, commands, timestamps, results, diagnostics, and cleanup outcome.

#### Scenario: Acceptance run starts

- **WHEN** the readiness command begins
- **THEN** it SHALL record initial Git and Docker inventories before build or startup
- **AND** it SHALL fail closed if an owned input changes during the run

#### Scenario: Evidence omits a target repository identity

- **WHEN** the manifest lacks an exact identity for agent-core, tdt-scheduler, tdt-observability, or openspec-store
- **THEN** readiness SHALL remain failed

#### Scenario: Scheduler sibling input identity is absent

- **WHEN** the scheduler image copies or mounts a sibling repository or mobile workspace whose absolute path, revision or content fingerprint, and dirt classification are absent from the manifest
- **THEN** build and runtime readiness SHALL remain failed

#### Scenario: Deployed host service and image provenance requires post-commit redeploy

- **WHEN** host services or container images are evaluated for acceptance
- **THEN** deployment reports and acceptance manifests SHALL capture post-commit source revisions
- **AND** host services with pre-commit report identities SHALL be redeployed after the commit is finalized before acceptance is marked passed

### Requirement: Every supported model renders and every owner-local image builds

Readiness SHALL render `base`, `langfuse`, `mlflow`, and `full` observability profiles plus the coordinated owner services. It SHALL build each first-party image through its owning repository and verify its runtime import and non-root identity before starting integration acceptance.

#### Scenario: Static and build gates pass

- **WHEN** the candidate is evaluated from clean owner worktrees
- **THEN** all supported models SHALL render without warnings, undeclared services, unresolved paths, fixed container names, or unapproved images
- **AND** all first-party images SHALL pass locked build and import gates

#### Scenario: Compose rendering succeeds but build fails

- **WHEN** a Dockerfile references an unreachable context path or its runtime Python cannot import a locked dependency
- **THEN** readiness SHALL fail and SHALL not promote the render-only result

### Requirement: Runtime PostgreSQL bootstrap is verified on fresh state

The gate SHALL start the agent-core-owned PostgreSQL service on a fresh run-scoped PostgreSQL-18 volume, verify the exact server version, and verify all required logical databases and representative consumers before accepting the coordinated services.

#### Scenario: Fresh PostgreSQL bootstrap passes

- **WHEN** the candidate starts on an empty versioned volume
- **THEN** `SHOW server_version` SHALL report `18.6`
- **AND** `agent_core`, `tdt_scheduler`, `tdt_scheduler_dbos_sys`, and `agent_harness` SHALL exist
- **AND** agent-core, scheduler, and agent-harness connection probes SHALL pass

#### Scenario: Required logical database is absent

- **WHEN** any required database or connection probe is missing or failed
- **THEN** dependent service readiness SHALL fail with the missing database and owning initializer identified

### Requirement: Gateway readiness is proven by an external network-scoped probe

The gate SHALL run a disposable pinned probe container attached to the run-scoped observability network and query the Collector `health_check` extension at `http://otel-gateway:13133/`. The probe SHALL use bounded retries with a finite per-attempt timeout. The probe SHALL fail closed on timeout, connection failure, non-success HTTP response, or malformed result. The probe SHALL NOT rely on Docker container health status. The probe container SHALL use the run-scoped observability network name as its explicit `--network` argument. The probe command and result SHALL be recorded in the acceptance manifest using redacted structured fields; credential values or credential-bearing environment values SHALL NOT appear in evidence.

#### Scenario: Gateway readiness probe succeeds

- **WHEN** the `otel-gateway` service has started and its Collector `health_check` extension is ready
- **THEN** the probe container SHALL reach `http://otel-gateway:13133/` and the gate SHALL record `gateway_readiness.status=passed`

#### Scenario: Gateway readiness probe fails

- **WHEN** the `otel-gateway` service is not reachable at `http://otel-gateway:13133/` within the bounded retry window
- **THEN** the gate SHALL record `gateway_readiness.status=failed` with the error class and SHALL fail readiness
- **AND** the manifest SHALL retain the probe endpoint, network, attempt count, timeout, and redacted error summary

### Requirement: Stable gateway routing is proven for every profile

The gate SHALL emit uniquely identified telemetry through `otel-gateway:4317` for every supported profile and SHALL prove one configured route per selected backend using trace identity, Collector receiver/export metrics, and a bounded duplicate-detection window. It SHALL fail if a duplicate backend record is observed without claiming that OTLP transport provides exactly-once delivery.

#### Scenario: Base telemetry passes

- **WHEN** the base profile emits a trace, metric, and log record
- **THEN** all three signals SHALL be queryable in the appropriate LGTM backend
- **AND** no optional exporter SHALL be active

#### Scenario: Full telemetry passes without observed duplicates

- **WHEN** the full profile emits a uniquely identified agent trace
- **THEN** one matching trace SHALL be observed in Tempo, Langfuse, and MLflow during the bounded acceptance window
- **AND** no additional matching record SHALL be observed in that window
- **AND** the manifest SHALL retain the trace identifier, window, gateway counters, backend query results, and active route modes

### Requirement: Optional backend failures remain isolated

The gate SHALL exercise a bounded failure of each optional backend and prove that LGTM and any other selected healthy backend continue receiving telemetry without application failure or duplicate delivery.

#### Scenario: Langfuse is unavailable

- **WHEN** Langfuse is stopped during a full-profile telemetry probe
- **THEN** LGTM and MLflow export SHALL continue
- **AND** the gateway SHALL report a bounded Langfuse exporter failure without crashing

#### Scenario: MLflow is unavailable

- **WHEN** MLflow is stopped during a full-profile telemetry probe
- **THEN** LGTM and Langfuse export SHALL continue
- **AND** the gateway SHALL report a bounded MLflow exporter failure without crashing

### Requirement: Scheduler backup evidence is complete

The readiness gate SHALL verify the owner-managed scheduler backup service produces a bounded readable `pg_dump` artifact for the configured scheduler database and SHALL retain value-free checksum and source identity evidence.

#### Scenario: Scheduler backup evidence is complete

- **WHEN** the scheduler backup service is enabled
- **THEN** the manifest SHALL retain the bounded `pg_dump` artifact identity, checksum, source database, source revision, and readability probe
- **AND** a missing dump or checksum SHALL fail readiness

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

### Requirement: MLflow-only artifact and trace acceptance is independent

The MLflow profile SHALL prove SQL-backed tracing and persistent local artifact behavior using `--artifacts-destination /mlartifacts --serve-artifacts` and the versioned `mlflow-artifacts-3-data` volume without starting or resolving Langfuse, MinIO, or an S3 endpoint.

#### Scenario: MLflow-only workflow passes

- **WHEN** the gate starts the MLflow profile
- **THEN** an OTLP trace SHALL appear in the selected MLflow experiment
- **AND** an artifact SHALL upload, list, download, and match its original digest through the MLflow server

#### Scenario: MLflow profile depends on MinIO

- **WHEN** the rendered MLflow-only model contains a required `minio` hostname or Langfuse service
- **THEN** model validation SHALL fail

### Requirement: Health-poller acceptance proves configuration and cycle freshness

Health-poller readiness SHALL prove that the intended configuration loaded and that a poll cycle completed recently. Target service health SHALL be recorded separately and SHALL not be confused with poller process liveness.

#### Scenario: Mixed targets are polled

- **WHEN** host-native webhook-receiver and ai-review plus the Docker scheduler are available
- **THEN** the poller SHALL record one current observation for each target using the expected host-gateway or service-DNS address

#### Scenario: Poller process runs with stale cycles

- **WHEN** the poller process exists but no cycle has completed within the configured freshness threshold
- **THEN** the poller SHALL be reported unhealthy

### Requirement: Log-collector acceptance proves real host-log ingestion

Log-collector readiness SHALL append a unique supported record to a run-owned host log, observe the record through the canonical mounted log path, persist it to the events database, and verify restart-safe offset behavior.

#### Scenario: New host log record is ingested

- **WHEN** the gate appends a uniquely identified line to a supported run-owned log
- **THEN** the events store SHALL contain one matching normalized record
- **AND** the manifest SHALL record source path, event identity, and persisted state path

#### Scenario: Collector restarts

- **WHEN** the log collector restarts after persisting its offset
- **THEN** it SHALL not re-ingest the previously accepted record

### Requirement: Image and Collector validation is exact and multi-architecture

The gate SHALL inspect every pulled third-party image manifest for `linux/amd64` and `linux/arm64`, retain immutable digests, and validate every selected Collector configuration using the exact pinned Collector image. First-party local images SHALL retain source and base-image identity and SHALL pass native arm64 plus clean amd64 CI or buildx compatibility evidence without requiring publication.

#### Scenario: Required architecture is absent

- **WHEN** a selected image lacks either required platform
- **THEN** readiness SHALL fail before pull, build, or startup promotion

#### Scenario: Collector profile config is invalid

- **WHEN** the exact Collector binary rejects a receiver, processor, exporter, extension, endpoint, or environment expression
- **THEN** readiness SHALL fail and identify the profile and rejected field

### Requirement: Concurrent acceptance and cleanup preserve unrelated resources

The gate SHALL use unique projects, network names, state roots, volumes, and loopback host ports. Diagnostics SHALL precede cleanup, and teardown SHALL remove only run-owned resources while leaving unrelated projects and all unapproved legacy data intact.

#### Scenario: Two acceptance runs overlap

- **WHEN** two run identities execute concurrently on one Docker host
- **THEN** both SHALL complete without resource-name or port collision

#### Scenario: Failed run is cleaned up

- **WHEN** a run fails after creating resources
- **THEN** it SHALL retain failure diagnostics
- **AND** it SHALL remove only resources labeled or named for that run
- **AND** it SHALL leave pre-existing networks, images, volumes, containers, and host data unchanged

### Requirement: Readiness verdict distinguishes structural and runtime outcomes

The final report SHALL classify structural validation, image/build verification, runtime integration, data migration, and cleanup independently and SHALL emit an overall `success`, `partial`, or `blocked` verdict without promoting a structural-only pass.

#### Scenario: Runtime is unavailable

- **WHEN** Docker is unavailable but OpenSpec and Compose rendering pass
- **THEN** the report SHALL mark structural checks successful and runtime readiness blocked
- **AND** it SHALL not report the deployment ready
