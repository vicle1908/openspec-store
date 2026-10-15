# temporal-service-orchestration-alignment Specification

## Purpose
Defines orchestration and toolchain standards across `go-microservices`, establishing activity heartbeating contracts for long-running batch operations, monorepo SDK version parity, and local CLI development server targets.

## Requirements

### Requirement: Activity Heartbeating for Long-Running Operations

Any Temporal activity implementation within `go-microservices` that configures a `StartToCloseTimeout` greater than or equal to 60 seconds SHALL declare an explicit `HeartbeatTimeout` and MUST periodically invoke `activity.RecordHeartbeat(ctx)`. The worker host failure detection latency SHALL not exceed the declared heartbeat interval plus the server timeout.

#### Scenario: Activity declares heartbeat timeout and records progress
- **WHEN** an activity definition specifies a `StartToCloseTimeout` exceeding 60 seconds
- **THEN** its activity options include an explicit non-zero `HeartbeatTimeout`
- **AND** the activity execution function calls `activity.RecordHeartbeat(ctx)` on every batch iteration or step

### Requirement: Monorepo Temporal Toolchain and Dependency Version Parity

All service modules and test harnesses within the `go-microservices` repository SHALL depend on the identical pinned `go.temporal.io/sdk` release (version `1.49.0` or greater) and `go.temporal.io/api` release (version `1.63.7` or greater). Verification configurations in `tools.env` SHALL declare the unified workstation Temporal CLI version `1.9.1`.

#### Scenario: Monorepo dependency and toolchain audit
- **WHEN** the monorepo dependency auditor runs against all `go.mod` files and `verification/tools.env`
- **THEN** zero modules report a lagging `go.temporal.io/sdk` version below `1.49.0`
- **AND** all verification `tools.env` declare `TEMPORAL_CLI_VERSION=1.9.1`

### Requirement: Root Makefile Inner-Loop Development Server Target

The repository root `Makefile` SHALL expose a `temporal-dev` target that starts a user-scoped, ephemeral Temporal CLI development server via `temporal server start-dev`. The command MUST execute without requiring root elevation, bind to default local ports `7233` and `8233`, and output actionable connection logs.

#### Scenario: Invocation of local development server target
- **WHEN** a developer or automated agent executes `make -n temporal-dev`
- **THEN** Make outputs the execution command invoking `temporal server start-dev` with standard port bindings
- **AND** the target does not invoke Docker Compose or system container runtimes
