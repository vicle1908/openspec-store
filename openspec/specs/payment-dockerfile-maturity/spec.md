# payment-dockerfile-maturity Specification

## Purpose

Modernizes `services/payment-service/Dockerfile.payment-service` to match the canonical Dockerfile pattern established by notification-service, adding cross-platform build support, profile-guided optimization, build caching, runtime health checks, and observability configuration.

## Requirements

> **Status**: IMPLEMENTED. Dockerfile has cross-platform builds, PGO, cache mounts, HEALTHCHECK, and OTEL env vars.

### Requirement: Dockerfile supports cross-platform builds

> **Status**: IMPLEMENTED. Dockerfile uses --platform=$BUILDPLATFORM with TARGETOS/TARGETARCH args.

The payment-service Dockerfile SHALL use `--platform=$BUILDPLATFORM` on the build stage and accept `TARGETOS` and `TARGETARCH` build arguments to support multi-architecture builds.

#### Scenario: Build on macOS Apple Silicon produces linux/arm64 binary
- **WHEN** a developer runs `docker build --platform linux/arm64 -f services/payment-service/Dockerfile.payment-service .`
- **THEN** the build completes successfully and the resulting image runs on `linux/arm64`

### Requirement: Dockerfile enables profile-guided optimization

> **Status**: IMPLEMENTED. Dockerfile passes -pgo=auto to go build for PGO support.

The payment-service Dockerfile SHALL pass `-pgo=auto` to the `go build` command to enable profile-guided optimization.

#### Scenario: PGO flag is present in build command
- **WHEN** the Dockerfile build stage executes `go build`
- **THEN** the command includes `-pgo=auto`

### Requirement: Dockerfile uses build cache mounts

> **Status**: IMPLEMENTED. Dockerfile uses --mount=type=cache for Go module and build caches.

The payment-service Dockerfile SHALL use `--mount=type=cache` for both `/go/pkg/mod` (Go module cache) and `/root/.cache/go-build` (Go build cache) to improve rebuild performance.

#### Scenario: Second build is faster due to cache mounts
- **WHEN** a developer builds the payment-service Dockerfile a second time without source changes
- **THEN** the build completes significantly faster due to cached modules and build artifacts

### Requirement: Runtime image includes HEALTHCHECK

> **Status**: IMPLEMENTED. Dockerfile includes HEALTHCHECK instruction for container health monitoring.

The payment-service runtime image SHALL include a `HEALTHCHECK` instruction that invokes the service binary's healthcheck subcommand.

#### Scenario: Docker reports container health status
- **WHEN** a payment-service container is running
- **THEN** `docker inspect --format='{{.State.Health.Status}}'` reports `healthy` after the health check passes

### Requirement: Runtime image includes observability environment variables

> **Status**: IMPLEMENTED. Dockerfile sets OTEL and GOMEMLIMIT_PERCENT env vars for observability.

The payment-service runtime image SHALL set `OTEL_SERVICE_NAME`, `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_RESOURCE_ATTRIBUTES`, and `GOMEMLIMIT_PERCENT=80` environment variables.

#### Scenario: OTEL environment variables are set in runtime container
- **WHEN** a payment-service container starts
- **THEN** `OTEL_SERVICE_NAME` is set to `payment-service` and `GOMEMLIMIT_PERCENT` is set to `80`
