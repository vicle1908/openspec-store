# Proposal: Clean-Break Full Workspace Python Dependency Upgrade

## Why

The workspace contains 22 Python repositories pinned to legacy minor releases and restricted by historical `<` upper bounds, accumulating technical debt and preventing adoption of modern framework capabilities (DBOS v3, Anthropic v1 SDK, Pydantic AI 2.51+, and Pandas 3.0 Copy-on-Write). Upgrading all repositories to their latest remote releases in a clean break eliminates compatibility shims, guarantees reproducible dependency resolution across modern Python 3.14 runtimes, and aligns the entire workspace with upstream standards.

## What Changes

- **BREAKING: Dependency Upper Bounds Purged**: Strip all `<` upper bounds from `dependencies` and `dependency-groups` across all 22 workspace `pyproject.toml` manifests.
- **BREAKING: DBOS v2 to v3 Migration**: Upgrade `dbos` to `v3.1.0` in `tdt-core`, `agent-core`, `jira-skill`, `webhook-receiver`, and `tdt-scheduler`. Refactor workflow, step, queue, and scheduler status queries to match DBOS v3 public client APIs.
- **BREAKING: Anthropic SDK v1 Migration**: Upgrade `anthropic` to `v1.8.0` in `agent-core`, `agent-docs-sync`, `agent-harness`, and `ai-review`. Remove legacy v0 client helpers, update exception handling, and adopt typed streaming event shapes.
- **BREAKING: Pydantic AI & Harness Modernization**: Upgrade `pydantic-ai` to `2.51.0` and `pydantic-ai-harness` to `0.36.0`. Unpin Monty from `v0.0.18`, adopting native harness sandboxed execution.
- **BREAKING: Pandas 3.0 Copy-on-Write**: Upgrade `pandas` to `3.0.6` in `viettel-excel-updater`, `agent-core`, and `tdt-observability`. Enforce explicit Copy-on-Write semantics and eliminate chained indexing assignments.
- **BREAKING: Internal SemVer Cascade**: Bump internal packages (`tdt-core` to `0.4.0`, `tdt-sheets` to `0.2.0`, `jira-skill` to `0.4.0`, `agent-core` to `0.3.0`) and synchronize all 12 consumer manifests without backward-compatibility shims.
- **Legacy Syntax & Deprecation Purge**:
  - Replace all `datetime.utcnow()` occurrences with `datetime.now(datetime.UTC)`.
  - Replace deprecated `@app.on_event` handlers with ASGI `lifespan` context managers.
  - Apply automated Pyupgrade rules (`UP`, `B`, `I`, `TCH`) to enforce Python 3.14 native typing (`T | None`, `list[T]`).
- **Complete Lockfile & Virtualenv Resync**: Re-generate `uv.lock` across all 21 lockfile-managed repos via `uv lock --upgrade` and sync `.venv` with `uv sync --all-extras`.

## Capabilities

### New Capabilities
- `python-dependency-clean-break`: Governs the clean-break dependency boundary, requiring all workspace Python repositories to track latest stable upstream packages, eliminate legacy shims, maintain unblocked lockfiles, and coordinate internal SDK version cascades.

### Modified Capabilities
- `uv-runtime-management`: Update runtime isolation and lockfile management requirements to require latest dependency pinning and prohibit legacy compatibility bounds.

## Impact

- **Affected Repositories (22 total)**:
  - Base SDK: `tdt/tdt-core`
  - Shared Libraries: `tdt/tdt-sheets`, `tdt/jira-skill`
  - Frameworks: `tdt/agent-core`, `tdt/ai-harness-skills`, `tdt/tdt-observability`, `tdt/jira-kanban-from-spreadsheet`
  - Downstream Consumers: `tdt/agent-docs-sync`, `tdt/agent-harness`, `tdt/code-daily-scan`, `tdt/jira-daily-reports`, `tdt/jira-epic-report`, `tdt/webhook-receiver`, `tdt/ai-review`
  - Standalone & Tooling: `platform/claude-code-provider-adapter`, `platform/hermes-webui`, `platform/openspec-store`, `tdt/browser-cli`, `tdt/ops-automation-suite`, `vds/viettel-excel-updater`, `ai-tooling/wiki-mcp-server`, `ai-tooling/workspace-python-template`
- **Infrastructure**: `tdt-scheduler` Docker deployment, `com.developer.index-refresh` LaunchAgent, GDrive `rclone bisync` filters.
