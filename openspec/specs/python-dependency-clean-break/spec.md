# python-dependency-clean-break Specification

## Purpose
Enforces a clean-break dependency modernization standard across all workspace Python repositories, requiring unrestricted tracking of latest stable releases, purging legacy shims, and coordinating internal SDK version cascades.

## Requirements

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

### Requirement: Zero backward-compatibility shims
Workspace Python source code SHALL adopt modern upstream APIs directly without preserving legacy polyfills, fallback imports, or deprecated framework mechanisms.

#### Scenario: Modern ASGI lifecycle and standard library usage
- **WHEN** FastAPI services or CLI modules initialize runtime contexts
- **THEN** they SHALL use async `lifespan` context managers rather than deprecated `@app.on_event` handlers
- **AND** timestamp calculations SHALL use `datetime.now(datetime.UTC)` instead of deprecated `datetime.utcnow()`
- **AND** type annotations SHALL use Python 3.14 native syntax (`T | None`, `list[T]`) without `typing.Optional` or `typing.Union`.

### Requirement: Coordinated internal SDK SemVer cascade
Internal workspace package versions SHALL be bumped synchronously, and all consuming repositories SHALL update their minimum version bounds without retaining backward-compatibility branches.

#### Scenario: Tiered SDK version propagation
- **WHEN** `tdt-core` is upgraded to `0.4.0` incorporating DBOS v3
- **THEN** `tdt-sheets` SHALL bump to `0.2.0`, `jira-skill` to `0.4.0`, and `agent-core` to `0.3.0`
- **AND** all 12 downstream consumers SHALL declare dependencies matching the new version floors (`tdt-core>=0.4.0`, `agent-core>=0.3.0`, `jira-skill>=0.4.0`)
- **AND** no consumer manifest SHALL retain legacy `<0.4` or `<0.3` bounds.

### Requirement: Upstream framework modernization
All runtime frameworks, including DBOS, Anthropic SDK, Pydantic AI, DuckDB, Redis, and Pandas, SHALL be upgraded to their latest major releases across all services, and callers SHALL conform strictly to updated public API signatures.

#### Scenario: Framework upgrade verification
- **WHEN** running test suites in `agent-core`, `shb-agent-core`, `tdt-core`, and `viettel-excel-updater`
- **THEN** `agent-core` and `shb-agent-core` SHALL execute against `pydantic-ai>=2.66.0`, `pydantic-ai-harness>=0.66.0`, and `anthropic>=1.8.0` without legacy v0 client helpers
- **AND** `tdt-core` and `shb-schedule` SHALL execute against `dbos>=3.4.0` public client APIs
- **AND** `viettel-excel-updater` SHALL execute against `pandas>=3.0.6` enforcing pure Copy-on-Write semantics without `SettingWithCopyError`
- **AND** `tdt-observability` SHALL execute against `duckdb>=2.0.0` LTS utilizing asynchronous I/O and native storage
- **AND** `agent-core` and `shb-agent-core` SHALL execute against `redis>=8.1.0` utilizing default RESP3 wire protocol connections.

#### Scenario: DBOS 3.3.0 public API conformance in tdt-core
- **WHEN** `tdt-core` initializes the DBOS client or registers persistent queues
- **THEN** client instantiation SHALL use `DBOSClient(system_database_url=...)`
- **AND** configuration TypedDicts SHALL use `system_database_url`
- **AND** persistent queue registration SHALL use `DBOS.register_queue(name, ...)` rather than direct `Queue(...)` instantiation.

### Requirement: Modern web framework and clean test client standards
FastAPI services and webhook handlers SHALL enforce modern boolean form field default resolution and provide clean test clients without deprecation warnings.

#### Scenario: Explicit boolean form field defaults
- **WHEN** FastAPI endpoints in `webhook-receiver`, `shb-webhook-receiver`, or `shb-schedule` define boolean form fields or models
- **THEN** they SHALL specify explicit default values (e.g. `Field(default=False)`) rather than relying on automatic falsy coercion
- **AND** dev dependency groups SHALL declare `httpx2>=2.16.0` alongside `httpx` to eliminate Starlette TestClient deprecation warnings.

### Requirement: Container packaging clean-break and zero dead requirements
Container Dockerfiles across workspace Python services SHALL declare base images satisfying the service's declared Python version baseline (`python:3.15.1-slim-trixie`), build dependencies exclusively using `uv sync --frozen`, and SHALL NOT reference obsolete or deleted `requirements.txt` manifests.

#### Scenario: Docker container builds cleanly with uv and matching Python baseline
- **WHEN** building a container image for a Python service (such as `tdt/jira-skill`)
- **THEN** the Dockerfile SHALL declare a base image satisfying the repository's `requires-python` specification (`python:3.15.1-slim-trixie`)
- **AND** the Dockerfile SHALL obtain `uv` from official multi-stage distribution images (`ghcr.io/astral-sh/uv`)
- **AND** the Dockerfile SHALL install locked dependencies using `uv sync --frozen --no-dev`
- **AND** the build SHALL NOT fail due to missing `requirements.txt` files or Python runtime mismatches
