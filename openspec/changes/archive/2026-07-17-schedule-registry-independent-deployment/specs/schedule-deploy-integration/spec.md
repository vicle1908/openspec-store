# schedule-deploy-integration Specification

## Purpose

Define how deploy scripts for scheduled repos generate `~/.tdt/schedules/<repo>.yaml` manifests and trigger hot-reload. The deploy script generates YAML from source code constants (cron expressions, workflow module paths) — mirroring the existing `uv-runtime-management` pattern where deploy copies source and generates config from it, rather than committing pre-generated config in source.

This aligns with the existing `code-daily-scan.yaml` pattern where per-repo config lives in `~/.tdt/`, and the `reminder-policies.yaml` pattern where generated config ships alongside source.

## ADDED Requirements

### Requirement: Generate YAML manifest during deploy

Each scheduled repo's deploy script SHALL generate `~/.tdt/schedules/<repo>.yaml` containing that repo's schedule definitions.

#### Scenario: Generate manifest for repo with schedules

- **WHEN** `webhook-receiver/scripts/deploy.sh` runs and `webhook-receiver` has three schedules: `webhook-selftest`, `dlq-reaper`, `scan-recent-mr`
- **THEN** it SHALL write `~/.tdt/schedules/webhook-receiver.yaml` containing all three schedule definitions

#### Scenario: Generate manifest with repo metadata

- **WHEN** the manifest is generated for `jira-skill` version `1.2.0`
- **THEN** it SHALL contain `apiVersion: tdt-schedule/v1`, `owner: jira-skill`, `version: "1.2.0"`

#### Scenario: Overwrites existing manifest

- **WHEN** `~/.tdt/schedules/jira-skill.yaml` already exists
- **THEN** the deploy script SHALL overwrite it with the current version

### Requirement: Generate YAML from source code constants

The deploy script SHALL generate YAML by extracting schedule definitions from Python source files, not from pre-committed YAML or config files.

#### Scenario: Extracts cron from Python decorator or constant

- **WHEN** the deploy script extracts schedule definitions from `agent-core/scheduler_setup.py`
- **THEN** it SHALL parse `@_ENGINE.scheduled_workflow(cron="*/5 * * * *", ...)` to extract `cron: "*/5 * * * *"`

#### Scenario: Maps schedule to workflow module path

- **WHEN** the `webhook_selftest` function is defined in `agent-core/scheduler_setup.py`
- **THEN** the generated YAML SHALL contain `workflow.module: agent_core.scheduler_setup` and `workflow.function: webhook_selftest`

#### Scenario: Inherits timezone from decorator or config

- **WHEN** a schedule uses `cron_timezone=workspace_timezone_name()` (from `~/.tdt/config.yaml`)
- **THEN** the generated YAML SHALL contain the resolved timezone value (e.g., `Asia/Ho_Chi_Minh`)

### Requirement: Create schedules directory on first deploy

When `~/.tdt/schedules/` does not exist, the deploy script SHALL create it.

#### Scenario: Creates directory on first scheduled deploy

- **WHEN** `code-daily-scan/scripts/deploy.sh` runs and `~/.tdt/schedules/` does not exist
- **THEN** it SHALL create `~/.tdt/schedules/` with mode `0o755`

#### Scenario: Uses existing directory on subsequent deploys

- **WHEN** `webhook-receiver/scripts/deploy.sh` runs and `~/.tdt/schedules/` already exists
- **THEN** it SHALL NOT recreate the directory

### Requirement: Trigger hot-reload after manifest write (Phase 2+)

After Phase 2 is enabled, deploy scripts SHALL trigger hot-reload by updating the `.reload` sentinel file.

#### Scenario: Touches reload sentinel

- **WHEN** `~/.tdt/schedules/webhook-receiver.yaml` is written and Phase 2 is enabled
- **THEN** the deploy script SHALL write the current ISO timestamp to `~/.tdt/schedules/.reload`

#### Scenario: No reload trigger in Phase 1

- **WHEN** the system is in Phase 1 mode (scheduler logs YAML but does not apply)
- **THEN** the deploy script SHALL NOT touch the `.reload` sentinel file

### Requirement: Remove manifest when repo has no schedules

When a repo deploys with zero schedules, the deploy script SHALL delete any existing YAML manifest for that repo.

#### Scenario: Removes manifest for unscheduled repo

- **WHEN** `tdt-sheets/scripts/deploy.sh` runs and `tdt-sheets` has no scheduled workflows
- **THEN** it SHALL delete `~/.tdt/schedules/tdt-sheets.yaml` if it exists

### Requirement: Atomic manifest write

The manifest write SHALL be atomic: write to a temporary file, then rename to the target path.

#### Scenario: Atomic write via rename

- **WHEN** the deploy script writes `~/.tdt/schedules/jira-skill.yaml`
- **THEN** it SHALL write to a temporary file first, then rename atomically to prevent partial reads by the scheduler

### Requirement: YAML generation script is repo-local

Each scheduled repo SHALL own its own YAML generation script (`scripts/generate_schedule_manifest.py`) rather than relying on a central generator.

#### Scenario: Repo-local generator

- **WHEN** `agent-core/scripts/generate_schedule_manifest.py` is invoked
- **THEN** it SHALL extract schedule definitions from `agent-core/scheduler_setup.py` source
- **AND** it SHALL NOT require schedules from other repos

#### Scenario: No cross-repo dependency in generators

- **WHEN** `jira-skill/scripts/generate_schedule_manifest.py` is invoked
- **THEN** it SHALL generate `~/.tdt/schedules/jira-skill.yaml` without requiring `agent-core` to be present
