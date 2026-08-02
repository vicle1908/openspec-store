# kafka-ui-tools-overlay Specification

## Purpose

Extends the Docker Compose tools overlay to include `kafbat/kafka-ui`, providing a web-based Kafka broker inspection UI for local development and operations.

## Requirements

> **Status**: IMPLEMENTED. kafka-ui service in tools overlay with pinned version, arm64 validation, and runtime isolation.

### Requirement: kafka-ui container is defined in the tools overlay

> **Status**: IMPLEMENTED. kafka-ui service exists in deploy/docker-compose.tools.yaml with correct configuration.

The project SHALL define a `kafka-ui` service in `deploy/docker-compose.tools.yaml` with image `ghcr.io/kafbat/kafka-ui:v1.0.0`, port mapping `8080:8080`, and environment variables configuring the `local` Kafka cluster connection to `kafka:9092`.

#### Scenario: Developer starts tools overlay with kafka-ui
- **WHEN** a developer runs `docker compose --profile tools -f deploy/docker-compose.yaml -f deploy/docker-compose.tools.yaml up -d`
- **THEN** the `kafka-ui` container starts on port 8080, connects to the `kafka` service over the internal network, and is accessible at `http://localhost:8080`

#### Scenario: kafka-ui requires healthy Kafka broker
- **WHEN** the `kafka` service has not yet passed its health check
- **THEN** the `kafka-ui` container MUST NOT start, and Docker Compose MUST wait for the `kafka` health check to succeed before starting `kafka-ui`

### Requirement: kafka-ui version is pinned in tools.env

> **Status**: IMPLEMENTED. KAFKA_UI_VERSION pinned in deploy/tools.env for image validation.

The project SHALL record `KAFKA_UI_VERSION=v1.0.0` in `deploy/tools.env` so that `make verify-images` can validate the image supports `linux/arm64`.

#### Scenario: verify-images rejects unsupported image tag
- **WHEN** `make verify-images` runs and the pinned `kafbat/kafka-ui:${KAFKA_UI_VERSION}` tag lacks a `linux/arm64` manifest
- **THEN** `verify-images` exits non-zero and the tag MUST be replaced before the tools overlay can start

### Requirement: kafka-ui does not affect runtime readiness

> **Status**: IMPLEMENTED. kafka-ui is isolated from runtime; does not affect health checks or write topics.

The `kafka-ui` container MUST NOT participate in any runtime health check and MUST NOT write to Kafka topics. It is a read-only inspection tool.

#### Scenario: Runtime stack starts without tools profile
- **WHEN** a developer runs `docker compose -f deploy/docker-compose.yaml up -d` without `--profile tools`
- **THEN** no kafka-ui container starts and the runtime stack readiness is unaffected

#### Scenario: kafka-ui is stopped while runtime is healthy
- **WHEN** a developer stops the kafka-ui container while the runtime stack is healthy
- **THEN** all runtime services continue operating and the Kafka cluster reports no errors
