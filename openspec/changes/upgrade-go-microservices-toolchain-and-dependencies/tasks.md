# Tasks: Upgrade Go Microservices Toolchain, Core Dependencies, and Docker Images

## 1. OpenSpec Change Authoring & Strict Validation

- [x] 1.1 Author `proposal.md`, `design.md`, `tasks.md`, and delta specs under `openspec/changes/upgrade-go-microservices-toolchain-and-dependencies/`. Verification: run `openspec validate upgrade-go-microservices-toolchain-and-dependencies --strict --store openspec-store`.

## 2. Infrastructure & Tooling Container Image Upgrades (`deploy/tools.env`)

- [x] 2.1 Update `deploy/tools.env` image pins (Temporal `1.32.0`, OTel Collector `0.161.0`, Grafana `13.2.3`, Prometheus `v3.15.0`, Debezium `3.6.3.Final`, Mailpit `v1.31.3`, Redis Exporter `v1.92.1`, Python `3.14.7-slim`, Go Image `1.27.1-alpine`). Verification: check `git diff deploy/tools.env`.
- [x] 2.2 Verify multi-architecture support (`linux/arm64` and `linux/amd64`) for all updated images. Verification: run `./scripts/verify-images.sh --arch arm64` and `./scripts/verify-images.sh --arch amd64` with exit code 0.

## 3. Go Toolchain Upgrade (`1.26.5` → `1.27.1`)

- [x] 3.1 Update root `Makefile` `GO_VERSION := 1.27.1`. Verification: `grep GO_VERSION Makefile`.
- [x] 3.2 Update Go toolchain directive across all 18 `go.mod` files (`platform/`, 8 `services/*/`, `tests/*/`, `scripts/*/`, `tools/*/`). Verification: verify with python check script that all `go.mod` files specify `go 1.27.1`.
- [x] 3.3 Update Dockerfile builder stages across services and deploy overlays to `golang:1.27.1-bookworm` (and `golang:1.27.1-alpine` / `alpine:3.24.2`). Verification: check `git diff` across `Dockerfile*`.

## 4. Core Go Dependencies Upgrade Across Modules

- [x] 4.1 Update `platform/go.mod` dependencies to target releases (`pgx/v5 v5.11.0`, `chi/v5 v5.3.2`, `testify v1.12.1`, `franz-go v1.22.1`, `temporal v1.49.0`, `otel v1.46.0`, `protobuf v1.36.12`, `grpc v1.84.0`, `connectrpc v1.21.0`, `protovalidate v1.4.0`) and run `go mod tidy`. Verification: run `go build ./...` in `platform/`.
- [x] 4.2 Update dependencies and run `go mod tidy` across all 8 microservices:
  - `services/catalog-service/`
  - `services/customer-service/`
  - `services/inventory-service/`
  - `services/notification-service/`
  - `services/order-service/`
  - `services/payment-service/`
  - `services/reporting-service/`
  - `services/shipping-service/`
  Verification: run `go build ./...` across each service directory.
- [x] 4.3 Update dependencies and run `go mod tidy` across `tests/` and `tools/`. Verification: run `go test -run=^$ ./...` across test packages.

## 5. Verification, Test Execution, and OpenSpec Completion

- [x] 5.1 Run `make -C platform verify` to ensure shared runtime and contracts pass all assertions. Verification: command passes with exit code 0.
- [x] 5.2 Run unit tests across all 8 services (`go test ./...` in each service). Verification: all tests pass.
- [x] 5.3 Mark all tasks complete in `tasks.md` and run strict OpenSpec validation (`openspec validate upgrade-go-microservices-toolchain-and-dependencies --strict --store openspec-store`). Verification: zero validation errors reported.
