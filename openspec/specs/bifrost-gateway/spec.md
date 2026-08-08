# OmniRoute Proxy Specification

## Purpose

This specification defines the local OmniRoute proxy deployment and its integration with agent-core's native pydantic-ai model API. OmniRoute provides an OpenAI-compatible endpoint; agent consumers resolve a pydantic-ai `Model` with `create_model()` and pass it through the `model=` parameter.

## Requirements

### Requirement: OmniRoute SHALL run as a Docker Compose service

The system SHALL deploy OmniRoute from `~/Omniroute/docker-compose.yml` with the `base` profile. The local override SHALL use the pre-built `diegosouzapw/omniroute:latest` image, and the service SHALL be named `omniroute` with `restart: unless-stopped`.

#### Scenario: Service starts successfully
- **WHEN** `docker compose --profile base up -d --no-build` is run from `~/Omniroute/`
- **THEN** the `omniroute` container starts and its Compose health check becomes healthy

#### Scenario: Service restarts automatically
- **WHEN** the OmniRoute container crashes or the host restarts Docker
- **THEN** Docker restarts the container using the `unless-stopped` policy

### Requirement: OmniRoute SHALL persist runtime data

The deployment SHALL mount `~/Omniroute/data` to `/app/data` in the container. OmniRoute runtime state, SQLite data, and backups SHALL survive container recreation. Redis rate-limiter state SHALL use the named `omniroute-redis-data` volume when the Redis service is enabled.

#### Scenario: Configuration persists across restarts
- **WHEN** OmniRoute runtime configuration is changed and the container is restarted
- **THEN** the configuration and runtime data remain available after restart

#### Scenario: Data directory is created if missing
- **WHEN** `~/Omniroute/data/` does not exist and the Compose profile is started
- **THEN** Docker creates the bind-mount source directory and the service can initialize its data store

### Requirement: OmniRoute SHALL expose an OpenAI-compatible model API

The deployment SHALL expose the configured model endpoint on the local host. In the standard single-port profile, the endpoint SHALL be `http://127.0.0.1:20128/v1`, including `/chat/completions`, `/responses`, and `/models` as supported by the selected provider. Published listeners SHALL bind to loopback unless an operator explicitly configures another network boundary.

#### Scenario: Chat completion through the proxy
- **WHEN** a valid OpenAI Chat Completions request is sent to `http://127.0.0.1:20128/v1/chat/completions`
- **THEN** OmniRoute returns an OpenAI-compatible completion response from the selected provider

#### Scenario: Models endpoint lists available models
- **WHEN** a client sends `GET http://127.0.0.1:20128/v1/models`
- **THEN** OmniRoute returns the models exposed by the configured provider set

#### Scenario: No LAN exposure by default
- **WHEN** the standard local profile is running
- **THEN** the model API is reachable from the host loopback interface and is not exposed to the LAN

### Requirement: Native model resolution SHALL be the consumer integration boundary

Agent-core consumers SHALL resolve the configured model through `create_model()` and pass the resulting pydantic-ai `Model` through `model=`. Endpoint, API key, and timeout overrides SHALL be represented by `ModelSettings` or explicit `create_model()` keyword arguments; consumers SHALL NOT construct a separate proxy client abstraction.

#### Scenario: Consumer resolves an OmniRoute model
- **WHEN** a consumer loads `model.primary` and `model.base_url` from its settings
- **THEN** it calls `create_model(model_id, base_url=base_url, api_key=api_key)` and receives a pydantic-ai `Model`
- **AND** it passes that instance to agent construction as `model=model`

#### Scenario: Explicit model settings override environment defaults
- **WHEN** `create_model()` receives an explicit `ModelSettings` value or explicit endpoint and API-key arguments
- **THEN** those values take precedence over the process environment and provider defaults

#### Scenario: Upstream model failure is typed
- **WHEN** OmniRoute returns an API failure or cannot reach the selected provider
- **THEN** the model call raises `ModelAPIError` with a safe diagnostic category and without exposing credentials

### Requirement: Native retry and fallback SHALL handle provider failures

Consumers SHALL use pydantic-ai's native retry behavior and `FallbackModel` for optional provider failover. They SHALL NOT add a second resilience wrapper around OmniRoute calls. A fallback SHALL be attempted only for configured retryable model failures; authentication and invalid-request failures SHALL remain terminal.

#### Scenario: Transient model failure is retried
- **WHEN** a model call fails with a timeout, connection error, or retryable 5xx response
- **THEN** native model retry applies the configured retry limit and backoff before returning failure

#### Scenario: Fallback model is attempted
- **WHEN** the primary OmniRoute-backed model fails with a retryable `ModelAPIError` and a fallback model is configured
- **THEN** `FallbackModel` attempts the fallback model

#### Scenario: Non-retryable model failure is not hidden
- **WHEN** the provider returns an authentication or invalid-request error
- **THEN** the error is surfaced immediately and no fallback attempt is made

### Requirement: OmniRoute SHALL expose a dashboard and health status

The service SHALL serve its dashboard on the configured main port and SHALL expose the health behavior used by the Compose health check. The health check SHALL use the image-provided `node healthcheck.mjs` command with a 30-second interval, 5-second timeout, 3 retries, and 15-second start period.

#### Scenario: Dashboard is accessible locally
- **WHEN** a browser navigates to `http://127.0.0.1:20128/`
- **THEN** the OmniRoute dashboard loads and reports the local proxy status

#### Scenario: Compose health check passes
- **WHEN** the service is running and its model proxy process is ready
- **THEN** `docker inspect --format='{{.State.Health.Status}}' omniroute` returns `healthy`

#### Scenario: Health check failure is visible
- **WHEN** the proxy process cannot serve its configured endpoint
- **THEN** the Compose health status becomes `unhealthy` and the container logs retain the diagnostic output

### Requirement: OmniRoute SHALL follow local deployment conventions

The deployment SHALL use Docker Compose v2 commands, keep the `base` profile opt-in, use loopback-only bindings for local model traffic by default, and keep secrets in the untracked `.env` file or an approved secret manager. The compose project and primary container name SHALL be `omniroute`.

#### Scenario: Docker Compose v2 is used
- **WHEN** the service is managed from the deployment directory
- **THEN** `docker compose` commands are used rather than the legacy `docker-compose` command

#### Scenario: Secrets are not committed
- **WHEN** the deployment is prepared for a new workstation
- **THEN** provider API keys are supplied through `.env` or an approved secret store and no secret value is committed to the repository
