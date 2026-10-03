# Tasks: Workspace Dependencies Modernization and Toolchain Reconciliation

## 1. Toolchain Metadata & Scoped Guidance Reconciliation (Go 1.27.1)

- [x] 1.1 Update `platform/AGENTS.md` and `services/AGENTS.md` to state `Use Go 1.27.1` and verify word counts via `make validate-agent-guidance`
- [x] 1.2 Update `services/{inventory,order,payment,shipping}-service/verification/tools.env` to `GO_VERSION=1.27.1`
- [x] 1.3 Update `tests/cross-service-smoke/Dockerfile` builder arg to `ARG GO_IMAGE_VERSION=1.27.1-alpine`
- [x] 1.4 Update `scripts/validation/preflight.go` minimum toolchain requirement to `1.27.1`
- [x] 1.5 Update `verification/testcontainers-ecosystem-compatibility.json` and `verification/reference-environment.yaml`

## 2. Go Monorepo Dependency Upgrades (`platform/` and 8 Services)

- [x] 2.1 Upgrade OpenTelemetry packages in `platform/go.mod` to `v1.47.0` (adopting GA `otel/log v1.47.0` and `otel/sdk/log v1.47.0`), `otelslog v0.21.0`, `otelhttp v0.72.0`, `connectrpc v1.21.0`, `ulid v2.1.2`, and run `go mod tidy`
- [x] 2.2 Verify `platform/` compiles and passes unit tests via `make -C platform verify`
- [x] 2.3 Upgrade dependencies in all 8 services (`catalog-service`, `customer-service`, `inventory-service`, `notification-service`, `order-service`, `payment-service`, `reporting-service`, `shipping-service`): `otel v1.47.0`, `otelpgx v0.12.0`, `goose v3.28.0`, `go-redis v9.22.0`, `ulid v2.1.2`, and run `go mod tidy`
- [x] 2.4 Verify all 8 services compile and pass unit tests with statement coverage $\ge 80.0\%$

## 3. SHB Python Ecosystem Dependency Bounds Alignment

- [x] 3.1 Update `shb-core/pyproject.toml` dependency bounds for `opentelemetry-api` and `opentelemetry-sdk` to `>=1.39.0,<=1.45.0`
- [x] 3.2 Run `uv sync` in `shb-core` and execute `uv run pytest tests/`
- [x] 3.3 Verify all 12 SHB repositories pass unit tests and ruff linting

## 4. Full Ecosystem Verification & OpenSpec Lifecycle Closure

- [x] 4.1 Run `make validate-agent-guidance` and `make validate-documentation` in `go-microservices`
- [x] 4.2 Verify git diff hygiene (`git diff --check`)
- [x] 4.3 Strictly validate OpenSpec change using `openspec validate upgrade-workspace-dependencies-and-reconcile-toolchain --strict --store openspec-store`
- [x] 4.4 Commit and push changes in `go-microservices`, `openspec-store`, and `shb`
