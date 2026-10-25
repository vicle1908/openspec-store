# Spec Delta: agent-core-docker-local-development

## ADDED Requirements

### Requirement: Python 3.15.1 and uv 0.13.5 Local Docker Stack Baseline
Following the workspace-wide Python 3.15.1 and `uv 0.13.5` standardization, the `tdt/agent-core` `Dockerfile`, `compose.yaml`, and local Docker verification tests (`tests/test_docker_local_dev.py`) SHALL pin `PYTHON_IMAGE=python:3.15.1-slim-trixie` and `UV_IMAGE=ghcr.io/astral-sh/uv:0.13.5` alongside `postgres:18.6-trixie`.

#### Scenario: Dockerfile and compose.yaml match Python 3.15.1 and uv 0.13.5 pins
- **WHEN** `tdt/agent-core/Dockerfile`, `tdt/agent-core/compose.yaml`, and `tdt/agent-core/tests/test_docker_local_dev.py` are inspected and executed via `uv run pytest tests/test_docker_local_dev.py`
- **THEN** both `Dockerfile` default `ARG` values and `compose.yaml` `services.app.build.args` SHALL specify `python:3.15.1-slim-trixie` and `ghcr.io/astral-sh/uv:0.13.5`
- **AND** `uv run pytest tests/test_docker_local_dev.py` SHALL exit `0`.
