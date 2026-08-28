## MODIFIED Requirements

### Requirement: OmniRoute SHALL expose an OpenAI-compatible model API

The deployment SHALL expose the configured model endpoint on the local host.
In the standard three-port profile, the model API endpoint SHALL be
`http://127.0.0.1:20128/v1`, including `/chat/completions`, `/responses`,
and `/models` as supported by the selected provider. Published listeners
SHALL bind to loopback unless an operator explicitly configures another
network boundary. `HEAD /v1/models` SHALL return HTTP 200 as the public
availability probe. Anonymous `GET /v1/models` SHALL return HTTP 200 with a
non-empty catalog when catalog authentication is disabled, and SHALL return
HTTP 401 with an `invalid_api_key` error when catalog authentication is
enabled. Since v3.8.50, catalog authentication is opt-out (enforced whenever
dashboard authentication is required unless `requireAuthForModels` is
explicitly false). A request carrying a valid Bearer API key SHALL receive
HTTP 200 with a non-empty catalog in either posture.

#### Scenario: Chat completion through the proxy

- **WHEN** a valid OpenAI Chat Completions request is sent to `http://127.0.0.1:20128/v1/chat/completions`
- **THEN** OmniRoute returns an OpenAI-compatible completion response from the selected provider

#### Scenario: Models endpoint lists available models

- **WHEN** a client sends an authenticated `GET http://127.0.0.1:20128/v1/models` with a valid Bearer API key
- **THEN** OmniRoute returns the models exposed by the configured provider set

#### Scenario: No LAN exposure by default

- **WHEN** the standard local profile is running
- **THEN** the model API is reachable from the host loopback interface and is not exposed to the LAN

#### Scenario: HEAD models probe is public

- **WHEN** a client sends `HEAD http://127.0.0.1:20128/v1/models` without credentials
- **THEN** OmniRoute returns HTTP 200 as the availability probe

#### Scenario: Anonymous catalog access follows the configured auth posture

- **WHEN** catalog authentication is enabled and a client sends an unauthenticated `GET http://127.0.0.1:20128/v1/models`
- **THEN** OmniRoute returns HTTP 401 with an `invalid_api_key` error
- **AND** when catalog authentication is disabled the same request returns HTTP 200 with a non-empty catalog

### Requirement: OmniRoute SHALL persist runtime data

The deployment SHALL persist OmniRoute runtime state on the Docker named
volume `omniroute-data` mounted at `/app/data`. Host filesystem bind mounts
SHALL NOT be used for `/app/data` because Docker Desktop for Mac virtiofs
bind mounts corrupt SQLite WAL databases and OmniRoute hardcodes WAL mode.
Redis rate-limiter state SHALL use the named `omniroute-redis-data` volume,
and the Redis service SHALL NOT publish any port to the host.

#### Scenario: Configuration persists across restarts

- **WHEN** OmniRoute runtime configuration is changed and the container is restarted
- **THEN** the configuration and runtime data remain available after restart

#### Scenario: Named volume survives container recreation

- **WHEN** `docker compose --profile base up -d --no-build` recreates the `omniroute` container
- **THEN** the `omniroute-data` volume is reattached at `/app/data` and the SQLite database and its runtime state remain intact

#### Scenario: Data directory is created if missing

- **WHEN** the `omniroute-data` named volume does not yet exist and the Compose profile is started
- **THEN** Docker creates the named volume mounted at `/app/data` and the service can initialize its data store

#### Scenario: Redis is not host-published

- **WHEN** the rendered Compose configuration is inspected
- **THEN** the `redis` service has no published ports and is reachable only via the Compose network

### Requirement: OmniRoute SHALL expose a dashboard and health status

The service SHALL serve its dashboard on the configured main port and SHALL
expose the health behavior used by the Compose health check. The health check
SHALL use the image-provided `node healthcheck.mjs` command with a
30-second interval, 15-second timeout, 3 retries, and 120-second start
period. The relaxed timeout and start period are deployment-owned overrides
in `docker-compose.override.yml` because the upstream 5-second timeout
false-positives during background model and credential sync while the app
remains functional.

#### Scenario: Dashboard is accessible locally

- **WHEN** a client requests `http://127.0.0.1:20128/`
- **THEN** the OmniRoute dashboard responds (directly or via redirect to login) and reports the local proxy status

#### Scenario: Compose health check passes

- **WHEN** the service is running and its model proxy process is ready
- **THEN** `docker inspect --format='{{.State.Health.Status}}' omniroute` returns `healthy`

#### Scenario: Health check failure is visible

- **WHEN** the proxy process cannot serve its configured endpoint
- **THEN** the Compose health status becomes `unhealthy` and the container logs retain the diagnostic output

## ADDED Requirements

### Requirement: OmniRoute image upgrades SHALL be fail-closed and evidence-gated

Upgrades of the OmniRoute runtime SHALL be performed by pulling the Docker
Hub image and recreating the container; source compilation SHALL NOT be
used. The update workflow SHALL pass a SQLite snapshot gate (live-database
`integrity_check` equals `ok` and a snapshot copy reaches the host) before
any image pull, SHALL verify the pulled image digest equals the flagged
target digest before deployment, and SHALL verify container health, the
in-image package version, the running container's image id, the dashboard
and health and model endpoints, and post-deploy database integrity and
persistence indicators before clearing the update flag. On any failed gate
the workflow SHALL stop, SHALL retain the update flag, and SHALL record the
failed gate; the flag SHALL be cleared only after all gates pass. An
application image upgrade SHALL NOT activate unrelated Compose profiles,
SHALL NOT change the deployed Redis major version, and SHALL NOT alter the
loopback-only port bindings, the named-volume layout, or the disabled
SOCKS5 proxy configuration.

#### Scenario: Snapshot gate blocks an unsafe upgrade

- **WHEN** the pre-update SQLite snapshot fails or the live database `integrity_check` is not `ok`
- **THEN** the update stops before any image pull and the update flag remains present

#### Scenario: Digest mismatch blocks deployment

- **WHEN** the pulled `diegosouzapw/omniroute:latest` RepoDigest differs from the flagged target digest
- **THEN** the update stops before container recreation and the update flag is retained

#### Scenario: Flag cleared only after full verification

- **WHEN** the health, version, image-id, endpoint, and post-deploy data gates all pass
- **THEN** the update flag is removed and the success is recorded in the update log

#### Scenario: Failed gate retains the flag

- **WHEN** any verification gate fails during or after deployment
- **THEN** the update flag remains present, the failed gate is logged, and no success notification is sent

#### Scenario: Upgrade does not change unrelated infrastructure

- **WHEN** an application image upgrade is applied
- **THEN** the Redis image remains the currently deployed major version, no new Compose profile is activated, published ports remain bound to 127.0.0.1, `/app/data` remains on the `omniroute-data` named volume, and the SOCKS5 proxy flags remain disabled
