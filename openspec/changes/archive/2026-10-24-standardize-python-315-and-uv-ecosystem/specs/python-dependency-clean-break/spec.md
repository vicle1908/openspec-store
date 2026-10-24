# Spec Delta: python-dependency-clean-break

## MODIFIED Requirements

### Requirement: Purge legacy upper bound constraints
All Python repositories in the workspace SHALL omit legacy `<` upper bound specifiers from direct runtime dependencies and developer dependency groups, allowing unconstrained resolution to the latest available PyPI releases, and SHALL enforce `requires-python = ">=3.15"`.

#### Scenario: Manifest constraints are unpinned from legacy ceilings
- **WHEN** inspecting `project.dependencies` and `dependency-groups` across all workspace `pyproject.toml` files
- **THEN** no dependency specification SHALL contain an upper bound operator (`<` or `<=`) restricting major framework upgrades
- **AND** all OpenTelemetry dependencies (`opentelemetry-sdk`, `opentelemetry-exporter-otlp-proto-grpc`) SHALL omit `<1.45.0` bounds and resolve to `>=1.45.1`
- **AND** dependencies SHALL specify minimum versions using `>=` aligned with latest tested releases.

#### Scenario: Minimum Python version requires-python is 3.15
- **WHEN** inspecting `project.requires-python` across all workspace `pyproject.toml` files
- **THEN** the value SHALL equal `">=3.15"`.

### Requirement: Upstream framework modernization
All runtime frameworks, including DBOS, Anthropic SDK, Pydantic AI, and Pandas, SHALL be upgraded to their latest major releases across all services, and callers SHALL conform strictly to updated public API signatures.

#### Scenario: Framework upgrade verification
- **WHEN** running test suites in `agent-core`, `tdt-core`, and `viettel-excel-updater`
- **THEN** `agent-core` SHALL execute against `pydantic-ai>=2.51.0` and `anthropic>=1.8.0` without legacy v0 client helpers
- **AND** `tdt-core` scheduler SHALL execute against `dbos>=3.1.0` public client APIs
- **AND** `viettel-excel-updater` SHALL execute against `pandas>=3.0.6` enforcing pure Copy-on-Write semantics without `SettingWithCopyError`.

#### Scenario: DBOS 3.3.0 public API conformance in tdt-core
- **WHEN** `tdt-core` initializes the DBOS client or registers persistent queues
- **THEN** client instantiation SHALL use `DBOSClient(system_database_url=...)`
- **AND** configuration TypedDicts SHALL use `system_database_url`
- **AND** persistent queue registration SHALL use `DBOS.register_queue(name, ...)` rather than direct `Queue(...)` instantiation.
