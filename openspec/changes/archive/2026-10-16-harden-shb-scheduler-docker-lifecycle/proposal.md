# Proposal

## Why

Operational and architectural investigation of the `shb-schedule` DBOS scheduling runtime and workstation tooling pipelines revealed three key production hardening opportunities:

1. **Abrupt Container Termination Risk**: The default Docker Compose stop timeout is 10 seconds before sending `SIGKILL`. Durable DBOS workflows (`eod_settlement_recon`, `nightly_compliance_scan`) and PostgreSQL transactions risk abrupt interruption during container restarts or host reboots without an explicit `stop_grace_period`.
2. **Health Check Log Growth**: With container health checks running every 5 seconds on both `db` and `scheduler` services, unbound stdout/stderr logging creates cumulative disk bloat on the macOS workstation unless capped by explicit Docker log rotation policies.
3. **Host Lifecycle Script Drift**: The workstation's unified Docker management tool (`~/Developer/scripts/docker-service.sh`) currently tracks only `Omniroute` in its `COMPOSE_STACKS` list. As a result, automated daemon restart or drainage operations bypass `shb-schedule`, leading to uncoordinated shutdowns.
4. **Execution Boundary Clarification**: The `workstation_update` workflow relies on macOS host binaries (`brew`, `mas`, `pmset`, host agent CLIs). While the workflow gracefully skips these inside Linux containers, the operational contract must formally partition host toolchain updates (run on host via launchd / CLI) from headless banking workflows (run containerized against PostgreSQL).

## What Changes

- **Graceful Termination Window**: Update `shb-schedule/compose.yaml` to declare `stop_grace_period: 60s` on the `scheduler` service, allowing inflight DBOS steps and database connections to finish cleanly and release PostgreSQL advisory locks.
- **Log Rotation Policy**: Add `logging: driver: "json-file", options: { max-size: "10m", max-file: "3" }` to `db` and `scheduler` services in `compose.yaml`.
- **Workstation Stack Registration**: Register `~/Developer/shb/shb-schedule` in `COMPOSE_STACKS` in `~/Developer/scripts/docker-service.sh` for unified daemon drain and startup coordination.
- **Workload Partitioning Contract**: Formally specify that host-coupled package/toolchain updates run on the host via launchd/CLI, while headless banking workloads run containerized in Docker Compose.
- **Specification Updates**: Amend `shb-schedule-engine` specification in the OpenSpec store to capture these lifecycle invariants and operational boundaries.

## Capabilities

### Modified Capabilities
- `shb-schedule-engine`: Update `Containerized Orchestration via Docker Compose` requirement with graceful termination semantics, and add requirements for log hygiene and host/container workload boundaries.

### New Capabilities
None.

## Impact

- **Target Repositories**:
  - `~/Developer/shb/shb-schedule` (`compose.yaml`, `Dockerfile`)
  - `~/Developer/scripts` (`docker-service.sh`)
  - `~/Developer/platform/openspec-store` (`openspec/specs/shb-schedule-engine/spec.md`)
- **Runtime Dependencies**: Zero new packages. Existing `uv`, `docker compose`, and `postgres:18.6-alpine` preserved.
- **Breaking Changes**: None. Backwards-compatible configuration enhancements.
