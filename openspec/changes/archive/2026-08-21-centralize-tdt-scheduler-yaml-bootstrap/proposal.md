# Proposal: Centralize TDT Scheduler YAML Bootstrap

## Why

Scheduler workflow schedules across ecosystem services must be bootstrapped from declarative YAML manifests via `ScheduleRegistryLoader.apply_from_yaml(engine)` before schedule activation to ensure all schedules are registered into the canonical DBOS scheduler engine.

Previously, scheduled workflows relied on distributed per-repo hardcoded setups or direct imports during container startup. Centralizing the YAML manifest loading mechanism into `tdt-core` via `ScheduleRegistryLoader.apply_from_yaml(engine)` allows declarative manifests placed in `~/.tdt/schedules/*.yaml` to be discovered, parsed, validated, and registered into `ScheduleRegistry` before `engine.apply_schedules()` is invoked. This change formalizes the specification contract for the accepted-main scheduler YAML bootstrap sequence.

## What Changes

- Introduce the canonical `schedule-registry-loader` capability specification defining manifest discovery, parsing, validation, dynamic workflow imports, `ScheduleRegistry` registration, and initial `ScheduleRegistryLoader.apply_from_yaml(engine)` execution before schedule application.
- Extend `scheduler-engine` specification with explicit requirements ensuring `ScheduleRegistryLoader.apply_from_yaml(engine)` is executed during scheduler host bootstrap prior to `engine.apply_schedules()`.
- Define error handling, missing directory handling, and hot-reload behavior for YAML schedule manifests.

## Capabilities

### New Capabilities
- `schedule-registry-loader`: Declarative YAML schedule manifest loader that discovers `~/.tdt/schedules/*.yaml`, parses `tdt-schedule/v1` manifests, imports workflow functions dynamically, and registers schedules into `ScheduleRegistry` via `apply_from_yaml(engine)`.

### Modified Capabilities
- `scheduler-engine`: Adds requirement for initial YAML schedule bootstrap via `ScheduleRegistryLoader.apply_from_yaml(engine)` before DBOS schedule application.

## Non-Goals

- Deprecating or removing programmatic `@engine.scheduled_workflow` decorator registrations (YAML manifests extend the registry).
- Modifying DBOS runtime internals or database schema.
- Re-implementing CLI command interfaces already specified in `scheduler-cli`.
- Performing immediate archive operations or code modifications within this planning proposal.

## Impact

- **Affected Ownership Boundaries**:
  - `tdt-core`: `tdt_core.scheduler.schedule_registry_loader` module owning YAML manifest discovery and bootstrap.
  - `tdt-scheduler`: Container service and `tdt-scheduler serve` entrypoint executing YAML bootstrap.
  - Ecosystem scheduled services: Services deploying declarative manifests to `~/.tdt/schedules/`.
