# Proposal

## Why

Workspace Python repositories exhibit configuration drift across `uv`, `pyproject.toml`, `.python-version`, Ruff rule baselines, and upper-bound constraints while remaining pinned to Python 3.14 despite full Python 3.15 availability and prebuilt wheel support across our entire dependency stack. Standardizing all first-party Python repositories on `uv`-managed Python 3.15 (`cpython-3.15.1`), canonical `hatchling.build` / `pyproject.toml` schemas, latest PyPI dependency releases, and native Python 3.15 language features eliminates cross-domain drift and unlocks modern runtime capabilities.

## What Changes

- **BREAKING**: Upgrade `requires-python` to `">=3.15"` and `.python-version` to `"3.15"` across all 34 first-party workspace Python repositories (`tdt/*`, `shb/*`, `platform/openspec-store`, `platform/claude-code-provider-adapter`, `ai-tooling/workspace-python-template`, `ai-tooling/wiki-mcp-server`, and `vds/viettel-excel-updater`).
- **Standardize `uv`-Managed Python 3.15 Runtime**: Install `uv`-managed `cpython-3.15.1-macos-aarch64-none`, retain `python-preference = "only-managed"` and `required-version = ">=0.13.5"` under `[tool.uv]`, migrate all `uv tool` environments (`browser-use`, `graphifyy`, `infinity-emb`, `tavily-cli`) to Python 3.15, and retire obsolete `uv` Python 3.14 runtimes while keeping Homebrew `Python.app` 3.15 (`org.python.python`) for macOS TCC Full Disk Access supervision.
- **Standardize Canonical `pyproject.toml` Blueprint**:
  - Enforce `hatchling.build` (`[build-system] requires = ["hatchling"]`) and `[tool.uv] package = true` across all installable library/service repositories, and `package = false` (without `[build-system]`) across non-package repositories (`platform/openspec-store`, `ai-tooling/workspace-python-template`).
  - Enforce PEP 735 `[dependency-groups] dev = [...]` with `[tool.uv] default-groups = ["dev"]` across all repositories (migrating legacy `[project.optional-dependencies] dev` in `claude-code-provider-adapter` and removing duplicate dev declarations in `tdt-observability`).
  - Align `[tool.ruff]` to `target-version = "py315"`, `line-length = 100`, and the canonical 19-rule lint selection (`E`, `W`, `F`, `I`, `N`, `UP`, `B`, `A`, `C4`, `SIM`, `TCH`, `TC`, `RUF`, `S`, `PTH`, `PIE`, `PT`, `ARG`, `SLF`), repairing missing or truncated rule sets in `shb-schedule`, `shb-jira-tools`, `shb-webhook-receiver`, `claude-code-provider-adapter`, `wiki-mcp-server`, and `viettel-excel-updater`.
  - Align `[tool.mypy]` to `python_version = "3.15"` and `strict = true`, and `[tool.pytest.ini_options]` to include `-p no:cacheprovider`.
- **Purge Remaining `<` Upper Bounds & Upgrade Dependencies to Latest**:
  - Remove legacy `<1.45.0` upper-bound ceilings on `opentelemetry-sdk` and `opentelemetry-exporter-otlp-proto-grpc` in `tdt/agent-core`, `tdt/agent-harness`, `tdt/ai-review`, and `tdt/webhook-receiver`.
  - Upgrade `dbos` in `tdt/tdt-core` to `>=3.3.0` and update `DBOSClient(system_database_url=...)`, `DBOSConfig`, and `Queue` call sites to match `dbos 3.3.0` typing contracts.
  - Refresh `uv.lock` across all covered repositories via `uv lock --upgrade` against Python 3.15 (`pydantic>=2.14.1`, `pydantic-ai>=2.61.0`, `fastapi>=0.162.0`, `langgraph>=1.2.17`, `opentelemetry-sdk>=1.45.1`, `ruff>=0.17.2`, `mypy>=2.4.0`, `pytest>=9.1.1`).
- **Full Python 3.15 Language Feature Modernization (Tier 1 + Tier 2)**:
  - **Tier 1 (Builtins, Enums, Generics & Type Aliases)**:
    - Rename local `sentinel` variables across `tdt-core`, `shb-schedule`, `agent-core`, `agent-docs-sync`, and `agent-harness` that shadow the new Python 3.15 builtin `sentinel()` (`A001`).
    - Convert legacy `class X(str, Enum):` definitions in `tdt/agent-harness` and `tdt/code-daily-scan` to `enum.StrEnum` (`UP042`).
    - Migrate legacy `TypeVar` and `Generic[T]` declarations (`tdt-core`, `agent-core`, `jira-skill`) and assignment type aliases (`shb/*`) to PEP 695 `class C[T]:`, `def f[T]():`, and `type X = ...` syntax.
  - **Tier 2 (PEP 649 Native Annotations & Python 3.15 Idioms)**:
    - Remove obsolete `from __future__ import annotations` imports across first-party package sources where Python 3.15's native PEP 649/749 deferred annotation evaluation (`annotationlib`) handles forward references natively.
    - Adopt Python 3.15 builtin `sentinel()` for unique sentinel singletons, `frozendict()` for immutable constant mappings, PEP 798 comprehension unpacking (`[*x for x in ...]`), and PEP 810 `lazy import` for heavy CLI/agent startup modules where appropriate.

## Non-Goals

- Modifying upstream third-party forks (`platform/hermes-webui`, `platform/goose-docs`) or archival/non-Python repositories.
- Migrating packaged repositories away from `hatchling.build` to `uv_build`.
- Switching `python-preference` away from `"only-managed"` or altering macOS TCC `Python.app` (`org.python.python`) code-signing provenance.
- Rewriting intentional syntax-error test fixtures under `shb/shb-agent-skills/skills/hexagonal-compliance-skill/tests/fixtures/`.

## Affected Ownership Boundaries

- **`platform/openspec-store`**: OpenSpec specifications, `pyproject.toml`, `uv.lock`, `.python-version`, and workstation maintenance scripts (`scripts/workstation-daily-update.sh`, `scripts/inventory-workstation-toolchain.py`).
- **`tdt/*` (16 repositories)**: `tdt-core`, `agent-core`, `agent-docs-sync`, `agent-harness`, `ai-harness-skills`, `ai-review`, `browser-cli`, `code-daily-scan`, `jira-daily-reports`, `jira-epic-report`, `jira-kanban-from-spreadsheet`, `jira-skill`, `ops-automation-suite`, `tdt-observability`, `tdt-sheets`, `webhook-receiver`.
- **`shb/*` (13 repositories)**: `shb-core`, `shb-agent-core`, `shb-agent-harness`, `shb-agent-skills`, `shb-ai-harness-skills`, `shb-ai-review`, `shb-browser-cli`, `shb-jira-tools`, `shb-mcp-servers`, `shb-observability`, `shb-schedule`, `shb-tools`, `shb-webhook-receiver`.
- **`platform/*`, `ai-tooling/*`, and `vds/*` (4 repositories)**: `platform/claude-code-provider-adapter`, `ai-tooling/workspace-python-template`, `ai-tooling/wiki-mcp-server`, `vds/viettel-excel-updater`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `uv-ecosystem-standardization`: Enforce `.python-version` (`3.15`), canonical `[build-system]` (`hatchling.build` for packages), PEP 735 `[dependency-groups]`, and `[tool.uv]` (`python-preference = "only-managed"`, `required-version = ">=0.13.5"`, explicit `package = true|false`) across all 34 first-party workspace Python repositories.
- `python-dependency-clean-break`: Advance minimum runtime floor to `requires-python = ">=3.15"`, purge remaining `<1.45.0` OpenTelemetry upper bounds, upgrade `tdt-core` to `dbos>=3.3.0` public APIs, and lock latest PyPI releases across all repositories.
- `python-syntax-modernization`: Target Python 3.15 (`target-version = "py315"`, `python_version = "3.15"`), eliminate Python 3.15 `sentinel` builtin shadowing (`A001`), enforce `StrEnum` (`UP042`) and PEP 695 type parameter syntax (`UP046`), remove redundant `from __future__ import annotations` under PEP 649, and adopt Python 3.15 `sentinel()`, `frozendict()`, and `lazy import` idioms.
- `portable-workstation-toolchain`: Advance `uv`-managed Python runtime and `uv tool` environments from `3.14` to `3.15` (`cpython-3.15.1-macos-aarch64-none`) and retire zero-dependent `uv` `3.14` runtimes.

## Impact

- **Runtime & Tooling**: All 34 first-party Python repositories and 4 global `uv` tools execute on `cpython-3.15.1-macos-aarch64-none` with prebuilt native wheels (`cp315`).
- **Developer Workflow**: Uniform `uv sync --locked`, `uv run ruff check .`, `uv run mypy src`, and `uv run pytest -p no:cacheprovider` behavior across TDT, SHB, Platform, AI-Tooling, and VDS domains.
