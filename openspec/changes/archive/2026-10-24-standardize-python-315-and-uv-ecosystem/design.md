# Design

## Context

See `proposal.md` for motivation and scope boundaries.
The workspace consists of 34 first-party Python repositories across 5 domains (`tdt/*`, `shb/*`, `platform/*`, `vds/*`, `ai-tooling/*`). Repositories are interconnected through relative editable paths (e.g. `tdt-core = { path = "../tdt-core", editable = true }`).
On the host, Homebrew provides Python 3.15.0 (`/opt/homebrew/bin/python3.15`), and `Python.app` is enrolled under macOS TCC (`org.python.python`) for FDA. `uv 0.13.5` manages isolated project environments under `~/.local/share/uv/python/`.

## Goals / Non-Goals

**Goals:**
- Upgrade all 34 first-party repositories to `cpython-3.15.1-macos-aarch64-none` via `uv`.
- Establish a uniform, canonical `pyproject.toml` schema for both package and non-package repositories.
- Eliminate all `<` upper bound specifiers and upgrade all dependencies to latest verified PyPI releases.
- Fix all Python 3.15 lint and runtime regressions (`A001` sentinel shadowing, `UP042` StrEnum, `dbos 3.3.0` API typing).
- Modernize codebase syntax to adopt PEP 695 generics/type aliases and PEP 649 native annotation evaluation.

**Non-Goals:**
- Migrating build backend from `hatchling.build` to `uv_build` (standardize on `hatchling` across all package repos).
- Modifying third-party vendor checkouts (`platform/hermes-webui`, `platform/goose-docs`).
- Altering the macOS TCC signing pipeline in `workstation_update.py` or LaunchAgents.

## Architecture & Blueprint

```
+-----------------------------------------------------------------------------------+
|                        CANONICAL REPOSITORY SCHEMAS                               |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [PACKAGED REPOSITORIES: 32 repos]        [NON-PACKAGE REPOSITORIES: 2 repos]     |
|  * tdt/*, shb/*, platform/claude-adapter, * platform/openspec-store               |
|    ai-tooling/wiki-mcp, vds/excel-updater * ai-tooling/workspace-python-template  |
|                                                                                   |
|  [build-system]                           [project]                               |
|  requires = ["hatchling"]                 name = "..."                            |
|  build-backend = "hatchling.build"        requires-python = ">=3.15"              |
|                                           dependencies = []                       |
|  [project]                                                                        |
|  requires-python = ">=3.15"               [dependency-groups]                     |
|  dependencies = [">=latest floors"]       dev = ["pytest>=9.1.1", ...]            |
|                                                                                   |
|  [dependency-groups]                      [tool.uv]                               |
|  dev = ["pytest>=9.1.1", ...]             default-groups = ["dev"]                |
|                                           required-version = ">=0.13.5"           |
|  [tool.uv]                                python-preference = "only-managed"      |
|  default-groups = ["dev"]                 package = false                         |
|  required-version = ">=0.13.5"                                                    |
|  python-preference = "only-managed"       [tool.ruff]                             |
|  package = true                           line-length = 100                       |
|                                           target-version = "py315"                |
|  [tool.hatch.build.targets.wheel]                                                 |
|  packages = ["src/<pkg_name>"]            [tool.ruff.lint]                        |
|                                           select = [<19 canonical rules>]         |
|  [tool.ruff]                                                                      |
|  line-length = 100                        [tool.mypy]                             |
|  target-version = "py315"                 python_version = "3.15"                 |
|                                           strict = true                           |
|  [tool.ruff.lint]                                                                 |
|  select = [<19 canonical rules>]          [tool.pytest.ini_options]               |
|                                           addopts = "-ra -q --tb=short            |
|  [tool.mypy]                                         -p no:cacheprovider"         |
|  python_version = "3.15"                                                          |
|  strict = true                                                                    |
|                                                                                   |
|  [tool.pytest.ini_options]                                                        |
|  addopts = "-ra -q --tb=short                                                     |
|             -p no:cacheprovider"                                                  |
+-----------------------------------------------------------------------------------+
```

## Decisions

### 1. `uv`-Managed Python 3.15 (`cpython-3.15.1`) with `python-preference = "only-managed"`
- **Decision**: Install `cpython-3.15.1-macos-aarch64-none` using `uv python install 3.15` and enforce `python-preference = "only-managed"` across all repos.
- **Rationale**: Isolates development environments from Homebrew formula updates, ensures deterministic clean-checkout reproducibility across machines, and avoids mixing Homebrew CPython headers with virtualenv binaries. Homebrew's signed `Python.app` remains dedicated to LaunchAgent TCC Full Disk Access.

### 2. Retain `hatchling.build` as the Universal Package Backend
- **Decision**: Standardize all 32 package repositories on `hatchling.build` with explicit `[tool.hatch.build.targets.wheel] packages = ["src/<pkg_name>"]`.
- **Rationale**: While `uv_build` performed well in testing, `hatchling` is already the established standard in 33 repositories, supports all current build targets, and avoids introducing unnecessary churn during a major Python runtime and dependency upgrade.

### 3. Canonical 19-Rule Ruff Lint Baseline on `py315`
- **Decision**: Enforce the canonical rule set `["E", "W", "F", "I", "N", "UP", "B", "A", "C4", "SIM", "TCH", "TC", "RUF", "S", "PTH", "PIE", "PT", "ARG", "SLF"]` with `target-version = "py315"`.
- **Rationale**: Aligns with `lint-config-baseline`. In Python 3.15, `UP` rules automatically guide migration to `StrEnum` (`UP042`) and PEP 695 generics (`UP046`). Rule `A` flags variable names that shadow the new Python 3.15 builtin `sentinel`.

### 4. Coordinated Rollout Order (SDK Foundation First)
- **Decision**: Execute the rollout in 4 dependency waves:
  1. **Wave 0 (Toolchain & Runtimes)**: Install `cpython-3.15.1` via `uv`, upgrade global `uv tools`, and update `workspace-python-template` + `openspec-store`.
  2. **Wave 1 (Core SDKs)**: Upgrade `shb-core` and `tdt-core` (fixing DBOS 3.3.0 typing and sentinel shadowing).
  3. **Wave 2 (Direct Dependents & Frameworks)**: Upgrade `agent-core`, `shb-agent-core`, `shb-schedule`, `tdt-sheets`, `jira-skill`.
  4. **Wave 3 (Leaves, CLIs, Applications)**: Upgrade remaining `tdt/*`, `shb/*`, `platform/*`, and `vds/*` repositories.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| **`sentinel` Builtin Shadowing (`A001`)** | Pre-scanned all 11 occurrences; rename to `reload_sentinel` / `mock_sentinel` / `_MISSING` before running `uv run ruff check`. |
| **`dbos 3.3.0` API Changes in `tdt-core`** | Update `database_url` -> `system_database_url` / `application_database_url` and queue call sites in `tdt-core` before syncing downstream. |
| **Cross-Repo Editable Link Invalidation** | Run `uv sync --upgrade --python 3.15` in topological order so shared editable dependencies are compiled against Python 3.15. |
| **Workspace Cache Contamination** | Enforce `-p no:cacheprovider` in `addopts` across all repositories. |
