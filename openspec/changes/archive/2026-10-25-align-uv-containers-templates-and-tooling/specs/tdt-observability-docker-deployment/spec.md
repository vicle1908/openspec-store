# Spec Delta: tdt-observability-docker-deployment

## ADDED Requirements

### Requirement: Python 3.15.1 and uv 0.13.5 Observability Builder and Runtime Image Baseline
The `tdt/tdt-observability` image inventory (`deploy/tools.env`), multi-stage `Dockerfile`, and deployment verification tests (`tests/test_compose_models.py`, `tests/test_dockerfile_paths.py`) SHALL advance `PYTHON_VERSION` to `3.15.1-slim-trixie` and `UV_VERSION` to `0.13.5`, and create `/app/.venv` using `python3.15 -m venv --copies --without-pip /app/.venv`.

#### Scenario: Authoritative deploy/tools.env and Dockerfile agree on Python 3.15.1 and uv 0.13.5
- **WHEN** `deploy/tools.env`, `Dockerfile`, `tests/test_compose_models.py`, and `tests/test_dockerfile_paths.py` are inspected and tested in `tdt/tdt-observability`
- **THEN** `deploy/tools.env` SHALL define `PYTHON_VERSION=3.15.1-slim-trixie` and `UV_VERSION=0.13.5`
- **AND** `Dockerfile` SHALL use `FROM python:3.15.1-slim-trixie` in both `builder` and `runtime` stages, `COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /usr/local/bin/uv`, and `RUN python3.15 -m venv --copies --without-pip /app/.venv`
- **AND** `uv run pytest` SHALL exit `0`.
