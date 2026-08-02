## ADDED Requirements

### Requirement: CLV2 observer runs as DBOS scheduled workflow
The Continuous Learning v2 observer SHALL run as a DBOS `@scheduled_workflow(cron="*/5 * * * *")` instead of a background shell `sleep` loop.

#### Scenario: Observer runs every 5 minutes
- **WHEN** the `clv2-observer` schedule is registered
- **THEN** it SHALL execute every 5 minutes via DBOS

#### Scenario: Observer survives crash
- **WHEN** the observer process is killed (`kill -9`)
- **THEN** DBOS SHALL restart it within the configured retry interval (confirm the exact DBOS parameter name / setting against the pinned `dbos>=2.22.0,<3` before implementation)

### Requirement: 3-gate system preserved
The observer's 3-gate system (time window, project cooldown, idle detection) SHALL remain in the shell script — only the outer scheduling loop changes.

#### Scenario: Time window gate still active
- **WHEN** the observer runs outside configured active hours
- **THEN** `session-guardian.sh` SHALL exit with code 1 and the workflow SHALL skip analysis

#### Scenario: Project cooldown gate still active
- **WHEN** the observer runs within the cooldown period for a project
- **THEN** `session-guardian.sh` SHALL exit with code 1

### Requirement: Remove PID file and signal handling
The PID file management and `SIGUSR1` signal handling in `observer-loop.sh` SHALL be removed — DBOS manages process lifecycle.

#### Scenario: No PID file created
- **WHEN** the observer workflow starts
- **THEN** no `.observer.pid` file SHALL be created

#### Scenario: No SIGUSR1 handling
- **WHEN** the observer workflow runs
- **THEN** there SHALL be no `trap on_usr1 USR1` signal handler
