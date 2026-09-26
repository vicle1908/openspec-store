# Spec Delta: python-dependency-clean-break

## Purpose

Enforces a clean-break dependency modernization standard across all workspace Python repositories, requiring unrestricted tracking of latest stable releases, purging legacy shims, and coordinating internal SDK version cascades.

## ADDED Requirements

### Requirement: Purge legacy upper bound constraints
All Python repositories in the workspace SHALL omit legacy `<` upper bound specifiers from direct runtime dependencies and developer dependency groups, allowing unconstrained resolution to the latest available PyPI releases.

#### Scenario: Manifest constraints are unpinned from legacy ceilings
- **WHEN** inspecting `project.dependencies` and `dependency-groups` across all workspace `pyproject.toml` files
- **THEN** no dependency specification SHALL contain an upper bound operator (`<` or `<=`) restricting major framework upgrades
- **AND** dependencies SHALL specify minimum versions using `>=` aligned with latest tested releases.

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
All runtime frameworks, including DBOS, Anthropic SDK, Pydantic AI, and Pandas, SHALL be upgraded to their latest major releases across all services.

#### Scenario: Framework upgrade verification
- **WHEN** running test suites in `agent-core`, `tdt-core`, and `viettel-excel-updater`
- **THEN** `agent-core` SHALL execute against `pydantic-ai>=2.51.0` and `anthropic>=1.8.0` without legacy v0 client helpers
- **AND** `tdt-core` scheduler SHALL execute against `dbos>=3.1.0` public client APIs
- **AND** `viettel-excel-updater` SHALL execute against `pandas>=3.0.6` enforcing pure Copy-on-Write semantics without `SettingWithCopyError`.
