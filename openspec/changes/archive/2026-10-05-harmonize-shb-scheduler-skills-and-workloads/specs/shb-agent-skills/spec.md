# Spec Delta: shb-agent-skills

## ADDED Requirements

### Requirement: Native Scheduler Skill Operation
The `shb-agent-skills` repository SHALL provide an operational skill (`skills/scheduler-skill/SKILL.md`) that documents and guides interaction with the native `shb-schedule` CLI, declarative YAML manifest definitions (`shb-schedule/v1`), health checks on port 9110, and dynamic reload mechanisms, completely excluding foreign CLI tools or un-sanitized external environment variables.

#### Scenario: Agent interacts with ecosystem scheduler
- **WHEN** an autonomous agent loads `scheduler-skill` to inspect or trigger scheduled workflows
- **THEN** the skill provides executable commands using `shb-schedule` (e.g. `shb-schedule validate`, `shb-schedule list`, `shb-schedule run-now`, `shb-schedule reload`)
- **AND** directs schedule declarations to `~/.shb/schedules/*.yaml` under the `shb-schedule/v1` schema
