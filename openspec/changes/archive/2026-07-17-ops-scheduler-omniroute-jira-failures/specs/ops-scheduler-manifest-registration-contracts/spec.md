# ops-scheduler-manifest-registration-contracts Specification

## Purpose

Define the contract between YAML manifests in `~/.tdt/schedules/` and the DBOS registration flow inside `agent_core/scheduler_setup.py`. Manifests MUST point at `register_fn` paths that are importable from the scheduler container's Python runtime, and the scheduler MUST gracefully handle missing modules instead of crashing the serve loop.

## ADDED Requirements

### Requirement: Manifests reference importable register_fn

Every entry under `schedules:` in a YAML manifest MUST specify a `workflow.register_fn` that resolves to a callable inside the scheduler's runtime venv.

#### Scenario: Manifest register_fn is importable
- **WHEN** the scheduler parses `~/.tdt/schedules/webhook-receiver.yaml`
- **AND** the `register_fn` is `webhook_receiver.dbos_scheduling:register_all_schedules`
- **THEN** `webhook_receiver.dbos_scheduling` SHALL be importable from inside the scheduler container (`docker exec agent-core-local-scheduler-1 python -c "import webhook_receiver.dbos_scheduling"`)
- **AND** the import SHALL NOT raise `ModuleNotFoundError`

#### Scenario: Manifest register_fn is not importable
- **WHEN** the scheduler parses a manifest whose `register_fn` module is not in `/opt/scheduler/.venv/lib/python*/site-packages/`
- **THEN** the scheduler SHALL log exactly one `WARNING scheduler.manifest.import_failed manifest=<path> module=<module> error=<exc>` per manifest per serve() call
- **AND** the scheduler SHALL continue processing other manifests (failure isolation)

### Requirement: webhook-receiver schedules register in the scheduler

The scheduler MUST register the `webhook-selftest` and `dlq-reaper` workflows via `webhook_receiver.dbos_scheduling.register_all_schedules`.

#### Scenario: Lazy-import at module top-level
- **WHEN** `agent_core.scheduler_setup` is imported inside the scheduler container
- **THEN** it SHALL attempt `from webhook_receiver.dbos_scheduling import register_all_schedules as _wr_register`
- **AND** on `ImportError` it SHALL log `scheduler_setup.webhook_receiver_import_skipped module=webhook_receiver error=<exc>` and set `_wr_register = None`
- **AND** it SHALL NOT crash the import

#### Scenario: register_all_schedules invoked once at startup
- **WHEN** `_apply_yaml_manifests()` completes
- **THEN** `_wr_register(engine=_ENGINE, apply=False)` SHALL be called (if `_wr_register` is not None)
- **AND** on exception it SHALL log `scheduler_setup.webhook_receiver_register_failed error=<exc>` and continue
- **AND** `apply=False` is used so the existing `engine.apply_schedules()` call is the only one (idempotency)

### Requirement: Module-presence failures do not crash the serve loop

A missing or broken `register_fn` module MUST never propagate an exception that causes the scheduler serve() loop to exit.

#### Scenario: All manifests fail to import
- **WHEN** every YAML manifest's `register_fn` module fails to import
- **THEN** the scheduler SHALL still bind to `SCHEDULER_HEALTH_LISTEN`, return HTTP 200 from `/scheduler/health`, and log the import failures as warnings
- **AND** the docker healthcheck SHALL continue passing

#### Scenario: One manifest fails, others succeed
- **WHEN** manifest A's `register_fn` imports cleanly and manifest B's does not
- **THEN** manifest A's workflows SHALL appear in the registered schedule list
- **AND** manifest B's workflows SHALL NOT appear, and exactly one warning SHALL be logged for manifest B