# schedule-manifest-schema Specification

## Purpose

Define the `tdt-schedule/v1` YAML schema for declarative schedule manifests. Each scheduled repo ships a YAML file declaring its schedules, which the `ScheduleRegistryLoader` reads to register them with DBOS. The schema is intentionally minimal — it maps directly to `ScheduledWorkflowSpec` fields from `tdt_core.scheduler.scheduling`, with env-var substitution for flexibility.

## ADDED Requirements

### Requirement: Manifest structure

A schedule manifest SHALL be a YAML file with the following top-level fields:

```yaml
apiVersion: tdt-schedule/v1  # required, must be "tdt-schedule/v1"
owner: <repo-name>          # required, kebab-case repo name
version: "<semver>"          # required, mirrors the repo's version
schedules: []                # required, list of schedule objects
```

#### Scenario: Valid minimal manifest

- **WHEN** a YAML file contains `apiVersion: tdt-schedule/v1`, `owner: jira-skill`, `version: "1.2.0"`, and `schedules: []`
- **THEN** it SHALL be parsed as a valid `ScheduleManifest`

#### Scenario: Rejects missing apiVersion

- **WHEN** a YAML file omits `apiVersion`
- **THEN** validation SHALL fail with error `"missing required field: apiVersion"`

#### Scenario: Rejects unknown apiVersion

- **WHEN** a YAML file contains `apiVersion: tdt-schedule/v99`
- **THEN** validation SHALL fail with error `"Unknown apiVersion: tdt-schedule/v99"`

### Requirement: Schedule object fields

Each entry in the `schedules` list SHALL contain:

| YAML field | Type | Required | Default | Maps to `ScheduledWorkflowSpec` |
|------------|------|----------|---------|-------------------------------|
| `name` | string | Yes | — | `schedule_name` |
| `description` | string | No | "" | — (metadata only) |
| `cron` | string | Yes | — | `cron` |
| `timezone` | string | No | null | `cron_timezone` (DBOS interprets null as UTC) |
| `automatic_backfill` | boolean | No | false | `automatic_backfill` |
| `workflow.module` | string | Conditional | — | — (used to resolve `workflow_fn`) |
| `workflow.function` | string | Conditional | — | — (used to resolve `workflow_fn`) |
| `workflow.register_fn` | string | Conditional | — | — (module:fn for batch registration) |
| `queue` | string | No | null | `queue_name` |

**Note:** Either `workflow.module` + `workflow.function` OR `workflow.register_fn` must be specified, but not both.

#### Scenario: Full schedule definition

- **WHEN** a schedule contains all fields including `automatic_backfill: true` and `queue: tdt-scheduler-queue`
- **THEN** it SHALL be parsed as a valid `ScheduleSpec` with all values preserved

#### Scenario: Minimal schedule with defaults

- **WHEN** a schedule contains only `name`, `cron`, `workflow.module`, and `workflow.function`
- **THEN** `timezone` SHALL default to `null`, `automatic_backfill` to `false`, and `queue` to `null`

#### Scenario: Rejects missing required fields

- **WHEN** a schedule omits `name`
- **THEN** validation SHALL fail with error `"schedule missing required field: name"`

#### Scenario: Rejects invalid cron expression

- **WHEN** a schedule contains `cron: "invalid-cron"`
- **THEN** validation SHALL fail with error `"invalid cron expression: invalid-cron"` (validated via `croniter`)

#### Scenario: Rejects invalid timezone

- **WHEN** a schedule contains `timezone: "Not/Valid"`
- **THEN** validation SHALL fail with error `"unknown timezone: Not/Valid"` (validated via `zoneinfo.ZoneInfo`)

## ADDED Requirement: Batch registration via register_fn

For schedules that are registered programmatically (e.g., `jira-daily-reports`), the `workflow.register_fn` field MAY be used instead of `workflow.module` + `workflow.function`.

#### Scenario: Batch registration via register_fn

- **WHEN** a schedule contains `workflow.register_fn: jira_daily_reports.dbos_scheduling:register_all_schedules`
- **THEN** the loader SHALL call the specified function to register schedules
- **AND** the loader SHALL NOT require `workflow.module` or `workflow.function`

#### Scenario: Rejects both module and register_fn

- **WHEN** a schedule contains both `workflow.module` and `workflow.register_fn`
- **THEN** validation SHALL fail with error `"schedule must specify either workflow or register_fn, not both"`

### Requirement: Environment variable substitution in string fields

The loader SHALL substitute `${VAR}` and `${VAR:-default}` patterns in string field values with environment variable values.

#### Scenario: Substitutes environment variable

- **WHEN** a string field contains `${JIRA_TICKET_ANALYSIS_FILTER_URL}`
- **THEN** it SHALL be substituted with the environment variable value

#### Scenario: Uses default when env var missing

- **WHEN** a string field contains `${MISSING_VAR:-default_value}` and `MISSING_VAR` is not set
- **THEN** it SHALL substitute with `default_value`

#### Scenario: Leaves field unchanged when required env var missing

- **WHEN** a string field contains `${REQUIRED_VAR}` with no default and `REQUIRED_VAR` is not set
- **THEN** the field value SHALL remain as `${REQUIRED_VAR}` (no substitution, loader logs a warning)

### Requirement: Pydantic model definition

The manifest and schedule schemas SHALL be defined as Pydantic models (`ScheduleManifest`, `ScheduleSpec`) in `tdt_core.scheduler.schedule_manifest`.

#### Scenario: Validates apiVersion prefix

- **WHEN** `apiVersion` is parsed
- **THEN** it SHALL be validated to start with `tdt-schedule/`

#### Scenario: Validates owner format

- **WHEN** `owner` is parsed
- **THEN** it SHALL be validated as kebab-case alphanumeric with hyphens allowed

#### Scenario: Validates version semver

- **WHEN** `version` is parsed
- **THEN** it SHALL be validated as semantic version via `packaging.version.Version`
