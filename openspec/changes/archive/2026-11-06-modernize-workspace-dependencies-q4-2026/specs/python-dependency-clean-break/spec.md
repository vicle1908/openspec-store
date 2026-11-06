# Spec Delta: python-dependency-clean-break

## MODIFIED Requirements

### Requirement: Purge legacy upper bound constraints
All Python repositories in the workspace SHALL omit legacy `<` upper bound specifiers from direct runtime dependencies and developer dependency groups, allowing unconstrained resolution to the latest available PyPI releases, and SHALL enforce `requires-python = ">=3.15"`.

#### Scenario: Manifest constraints are unpinned from legacy ceilings
- **WHEN** inspecting `project.dependencies` and `dependency-groups` across all workspace `pyproject.toml` files
- **THEN** no dependency specification SHALL contain an upper bound operator (`<` or `<=`) restricting major framework upgrades
- **AND** all OpenTelemetry dependencies (`opentelemetry-sdk`, `opentelemetry-exporter-otlp-proto-grpc`) SHALL resolve to `>=1.45.2`
- **AND** dependencies SHALL specify minimum versions using `>=` aligned with latest tested releases.

#### Scenario: Minimum Python version requires-python is 3.15
- **WHEN** inspecting `project.requires-python` across all workspace `pyproject.toml` files
- **THEN** the value SHALL equal `">=3.15"`.

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

## ADDED Requirements

### Requirement: Modern web framework and clean test client standards
FastAPI services and webhook handlers SHALL enforce modern boolean form field default resolution and provide clean test clients without deprecation warnings.

#### Scenario: Explicit boolean form field defaults
- **WHEN** FastAPI endpoints in `webhook-receiver`, `shb-webhook-receiver`, or `shb-schedule` define boolean form fields or models
- **THEN** they SHALL specify explicit default values (e.g. `Field(default=False)`) rather than relying on automatic falsy coercion
- **AND** dev dependency groups SHALL declare `httpx2>=2.16.0` alongside `httpx` to eliminate Starlette TestClient deprecation warnings.
