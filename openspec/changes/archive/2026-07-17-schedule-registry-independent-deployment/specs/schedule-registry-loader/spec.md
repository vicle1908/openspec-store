# schedule-registry-loader Specification

## Purpose

Define the `ScheduleRegistryLoader` that reads `~/.tdt/schedules/*.yaml` manifests and registers them into the existing `ScheduleRegistry` (from `tdt_core.scheduler.scheduling`). This is an extension of the existing decorator-based registration, not a replacement. The loader feeds YAML-defined schedules into the same `ScheduleRegistry` that `SchedulerEngine.apply_schedules()` consumes.

This spec extends the existing `scheduler-engine` spec (specifically the `ScheduleRegistry` class) with YAML-based registration.

## ADDED Requirements

### Requirement: YAML manifest discovery

The loader SHALL discover schedule YAML manifests by scanning `~/.tdt/schedules/*.yaml` (excluding hidden files and the `.reload` sentinel file).

#### Scenario: Discovers YAML files in schedules directory

- **WHEN** `ScheduleRegistryLoader.discover_manifests()` is called and `~/.tdt/schedules/` contains `jira-skill.yaml`, `code-daily-scan.yaml`, and `webhook-receiver.yaml`
- **THEN** it SHALL return a list containing paths to all three YAML files, sorted by filename

#### Scenario: Excludes hidden files and sentinel

- **WHEN** `ScheduleRegistryLoader.discover_manifests()` is called and `~/.tdt/schedules/` contains `.hidden.yaml`, `.reload`, `valid.yaml`, and `README.txt`
- **THEN** it SHALL return only the path to `valid.yaml`

#### Scenario: Handles missing schedules directory

- **WHEN** `~/.tdt/schedules/` does not exist and `discover_manifests()` is called
- **THEN** it SHALL return an empty list and SHALL NOT raise an exception

### Requirement: YAML manifest parsing and validation

The loader SHALL parse each YAML manifest as `tdt-schedule/v1` schema and validate required fields. Invalid manifests SHALL be logged with a warning and skipped. This aligns with the existing `ScheduleRegistry.register()` API which accepts `ScheduledWorkflowSpec` objects.

#### Scenario: Parses valid v1 manifest

- **WHEN** a YAML file with `apiVersion: tdt-schedule/v1`, `owner`, `version`, and `schedules[]` is parsed
- **THEN** it SHALL return a parsed manifest matching the schema in `schedule-manifest-schema/spec.md`

#### Scenario: Rejects unknown apiVersion

- **WHEN** a YAML file with `apiVersion: tdt-schedule/v99` is parsed
- **THEN** it SHALL log a warning `"Unknown schedule manifest apiVersion: v99"` and SHALL skip the manifest

#### Scenario: Rejects manifest missing required fields

- **WHEN** a YAML file with `apiVersion: tdt-schedule/v1` but missing `owner` is parsed
- **THEN** it SHALL log a warning with the missing field name and SHALL skip the manifest

#### Scenario: Handles malformed YAML

- **WHEN** a file containing invalid YAML is parsed
- **THEN** it SHALL log a warning with the parse error and SHALL skip the manifest

### Requirement: Dynamic workflow module import

The loader SHALL dynamically import the workflow module specified in each schedule's `workflow.module` field. The module must be resolvable via the existing `sys.path` pattern from `agent-core/scheduler_setup.py`.

#### Scenario: Imports module successfully

- **WHEN** a schedule specifies `workflow.module: jira_skill.cli` and `workflow.function: analyze_filter`
- **THEN** it SHALL import `jira_skill.cli` and SHALL return a reference to the `analyze_filter` function

#### Scenario: Fails gracefully on import error

- **WHEN** a schedule specifies `workflow.module: nonexistent_module` and the module does not exist
- **THEN** it SHALL log a warning `"Failed to import workflow module nonexistent_module: <error>"` and SHALL skip that schedule

#### Scenario: Fails gracefully when function not found

- **WHEN** a schedule specifies `workflow.module: jira_skill.cli` but `workflow.function: nonexistent_function`
- **THEN** it SHALL log a warning `"Workflow function jira_skill.cli.nonexistent_function not found"` and SHALL skip that schedule

### Requirement: Register YAML schedules into ScheduleRegistry

The loader SHALL convert each valid YAML schedule to a `ScheduledWorkflowSpec` (from `tdt_core.scheduler.scheduling`) and call `schedule_registry.register(spec)`.

#### Scenario: Registers schedule with all fields

- **WHEN** a valid schedule with `name: ticket-analysis`, `cron: "0 8 * * *"`, `timezone: Asia/Ho_Chi_Minh`, and workflow reference is registered
- **THEN** `ScheduleRegistry.register()` SHALL be called with a `ScheduledWorkflowSpec` matching the YAML fields

#### Scenario: Uses defaults for optional fields

- **WHEN** a schedule omits `timezone` (defaults to `None`/UTC) and `automatic_backfill` (defaults to `False`)
- **THEN** the registered `ScheduledWorkflowSpec` SHALL use those defaults

#### Scenario: Skips schedule with invalid cron expression

- **WHEN** a schedule contains `cron: "invalid-cron"`
- **THEN** the loader SHALL log a validation error and SHALL NOT register that schedule

### Requirement: Applies schedules to DBOS via existing apply_schedules()

After loading all YAML manifests, the loader SHALL call `engine.apply_schedules()` once to push all registered schedules (decorator + YAML) to DBOS.

#### Scenario: Applies all schedules on startup

- **WHEN** `ScheduleRegistryLoader.apply_from_yaml(engine)` is called with valid manifests
- **THEN** it SHALL call `engine.apply_schedules()` exactly once after all manifests are parsed and registered

#### Scenario: Continues on individual schedule failure

- **WHEN** one schedule in a manifest fails to import but others succeed
- **THEN** it SHALL log a warning for the failed schedule and SHALL still apply the successful schedules

#### Scenario: Respects ownership contract

- **WHEN** `apply_from_yaml()` is called
- **THEN** the `SchedulerContractViolationError` contract from `tdt-scheduler-ownership-contract` SHALL still be enforced — only the `tdt-scheduler` app_name may call `apply_schedules()`

### Requirement: Module-level singleton

The system SHALL provide a `get_registry_loader()` function that returns a module-level `ScheduleRegistryLoader` singleton.

#### Scenario: Returns same instance

- **WHEN** `get_registry_loader()` is called multiple times
- **THEN** it SHALL return the same `ScheduleRegistryLoader` instance

#### Scenario: Accepts custom schedules directory

- **WHEN** `get_registry_loader(schedules_dir="/custom/path")` is called
- **THEN** the returned loader SHALL use `/custom/path` instead of `~/.tdt/schedules/`
