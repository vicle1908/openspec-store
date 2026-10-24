# Spec Delta: uv-ecosystem-standardization

## MODIFIED Requirements

### Requirement: .python-version presence
All Python repositories in the workspace SHALL maintain a committed `.python-version` file specifying Python version `3.15` exactly matching `requires-python = ">=3.15"`.

#### Scenario: Missing .python-version
- **WHEN** a Python repo has pyproject.toml but no .python-version
- **THEN** a .python-version file is created specifying Python version 3.15 matching requires-python.

#### Scenario: Missing or outdated .python-version is created or updated
- **WHEN** inspecting any workspace Python repository containing a `pyproject.toml`
- **THEN** a `.python-version` file SHALL exist containing `3.15`
- **AND** it SHALL match the `requires-python = ">=3.15"` declaration in `pyproject.toml`.

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

## ADDED Requirements

### Requirement: Standard PEP 735 dependency groups
All workspace Python repositories SHALL declare developer and testing tooling using PEP 735 `[dependency-groups] dev = [...]` and SHALL NOT use deprecated `[project.optional-dependencies] dev`.

#### Scenario: Developer dependencies declared under dependency-groups
- **WHEN** inspecting dependency definitions across all workspace `pyproject.toml` files
- **THEN** test and lint dependencies (`pytest`, `ruff`, `mypy`) SHALL reside under `[dependency-groups].dev`
- **AND** no `[project.optional-dependencies]` section SHALL declare a `dev` group.
