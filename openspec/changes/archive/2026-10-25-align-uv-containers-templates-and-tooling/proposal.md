# Proposal: Align Python 3.15 & uv 0.13.5 Across Containers, Templates, Tool Manifests, and Secondary Repositories

## Why

Following the archive of `2026-10-24-standardize-python-315-and-uv-ecosystem` (`5153402b`), all 34 first-party Python repositories on the workstation declare `requires-python = ">=3.15"` and `required-version = ">=0.13.5"`, yet five container build stacks remain pinned to Python 3.14 and `uv 0.12.x` (breaking `docker build` across `shb-schedule`, `tdt-scheduler`, `agent-core`, `tdt-observability`, and `claude-code-provider-adapter`), while `tdt/agent-core` CLI templates, `platform/prime-agent`, `platform/hermes-webui/.venv`, `config/uv-tools.json`, `shb/shb-ai-review` Ruff rules, and repo docs/configs (`pyrightconfig.json`, `README.md`, `AGENTS.md`) retain pre-3.15 drift.

Specifically:
1. **Container Runtime & `uv` Version Mismatch (5 Stacks)**:
   - `shb/shb-schedule/Dockerfile` (`python:3.14-slim`, `ghcr.io/astral-sh/uv:0.12.23`)
   - `tdt/tdt-scheduler/Dockerfile` & `compose.yaml` (`python:3.14.7-slim-trixie`, `UV_VERSION=0.12.5`, plus hardcoded `"pydantic>=2.13.4,<2.14"` and `"pydantic-settings>=2.14.1,<2.15"` overrides at `Dockerfile:136-137` and `docs/tdt-scheduler-compose-verification.md:178`)
   - `tdt/agent-core/Dockerfile` & `compose.yaml` (`python:3.14.7-slim-trixie`, `ghcr.io/astral-sh/uv:0.12.5`)
   - `tdt/tdt-observability/Dockerfile` & `deploy/tools.env` (`PYTHON_VERSION=3.14.7-slim-trixie`, `UV_VERSION=0.12.5`, `python3.14 -m venv`)
   - `platform/claude-code-provider-adapter/Dockerfile` (`python:3.14-slim`, `ghcr.io/astral-sh/uv:0.12.3`)
2. **CLI Scaffolding Template & Pyright Config Drift (`tdt/agent-core`, `tdt/agent-docs-sync`)**:
   - `tdt/agent-core/src/agent_core/cli/templates/{explorer,proposer,reviewer}/pyproject.toml` and `examples/code_reviewer/pyproject.toml` still emit `requires-python = ">=3.14,<3.15"` without `[tool.uv]`, `src/agent_core/cli/init_cmd.py` does not write `.python-version`, and `pyrightconfig.json` in `tdt/agent-core` and `tdt/agent-docs-sync` still specifies `"pythonVersion": "3.14"`.
3. **Platform Repository & Broken `.venv` Drift (`prime-agent`, `hermes-webui`)**:
   - `platform/prime-agent/prime-agent-runtime/pyproject.toml` enforces `"mcp>=2,<3"` on `requires-python = ">=3.11"` and locks `pydantic==2.13.4` (no `cp315` wheel), while `skills/websearch/pyproject.toml` enforces `"httpx>=0.27,<1"` and both `skills/{attach-image,websearch}` reference `"prime-agent-runtime"` without `[tool.uv.sources]`.
   - `platform/hermes-webui/.venv/bin/python` is a dangling symlink to uninstalled `~/.local/share/uv/python/cpython-3.14-macos-aarch64-none/bin/python3.14` after `uv` Python 3.14 retirement; because `hermes-webui` is an upstream third-party fork whose test harness (`tests/conftest.py:30`, `scripts/test.sh:24`) requires `(3, 11) <= sys.version_info[:2] <= (3, 13)`, its untracked `.venv` must be re-bound to `/opt/homebrew/bin/python3.13` without mutating upstream tracked files.
4. **Sanctioned `uv tool` Manifest & Setup Doc Drift (`config/uv-tools.json`, `docs/mac-development-setup.md`)**:
   - `platform/openspec-store/config/uv-tools.json` omits `infinity-emb` (`~/.local/share/uv/tools/infinity-emb/uv-receipt.toml`) and lists `graphifyy` without its `[mcp,watch,office,pdf,postgres]` extras and `==0.9.95` pin, and `docs/mac-development-setup.md:243` still cites Python `3.14.9`.
5. **Blanket Ruff Rule Suppressions (`shb/shb-ai-review`) & Stale `cpython-314.pyc` Bytecode**:
   - `shb/shb-ai-review/pyproject.toml` appends 29 extra ignored Ruff rules (`F401`, `I001`, `F841`, `TC001`–`TC006`, `B904`, `N818`, `A002`, etc.) beyond `shb-core`'s canonical 21-rule baseline, masking 69 lint violations across 18 files, while stale `cpython-314*.pyc` files and `Python 3.14` doc strings remain across `shb/` and `tdt/`.

## What Changes

- **Align All 5 Container Stacks, Image Inventories, and Static Contract Tests to Python 3.15.1 & `uv 0.13.5`**:
  - Update `shb/shb-schedule/Dockerfile`, `tdt/tdt-scheduler/{Dockerfile,compose.yaml,docs/tdt-scheduler-compose-verification.md}`, `tdt/agent-core/{Dockerfile,compose.yaml}`, `tdt/tdt-observability/{Dockerfile,deploy/tools.env}`, and `platform/claude-code-provider-adapter/Dockerfile` to `python:3.15.1-slim-trixie` and `ghcr.io/astral-sh/uv:0.13.5` (with `UV_PYTHON_PREFERENCE=only-system`, `UV_PYTHON_DOWNLOADS=never`, and `UV_COMPILE_BYTECODE=1`).
  - Remove the stale `"pydantic>=2.13.4,<2.14"` and `"pydantic-settings>=2.14.1,<2.15"` overrides in `tdt/tdt-scheduler/Dockerfile:136-137` and `docs/tdt-scheduler-compose-verification.md:178`.
  - Update static contract tests in `tdt/tdt-scheduler/tests/test_observability_command.py`, `tdt/agent-core/tests/test_docker_local_dev.py`, and `tdt/tdt-observability/tests/{test_compose_models.py,test_dockerfile_paths.py}`.
- **Update `tdt/agent-core` Scaffolding Templates, `init_cmd.py`, `pyrightconfig.json`, and Active Docs to Python 3.15**:
  - Update `src/agent_core/cli/templates/{explorer,proposer,reviewer}/pyproject.toml` and `examples/code_reviewer/pyproject.toml` to `requires-python = ">=3.15"` with the canonical `[tool.uv]` block, emit `.python-version` (`3.15\n`) in `init_cmd.py`, update `pyrightconfig.json` in `tdt/agent-core` and `tdt/agent-docs-sync` to `"pythonVersion": "3.15"`, and update active `README.md` / `AGENTS.md` / `docs/` references across `tdt/*` and `shb/README.md`.
- **Modernize `platform/prime-agent` onto Python 3.15 and Repair Untracked `platform/hermes-webui/.venv`**:
  - Migrate `platform/prime-agent/prime-agent-runtime` and `skills/{attach-image,websearch}` to `requires-python = ">=3.15"`, `.python-version = 3.15`, `hatchling.build`, PEP 735 `[dependency-groups]`, and standard `[tool.uv]`, removing `<` upper bounds (`mcp>=2,<3` and `httpx>=0.27,<1`) and wiring `[tool.uv.sources]`.
  - Recreate untracked `platform/hermes-webui/.venv` against `/opt/homebrew/bin/python3.13` (`uv venv --python /opt/homebrew/bin/python3.13` + `uv sync --frozen --python /opt/homebrew/bin/python3.13`) so its upstream Python 3.11–3.13 test suite passes without modifying tracked upstream files.
- **Reconcile `config/uv-tools.json` and `docs/mac-development-setup.md` with Live `uv-receipt.toml` State**:
  - Update `platform/openspec-store/config/uv-tools.json` (and `tests/test_portable_workstation_slice_a.py`) to record `infinity-emb[server]` and `graphifyy[mcp,watch,office,pdf,postgres]==0.9.95`, and update `docs/mac-development-setup.md:243` from `3.14.9` to `3.15.1`.
- **Restore Canonical Ruff Lint Hygiene in `shb/shb-ai-review` and Purge Stale `cpython-314*.pyc` Bytecode**:
  - Restore `shb/shb-ai-review/pyproject.toml`'s `[tool.ruff.lint] ignore` list to the canonical 21-rule SHB baseline, resolve all 69 uncovered Ruff violations across the 18 affected files, and remove all stale `cpython-314*.pyc` files across `shb/`, `tdt/`, and `platform/openspec-store/`.

## Non-Goals

- Modifying tracked source or packaging files in upstream third-party forks (`platform/hermes-webui`, `platform/goose-docs`).
- Migrating `vds/INSURANCE-project` (`vds-ai-memory` / `vds-ai-memory-multi-agent`) off Python 3.12 (`spacy==3.8.x` and `thinc` do not publish `cp314`/`cp315` wheels and depend on Pydantic v1 internals).
- Replacing `hatchling` with `uv_build` across the 32 package repositories in this change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `uv-ecosystem-standardization`: Require container `Dockerfile` / `compose.yaml` / `deploy/tools.env` Python and `uv` versions, `agent-core` CLI project templates, and `platform/prime-agent` to match the workspace `requires-python = ">=3.15"` and `required-version = ">=0.13.5"` contract, and prohibit repo-specific global suppression of core Ruff import/variable rules (`F401`, `I001`, `F841`).
- `portable-workstation-toolchain`: Require `config/uv-tools.json` entries to match installed `~/.local/share/uv/tools/*/uv-receipt.toml` package extras, version pins, and companion `--with` requirements (`infinity-emb` and `graphifyy`).
- `agent-core-docker-local-development`: Advance `tdt/agent-core` `Dockerfile`, `compose.yaml`, and `tests/test_docker_local_dev.py` image pins to `python:3.15.1-slim-trixie` and `ghcr.io/astral-sh/uv:0.13.5`.
- `agent-docker-local-dev`: Advance the `agent-core` local development Docker Compose app image baseline to `python:3.15.1-slim-trixie` and `ghcr.io/astral-sh/uv:0.13.5`.
- `tdt-observability-docker-deployment`: Advance `tdt/tdt-observability/deploy/tools.env`, `Dockerfile`, and deployment tests to `PYTHON_VERSION=3.15.1-slim-trixie`, `UV_VERSION=0.13.5`, and `python3.15 -m venv`.
- `shb-ecosystem-tooling`: Advance SHB documentation (`shb/README.md`) to `Python 3.15` and require `__pycache__/` trees free of stale `cpython-314*.pyc` bytecode artifacts.

## Impact

- **Ownership Boundaries**:
  - **Central OpenSpec Store (`/Users/androidteam/Developer/platform/openspec-store`)**: Owns `config/uv-tools.json`, `docs/mac-development-setup.md`, `tests/test_portable_workstation_slice_a.py`, and OpenSpec specifications.
  - **SHB Banking Ecosystem (`/Users/androidteam/Developer/shb/`)**: Owns `shb/shb-schedule/Dockerfile`, `shb/shb-ai-review` (`pyproject.toml` + 18 source/test files), `shb/README.md`, and stale `cpython-314*.pyc` cleanup across `shb/*`.
  - **TDT Ecosystem (`/Users/androidteam/Developer/tdt/`)**: Owns `tdt/tdt-scheduler` (`Dockerfile`, `compose.yaml`, `docs/`, `tests/`), `tdt/agent-core` (`Dockerfile`, `compose.yaml`, `pyrightconfig.json`, `docs/`, `tests/`, `src/agent_core/cli/templates/`, `examples/code_reviewer/`), `tdt/tdt-observability` (`Dockerfile`, `deploy/tools.env`, `README.md`, `src/`, `tests/`), and `tdt/*` active doc/`pyrightconfig.json` alignment.
  - **Platform Repositories (`/Users/androidteam/Developer/platform/`)**: Owns `claude-code-provider-adapter/Dockerfile`, `prime-agent` (`prime-agent-runtime/` and `skills/`), and untracked `hermes-webui/.venv` repair.
