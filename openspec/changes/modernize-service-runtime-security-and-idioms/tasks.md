# Tasks: Modernize Service Runtime Security, BuildKit Caching, and Go Standard Library Idioms

## 1. HTTP Server Security Standards (Slowloris Hardening)

- [ ] 1.1 Inject `ReadHeaderTimeout: 10 * time.Second` and standard deadlines into `services/notification-service/internal/runtime/fx.go` for both the main API and metrics HTTP servers. Verification: unit tests pass and timeout properties verified in test.
- [ ] 1.2 Inject `ReadHeaderTimeout: 10 * time.Second` and standard deadlines into `services/customer-service/cmd/customer-service/run.go`. Verification: run `go test ./cmd/customer-service/...` and verify server configuration.
- [ ] 1.3 Add `ReadHeaderTimeout: 10 * time.Second` to `NewHTTPServer` in `services/order-service/internal/runtime/runtime.go`. Verification: run `go test ./internal/runtime/...` in `order-service`.
- [ ] 1.4 Add `ReadHeaderTimeout: 10 * time.Second` to `NewHTTPServer` in `services/catalog-service/internal/runtime/runtime.go`. Verification: run `go test ./internal/runtime/...` in `catalog-service`.
- [ ] 1.5 Add `ReadHeaderTimeout: 10 * time.Second` to `NewHTTPServer` in `services/reporting-service/internal/runtime/wire.go`. Verification: run `go test ./internal/runtime/...` in `reporting-service`.

## 2. Signal Handling Modernization (`signal.NotifyContext`)

- [ ] 2.1 Refactor `platform/runtime/roles.go` `WithSignal` to use `signal.NotifyContext(ctx, os.Interrupt, syscall.SIGTERM)` instead of manual channels and uncoordinated goroutines. Verification: run `go test ./runtime/...` in `platform/`.
- [ ] 2.2 Refactor `services/customer-service/cmd/customer-service/run.go` `withSignal` to use `signal.NotifyContext`. Verification: run `go test ./cmd/customer-service/...`.
- [ ] 2.3 Refactor `services/order-service/internal/runtime/runtime.go` `NewShutdownSignalContext` and `cmd/diag-consumer/main.go` to use `signal.NotifyContext`. Verification: run `go test ./internal/runtime/...` in `order-service`.
- [ ] 2.4 Refactor `services/catalog-service/internal/runtime/runtime.go` `SignalContext` to use `signal.NotifyContext`. Verification: run `go test ./internal/runtime/...` in `catalog-service`.

## 3. Container BuildKit Cache Mounts

- [ ] 3.1 Add `--mount=type=cache,target=/go/pkg/mod` and `--mount=type=cache,target=/root/.cache/go-build` to `services/inventory-service/Dockerfile.inventory-service`. Verification: `git diff services/inventory-service/Dockerfile.inventory-service`.
- [ ] 3.2 Add `--mount=type=cache,target=/go/pkg/mod` and `--mount=type=cache,target=/root/.cache/go-build` to `services/shipping-service/Dockerfile.shipping-service`. Verification: `git diff services/shipping-service/Dockerfile.shipping-service`.
- [ ] 3.3 Add BuildKit cache mounts to `tools/templates/Dockerfile.platform`. Verification: `git diff tools/templates/Dockerfile.platform`.

## 4. Standard Library Collections & Modern Idioms

- [ ] 4.1 Replace `sort.Slice` and `sort.Strings` with `slices.Sort` and `slices.SortFunc` across `tools/agentguide/validator.go`, `tools/doccheck/validator.go`, `platform/architecture/architecture.go`, `platform/cdc/register.go`, and `platform/health/probe.go`. Verification: run tests across `tools/` and `platform/`.
- [ ] 4.2 Replace `sort.Slice` and `sort.Strings` across remaining services. Verification: run `go vet ./...` across all services.
- [ ] 4.3 Remove redundant `tc := tc` / `c := c` loop variable copies in test files across `platform/temporal`, `platform/observability`, `platform/kafka`, and services. Verification: run `go test ./...` in `platform/`.
- [ ] 4.4 Simplify configuration default assignments using `cmp.Or` across `platform/temporal`, `platform/observability`, and service runtimes. Verification: run `go test ./...`.

## 5. Verification & OpenSpec Governance

- [ ] 5.1 Run `make -C platform verify` to ensure all platform contracts and architecture checks pass. Verification: command exits 0.
- [ ] 5.2 Run unit tests across all 8 microservices (`go test ./...`). Verification: all tests pass.
- [ ] 5.3 Run strict OpenSpec validation for `modernize-service-runtime-security-and-idioms`. Verification: `openspec validate modernize-service-runtime-security-and-idioms --strict --store openspec-store` exits 0 with no errors.
