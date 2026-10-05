# Proposal

## Why

The SHB ecosystem has 12 independent repositories under `~/Developer/shb/` but no shared, durable scheduler. Existing automation is split across ad-hoc scripts, macOS-only service definitions, and TDT-coupled tooling. SHB needs an isolated scheduler with explicit ownership, recoverable state, and portable local execution.

## What Changes

- **New repository (`shb-schedule`)**: Establish `~/Developer/shb/shb-schedule` as the 13th official SHB repository, managed with `uv` on Python `>=3.14`, PEP 621 metadata, `hatchling` build backend, and consuming only SHB-owned packages.
- **Durable scheduling engine**: Wrap the DBOS Python SDK (`dbos>=3.1.0`) for crash recovery, durable workflow history, retries, and step-level idempotency. Strictly separate deterministic orchestration (`@DBOS.workflow`) from non-deterministic subprocess and system operations (`@DBOS.step`). Local execution uses SQLite with WAL at `Path.home() / ".shb" / "scheduler.db"`; enterprise deployments may use PostgreSQL 18.
- **Canonical scheduler ownership**: Only the `shb-schedule` daemon may apply recurring schedules. Other SHB services must not mutate the shared schedule registry.
- **Declarative manifests (`shb-schedule/v1`)**: Load YAML schedules from `~/.shb/schedules/*.yaml` with modern Pydantic v2 schemas (`pydantic>=2.10`), cron, timezone, timeout, retry, non-evaluating environment substitution (`${VAR:-default}`), explicit queue declarations, and automatic backfill disabled by default.
- **Modern CLI & Service Surface**: Typer (`>=0.15`) utilizing `typing.Annotated` options, Starlette/Uvicorn health endpoints on port `9110`, and safe hot reload via `.reload` or `SIGUSR1`.
- **Safe hot reload**: Reload on `.reload` or `SIGUSR1`; invalid or partially unloadable manifests retain the last known-good registry and report a failed reload.
- **Persisted-state reconciliation**: Reconcile DBOS schedule state with the accepted manifest set at startup and during controlled reloads; retire removed schedules and clean up stale enqueued/error work without affecting active valid runs.
- **Cross-platform service and CLI support**: Provide `serve`, `list`, `run-now`, `validate`, `reload`, and `service install`, plus macOS LaunchAgent and Linux systemd user-service generators. Expose health and schedule-status endpoints on port `9110` by default.
- **Flagship workload (`shb-docs-sync`)**: Schedule the existing SHB-native documentation synchronizer from `shb-tools` across the 12 existing SHB repositories at 03:30 in `Asia/Ho_Chi_Minh`, with dirty-worktree protection and per-repository timeouts.

## Capabilities

### New Capabilities

- `shb-schedule-engine`: Defines durable scheduling, manifest validation, ownership, reconciliation, hot reload, health reporting, and cross-platform service integration.

### Modified Capabilities

- `shb-ecosystem-tooling`: Adds `shb-schedule` as the 13th managed repository and makes it the sole official recurring execution engine without importing TDT scheduler or documentation-sync packages.

## Impact

- Adds `~/Developer/shb/shb-schedule` without changing existing banking client factories or ReAct loops.
- Consolidates recurring SHB operations behind declarative manifests while preserving existing SHB-native workload implementations.
- Adds durable execution history, explicit scheduler ownership, state cleanup, and operational health visibility.

## Non-Goals

- Coupling SHB scheduling to `tdt-core`, `tdt-scheduler`, `~/Developer/tdt/`, or `~/.tdt/`.
- Replacing `shb-tools` workload implementations with TDT commands.
- Requiring Docker for local execution.
- Auto-committing documentation changes or modifying dirty worktrees.
- Providing a general distributed scheduler beyond the SHB ecosystem.
