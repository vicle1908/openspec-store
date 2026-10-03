# Design: Workspace Dependencies Modernization and Toolchain Reconciliation

## Architecture Overview
This change modernizes core Go dependencies across `go-microservices` and OpenTelemetry bounds in `shb`, reconciles historical Go 1.26.5 metadata to Go 1.27.1, and verifies multi-module compatibility without breaking changes.

## Key Design Decisions

### 1. OpenTelemetry v1.47.0 & Stable Logging API (`otel/log`)
- Upgrades `go.opentelemetry.io/otel` from `v1.46.0` to `v1.47.0`.
- Promotes `go.opentelemetry.io/otel/log` and `go.opentelemetry.io/otel/sdk/log` from experimental `v0.22.0` to official General Availability (`v1.47.0`).
- Updates `go.opentelemetry.io/contrib/bridges/otelslog` to `v0.21.0` and `otelhttp` to `v0.72.0`, standardizing structured log-trace correlation across `log/slog` and OTLP gRPC log shipping.

### 2. ConnectRPC & Database Driver Ecosystem
- Upgrades `connectrpc.com/connect` to `v1.21.0` for improved memory buffer reuse and Go 1.27 compatibility.
- Upgrades `github.com/exaring/otelpgx` to `v0.12.0` ensuring OpenTelemetry span context attachment across `pgx/v5` connection pools.
- Upgrades `github.com/pressly/goose/v3` to `v3.28.0` and `github.com/redis/go-redis/v9` to `v9.22.0`.
- Upgrades `github.com/oklog/ulid/v2` to `v2.1.2` and `go.temporal.io/sdk/contrib/opentelemetry` to `v0.8.1`.

### 3. Toolchain Metadata & Scoped Guidance Reconciliation (Go 1.27.1)
- Reconciles `services/AGENTS.md` and `platform/AGENTS.md` to state `Use Go 1.27.1`. Scoped guidance files strictly retain word bounds between 200 and 550 words to satisfy `tools/agentguide`.
- Reconciles `services/{inventory,order,payment,shipping}-service/verification/tools.env` to `GO_VERSION=1.27.1`.
- Aligns `tests/cross-service-smoke/Dockerfile` builder arg to `ARG GO_IMAGE_VERSION=1.27.1-alpine`.
- Aligns `scripts/validation/preflight.go` toolchain check minimum to `1.27.1`.
- Aligns `verification/testcontainers-ecosystem-compatibility.json` and `verification/reference-environment.yaml`.

### 4. SHB Python Ecosystem OTel Bounds
- Expands `opentelemetry-api` and `opentelemetry-sdk` upper bounds in `shb-core/pyproject.toml` to `>=1.39.0,<=1.45.0` to support Python 3.14 runtime telemetry.

## Verification & Risk Mitigation
- **Module Graph Integrity**: Execute `go mod tidy` and verify all 18 Go modules build cleanly without dependency conflicts.
- **Coverage Policy Gate**: Enforce aggregate statement coverage $\ge 80.0\%$ across all 8 microservices via `scripts/check-coverage.sh`.
- **Documentation Parity**: Synchronize `docs/local-service-verification.md` coverage table with exact test summaries to satisfy `tools/doccheck` within $\pm 0.5\%$.
- **Guidance Validation**: Run `make validate-agent-guidance` ensuring 0 violations across all 5 repository guides.
