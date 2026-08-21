## ADDED Requirements

### Requirement: ScheduleRegistryLoader bootstrap before schedule application

The scheduler runtime host SHALL execute `ScheduleRegistryLoader.apply_from_yaml(engine)` during process startup before invoking `engine.apply_schedules()`, ensuring all declarative manifests in `~/.tdt/schedules/` are registered into `ScheduleRegistry`.

#### Scenario: Bootstrap loads YAML manifests before DBOS schedule push

- **WHEN** `tdt-scheduler serve` starts up
- **THEN** `ScheduleRegistryLoader.apply_from_yaml(engine)` SHALL be called before `engine.apply_schedules()`
- **AND** all valid schedule manifests in `~/.tdt/schedules/` SHALL be loaded and pushed to DBOS atomically

#### Scenario: Schedule application aggregates decorator and YAML schedules

- **WHEN** both `@engine.scheduled_workflow` decorators and declarative YAML manifests exist
- **THEN** `apply_schedules()` SHALL activate the unified set of registered `ScheduledWorkflowSpec` entries in DBOS
