## ADDED Requirements

### Requirement: Langfuse worker readiness is queue-aware

The Langfuse and full profiles SHALL gate worker readiness on the pinned worker image's bounded readiness endpoint with queue-stuck detection enabled. Langfuse web and worker SHALL depend on a healthy Redis service, and worker process liveness or a bare Redis ping MUST NOT substitute for queue-consumption readiness.

#### Scenario: Worker queue readiness passes

- **WHEN** Redis is healthy and the Langfuse worker has initialized its registered queue consumers
- **THEN** the bounded worker readiness endpoint SHALL return success with queue consumption enabled and not stuck
- **AND** the worker SHALL become healthy without any container restart

#### Scenario: Worker queue consumption is stuck

- **WHEN** the worker process remains running but its queue-consumption readiness reports stuck or unavailable
- **THEN** the worker health gate SHALL fail
- **AND** the Langfuse or full profile SHALL not be accepted as ready

#### Scenario: Redis is only started

- **WHEN** Redis has started but has not passed its authenticated healthcheck
- **THEN** Langfuse web and worker startup SHALL remain dependency-blocked
- **AND** no running-only Redis state SHALL satisfy profile readiness

## MODIFIED Requirements

### Requirement: Redis 8 and ClickHouse 26 compatibility is proven with Langfuse

Because Langfuse `4.16.0` publishes Redis 7 and ClickHouse 25.12 as its default Compose baseline, the selected Redis `8.10.1` and ClickHouse `26.7.5.10` images SHALL be treated as explicit compatibility deviations. Promotion MUST require fresh Langfuse migration, queue, ingestion, worker, and no-error evidence under those exact images. The selected local deployment SHALL reject any file or ambient override that enables the BullMQ Redis-version-check bypass.

#### Scenario: Redis 8 compatibility passes

- **WHEN** Langfuse web and worker run against Redis `8.10.1-alpine`
- **THEN** authentication, ingestion, queue production, queue consumption, retry, and scheduled background work SHALL complete
- **AND** web and worker logs SHALL contain no Redis-version, command, BullMQ, socket-timeout, or restart failure during the bounded acceptance window

#### Scenario: BullMQ version gate is evaluated explicitly

- **WHEN** Langfuse runs against Redis 8
- **THEN** `LANGFUSE_BULLMQ_SKIP_REDIS_VERSION_CHECK` SHALL remain exactly false and the real BullMQ version gate SHALL be observed
- **AND** any file or ambient attempt to set it to another value SHALL fail preflight before Docker mutation

#### Scenario: ClickHouse 26 compatibility passes

- **WHEN** Langfuse `4.16.0` initializes against ClickHouse `26.7.5.10-alpine`
- **THEN** all migrations SHALL complete
- **AND** trace ingestion and representative analytics queries SHALL pass
- **AND** logs SHALL contain no unsupported-version, analyzer, missing-column, or migration error

#### Scenario: Compatibility deviation fails

- **WHEN** either Redis 8 or ClickHouse 26 acceptance fails
- **THEN** the deployment SHALL remain blocked
- **AND** it SHALL not silently bypass the version gate or fall back to a different image than the approved inventory

### Requirement: Backend credentials and Collector configuration fail closed

Secret values SHALL enter containers only through documented runtime injection and SHALL not be committed in Compose or Collector configuration. Langfuse OTLP authentication SHALL use both a real initialized project public key and secret key, every selected Langfuse Collector route SHALL use the v4 ingestion header, and every Collector configuration SHALL use supported environment-provider syntax and validate under the exact pinned Collector image.

#### Scenario: Langfuse OTLP authentication succeeds

- **WHEN** the Langfuse profile starts with an initialized project key pair
- **THEN** the gateway SHALL authenticate with both key parts
- **AND** it SHALL export to `/api/public/otel/v1/traces` with `x-langfuse-ingestion-version` exactly `4`
- **AND** no legacy ingestion route or header fallback SHALL be selected

#### Scenario: Required backend credential is missing

- **WHEN** a selected profile lacks a required credential or initialized backend identity
- **THEN** preflight SHALL fail before producers are switched to that profile
- **AND** no placeholder public key SHALL be treated as valid Basic authentication

#### Scenario: Collector config uses unsupported syntax

- **WHEN** the pinned Collector validates a selected profile configuration containing an unsupported field, component, endpoint, header, or environment expression
- **THEN** validation SHALL exit non-zero and block startup
