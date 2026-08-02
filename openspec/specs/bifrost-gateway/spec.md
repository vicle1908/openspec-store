## Purpose

This specification defines requirements for Bifrost Gateway.

## Requirements

### Requirement: Bifrost SHALL run as a Docker Compose service

The system SHALL deploy Bifrost via a Docker Compose file located at `deployments/bifrost/docker-compose.yml`. The service SHALL use the upstream `maximhq/bifrost:latest` image without a custom Dockerfile.

#### Scenario: Service starts successfully
- **WHEN** `docker compose up -d` is run from `deployments/bifrost/`
- **THEN** the Bifrost container starts and becomes healthy within 30 seconds

#### Scenario: Service restarts automatically
- **WHEN** the Bifrost container crashes or the host reboots
- **THEN** the container restarts automatically (restart policy: unless-stopped)

### Requirement: Bifrost SHALL persist configuration and logs

The system SHALL mount `${HOME}/.tdt/bifrost` to `/app/data` inside the container. Bifrost's SQLite database (`config.db`), request logs (`logs.db`), and any `config.json` seed file SHALL survive container rebuilds and restarts.

#### Scenario: Configuration persists across restarts
- **WHEN** a provider is configured via the Web UI and the container is restarted
- **THEN** the provider configuration is still present after restart

#### Scenario: Data directory is created if missing
- **WHEN** `~/.tdt/bifrost/` does not exist and `docker compose up -d` is run
- **THEN** Docker creates the directory automatically as a root-owned volume mount

### Requirement: Bifrost SHALL expose an OpenAI-compatible API

The system SHALL expose the Bifrost gateway at `http://localhost:8180/v1/chat/completions` (and other `/v1/*` endpoints). The host port SHALL be 8180, bound to loopback only (`127.0.0.1`).

#### Scenario: Chat completion via API
- **WHEN** a POST request is sent to `http://localhost:8180/v1/chat/completions` with a valid model and messages
- **THEN** Bifrost returns an OpenAI-compatible chat completion response

#### Scenario: Models endpoint lists configured models
- **WHEN** a GET request is sent to `http://localhost:8180/v1/models`
- **THEN** Bifrost returns a list of models configured through the Web UI

#### Scenario: No LAN exposure
- **WHEN** the Bifrost service is running
- **THEN** port 8180 is only accessible from `127.0.0.1` (not from LAN or other machines)

### Requirement: Bifrost SHALL expose a health check endpoint

The system SHALL provide a health check at `GET /health` returning HTTP 200 with `"status":"ok"` in the response body. The full response format is `{"components":{"db_pings":"ok"},"status":"ok"}`. The Docker Compose healthcheck SHALL use this endpoint.

#### Scenario: Health check returns OK
- **WHEN** a GET request is sent to `http://localhost:8180/health`
- **THEN** the response is HTTP 200 with body containing `"status":"ok"`

#### Scenario: Docker health check uses wget
- **WHEN** the Docker healthcheck runs inside the container
- **THEN** it uses `wget -qO- http://localhost:8080/health` (Bifrost image has wget, not curl)

#### Scenario: Docker health check passes
- **WHEN** the container is running and healthy
- **THEN** `docker inspect --format='{{.State.Health.Status}}'` returns `"healthy"`

### Requirement: Bifrost SHALL expose a Web UI

The system SHALL serve a Web UI at `http://localhost:8180/` for configuring providers, viewing request logs, and managing gateway settings.

#### Scenario: Web UI is accessible
- **WHEN** a browser navigates to `http://localhost:8180/`
- **THEN** the Bifrost dashboard loads successfully

#### Scenario: Provider can be added via Web UI
- **WHEN** a user adds a provider (e.g., OpenAI) with an API key through the Web UI
- **THEN** the provider is saved to the SQLite database and available for routing requests

### Requirement: Bifrost SHALL follow TDT deployment conventions

The deployment SHALL use `docker compose` (v2, no hyphen). The service SHALL bind to loopback only. The compose file SHALL include a health check with appropriate intervals. The compose project name SHALL be `bifrost`.

#### Scenario: Docker compose v2 is used
- **WHEN** the service is managed via Docker Compose
- **THEN** `docker compose` (v2) commands are used, not `docker-compose` (hyphen)

#### Scenario: Health check is configured
- **WHEN** the container is running
- **THEN** Docker reports health status with 30s interval, 5s timeout, 3 retries, and 15s start period
