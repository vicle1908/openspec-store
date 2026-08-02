## MODIFIED Requirements

### Requirement: Optional infrastructure is capability driven
Redis, search stores, schema registries, gateways, and other infrastructure SHALL be introduced only with an owned capability, failure model, operational metric, and removal strategy. The same rule SHALL apply to optional inspection tooling such as a Kafka broker UI.

#### Scenario: Cache proposal
- **WHEN** a read cache is proposed
- **THEN** the design identifies the authority, invalidation policy, stale-read tolerance, observability, and fallback behavior before adding Redis

#### Scenario: Broker UI proposal
- **WHEN** the broker-UI tools profile is proposed
- **THEN** the design identifies the authority (developer inspection only), the failure model (container stop has zero runtime impact), the operational metric (none — non-runtime dependency), and the removal strategy (drop the overlay and remove the `verify-images` entry) before adding the image

## ADDED Requirements

### Requirement: Broker UI tools profile is opt-in and arm64-validated
The Kafka broker UI SHALL be exposed only via a separate `deploy/docker-compose.tools.yaml` overlay activated by `--profile tools`. The pinned image MUST advertise a native `linux/arm64` manifest entry and SHALL be checked by `make verify-images` on every PR.

#### Scenario: Broker UI starts with the tools profile
- **WHEN** a developer runs `docker compose --profile tools -f deploy/docker-compose.yaml -f deploy/docker-compose.tools.yaml up`
- **THEN** the broker UI container starts on a documented `localhost` port and connects to the runtime Kafka broker over the internal listener

#### Scenario: Broker UI does not start without the tools profile
- **WHEN** a developer runs `docker compose -f deploy/docker-compose.yaml up` without `--profile tools`
- **THEN** the broker UI container does not start, no optional image is downloaded, and the runtime stack's readiness is unaffected

#### Scenario: Broker UI image lacks arm64 manifest
- **WHEN** `make verify-images` runs and the pinned `KAFKA_UI_VERSION` image lacks a `linux/arm64` manifest entry
- **THEN** `verify-images` exits non-zero, the broker-UI overlay is rejected, and `verify-traceability` records the gap as an unmapped scenario

### Requirement: Broker UI is a non-runtime dependency
The broker UI SHALL NOT participate in any Order Service readiness check, SHALL NOT receive traffic on behalf of the API, orchestrator, or worker roles, and SHALL NOT write to any Kafka topic.

#### Scenario: Broker UI stops during a developer session
- **WHEN** a developer stops the broker-UI container while the runtime stack is healthy
- **THEN** the runtime stack's `/health/ready` continues to return 200 and no Order Service log line attributes the UI's state to readiness

#### Scenario: Broker UI attempts to write to a Kafka topic
- **WHEN** a developer misconfigures the broker UI with write permissions
- **THEN** the design records this as a forbidden scenario, `verify-traceability` flags the misconfiguration, and the overlay MUST be configured read-only by default