# Design: Upgrade Go Microservices Toolchain, Core Dependencies, and Docker Images

## Context

The `go-microservices` repository is a greenfield monorepo with 8 independently deployable microservices (`catalog`, `customer`, `inventory`, `notification`, `order`, `payment`, `reporting`, `shipping`), a shared `platform/` module, ecosystem test suites (`tests/cross-service-smoke`, `tests/ecosystem-verification`, `tests/platform`), deployment manifests (`deploy/`), and developer tooling.

Currently, all services and tooling pin Go `1.26.5` with container images pinned in `deploy/tools.env`. Standard library CVE `GO-2026-5026` in `net/http@go1.26.5` necessitates updating the compiler toolchain to `1.27.1` (or `1.26.6+`). In addition, upstream container images and core Go dependencies have accumulated stable minor and patch upgrades.

## Architecture & Upgrade Strategy

### 1. Unified Go Toolchain Upgrade (`1.27.1`)
- All 18 `go.mod` files pin `go 1.27.1`.
- Root `Makefile` sets `GO_VERSION := 1.27.1`.
- Multi-stage Dockerfiles use `--platform=$BUILDPLATFORM golang:1.27.1-bookworm AS build` (and `golang:1.27.1-alpine`).
- Minimal runner containers bump from `alpine:3.23` to `alpine:3.24.2`.
- Distroless runtime remains `gcr.io/distroless/static-debian12:nonroot`.

### 2. Infrastructure Images (`deploy/tools.env`)
All updates in `deploy/tools.env` must pass `./scripts/verify-images.sh` for both `linux/arm64` and `linux/amd64`:
- `TEMPORAL_SERVER_VERSION`: `1.31.2` → `1.32.0`
- `TEMPORAL_ADMIN_TOOLS_VERSION`: `1.31.2` → `1.32.0`
- `OTEL_COLLECTOR_VERSION`: `0.158.0` → `0.162.0`
- `OTEL_LGTM_VERSION`: `0.29.0` → `0.34.0`
- `GRAFANA_VERSION`: `13.1.3` → `13.2.3`
- `PROMETHEUS_VERSION`: `v3.13.1` → `v3.15.0`
- `DEBEZIUM_VERSION`: `3.6.0.Final` → `3.6.3.Final`
- `MAILPIT_VERSION`: `v1.30.7` → `v1.31.3`
- `REDIS_EXPORTER_VERSION`: `v1.87.0` → `v1.92.1`
- `PYTHON_IMAGE_VERSION`: `3.14.5-slim` → `3.14.7-slim`
- `GO_IMAGE_VERSION`: `1.26.5-alpine` → `1.27.1-alpine`

### 3. Core Go Dependencies Across Modules
Dependencies are updated to latest compatible stable releases across `platform/` and services:
- **Database**:
  - `github.com/jackc/pgx/v5`: `v5.10.0` → `v5.11.0`
  - `github.com/exaring/otelpgx`: `v0.11.1` → `v0.12.0`
  - `github.com/pressly/goose/v3`: `v3.27.2` → `v3.28.0`
- **Routing & Protobuf / RPC**:
  - `github.com/go-chi/chi/v5`: `v5.3.1` → `v5.3.2`
  - `google.golang.org/protobuf`: `v1.36.11` → `v1.36.12`
  - `google.golang.org/grpc`: `v1.82.1` → `v1.84.0`
  - `connectrpc.com/connect`: `v1.20.0` → `v1.21.0`
  - `buf.build/go/protovalidate`: `v1.2.0` → `v1.4.0`
- **Kafka & Event Streaming**:
  - `github.com/twmb/franz-go`: `v1.21.5` → `v1.22.1`
  - `github.com/twmb/franz-go/pkg/kmsg`: `v1.13.1` → `v1.14.0`
  - `github.com/twmb/franz-go/plugin/kotel`: `v1.7.0` → `v1.7.1`
- **Temporal & Workflow Engine**:
  - `go.temporal.io/sdk`: `v1.46.0` → `v1.49.0`
  - `go.temporal.io/api`: `v1.63.0` → `v1.63.6`
  - `github.com/nexus-rpc/sdk-go`: `v0.6.0` → `v0.7.0`
- **OpenTelemetry & Observability**:
  - `go.opentelemetry.io/otel`: `v1.44.0` → `v1.46.0`
  - `go.opentelemetry.io/contrib/bridges/otelslog`: `v0.19.0` → `v0.20.1`
  - `go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp`: `v0.69.0` → `v0.71.0`
  - `github.com/prometheus/client_golang`: `v1.23.2` → `v1.24.1`
- **Cache & Utilities**:
  - `github.com/redis/go-redis/v9`: `v9.21.0` → `v9.22.0`
  - `github.com/oklog/ulid/v2`: `v2.1.1` → `v2.1.2`
  - `github.com/stretchr/testify`: `v1.11.1` → `v1.12.1`
  - `github.com/testcontainers/testcontainers-go`: `v0.43.0` → `v0.44.0`
  - `golang.org/x/tools`: `v0.48.0` → `v0.50.0`

### 4. Verification Workflow
1. Execute multi-arch verification: `./scripts/verify-images.sh --arch arm64` and `--arch amd64`.
2. Run `go mod tidy` in all 18 modules.
3. Run `make -C platform verify` for platform contracts.
4. Run `go test ./...` in each microservice to guarantee zero compile errors or API regressions.
5. Re-run `openspec validate upgrade-go-microservices-toolchain-and-dependencies --strict --store openspec-store`.
