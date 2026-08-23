## Purpose

Defines the federated, reproducible local Docker deployment for TDT runtime and observability services, including ownership, image identities, telemetry routing, persistence, security, and lifecycle boundaries.

## ADDED Requirements

### Requirement: Repository-owned Compose projects form one coordinated deployment

The local TDT deployment SHALL preserve repository ownership: `agent-core` SHALL own its application and shared runtime PostgreSQL services, `tdt-scheduler` SHALL own its scheduler and backup services, and `tdt-observability` SHALL own LGTM, the OTel gateway, health-poller, log-collector, Langfuse, and MLflow services. A tdt-observability-owned operator command SHALL coordinate the owner-defined projects without redefining the agent-core or scheduler services in tdt-observability Compose files.

#### Scenario: Operator starts the coordinated deployment

- **WHEN** an operator invokes the supported stack-up command for a selected profile
- **THEN** it SHALL build or select each image through its owning repository
- **AND** it SHALL start the required owner-defined Compose projects in dependency order
- **AND** it SHALL report the selected projects, profile, networks, ports, source revisions, and image identities

#### Scenario: Duplicate service definition is introduced

- **WHEN** a tdt-observability Compose model defines an `agent-core`, `scheduler`, or `postgres-backup` service already owned by another repository
- **THEN** model validation SHALL fail before any container or network is created

### Requirement: Supported observability profiles are explicit

The deployment SHALL support exactly four observability profiles: `base` for LGTM-only export, `langfuse` for LGTM plus Langfuse, `mlflow` for LGTM plus MLflow, and `full` for LGTM plus both optional backends. The selected profile SHALL determine the required services and one validated OTel gateway configuration.

#### Scenario: Base profile is selected

- **WHEN** the operator selects `base`
- **THEN** LGTM and the OTel gateway SHALL start
- **AND** Langfuse, MLflow, Redis, ClickHouse, MinIO, and their backend databases SHALL not start

#### Scenario: MLflow profile is selected independently

- **WHEN** the operator selects `mlflow`
- **THEN** MLflow and its PostgreSQL and local artifact volumes SHALL start without requiring Langfuse or MinIO

#### Scenario: Unsupported profile is requested

- **WHEN** the operator supplies a profile outside `base`, `langfuse`, `mlflow`, or `full`
- **THEN** the command SHALL exit non-zero before Docker mutation
- **AND** it SHALL list the supported profiles

### Requirement: One stable OTel gateway is the authoritative producer endpoint

Every containerized TDT telemetry producer SHALL export OTLP to the single service endpoint `http://otel-gateway:4317`. The gateway SHALL always export selected telemetry to LGTM and SHALL add only the optional exporters named by the active profile. Each backend SHALL be configured through exactly one authoritative route. Because OTLP export is retrying and at-least-once, acceptance SHALL use a unique trace identity and bounded observation window to detect and reject observed duplicates without claiming protocol-level exactly-once delivery.

#### Scenario: Full profile uses one route to every backend

- **WHEN** a producer emits one trace while the `full` profile is active
- **THEN** LGTM, Langfuse, and MLflow SHALL each be reachable only through the selected gateway configuration
- **AND** no direct SDK, autolog, or alternate collector route SHALL be active
- **AND** acceptance SHALL fail if more than one matching backend record is observed within the bounded window

#### Scenario: Collector route cannot initialize

- **WHEN** a coordinated profile selects Collector mode but the gateway endpoint or selected backend exporter cannot validate
- **THEN** the producer SHALL fail closed for that route
- **AND** it SHALL not fall back to direct Langfuse processing, MLflow autolog, or an unselected endpoint

#### Scenario: Optional exporter is absent

- **WHEN** the `base` profile is active
- **THEN** the loaded gateway configuration SHALL not contain Langfuse or MLflow exporters
- **AND** the gateway SHALL not log retries for intentionally absent backends

#### Scenario: Optional backend fails

- **WHEN** Langfuse or MLflow becomes unavailable in a profile that selects it
- **THEN** gateway export to LGTM and every other healthy selected backend SHALL continue
- **AND** the failed exporter SHALL emit bounded actionable diagnostics

### Requirement: Deployment images use the latest verified exact release baseline

The deployment SHALL use the exact release tags verified on 2026-08-22: `python:3.14.7-slim-trixie`, `ghcr.io/astral-sh/uv:0.12.5`, `postgres:18.6-trixie`, `grafana/otel-lgtm:0.31.0`, `otel/opentelemetry-collector-contrib:0.159.0`, `langfuse/langfuse:4.16.0`, `langfuse/langfuse-worker:4.16.0`, `redis:8.10.1-alpine`, `clickhouse/clickhouse-server:26.7.5.10-alpine`, `minio/minio:RELEASE.2025-09-07T16-13-09Z`, `minio/mc:RELEASE.2025-08-13T08-35-41Z`, and `ghcr.io/mlflow/mlflow:v3.15.1`. Every pulled third-party image MUST expose both `linux/amd64` and `linux/arm64` manifests before promotion. First-party local images SHALL retain exact source and base-image provenance and SHALL pass arm64 local build plus amd64 clean-CI or buildx compatibility evidence; publication is not required for this local deployment.

#### Scenario: Exact image inventory is rendered

- **WHEN** any supported profile is rendered
- **THEN** every selected image SHALL match the approved exact tag
- **AND** no selected service SHALL use `latest`, a major-only tag, or an unrecorded fallback tag

#### Scenario: A newer release is proposed later

- **WHEN** an operator updates an approved image pin
- **THEN** the update SHALL re-resolve the latest upstream release at that time
- **AND** it SHALL record release provenance, both required architectures, compatibility evidence, and any state migration before replacing this baseline

#### Scenario: Latest source release has no published image

- **WHEN** an upstream source release does not have a pullable official multi-architecture image
- **THEN** the deployment SHALL retain the newest pullable official exact image tag
- **AND** the evidence SHALL record the newer unavailable source release and the selected image exception

#### Scenario: Canonical root requires reconciliation to Redis 8.10.1

- **GIVEN** the approved deployment baseline requires `redis:8.10.1-alpine`
- **WHEN** unpromoted or dirty canonical checkouts retaining older Redis 8.10.0 images are evaluated
- **THEN** they SHALL be classified as unpromoted implementation state
- **AND** the deployment SHALL NOT be promoted or accepted until the canonical root is reconciled to `redis:8.10.1-alpine`

### Requirement: Redis 8 and ClickHouse 26 compatibility is proven with Langfuse

Because Langfuse `4.16.0` publishes Redis 7 and ClickHouse 25.12 as its default Compose baseline, the selected Redis `8.10.1` and ClickHouse `26.7.5.10` images SHALL be treated as explicit compatibility deviations. Promotion MUST require fresh Langfuse migration, queue, ingestion, worker, and no-error evidence under those exact images.

#### Scenario: Redis 8 compatibility passes

- **WHEN** Langfuse web and worker run against Redis `8.10.1-alpine`
- **THEN** authentication, ingestion, queue production, queue consumption, retry, and scheduled background work SHALL complete
- **AND** web and worker logs SHALL contain no Redis-version, command, BullMQ, or restart failure

#### Scenario: BullMQ version gate is evaluated explicitly

- **WHEN** Langfuse first runs against Redis 8
- **THEN** `LANGFUSE_BULLMQ_SKIP_REDIS_VERSION_CHECK` SHALL remain false and the real BullMQ version gate SHALL be observed
- **AND** setting it true SHALL require a separately retained exception proving queue behavior and identifying the version check as the only failure

#### Scenario: ClickHouse 26 compatibility passes

- **WHEN** Langfuse `4.16.0` initializes against ClickHouse `26.7.5.10-alpine`
- **THEN** all migrations SHALL complete
- **AND** trace ingestion and representative analytics queries SHALL pass
- **AND** logs SHALL contain no unsupported-version, analyzer, missing-column, or migration error

#### Scenario: Compatibility deviation fails

- **WHEN** either Redis 8 or ClickHouse 26 acceptance fails
- **THEN** the deployment SHALL remain blocked
- **AND** it SHALL not silently fall back to a different image than the approved inventory

### Requirement: Owner-local Python images are locked, non-root, and reproducible

Each first-party Python image SHALL build through its owning repository from declared build contexts, SHALL use the repository lockfile without re-resolving dependencies, SHALL put the synchronized environment on the runtime `PATH`, and SHALL execute as a non-root user. Health-poller and log-collector SHALL use one shared tdt-observability image identity with different commands.

#### Scenario: Clean owner-local build succeeds

- **WHEN** agent-core, scheduler, or tdt-observability is built from a clean checkout at the recorded revision
- **THEN** all declared sibling inputs SHALL remain within explicit build contexts
- **AND** locked dependency synchronization and an import integrity gate SHALL pass

#### Scenario: Runtime bypasses the synchronized environment

- **WHEN** an entrypoint invokes a Python interpreter that cannot import the locked project dependency closure
- **THEN** image verification SHALL fail before the image is accepted or tagged

### Requirement: Runtime PostgreSQL remains agent-core owned

The shared TDT runtime PostgreSQL service, its PostgreSQL-18 versioned volume, and its logical-database initializers SHALL remain owned by agent-core. The coordinated deployment SHALL create and verify the `agent_core`, `tdt_scheduler`, `tdt_scheduler_dbos_sys`, and `agent_harness` databases without defining a duplicate runtime PostgreSQL service in tdt-observability. Langfuse and MLflow SHALL retain isolated PostgreSQL-18 versioned volumes owned by their optional backends.

#### Scenario: Fresh runtime database volume initializes

- **WHEN** agent-core PostgreSQL starts with a fresh versioned PostgreSQL 18 volume
- **THEN** all four required logical databases SHALL exist before dependent acceptance runs
- **AND** scheduler, agent-core, and agent-harness connection checks SHALL pass

#### Scenario: Duplicate runtime PostgreSQL is rendered

- **WHEN** a tdt-observability profile renders a second generic runtime `postgres` service
- **THEN** model validation SHALL fail
- **AND** no ambiguous `postgres` DNS target SHALL be accepted

### Requirement: TDT home mounts preserve canonical layout with least privilege

Container bind sources and targets SHALL preserve `$TDT_HOME/<kind>/<app>/<name>` semantics. Host-source resolution SHALL use a host-root value that defaults correctly when `TDT_HOME` is absent, while container processes SHALL use an explicit container root. Health-poller and log-collector SHALL receive only required observability state, configuration, log, and deployment-log subtrees and MUST NOT receive the credentials subtree.

#### Scenario: Host TDT_HOME is unset

- **WHEN** the operator starts the deployment without exporting `TDT_HOME`
- **THEN** bind sources SHALL resolve below the canonical host default
- **AND** no bind source SHALL resolve to the container-only path `/home/agent/tdt` on the host

#### Scenario: Log collector starts with canonical mounts

- **WHEN** the log collector uses container `TDT_HOME=/data`
- **THEN** host logs SHALL be mounted at `/data/logs`
- **AND** state SHALL persist at the host's `state/observability` subtree
- **AND** the default source discovery SHALL observe newly appended supported logs

#### Scenario: Credential isolation is inspected

- **WHEN** health-poller and log-collector mounts are rendered
- **THEN** neither service SHALL mount `$TDT_HOME/credentials` or the complete TDT home root

### Requirement: Shared networks and published ports are run-scoped

The coordinator SHALL create configurable runtime and observability network names, SHALL avoid fixed `container_name` values, and SHALL publish local interfaces only on `127.0.0.1` with configurable host ports. Service-to-service traffic SHALL use service DNS names on the appropriate shared network.

#### Scenario: Two verification runs execute concurrently

- **WHEN** two runs select different project, network, state-root, and host-port identities
- **THEN** both SHALL render and start without container-name, network-name, volume-name, or port collisions

#### Scenario: Port is exposed publicly

- **WHEN** a supported model publishes an application or observability port on `0.0.0.0`
- **THEN** validation SHALL fail before startup

#### Scenario: Backend data services remain private

- **WHEN** the full profile renders
- **THEN** Langfuse PostgreSQL, Redis, ClickHouse, and MinIO SHALL reside only on a Langfuse-private network
- **AND** MLflow PostgreSQL SHALL reside only on an MLflow-private network
- **AND** only the gateway and the relevant backend web or server service SHALL bridge from the shared observability network to a backend-private network

### Requirement: Host-native monitored services remain reachable without containerization

The containerized health-poller SHALL reach launchd-owned webhook-receiver and ai-review through an explicitly supported host-gateway address, while it SHALL reach the scheduler through the scheduler service DNS name on the observability network. The deployment SHALL not require host-native services to join Docker DNS.

#### Scenario: Polling mixed host and container targets

- **WHEN** webhook-receiver (`127.0.0.1:8080`) and ai-review (`127.0.0.1:8090`) run on the host and scheduler runs in Docker
- **THEN** one health-poller cycle SHALL record all three configured outcomes using their supported address classes
- **AND** missing optional ai-review providers SHALL be recorded as degraded target status without causing poller process failure

#### Scenario: Host gateway is unavailable

- **WHEN** the configured Docker host-gateway name cannot resolve
- **THEN** preflight or health acceptance SHALL fail with a platform-specific diagnostic
- **AND** the deployment SHALL not report the health-poller as ready merely because its process exists

### Requirement: Local services have explicit resource budgets

Every long-lived service and one-shot initializer in a supported profile SHALL declare reviewed CPU and memory limits and reservations appropriate to its role. Budgets SHALL be derived from retained profile measurements with at least 20% safety margin over observed p95 reservations and p99 limits unless an owner documents a stricter safe ceiling. The selected profile's aggregate reservation plus 20% host headroom SHALL be checked against available Docker resources before startup so latest-image compatibility tests do not fail ambiguously from host exhaustion.

#### Scenario: Selected profile fits available resources

- **WHEN** preflight compares the selected profile's aggregate reservations and limits with Docker's available CPU and memory
- **THEN** startup SHALL proceed only when the documented minimum budget is available
- **AND** the acceptance manifest SHALL retain the service and aggregate budgets

#### Scenario: Full profile exceeds available resources

- **WHEN** the full profile cannot fit within the available Docker resource budget
- **THEN** preflight SHALL fail before starting containers
- **AND** it SHALL identify the limiting resources and lower-cost supported profiles

#### Scenario: One-shot initializer completes within its budget

- **WHEN** a database or object-store initializer runs
- **THEN** it SHALL use a bounded resource allocation and `restart: "no"`
- **AND** dependent services SHALL consume its successful completion rather than a long-running health state

### Requirement: Backend credentials and Collector configuration fail closed

Secret values SHALL enter containers only through documented runtime injection and SHALL not be committed in Compose or Collector configuration. Langfuse OTLP authentication SHALL use both a real initialized project public key and secret key, and every Collector configuration SHALL use supported environment-provider syntax and validate under the exact pinned Collector image.

#### Scenario: Langfuse OTLP authentication succeeds

- **WHEN** the Langfuse profile starts with an initialized project key pair
- **THEN** the gateway SHALL authenticate with both key parts
- **AND** it SHALL export to the Langfuse OTLP base path that resolves to `/api/public/otel/v1/traces`

#### Scenario: Required backend credential is missing

- **WHEN** a selected profile lacks a required credential or initialized backend identity
- **THEN** preflight SHALL fail before producers are switched to that profile
- **AND** no placeholder public key SHALL be treated as valid Basic authentication

#### Scenario: Collector config uses unsupported syntax

- **WHEN** the pinned Collector validates a selected profile configuration containing an unsupported field, component, endpoint, or environment expression
- **THEN** validation SHALL exit non-zero and block startup

### Requirement: Cleanup is ownership-aware and separately authorized

Normal shutdown SHALL stop only resources created for the selected run. Legacy networks, images, volumes, data directories, and launchd services MUST remain untouched until an operator reviews retained ownership and data-classification evidence and separately authorizes retirement.

#### Scenario: Normal verification teardown runs

- **WHEN** a run completes or fails
- **THEN** the coordinator SHALL collect bounded diagnostics before teardown
- **AND** it SHALL remove only the run-scoped Compose projects and networks it created

#### Scenario: Legacy data retirement lacks approval

- **WHEN** a cleanup step identifies an old volume or host directory without exact ownership, backup, and operator approval
- **THEN** it SHALL preserve the resource and report it as pending retirement
