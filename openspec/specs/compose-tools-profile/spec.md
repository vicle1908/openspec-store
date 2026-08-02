# compose-tools-profile Specification

## Purpose

Provides a Docker Compose overlay (deploy/docker-compose.tools.yaml) with optional developer tooling (kcat, pgcli, redis-cli) accessible via `docker compose --profile tools up`, enabling day-2 operational tasks without polluting the base data plane.

## Requirements

> **Status**: IMPLEMENTED. docker-compose.tools.yaml with Kafka UI, pinned arm64 image, verify-images script, isolated from runtime.

### Requirement: Broker UI overlay pins an immutable arm64 image

> **Status**: IMPLEMENTED. docker-compose.tools.yaml exists with Kafka UI and verify-images script.

The project SHALL publish a `deploy/docker-compose.tools.yaml` overlay that activates a Kafka broker UI only when the developer explicitly passes `--profile tools`. The overlay MUST pin an immutable image tag recorded in `verification/tools.env` as `KAFKA_UI_VERSION` and MUST configure the service such that `make verify-images` rejects any future tag that lacks a native `linux/arm64` manifest entry.

#### Scenario: Local developer inspects Kafka state via the broker UI
- **WHEN** a developer runs `docker compose --profile tools -f deploy/docker-compose.yaml -f deploy/docker-compose.tools.yaml up -d`
- **THEN** the broker UI container starts on a documented port, connects to the pinned `kafka` service over the internal listener, and exposes a read-only view of topics, consumer groups, and schema state without touching the runtime API or worker

#### Scenario: Broker UI tag lacks native arm64 support
- **WHEN** `make verify-images` runs and the pinned `kafbat/kafka-ui:${KAFKA_UI_VERSION}` tag does not advertise a `linux/arm64` manifest entry
- **THEN** `verify-images` exits non-zero, the tag is rejected, and the broker-UI overlay MUST NOT start until a supported tag replaces it

#### Scenario: Runtime stack starts without the tools profile
- **WHEN** a developer runs `docker compose -f deploy/docker-compose.yaml up -d` without `--profile tools`
- **THEN** the broker UI container does not start, the runtime stack's readiness is unaffected, and no optional tooling image is downloaded

### Requirement: Broker UI never influences runtime health or readiness

> **Status**: IMPLEMENTED. Tools overlay is isolated from runtime stack; health checks unaffected.

The broker-UI overlay MUST NOT publish ports into the runtime network on behalf of the Order Service, MUST NOT participate in any runtime health check, and MUST NOT write to any Kafka topic. The service MAY expose its own UI port on `localhost` for developer inspection.

#### Scenario: Broker UI container is stopped
- **WHEN** a developer stops the broker-UI container while the runtime stack is healthy
- **THEN** the runtime stack's `/health/ready` endpoint continues to return 200, no Order Service log line attributes the UI's state to readiness, and the Kafka cluster reports no broker-side error

#### Scenario: Broker UI is upgraded independently of the runtime stack
- **WHEN** a developer changes the pinned `KAFKA_UI_VERSION` and recreates only the broker-UI container
- **THEN** the Order Service API, orchestrator, and worker containers are unaffected and continue serving traffic with the previously validated images

