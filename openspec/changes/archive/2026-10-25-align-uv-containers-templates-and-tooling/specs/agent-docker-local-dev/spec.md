# Spec Delta: agent-docker-local-dev

## ADDED Requirements

### Requirement: Python 3.15.1 and uv 0.13.5 App Container Image Baseline
The `agent-core` local development Docker Compose stack SHALL build the `app` service from `python:3.15.1-slim-trixie` using `ghcr.io/astral-sh/uv:0.13.5` to satisfy `requires-python = ">=3.15"` and `required-version = ">=0.13.5"` in `pyproject.toml`.

#### Scenario: Local development stack uses Python 3.15.1 and uv 0.13.5
- **WHEN** the `agent-core` local Docker Compose configuration is inspected
- **THEN** the `app` image SHALL build from `python:3.15.1-slim-trixie` with `ghcr.io/astral-sh/uv:0.13.5`
- **AND** the `postgres` service SHALL retain `postgres:18.6-trixie` with its PostgreSQL-18-versioned named volume.
