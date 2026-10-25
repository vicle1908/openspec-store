# UV Ecosystem Standardization

**Capability:** uv-ecosystem-standardization
**Status:** Implemented (2026-07-25)
**Date:** 2026-07-25

## Purpose

Enforce uv package manager practices across all TDT Python repositories for consistent dependency management, environment configuration, and developer experience.

## Requirements

### Requirement: uv.lock presence
All Python repos with pyproject.toml SHALL have a committed uv.lock file.

#### Scenario: Missing uv.lock
- **WHEN** a Python repo has pyproject.toml but no uv.lock
- **THEN** `uv sync` is run to generate uv.lock, and it is committed

### Requirement: .python-version presence
All Python repositories in the workspace SHALL maintain a committed `.python-version` file specifying Python version `3.15` exactly matching `requires-python = ">=3.15"`.

#### Scenario: Missing .python-version
- **WHEN** a Python repo has pyproject.toml but no .python-version
- **THEN** a .python-version file is created specifying Python version 3.15 matching requires-python.

#### Scenario: Missing or outdated .python-version is created or updated
- **WHEN** inspecting any workspace Python repository containing a `pyproject.toml`
- **THEN** a `.python-version` file SHALL exist containing `3.15`
- **AND** it SHALL match the `requires-python = ">=3.15"` declaration in `pyproject.toml`.

### Requirement: AGENTS.md uv practices
All Python repos SHALL have a uv practices section in AGENTS.md.

#### Scenario: Missing uv practices
- **WHEN** a Python repo's AGENTS.md lacks uv practices
- **THEN** a uv practices section is added with standard commands

### Requirement: No pip references in active docs
Active documentation SHALL NOT reference `pip install`.

#### Scenario: Pip reference found
- **WHEN** an active .md doc contains `pip install`
- **THEN** the reference is replaced with `uv add`

### Requirement: Standard [tool.uv] configuration
All Python repositories SHALL declare consistent `[tool.uv]` configurations in `pyproject.toml` enforcing `default-groups = ["dev"]`, `required-version = ">=0.13.5"`, `python-preference = "only-managed"`, and an explicit `package` boolean (`true` for library/service packages, `false` for non-package roots).

#### Scenario: Missing or inconsistent config
- **WHEN** a Python repo lacks or has non-standard [tool.uv]
- **THEN** the standard config is added or updated with required-version, default-groups, python-preference, and package settings.

#### Scenario: Non-package repository configuration
- **WHEN** inspecting non-package workspaces (`platform/openspec-store`, `ai-tooling/workspace-python-template`)
- **THEN** `[tool.uv]` SHALL set `package = false`
- **AND** no `[build-system]` section SHALL be present.

#### Scenario: Packaged library or application repository configuration
- **WHEN** inspecting first-party installable repositories across `tdt/*`, `shb/*`, `platform/*`, and `vds/*`
- **THEN** `[tool.uv]` SHALL set `package = true`
- **AND** `[build-system]` SHALL specify `requires = ["hatchling"]` and `build-backend = "hatchling.build"`.

### Requirement: Standard PEP 735 dependency groups
All workspace Python repositories SHALL declare developer and testing tooling using PEP 735 `[dependency-groups] dev = [...]` and SHALL NOT use deprecated `[project.optional-dependencies] dev`.

#### Scenario: Developer dependencies declared under dependency-groups
- **WHEN** inspecting dependency definitions across all workspace `pyproject.toml` files
- **THEN** test and lint dependencies (`pytest`, `ruff`, `mypy`) SHALL reside under `[dependency-groups].dev`
- **AND** no `[project.optional-dependencies]` section SHALL declare a `dev` group.

### Requirement: Container Dockerfile and Compose Runtime Parity
All containerized Python services in the workspace SHALL declare base Python images (`python:3.15.1-slim-trixie` or `python:3.15-slim`) and `uv` container images (`ghcr.io/astral-sh/uv:0.13.5` or higher) that satisfy the repository `requires-python = ">=3.15"` and `required-version = ">=0.13.5"` declarations in `pyproject.toml`. Container build instructions SHALL NOT hardcode legacy dependency upper bounds (`<`) that conflict with the repository's committed `uv.lock`.

#### Scenario: Multi-stage container build with system Python and frozen lockfile
- **WHEN** a container image is built for a workspace Python service (`shb-schedule`, `tdt-scheduler`, `agent-core`, `tdt-observability`, or `claude-code-provider-adapter`)
- **THEN** the `Dockerfile` and any companion `compose.yaml` build arguments SHALL select Python `3.15` (`python:3.15.1-slim-trixie` or `python:3.15-slim`) and `uv` `>=0.13.5`
- **AND** `UV_PYTHON_PREFERENCE=only-system`, `UV_PYTHON_DOWNLOADS=never`, and `UV_COMPILE_BYTECODE=1` SHALL succeed without downloading an unmanaged Python runtime or leaving dangling symlinks across multi-stage image layers.

#### Scenario: No conflicting dependency upper-bound overrides in Dockerfile
- **WHEN** inspecting `RUN uv pip install` or `RUN uv sync` commands across workspace `Dockerfile` definitions
- **THEN** no command SHALL specify `<` upper-bound constraints (such as `pydantic<2.14` or `pydantic-settings<2.15`) that downgrade or conflict with packages locked in `uv.lock`.

### Requirement: CLI Scaffolding Template Parity
Project scaffolding templates and examples in `tdt/agent-core` SHALL generate projects that conform to the workspace Python `3.15` and `uv` `>=0.13.5` contract out of the box.

#### Scenario: Scaffolding a new agent project via agent-core CLI
- **WHEN** a user scaffolds a project from `agent-core` templates (`explorer`, `proposer`, `reviewer`) or inspects `examples/code_reviewer`
- **THEN** the generated `pyproject.toml` SHALL declare `requires-python = ">=3.15"` without `<` upper bounds and include the standard `[tool.uv]` block (`default-groups = ["dev"]`, `required-version = ">=0.13.5"`, `python-preference = "only-managed"`, `package = true`)
- **AND** `agent-core init` SHALL write a `.python-version` file containing `3.15`.

### Requirement: Canonical Ruff Lint Baseline Without Blanket Rule Suppression
Workspace Python repositories SHALL enforce the canonical 19-family Ruff selector (`E`, `W`, `F`, `I`, `N`, `UP`, `B`, `A`, `C4`, `SIM`, `TCH`, `TC`, `RUF`, `S`, `PTH`, `PIE`, `PT`, `ARG`, `SLF`) with `target-version = "py315"` and SHALL NOT globally ignore core unused-import (`F401`), import-sorting (`I001`), or unused-variable (`F841`) rules across first-party source modules.

#### Scenario: Running Ruff check on shb-ai-review
- **WHEN** `uv run ruff check` is executed in `shb/shb-ai-review`
- **THEN** `[tool.ruff.lint] ignore` SHALL match the canonical 21-rule SHB baseline without global `F401`, `I001`, or `F841` suppressions
- **AND** `uv run ruff check` SHALL exit `0` with zero violations.
