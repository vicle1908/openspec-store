# Design: Align Python 3.15 & uv 0.13.5 Across Containers, Templates, Tool Manifests, and Secondary Repositories

## Context

Following the archive of `2026-10-24-standardize-python-315-and-uv-ecosystem` (`5153402b`), our workspace-wide verification across 39 project roots confirmed that all 34 first-party SHB, TDT, Platform, VDS, and AI-Tooling repositories pass `uv lock --check --offline` on managed CPython `3.15.1` (`~/.local/share/uv/python/cpython-3.15.1-macos-aarch64-none/bin/python3.15`). However, a line-by-line cross-check against current code, tests, docs, and OpenSpec specifications identified five concrete drift areas:

1. **Five Container Build Stacks (`shb-schedule`, `tdt-scheduler`, `agent-core`, `tdt-observability`, `claude-code-provider-adapter`)**:
   - `shb/shb-schedule/Dockerfile` (lines 4, 7, 26) pins `python:3.14-slim` and `ghcr.io/astral-sh/uv:0.12.23`.
   - `tdt/tdt-scheduler/Dockerfile` (lines 8, 11, 136–137) and `compose.yaml` (lines 14–15) pin `PYTHON_IMAGE=python:3.14.7-slim-trixie`, `UV_VERSION=0.12.5`, and hardcode `"pydantic>=2.13.4,<2.14"` and `"pydantic-settings>=2.14.1,<2.15"` (which `tests/test_observability_command.py:74-75,286` and `docs/tdt-scheduler-compose-verification.md:178` also assert).
   - `tdt/agent-core/Dockerfile` (lines 2–3) and `compose.yaml` (lines 34–35) pin `PYTHON_IMAGE=python:3.14.7-slim-trixie` and `UV_IMAGE=ghcr.io/astral-sh/uv:0.12.5` (asserted in `tests/test_docker_local_dev.py:12-13,29-39` and specs `agent-core-docker-local-development` / `agent-docker-local-dev`).
   - `tdt/tdt-observability/Dockerfile` (lines 23, 30, 47, 52) and `deploy/tools.env` (lines 25, 28) pin `PYTHON_VERSION=3.14.7-slim-trixie`, `UV_VERSION=0.12.5`, and `python3.14 -m venv --copies --without-pip /app/.venv` (asserted in `tests/test_compose_models.py:35-36`, `tests/test_dockerfile_paths.py:144,491-494`, and spec `tdt-observability-docker-deployment`).
   - `platform/claude-code-provider-adapter/Dockerfile` (lines 1, 3, 11) pins `python:3.14-slim` and `ghcr.io/astral-sh/uv:0.12.3` without `UV_PYTHON_DOWNLOADS=never`.
2. **`tdt/agent-core` Scaffolding Templates, `pyrightconfig.json`, and Active Docs**:
   - The 3 built-in agent templates (`explorer`, `proposer`, `reviewer`) and `examples/code_reviewer` declare `requires-python = ">=3.14,<3.15"` and omit `[tool.uv]`. Template directories should declaratively include `.python-version` containing `3.15` rather than procedurally generating it in Python code.
   - `tdt/agent-core/pyrightconfig.json:4` and `tdt/agent-docs-sync/pyrightconfig.json:4` specify `"pythonVersion": "3.14"`, and active `README.md` / `AGENTS.md` / `docs/` files in `tdt/*` and `shb/README.md:21` still cite `Python 3.14` / `uv 0.12.5`.
3. **Platform Repositories (`platform/prime-agent`, `platform/hermes-webui`)**:
   - `prime-agent/prime-agent-runtime/pyproject.toml` uses `mcp>=2,<3` on `>=3.11` with `pydantic==2.13.4` (no `cp315` wheel), while `skills/websearch/pyproject.toml` uses `httpx>=0.27,<1` and both `skills/{attach-image,websearch}` omit `[tool.uv.sources]` for `prime-agent-runtime` and must retain their `[project.scripts]` CLI entry points (`attach_image = "rlm.skill:cli"` and `websearch = "rlm.skill:cli"`).
   - `platform/hermes-webui` is an upstream third-party fork (`2026-10-24-standardize-python-315-and-uv-ecosystem` Non-Goal) whose test suite (`tests/conftest.py:30`, `scripts/test.sh:24`) requires Python `3.11`–`3.13`, but its untracked `.venv/bin/python` is a dangling symlink to uninstalled `cpython-3.14-macos-aarch64-none`.
4. **Workstation `uv tool` Manifest (`config/uv-tools.json`)**:
   - `platform/openspec-store/config/uv-tools.json` omits `infinity-emb` (`~/.local/share/uv/tools/infinity-emb`) and omits `[mcp,watch,office,pdf,postgres]` extras and `==0.9.95` on `graphifyy`, and `docs/mac-development-setup.md:243` still cites `3.14.9`.
5. **Ruff Lint Suppressions in `shb/shb-ai-review` & Stale Bytecode**:
   - `shb/shb-ai-review/pyproject.toml` suppresses 29 extra Ruff rules beyond `shb-core`'s canonical 21-rule ignore list, hiding 69 lint violations across 18 files, and stale `cpython-314*.pyc` files remain across `shb/`, `tdt/`, and `platform/openspec-store/`.

## Goals / Non-Goals

- **Goals**:
  - Restore container build parity across all 5 containerized Python services using upstream multi-arch `python:3.15.1-slim-trixie` (`sha256:533b0b2f9b5d46fd097091cf826f27902f1d6c3bca714b6dc74551356aa97a51`) and `ghcr.io/astral-sh/uv:0.13.5` (`sha256:32a7bb39b496babbd997b0a39a4d66c126bdaf5661b302bf6f06abda8deca6ff`).
  - Ensure `tdt/agent-core` CLI templates and examples generate valid Python 3.15 + `uv 0.13.5` projects, and align `pyrightconfig.json` and active docs across `tdt/*` and `shb/README.md`.
  - Bring `platform/prime-agent` onto the workspace Python 3.15 + `uv` contract and repair untracked `platform/hermes-webui/.venv` using `/opt/homebrew/bin/python3.13`.
  - Synchronize `config/uv-tools.json` and `docs/mac-development-setup.md` with live `~/.local/share/uv/tools/*/uv-receipt.toml` state.
  - Eliminate the 29 extra Ruff rule ignores in `shb/shb-ai-review` (fixing all 69 violations) and purge stale `cpython-314*.pyc` files.
- **Non-Goals**:
  - Modifying tracked source or packaging files in upstream third-party forks (`platform/hermes-webui`, `platform/goose-docs`).
  - Upgrading `vds/INSURANCE-project` off Python 3.12 (blocked upstream by `spacy`/`thinc` Pydantic v1 Cython internals).
  - Migrating all 32 package repositories from `hatchling` to `uv_build` in this change.

## Decisions

### Decision 1: Standardized Multi-Stage Container Pattern on `python:3.15.1-slim-trixie` and `ghcr.io/astral-sh/uv:0.13.5`
- **Choice**: Update all 5 Dockerfiles, `tdt/tdt-scheduler/compose.yaml`, `tdt/agent-core/compose.yaml`, and `tdt/tdt-observability/deploy/tools.env` to `python:3.15.1-slim-trixie` and `ghcr.io/astral-sh/uv:0.13.5` (or `UV_VERSION=0.13.5`), change `python3.14 -m venv` to `python3.15 -m venv` in `tdt/tdt-observability/Dockerfile:47`, and set `UV_PYTHON_PREFERENCE=only-system`, `UV_PYTHON_DOWNLOADS=never`, and `UV_COMPILE_BYTECODE=1` in `platform/claude-code-provider-adapter/Dockerfile`.
- **Rationale**: Ensures builder and runtime stages share `/usr/local/bin/python3` (`3.15.1`) without downloading unmanaged interpreters into `/root/.local/share/uv` or failing `requires-python = ">=3.15"` / `required-version = ">=0.13.5"`.
- **Removal of `tdt-scheduler` Hardcoded Pydantic Upper Bounds**: In `tdt/tdt-scheduler/Dockerfile:136-137` and `docs/tdt-scheduler-compose-verification.md:178`, replace `"pydantic>=2.13.4,<2.14"` and `"pydantic-settings>=2.14.1,<2.15"` with unconstrained `"pydantic>=2.14.1"` and `"pydantic-settings>=2.16.1"` (matching locked sibling workloads) and update `tests/test_observability_command.py:74-75,286` in lockstep.

### Decision 2: Lockstep Update of Dockerfile Static Contract Tests and OpenSpec Capabilities
- **Choice**: Update the static assertions in:
  - `tdt/tdt-scheduler/tests/test_observability_command.py:74-75,286`
  - `tdt/agent-core/tests/test_docker_local_dev.py:12-13`
  - `tdt/tdt-observability/tests/test_compose_models.py:35-36` and `tests/test_dockerfile_paths.py:144`
  and append `## ADDED Requirements` delta specs in `agent-core-docker-local-development`, `agent-docker-local-dev`, and `tdt-observability-docker-deployment`.
- **Rationale**: Preserves OpenSpec canonical requirement immutability while recording the new `python:3.15.1-slim-trixie` and `ghcr.io/astral-sh/uv:0.13.5` baseline across specs, tests, and docs.

### Decision 3: `platform/prime-agent` Clean-Break Cutover and `platform/hermes-webui` Untracked `.venv` Repair
- **Choice**:
  - In `platform/prime-agent`: Update `prime-agent-runtime/pyproject.toml` and `skills/{attach-image,websearch}/pyproject.toml` to `requires-python = ">=3.15"`, replace `mcp>=2,<3` with `mcp>=2.0.0` and `httpx>=0.27,<1` with `httpx>=0.27.0`, preserve `[project.scripts]` CLI entry points (`attach_image` and `websearch`) so binaries are generated in `.venv/bin/`, add `[tool.uv]` and `.python-version` (`3.15`), wire `[tool.uv.sources] prime-agent-runtime = { path = "../../prime-agent-runtime", editable = true }` in both skill packages, and re-lock (`pydantic 2.13.4 -> 2.14.1`).
  - In `platform/hermes-webui`: Respect the non-goal on upstream tracked files and repair only the untracked `.venv` by running `uv venv --python /opt/homebrew/bin/python3.13 .venv && uv sync --frozen --python /opt/homebrew/bin/python3.13`, satisfying `tests/conftest.py:30` (`3.11..3.13`) and keeping `git status` clean.

### Decision 4: `shb/shb-ai-review` Ruff Alignment & HunkGate Safety
- **Choice**: Replace the 50-rule `[tool.ruff.lint] ignore` list in `shb/shb-ai-review/pyproject.toml:55-62` with the canonical 21-rule SHB ignore list (matching `shb-core/pyproject.toml`), add `[tool.ruff.lint.per-file-ignores] "__init__.py" = ["F401"]` without broad test ignore suppressions, fix all 69 lint violations across the 18 source and test files, and update `HunkGate.has_truncated_or_binary` in `src/shb_review/validation/hunk_gate.py` to inspect both `_by_new_path` and `_by_old_path` with a unit regression test for deleted files (`new_path == "/dev/null"`).

## Risks / Trade-offs

- **Multi-Repo Scope**: Touching Dockerfiles, docs, and packaging across `shb/`, `tdt/`, `platform/`, and `openspec-store` spans multiple Git repositories. Mitigation: Group tasks strictly by owning repository, run each repository's full `uv lock --check`, `uv run ruff check`, `uv run mypy`, and `uv run pytest` suite before committing, and verify clean git status per repo.
