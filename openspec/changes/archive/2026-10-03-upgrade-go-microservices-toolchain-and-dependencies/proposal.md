# Proposal: Upgrade Go Microservices Toolchain, Core Dependencies, and Docker Images

## Why

The `go-microservices` repository (8 microservices + shared platform module + tests + tooling) is currently pinned to Go `1.26.5` with container base images and dependencies that carry known security notices and lag upstream releases. Specifically:
- Go stdlib vulnerability `GO-2026-5026` (`net/http@go1.26.5`) is resolved in Go `1.26.6+` and Go `1.27.1`. The local development environment and current toolchain have Go `1.27.1` available.
- Pinned Docker images in `deploy/tools.env` have available maintenance and feature updates (e.g. Temporal Server `1.31.2` → `1.32.0`, OTel Collector `0.158.0` → `0.162.0`, Grafana `13.1.3` → `13.2.3`, Prometheus `v3.13.1` → `v3.15.0`, Redis Exporter `v1.87.0` → `v1.92.1`, Mailpit `v1.30.7` → `v1.31.3`, Debezium `3.6.0.Final` → `3.6.3.Final`, Python `3.14.5-slim` → `3.14.7-slim`, Alpine `3.23` → `3.24.2`).
- Core Go ecosystem dependencies across `platform/` and all 8 services (`pgx/v5`, `chi/v5`, `testify`, `franz-go`, `temporalio/sdk`, `opentelemetry`, `connectrpc`, `protobuf`, `grpc`, `go-redis`, `goose`) have accumulated stable minor and patch upgrades with performance, correctness, and security enhancements.

Upgrading the entire monorepo toolchain, container definitions, and Go module graph in a single coordinated, spec-governed change eliminates technical drift and ensures all services compile and pass multi-arch verification.

## What Changes

- **Go Toolchain & Compiler Upgrade (`1.26.5` → `1.27.1`)**:
  - Update `go` directive to `1.27.1` across all 18 `go.mod` files (`platform/`, 8 `services/*/`, `tests/*/`, `scripts/*/`, `tools/*/`).
  - Update root `Makefile` `GO_VERSION := 1.27.1`.
  - Update all Dockerfiles building Go binaries to `golang:1.27.1-bookworm` (or `golang:1.27.1-alpine`).
  - Update minimal test runners to `alpine:3.24.2`.
- **Infrastructure & Development Docker Images (`deploy/tools.env`)**:
  - Upgrade `TEMPORAL_SERVER_VERSION` from `1.31.2` to `1.32.0`.
  - Upgrade `TEMPORAL_ADMIN_TOOLS_VERSION` from `1.31.2` to `1.32.0`.
  - Upgrade `OTEL_COLLECTOR_VERSION` from `0.158.0` to `0.162.0`.
  - Upgrade `OTEL_LGTM_VERSION` from `0.29.0` to `0.34.0`.
  - Upgrade `GRAFANA_VERSION` from `13.1.3` to `13.2.3`.
  - Upgrade `PROMETHEUS_VERSION` from `v3.13.1` to `v3.15.0`.
  - Upgrade `DEBEZIUM_VERSION` from `3.6.0.Final` to `3.6.3.Final`.
  - Upgrade `MAILPIT_VERSION` from `v1.30.7` to `v1.31.3`.
  - Upgrade `REDIS_EXPORTER_VERSION` from `v1.87.0` to `v1.92.1`.
  - Upgrade `PYTHON_IMAGE_VERSION` from `3.14.5-slim` to `3.14.7-slim`.
  - Run `./scripts/verify-images.sh --arch arm64` and `--arch amd64` to validate multi-arch manifest availability.
- **Core Go Dependencies Alignment**:
  - Upgrade database drivers: `github.com/jackc/pgx/v5` (`v5.10.0` → `v5.11.0`), `github.com/exaring/otelpgx` (`v0.11.1` → `v0.12.0`), `github.com/pressly/goose/v3` (`v3.27.2` → `v3.28.0`).
  - Upgrade HTTP & RPC: `github.com/go-chi/chi/v5` (`v5.3.1` → `v5.3.2`), `google.golang.org/protobuf` (`v1.36.11` → `v1.36.12`), `google.golang.org/grpc` (`v1.82.1` → `v1.84.0`), `connectrpc.com/connect` (`v1.20.0` → `v1.21.0`), `buf.build/go/protovalidate` (`v1.2.0` → `v1.4.0`).
  - Upgrade messaging & streaming: `github.com/twmb/franz-go` (`v1.21.5` → `v1.22.1`), `github.com/twmb/franz-go/pkg/kmsg` (`v1.13.1` → `v1.14.0`), `github.com/twmb/franz-go/plugin/kotel` (`v1.7.0` → `v1.7.1`).
  - Upgrade workflow orchestration: `go.temporal.io/sdk` (`v1.46.0` → `v1.49.0`), `go.temporal.io/api` (`v1.63.0` → `v1.63.6`), `github.com/nexus-rpc/sdk-go` (`v0.6.0` → `v0.7.0`).
  - Upgrade telemetry: `go.opentelemetry.io/otel` (`v1.44.0` → `v1.46.0`), `go.opentelemetry.io/otel/trace`, `metric`, `sdk` (`v1.44.0` → `v1.46.0`), `go.opentelemetry.io/contrib/bridges/otelslog` (`v0.19.0` → `v0.20.1`), `go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp` (`v0.69.0` → `v0.71.0`), `github.com/prometheus/client_golang` (`v1.23.2` → `v1.24.1`).
  - Upgrade caching & utilities: `github.com/redis/go-redis/v9` (`v9.21.0` → `v9.22.0`), `github.com/oklog/ulid/v2` (`v2.1.1` → `v2.1.2`), `github.com/stretchr/testify` (`v1.11.1` → `v1.12.1`), `github.com/testcontainers/testcontainers-go` (`v0.43.0` → `v0.44.0`), `golang.org/x/tools` (`v0.48.0` → `v0.50.0`).
- **Monorepo Tidy & Test Verification**:
  - Run `go mod tidy` in `platform/` and all 8 services.
  - Execute compilation and unit test gates (`make -C platform verify`, `go test ./...` in each service).

## Capabilities

### Modified Capabilities
- `platform-go-runtime`: Modifies the required toolchain directive in `go.mod` from `go 1.26.5` to `go 1.27.1`.
- `platform-verification`: Aligns verification requirements with Go `1.27.1`.

## Non-Goals

- Refactoring service business logic, domain boundaries, or hexagonal architectures.
- Changing database schemas, stored procedures, or Kafka event topic naming.
- Introducing incompatible major framework breaks without backward-compatible API adaptation.

## Impact

- **Affected Systems**:
  - `platform/go-microservices`: `platform/`, `services/*`, `tests/*`, `deploy/tools.env`, `Dockerfile*`, `Makefile`.
  - `openspec-store`: Change tracking and delta specification updates under `upgrade-go-microservices-toolchain-and-dependencies`.
