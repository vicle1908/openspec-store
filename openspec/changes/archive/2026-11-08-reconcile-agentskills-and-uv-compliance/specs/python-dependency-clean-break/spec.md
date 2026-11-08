# Spec Delta: python-dependency-clean-break

## ADDED Requirements

### Requirement: Container packaging clean-break and zero dead requirements
Container Dockerfiles across workspace Python services SHALL declare base images satisfying the service's declared Python version baseline (`python:3.15.1-slim-trixie`), build dependencies exclusively using `uv sync --frozen`, and SHALL NOT reference obsolete or deleted `requirements.txt` manifests.

#### Scenario: Docker container builds cleanly with uv and matching Python baseline
- **WHEN** building a container image for a Python service (such as `tdt/jira-skill`)
- **THEN** the Dockerfile SHALL declare a base image satisfying the repository's `requires-python` specification (`python:3.15.1-slim-trixie`)
- **AND** the Dockerfile SHALL obtain `uv` from official multi-stage distribution images (`ghcr.io/astral-sh/uv`)
- **AND** the Dockerfile SHALL install locked dependencies using `uv sync --frozen --no-dev`
- **AND** the build SHALL NOT fail due to missing `requirements.txt` files or Python runtime mismatches

## MODIFIED Requirements

### Requirement: Purge legacy upper bound constraints
All Python repositories in the workspace, including auxiliary web interfaces such as `platform/hermes-webui`, SHALL omit legacy `<` upper bound specifiers from direct runtime dependencies and developer dependency groups, allowing unconstrained resolution to the latest available PyPI releases, and SHALL enforce `requires-python = ">=3.15"`.

#### Scenario: Manifest constraints are unpinned from legacy ceilings
- **WHEN** inspecting `project.dependencies` and `dependency-groups` across all workspace `pyproject.toml` files
- **THEN** no dependency specification SHALL contain an upper bound operator (`<` or `<=`) restricting major framework upgrades
- **AND** all OpenTelemetry dependencies (`opentelemetry-sdk`, `opentelemetry-exporter-otlp-proto-grpc`) SHALL resolve to `>=1.45.2`
- **AND** dependencies SHALL specify minimum versions using `>=` aligned with latest tested releases.

#### Scenario: Minimum Python version requires-python is 3.15
- **WHEN** inspecting `project.requires-python` across all workspace `pyproject.toml` files
- **THEN** the value SHALL equal `">=3.15"`.

#### Scenario: Platform Hermes WebUI conforms to workspace Python baseline
- **WHEN** inspecting `platform/hermes-webui/pyproject.toml`
- **THEN** `project.requires-python` SHALL specify `">=3.15"`
- **AND** `requirements.txt` SHALL NOT be present in the repository root
- **AND** dev dependencies SHALL be defined using modern `[dependency-groups]`
