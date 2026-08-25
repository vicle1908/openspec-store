## ADDED Requirements

### Requirement: Langfuse worker readiness is queue-aware and externally composite

The Langfuse and full profiles SHALL retain the pinned worker image's bounded `/api/ready?failIfQueueConsumptionStuck=true` healthcheck with queue-stuck detection enabled and SHALL publish deployment readiness through an external composite. The composite SHALL require the strict worker endpoint, a bounded authenticated Redis PING or equivalent command from the same private network path used by `langfuse-worker`, `langfuse-redis` running with its existing Docker health `healthy`, and `langfuse-worker` without an unhealthy Docker health state. Worker process liveness, a fresh queue-activity timestamp, or a container-local Redis ping alone MUST NOT substitute for this composite.

#### Scenario: Worker queue and composite readiness pass

- **WHEN** Redis is healthy, the worker has initialized its registered queue consumers, the strict endpoint returns HTTP 200 with queue consumption enabled and `stuck: false`, and the same-worker-network authenticated Redis probe succeeds
- **THEN** the external composite SHALL report ready without a container restart
- **AND** the result SHALL retain each endpoint, Redis probe, Redis container-health, and worker container-health input separately

#### Scenario: Worker queue consumption is stuck

- **WHEN** the worker process remains running but the strict endpoint reports stuck or unavailable queue consumption
- **THEN** the worker health gate SHALL fail
- **AND** the Langfuse or full profile SHALL not be accepted as ready

#### Scenario: Redis is only started

- **WHEN** Redis has started but has not passed its authenticated healthcheck
- **THEN** Langfuse web and worker startup SHALL remain dependency-blocked by the existing healthy-Redis ordering
- **AND** running-only Redis state MUST NOT satisfy external composite readiness

#### Scenario: Worker remains live during a Redis interruption

- **WHEN** same-worker-network Redis connectivity is interrupted after clean convergence while the worker remains running or retains a recent activity timestamp
- **THEN** the external composite SHALL report non-ready within its declared finite probe budget
- **AND** the result SHALL not require or claim that the upstream strict endpoint returns HTTP 503
- **AND** the deployment SHALL remain blocked while the authenticated Redis probe or required container health is failing

#### Scenario: Composite recovery requires consecutive passes

- **WHEN** Redis connectivity and required container health are restored after a bounded interruption
- **THEN** the external composite SHALL return ready only after three consecutive successful evaluations within the declared 120-second recovery bound
- **AND** representative post-recovery queue work SHALL complete
- **AND** the deployment SHALL remain blocked if the bound, consecutive-pass requirement, or queue-work requirement is not met

## MODIFIED Requirements

### Requirement: Redis 8 and ClickHouse 26 compatibility is proven with Langfuse

Because Langfuse `4.16.0` publishes Redis 7 and ClickHouse 25.12 as its default Compose baseline, the selected Redis `8.10.1-alpine` and ClickHouse `26.7.5.10-alpine` images SHALL remain explicit compatibility deviations. The selected Compose models SHALL contain the fixed `REDIS_SOCKET_TIMEOUT_MS: "0"` literal in both Langfuse web and worker, SHALL keep `LANGFUSE_BULLMQ_SKIP_REDIS_VERSION_CHECK` exactly `false`, and SHALL reject file or ambient attempts to change that bypass. Promotion MUST require fresh migration, queue, ingestion, worker, clean-window, and bounded interruption/recovery evidence under those exact images.

#### Scenario: Redis 8 compatibility passes

- **WHEN** Langfuse web and worker run against Redis `8.10.1-alpine`
- **THEN** both Compose services SHALL contain the fixed `REDIS_SOCKET_TIMEOUT_MS: "0"` literal
- **AND** authentication, ingestion, queue production, queue consumption, retry, and scheduled background work SHALL complete with the real BullMQ version gate enabled
- **AND** web and worker logs SHALL contain no relevant Redis-version, command, BullMQ, socket-timeout, or unplanned-restart error in the clean and post-recovery windows

#### Scenario: BullMQ version gate is evaluated explicitly

- **WHEN** Langfuse runs against Redis 8
- **THEN** `LANGFUSE_BULLMQ_SKIP_REDIS_VERSION_CHECK` SHALL remain exactly `false` and the real BullMQ Redis-version gate SHALL be observed
- **AND** any file or ambient attempt to set it to another value SHALL fail preflight before Docker mutation
- **AND** `REDIS_SOCKET_TIMEOUT_MS: "0"` MUST NOT be treated as a version-check bypass

#### Scenario: ClickHouse 26 compatibility passes

- **WHEN** Langfuse `4.16.0` initializes against ClickHouse `26.7.5.10-alpine`
- **THEN** all migrations SHALL complete
- **AND** v4 trace ingestion and representative analytics queries SHALL pass
- **AND** logs SHALL contain no unsupported-version, analyzer, missing-column, or migration error in the clean acceptance window

#### Scenario: Compatibility deviation fails

- **WHEN** either Redis 8 or ClickHouse 26 acceptance fails
- **THEN** the deployment SHALL remain blocked
- **AND** it SHALL not silently bypass the version gate, replace an approved image, or use health-only evidence

### Requirement: Backend credentials and Collector configuration fail closed

Secret values SHALL enter containers only through documented runtime injection and SHALL not be committed in Compose, Collector configuration, or acceptance artifacts. The non-secret fixed socket literal SHALL be represented only in the web and worker Compose models. Langfuse OTLP authentication SHALL use an initialized project public/secret key pair without recording values, every selected Collector route SHALL use the v4 ingestion header, and every Collector configuration SHALL use supported environment-provider syntax and validate under the exact pinned Collector image.

#### Scenario: Langfuse OTLP authentication succeeds

- **WHEN** the Langfuse profile starts with an initialized project key pair supplied through documented runtime injection
- **THEN** the gateway SHALL authenticate with both key parts without recording their values
- **AND** it SHALL export to `/api/public/otel/v1/traces` with `x-langfuse-ingestion-version` exactly `4`
- **AND** no legacy ingestion route or header fallback SHALL be selected

#### Scenario: Required backend credential is missing

- **WHEN** a selected profile lacks a required credential or initialized backend identity
- **THEN** preflight SHALL fail before producers are switched to that profile
- **AND** no placeholder public key SHALL be treated as valid authentication
- **AND** no credential value SHALL be printed or written into evidence

#### Scenario: A backend credential is exposed during diagnostics

- **WHEN** a local diagnostic prints or otherwise exposes a backend credential
- **THEN** that credential MUST be treated as compromised and rotated without recording the old or replacement value in artifacts
- **AND** in-place rotation SHALL be preferred
- **AND** if in-place rotation is unavailable and explicit no-old-data authority exists, only the affected backend MAY be recreated on a fresh versioned volume
- **AND** migrations, composite readiness, exact event fan-out, restart checks, and the final clean window SHALL be rerun before promotion

#### Scenario: Collector config uses unsupported syntax

- **WHEN** the pinned Collector validates a selected profile configuration containing an unsupported field, component, endpoint, header, or environment expression
- **THEN** validation SHALL exit non-zero and block startup
