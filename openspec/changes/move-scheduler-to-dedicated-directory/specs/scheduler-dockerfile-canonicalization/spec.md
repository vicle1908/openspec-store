## MODIFIED Requirements

### Requirement: There SHALL be exactly one scheduler Dockerfile in the workspace

A single canonical scheduler Dockerfile SHALL live at `tdt-scheduler/Dockerfile`. The previous path `agent-core/deployments/scheduler/Dockerfile` SHALL NOT contain a scheduler Dockerfile at the time of archive.

#### Scenario: Workspace-wide search finds exactly one scheduler Dockerfile

- **WHEN** `find ~/Developer -name Dockerfile -path '*scheduler*'` runs
- **AND** the result is filtered to scheduler Dockerfile files (excluding any test fixtures)
- **THEN** exactly one path SHALL remain
- **AND** that path SHALL be `~/Developer/tdt-scheduler/Dockerfile`

#### Scenario: The orphan path is removed

- **GIVEN** `agent-core/deployments/scheduler/Dockerfile` exists at archive time
- **WHEN** the change is archived
- **THEN** the old Dockerfile SHALL be deleted from `agent-core/deployments/scheduler/`
- **AND** the deletion SHALL be preceded by a successful healthcheck + scheduled-run verification

### Requirement: The canonical Dockerfile SHALL use `user=agent`

The canonical `tdt-scheduler/Dockerfile` SHALL configure the container to run as the non-root `agent` user. The compose.yaml `user: agent` directive and the Dockerfile `USER` instruction SHALL be consistent.

#### Scenario: Running container reports uid 1000

- **WHEN** `docker exec <scheduler-container> id` runs
- **THEN** the output SHALL contain `uid=1000(agent) gid=1000(agent)`

#### Scenario: USER instruction in the Dockerfile matches runtime

- **GIVEN** the canonical Dockerfile at `tdt-scheduler/Dockerfile`
- **WHEN** `grep '^USER ' tdt-scheduler/Dockerfile` runs
- **THEN** the output SHALL equal `USER agent`

### Requirement: The canonical Dockerfile SHALL install `tzdata` and set `Asia/Ho_Chi_Minh`

The canonical Dockerfile SHALL include `tzdata` in its `apt-get install` step and SHALL configure `/etc/localtime` to point at `Asia/Ho_Chi_Minh`.

#### Scenario: The container has the expected timezone

- **WHEN** `docker exec <scheduler-container> cat /etc/timezone` runs
- **THEN** the output SHALL equal `Asia/Ho_Chi_Minh\n`

#### Scenario: Dockerfile declares tzdata

- **GIVEN** the canonical Dockerfile at `tdt-scheduler/Dockerfile`
- **WHEN** `grep -E 'tzdata|/etc/localtime|/etc/timezone' tdt-scheduler/Dockerfile` runs
- **THEN** at least 3 matching lines SHALL be present

### Requirement: The compose.yaml build context SHALL resolve to the canonical Dockerfile

`tdt-scheduler/compose.yaml` SHALL declare the scheduler service's `build.context` to be `..` (the workspace root) and `build.dockerfile` to be `tdt-scheduler/Dockerfile` so `docker compose build` picks up the canonical Dockerfile. The context MUST be the workspace root because the Dockerfile COPY paths reference sibling repos (`../tdt-core`, `../jira-daily-reports`, etc.) that are unreachable from `tdt-scheduler/` alone.

#### Scenario: After the move, `context: ..` and `dockerfile: agent-core/deployments/scheduler/Dockerfile` resolve correctly

- **WHEN** `docker compose -f tdt-scheduler/compose.yaml config --services` runs after the move
- **THEN** the output SHALL list `scheduler` with `build.context = ..`
- **AND** `build.dockerfile = tdt-scheduler/Dockerfile`
- **AND** the canonical Dockerfile SHALL be resolved correctly from the workspace root context

#### Scenario: The build fails fast if the path is wrong

- **GIVEN** the canonical Dockerfile has been moved
- **WHEN** a contributor accidentally sets `dockerfile: agent-core/deployments/scheduler/Dockerfile`
- **THEN** `docker compose -f tdt-scheduler/compose.yaml build scheduler` SHALL fail with a clear "Dockerfile not found" error

### Requirement: At least one top-of-hour scheduled job SHALL run successfully post-redeploy

Within one hour of the redeploy, at least one scheduled job SHALL fire and complete successfully. This proves the new image can resolve the host-mounted workload code paths and execute a typical workflow.

#### Scenario: A scheduled job completes

- **WHEN** the next top-of-hour tick passes after the redeploy
- **THEN** `docker compose -f tdt-scheduler/compose.yaml logs scheduler` SHALL show a successful run marker

#### Scenario: A scheduled job fails post-redeploy

- **GIVEN** the new image is in production
- **WHEN** the first scheduled job fails
- **THEN** the operator SHALL roll back by tagging and re-running the previous image

### Requirement: The scheduler SHALL pass the canonical healthcheck after redeploy

After every build and redeploy, the scheduler container SHALL respond to `curl -fsS http://127.0.0.1:9100/scheduler/health` with HTTP 200.

#### Scenario: Healthcheck returns 200 within start_period

- **GIVEN** a freshly built image
- **WHEN** `docker compose -f tdt-scheduler/compose.yaml up -d scheduler` starts the container
- **THEN** `curl -fsS http://127.0.0.1:9100/scheduler/health` SHALL return 200 within the `start_period`

#### Scenario: Healthcheck fails fast on misconfiguration

- **WHEN** the container starts but DBOS cannot initialize
- **THEN** `docker compose ps` SHALL show the container in a restart loop
