# Design: Centralize TDT Scheduler YAML Bootstrap

## Context

See proposal.md - Why.
The TDT scheduler architecture uses DBOS to orchestrate cron-scheduled workflows across multiple microservices and agent packages. Originally, schedules were hardcoded or manually imported inside individual application scripts. With declarative schedule manifests (`tdt-schedule/v1`), each service drops a YAML manifest into `~/.tdt/schedules/`. The canonical scheduler service (`tdt-scheduler serve`) requires a centralized loader (`ScheduleRegistryLoader`) that scans this directory and invokes `apply_from_yaml(engine)` before applying schedules to DBOS.

## Goals / Non-Goals

**Goals:**
- Provide a centralized loader class `ScheduleRegistryLoader` in `tdt-core` that parses manifests and registers them into `ScheduleRegistry`.
- Standardize the bootstrap sequence in `tdt-scheduler serve` to run `ScheduleRegistryLoader.apply_from_yaml(engine)` prior to `engine.apply_schedules()`.
- Ensure robust error handling (skipping malformed manifests, missing directories, import errors) without crashing the scheduler host.

**Non-Goals:**
- Removing decorator-based `@engine.scheduled_workflow` registrations.
- Modifying DBOS schema or client library internals.
- Rewriting individual service business logic workflows.

## Decisions

### Decision 1: Extend ScheduleRegistry rather than replace it
- **Rationale**: `ScheduleRegistry` is already the unified in-memory registry of `ScheduledWorkflowSpec` instances consumed by `SchedulerEngine.apply_schedules()`. `ScheduleRegistryLoader` translates YAML definitions into `ScheduledWorkflowSpec` instances and calls `register(spec)`, preserving full compatibility with decorator-based registrations.
- **Alternatives Considered**: Direct DBOS insertion bypassed validation and ownership checks; rejected in favor of leveraging `ScheduleRegistry`.

### Decision 2: Centralized singleton accessor get_registry_loader()
- **Rationale**: Providing `get_registry_loader(schedules_dir)` allows CLI commands, background watchdogs, and hot-reload handlers to share a consistent loader instance while supporting custom directories for tests.
- **Alternatives Considered**: Instantiating ad-hoc loaders per call was rejected to avoid duplicate state and redundant directory scans.

## Risks / Trade-offs

- [Risk] Broken or missing workflow imports in YAML manifest → Mitigation: Dynamic import failure is caught, logged with warning, and skipped, allowing other valid schedules to be registered.
- [Risk] Non-owner process invoking apply_schedules() → Mitigation: The ownership contract (`SchedulerContractViolationError`) is strictly enforced unless `SCHEDULER_ENFORCE_OWNERSHIP=false`.

## Migration Plan

1. Define planning artifacts for `centralize-tdt-scheduler-yaml-bootstrap`.
2. Validate spec relationships and schema conformance (`openspec validate --strict`).
3. Downstream implementation registers `ScheduleRegistryLoader.apply_from_yaml(engine)` in `tdt-scheduler serve` bootstrap.

## Transaction Boundaries

Schedule registration is staged in-memory within `ScheduleRegistry`. DBOS atomic push occurs during `DBOS.apply_schedules()` inside `engine.apply_schedules()`.
