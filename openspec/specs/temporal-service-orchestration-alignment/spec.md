# temporal-service-orchestration-alignment Specification

## Purpose
Defines orchestration and toolchain standards across `go-microservices`, establishing activity heartbeating contracts for long-running batch operations, monorepo SDK version parity, and local CLI development server targets.

## Requirements

### Requirement: Activity Heartbeating for Long-Running Operations

Any Temporal activity implementation within `go-microservices` that configures a `StartToCloseTimeout` greater than or equal to 60 seconds SHALL declare an explicit `HeartbeatTimeout` and MUST periodically invoke `activity.RecordHeartbeat(ctx)`. The inventory validator `scripts/validate-temporal-inventory.rb` SHALL fail closed when any activity declares `StartToClose >= 60s` without `HeartbeatTimeout` or `activity.RecordHeartbeat`.

#### Scenario: Activity declares heartbeat timeout and records progress
- **WHEN** an activity definition in `order-service` (`StartToClose: 5m`), `reporting-service` (`StartToClose: 2m`), or `inventory-service` specifies a `StartToCloseTimeout` greater than or equal to 60 seconds
- **THEN** its activity options SHALL include an explicit non-zero `HeartbeatTimeout`
- **AND** the activity execution function SHALL check `ctx.Err()` and invoke `activity.RecordHeartbeat(ctx)` guarded by `activity.IsActivity(ctx)` so direct `context.Background()` unit tests execute without `getActivityOutboundInterceptor` panics

#### Scenario: Inventory validator rejects long-running activities missing HeartbeatTimeout
- **WHEN** `ruby scripts/validate-temporal-inventory.rb` inspects service Temporal adapters
- **THEN** it SHALL resolve file-scoped duration constants per `MustSDKActivityOptions` block and fail validation with a non-zero exit code if any block with `StartToClose >= 60s` lacks `Heartbeat:` or if `internal/adapters/temporal/` lacks `activity.RecordHeartbeat` and `ctx.Err()` / `<-ctx.Done()`

### Requirement: Monorepo Temporal Toolchain and Dependency Version Parity

All service modules, test harnesses, and verification fixtures within the `go-microservices` repository SHALL depend on the identical pinned `go.temporal.io/sdk` release (`v1.49.0` or greater) and `go.temporal.io/api` release (`v1.63.7` or greater), and every `services/*/verification/tools.env` file referencing Temporal SHALL declare `TEMPORAL_CLI_VERSION=1.9.1`.

#### Scenario: Monorepo dependency and toolchain audit
- **WHEN** the monorepo dependency auditor runs against all `go.mod` files (including `tests/platform/go.mod` and `verification/fixtures/temporal-determinism/nondeterministic/go.mod`) and all `services/*/verification/tools.env` files (including `catalog-service` and `notification-service`)
- **THEN** zero modules report a lagging `go.temporal.io/sdk` version below `1.49.0` or `go.temporal.io/api` version below `1.63.7`
- **AND** all verification `tools.env` files declare `TEMPORAL_CLI_VERSION=1.9.1` (or `TEMPORAL_CLI_VERSION := 1.9.1`)
### Requirement: Root Makefile Inner-Loop Development Server Target

The repository root `Makefile` SHALL expose a `temporal-dev` target that starts a user-scoped, ephemeral Temporal CLI development server via `temporal server start-dev`. The command MUST execute without requiring root elevation, bind to default local ports `7233` and `8233`, and output actionable connection logs.

#### Scenario: Invocation of local development server target
- **WHEN** a developer or automated agent executes `make -n temporal-dev`
- **THEN** Make outputs the execution command invoking `temporal server start-dev` with standard port bindings
- **AND** the target does not invoke Docker Compose or system container runtimes
