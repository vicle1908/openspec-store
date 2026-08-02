# scheduler-dockerfile-canonicalization Specification

## Purpose
Consolidates the workspace to a single canonical scheduler Dockerfile with non-root user, timezone configuration, and a verify-before-delete protocol for orphan cleanup.
## Requirements
### Requirement: There SHALL be exactly one scheduler Dockerfile in the workspace

A single canonical scheduler Dockerfile SHALL live at `agent-core/deployments/scheduler/Dockerfile`. The path `deployments/scheduler/Dockerfile` (workspace-root relative) SHALL NOT contain a scheduler Dockerfile at the time of archive.

#### Scenario: Workspace-wide search finds exactly one scheduler Dockerfile

- **WHEN** `find /Users/lekhanhvinh/Developer/tdt -name Dockerfile -path '*scheduler*'` runs
- **AND** the result is filtered to scheduler Dockerfile files (excluding any test fixtures)
- **THEN** exactly one path SHALL remain
- **AND** that path SHALL be `/Users/lekhanhvinh/Developer/tdt/agent-core/deployments/scheduler/Dockerfile`

#### Scenario: The orphan path is removed

- **GIVEN** `deployments/scheduler/Dockerfile` (workspace-root relative) exists at archive time
- **WHEN** `git -C /Users/lekhanhvinh/Developer/tdt/deployments ls-files 2>/dev/null | grep -F 'scheduler/Dockerfile'` runs (and `deployments/` is not a git repo)
- **THEN** the orphan SHALL be deleted as the final step of the change
- **AND** the deletion SHALL be preceded by a successful healthcheck + scheduled-run verification

### Requirement: The canonical Dockerfile SHALL use `user=agent`

The canonical `agent-core/deployments/scheduler/Dockerfile` SHALL configure the container to run as the non-root `agent` user. The compose.yaml `user: agent` directive and the Dockerfile `USER` instruction SHALL be consistent.

#### Scenario: Running container reports uid 1000

- **WHEN** `docker exec agent-core-local-scheduler-1 id` runs
- **THEN** the output SHALL contain `uid=1000(agent) gid=1000(agent)`
- **AND** it SHALL NOT contain `uid=1000(scheduler)`

#### Scenario: USER instruction in the Dockerfile matches runtime

- **GIVEN** the canonical Dockerfile
- **WHEN** `grep '^USER ' /Users/lekhanhvinh/Developer/tdt/agent-core/deployments/scheduler/Dockerfile` runs
- **THEN** the output SHALL equal `USER agent`

### Requirement: The canonical Dockerfile SHALL install `tzdata` and set `Asia/Ho_Chi_Minh`

The canonical Dockerfile SHALL include `tzdata` in its `apt-get install` step and SHALL configure `/etc/localtime` to point at `Asia/Ho_Chi_Minh`. This closes the gap where the prior live image lacked `/etc/timezone` and could fall back to UTC even when the scheduler ran schedules that referenced local times.

#### Scenario: The container has the expected timezone

- **WHEN** `docker exec agent-core-local-scheduler-1 cat /etc/timezone` runs
- **THEN** the output SHALL equal `Asia/Ho_Chi_Minh\n`
- **AND** `/etc/localtime` SHALL be a symlink to `/usr/share/zoneinfo/Asia/Ho_Chi_Minh`

#### Scenario: Dockerfile declares tzdata

- **GIVEN** the canonical Dockerfile
- **WHEN** `grep -E 'tzdata|/etc/localtime|/etc/timezone' /Users/lekhanhvinh/Developer/tdt/agent-core/deployments/scheduler/Dockerfile` runs
- **THEN** at least 3 matching lines SHALL be present

### Requirement: The scheduler SHALL pass the canonical healthcheck after redeploy

After every build and redeploy, the scheduler container SHALL respond to `curl -fsS http://127.0.0.1:9100/scheduler/health` with HTTP 200 and a JSON body indicating `status: ok` (or the contract defined in `scheduler-engine`).

#### Scenario: Healthcheck returns 200 within start_period

- **GIVEN** a freshly built image
- **WHEN** `docker compose -f agent-core/compose.yaml up -d scheduler` starts the container
- **THEN** `curl -fsS http://127.0.0.1:9100/scheduler/health` SHALL return 200 within the `start_period` (120s default)

#### Scenario: Healthcheck fails fast on misconfiguration

- **WHEN** the container starts but DBOS cannot initialize
- **THEN** `docker compose ps` SHALL show the container in a restart loop
- **AND** the operator SHALL investigate before deleting the prior Dockerfile

### Requirement: The compose.yaml build context SHALL resolve to the canonical Dockerfile

`agent-core/compose.yaml` SHALL declare the scheduler service's `build.dockerfile` to be `agent-core/deployments/scheduler/Dockerfile` (relative to the workspace-root build context) so a `docker compose build` always picks up the canonical path. The build `context` SHALL be `..` (the workspace root) so the canonical Dockerfile's COPY paths can reference sibling repos and `agent-core/` without leaving the context tree.

> **Implementation note (2026-06-29):** The original draft of this requirement specified `context: .` (i.e., `agent-core/`). That is infeasible in practice because the canonical Dockerfile's COPY paths reference sibling repos (`jira-daily-reports`, `tdt-core`, etc.) and `agent-core/` is a sibling of those — Docker restricts COPY to the build-context tree, so `../jira-...` paths fail with `"/jira-daily-reports/...: not found"`. The implementation keeps `context: ..` (workspace root) and uses `dockerfile: agent-core/deployments/scheduler/Dockerfile`.

#### Scenario: After the move, `context: ..` and `dockerfile: agent-core/deployments/scheduler/Dockerfile` resolve correctly

- **WHEN** `docker compose -f agent-core/compose.yaml config --services` runs after the move
- **THEN** the output SHALL list `scheduler` with `build.context = ..`
- **AND** `build.dockerfile = agent-core/deployments/scheduler/Dockerfile`

#### Scenario: The build fails fast if the path is wrong

- **GIVEN** the canonical Dockerfile has been moved
- **WHEN** a contributor accidentally reverts `context: ..` or `dockerfile: agent-core/deployments/scheduler/Dockerfile`
- **THEN** `docker compose -f agent-core/compose.yaml build scheduler` SHALL fail with a clear "Dockerfile not found" error
- **AND** the validator SHALL report the path mismatch

### Requirement: At least one top-of-hour scheduled job SHALL run successfully post-redeploy

Within one hour of the redeploy, at least one scheduled job (e.g., `jira-sprint-sheet`) SHALL fire and complete successfully. This proves the new image can resolve the host-mounted workload code paths and execute a typical workflow.

#### Scenario: A scheduled job completes

- **WHEN** the next top-of-hour tick passes after the redeploy
- **THEN** `docker compose -f agent-core/compose.yaml logs scheduler | grep -i 'jira-sprint-sheet'` SHALL show a successful run marker
- **AND** the scheduler DBOS system database SHALL contain a recent successful workflow row

#### Scenario: A scheduled job fails post-redeploy

- **GIVEN** the new image is in production
- **WHEN** the first scheduled job fails
- **THEN** the operator SHALL roll back by tagging and re-running the previous image
- **AND** the orphan Dockerfile SHALL NOT be deleted until the failure is diagnosed

### Requirement: The orphan Dockerfile SHALL be deleted only after a verified redeploy

The orphan `deployments/scheduler/Dockerfile` SHALL NOT be deleted until the new canonical image has been built, the container has passed the healthcheck, and at least one scheduled job has run successfully. The verify-before-delete protocol is mandatory; an OpenSpec archive event SHALL NOT proceed while the orphan remains.

#### Scenario: Verification checklist is enforced

- **GIVEN** the cleanup is in progress
- **WHEN** the operator reaches the orphan-deletion step
- **THEN** the operator SHALL first confirm:
  1. `docker compose -f agent-core/compose.yaml build scheduler` exits 0
  2. `docker compose -f agent-core/compose.yaml up -d scheduler` exits 0
  3. `curl -fsS http://127.0.0.1:9100/scheduler/health` returns 200
  4. `docker compose logs scheduler` shows a recent scheduled-run success
- **AND** only then SHALL `rm /Users/lekhanhvinh/Developer/tdt/deployments/scheduler/Dockerfile` execute

#### Scenario: Rollback if healthcheck fails

- **GIVEN** the canonical image fails the healthcheck
- **WHEN** the operator verifies the failure
- **THEN** the operator SHALL roll back by `docker compose -f agent-core/compose.yaml up -d --force-recreate --image <prior-tag>`
- **AND** the orphan Dockerfile SHALL be preserved until the failure is fixed

