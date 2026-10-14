# Tasks

## 1. Monorepo Dependency & Toolchain Parity

- [ ] 1.1 Align `tests/cross-service-smoke/go.mod` Temporal SDK from `v1.46.0` to `v1.49.0` and verify with `go mod tidy`
- [ ] 1.2 Reconcile `TEMPORAL_CLI_VERSION` in service `verification/tools.env` to `1.9.1` matching workstation CLI

## 2. Activity Heartbeating Standard

- [ ] 2.1 Enforce `HeartbeatTimeout` and periodic `activity.RecordHeartbeat(ctx)` across batch and aggregation activities (`reporting-service`, `inventory-service`)
- [ ] 2.2 Verify heartbeat policy tests and progress assertions via `ruby scripts/validate-temporal-inventory.rb`

## 3. Inner-Loop Development Server Target

- [ ] 3.1 Add `temporal-dev` target to root `Makefile` invoking `temporal server start-dev` with standard port configuration
- [ ] 3.2 Verify dry-run execution of `make -n temporal-dev` confirms non-root, containerless local execution

## 4. Ecosystem & Determinism Verification

- [ ] 4.1 Run full repository verification via `make temporal-verify` (audits, AST determinism checks, negative controls, replay fixtures)
- [ ] 4.2 Verify OpenSpec store validation via `openspec validate align-temporal-go-microservices-patterns --strict --store openspec-store`
