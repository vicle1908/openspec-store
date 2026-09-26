# Tasks: Clean-Break Full Workspace Python Dependency Upgrade

## 1. Pre-flight Baseline & Branch Hygiene

- [x] 1.1 Verify clean git working tree and create feature branch `feature/python-deps-clean-break` across all 22 repositories; verify with `git status` per repository
- [x] 1.2 Snapshot baseline test and lint status across all 22 repositories to `/tmp/workspace-python-baseline.json` and verify report contains all repo statuses

## 2. Tier 0 Base SDK (tdt-core) Clean-Break Upgrade

- [x] 2.1 Update `tdt/tdt-core/pyproject.toml` to remove all `<` upper bounds, update direct dependencies (`dbos>=3.1.0`, `atlassian-python-api>=5.0.5`, `requests>=2.34.2`, `pydantic>=2.13.5`), and bump package version to `0.4.0`; verify with `uv lock --upgrade`
- [x] 2.2 Refactor `tdt/tdt-core/src/tdt_core/scheduler/` to replace private DBOS imports (`_dbos`, `_queue`) with DBOS v3 public client APIs (`DBOS`, `DBOSConfig`, `Queue`, `Debouncer`); verify imports resolve cleanly with `uv run python -c "import tdt_core.scheduler"`
- [x] 2.3 Update scheduler system table queries in `tdt_core/scheduler/cli.py` and `engine.py` from `dbos.application_versions` to DBOS v3 `system.workflow_status`; verify test fixtures in `tests/scheduler/test_cli.py` pass
- [x] 2.4 Resync environment and execute test suite: `uv sync --all-extras` and `uv run pytest tests/ -v`; verify all tests pass and strict type checks succeed

## 3. Tier 1 Shared Subsystems (tdt-sheets & jira-skill) Upgrade

- [x] 3.1 Update `tdt/tdt-sheets/pyproject.toml` to require `tdt-core>=0.4.0`, remove all `<` upper bounds, and bump version to `0.2.0`; verify with `uv lock --upgrade && uv sync --all-extras`
- [x] 3.2 Execute `tdt-sheets` test suite with `uv run pytest tests/`; verify all tests pass
- [x] 3.3 Update `tdt/jira-skill/pyproject.toml` to require `tdt-core>=0.4.0`, `tdt-sheets>=0.2.0`, update `python-gitlab>=8.5.0`, `aiohttp>=3.14.3`, remove all `<` bounds, and bump version to `0.4.0`; verify with `uv lock --upgrade`
- [x] 3.4 Purge deprecated `datetime.utcnow()` from `tdt/jira-skill/src/jira_skill/schedule.py` (7 call sites) and replace with `datetime.now(datetime.UTC)`; verify with `git grep "utcnow" src/` returning 0 matches
- [x] 3.5 Execute `jira-skill` test suite with `uv sync --all-extras && uv run pytest tests/ -q`; verify all 1,903 tests pass

## 4. Tier 2 Frameworks (agent-core, ai-harness-skills, tdt-observability, jira-kanban)

- [x] 4.1 Update `tdt/agent-core/pyproject.toml` to require `tdt-core>=0.4.0`, lift all upper bounds to `pydantic-ai>=2.51.0`, `pydantic-ai-harness>=0.36.0`, `anthropic>=1.8.0`, `langgraph>=1.2.12`, `psycopg>=3.3.6`, `opentelemetry-sdk>=1.45.0`, and bump version to `0.3.0`; verify with `uv lock --upgrade`
- [x] 4.2 Modernize `tdt/agent-core/src/agent_core/llm/model.py` and `_ai/` to consume Anthropic v1 client APIs and native Harness 0.36 execution primitives; verify agent build factory runs with `uv run python -c "import agent_core.sdk"`
- [x] 4.3 Execute `agent-core` test suite and strict type checking: `uv sync --all-extras && uv run pytest tests/ -q && uv run mypy src/agent_core/ --strict`; verify 852+ tests pass
- [x] 4.4 Update `tdt/ai-harness-skills/pyproject.toml` to require `tdt-core>=0.4.0`, bump to `0.3.0`, run `uv lock --upgrade && uv sync --all-extras && uv run pytest tests/`; verify all tests pass
- [x] 4.5 Update `tdt/tdt-observability/pyproject.toml` to require `tdt-core>=0.4.0`, bump to `0.3.0`, update `streamlit>=1.64.0`, `duckdb>=1.5.5`, run `uv lock --upgrade && uv sync --all-extras && uv run pytest tests/`; verify dashboard modules import cleanly
- [x] 4.6 Update `tdt/jira-kanban-from-spreadsheet/pyproject.toml` to require `tdt-core>=0.4.0`, `tdt-sheets>=0.2.0`, run `uv lock --upgrade && uv sync --all-extras && uv run pytest tests/`; verify all tests pass

## 5. Tier 3 Downstream Consumer Services Upgrade

- [x] 5.1 Update `tdt/agent-docs-sync/pyproject.toml` to require `agent-core>=0.3.0`, `tdt-core>=0.4.0`, remove `<` bounds, run `uv lock --upgrade && uv sync --all-extras && uv run pytest tests/`; verify documentation agent tests pass
- [x] 5.2 Update `tdt/agent-harness/pyproject.toml` to require `agent-core>=0.3.0`, `tdt-core>=0.4.0`, remove `<` bounds, run `uv lock --upgrade && uv sync --all-extras && uv run pytest tests/`; verify planning harness tests pass
- [x] 5.3 Update `tdt/code-daily-scan/pyproject.toml` to require `agent-core>=0.3.0`, `tdt-core>=0.4.0`, `tdt-sheets>=0.2.0`, remove `<` bounds, run `uv lock --upgrade && uv sync --all-extras && uv run pytest tests/`; verify scanner tests pass
- [x] 5.4 Update `tdt/jira-daily-reports/pyproject.toml` to require `tdt-core>=0.4.0`, `tdt-sheets>=0.2.0`, `jira-skill>=0.4.0`, remove `<` bounds, run `uv lock --upgrade && uv sync --all-extras && uv run pytest tests/`; verify reporting tests pass
- [x] 5.5 Update `tdt/jira-epic-report/pyproject.toml` to require `tdt-core>=0.4.0`, `tdt-sheets>=0.2.0`, `jira-skill>=0.4.0`, remove `<` bounds, run `uv lock --upgrade && uv sync --all-extras && uv run pytest tests/`; verify 650 tests pass
- [x] 5.6 Update `tdt/webhook-receiver/pyproject.toml` to require `tdt-core>=0.4.0`, `jira-skill>=0.4.0`, update FastAPI and DBOS, purge `datetime.utcnow()` from `src/webhook_receiver/router.py`, run `uv lock --upgrade && uv sync --all-extras && uv run pytest tests/`; verify webhook endpoints test suite passes
- [x] 5.7 Update `tdt/ai-review/pyproject.toml` to require `tdt-core>=0.4.0`, `code-daily-scan`, update FastAPI to 0.141.1, run `uv lock --upgrade && uv sync --all-extras && uv run pytest tests/`; verify AI review service tests pass

## 6. Standalone Tooling & Platform Modernization

- [x] 6.1 Update `vds/viettel-excel-updater/pyproject.toml` to `pandas>=3.0.6`, `numpy>=2.5.3`, audit and refactor all dataframe manipulations to strict Copy-on-Write (`.copy()` and `.loc[]`); verify with `uv lock --upgrade && uv run python -c "import excel_updater"`
- [x] 6.2 Update `platform/claude-code-provider-adapter/pyproject.toml` to `fastapi>=0.141.1`, `httpx>=0.28.1`, `uvicorn>=0.54.0`, run `uv lock --upgrade && uv sync --all-extras && uv run pytest tests/`; verify adapter integration tests pass
- [x] 6.3 Update `tdt/browser-cli/pyproject.toml` to `playwright>=1.63.0`, run `uv lock --upgrade && uv sync && uv run playwright install && uv run pytest tests/`; verify browser CLI tests pass
- [x] 6.4 Update `platform/openspec-store`, `platform/hermes-webui`, `tdt/ops-automation-suite`, `ai-tooling/wiki-mcp-server`, and `ai-tooling/workspace-python-template`; run `uv lock --upgrade && uv sync` across each

## 7. Tooling Alignment, Hooks & Daemons Verification

- [x] 7.1 Update `.pre-commit-config.yaml` across all 16 repositories: bump `ruff-pre-commit` to `v0.16.9` and `uv-pre-commit` to `0.12.19`; verify with `pre-commit validate-config .pre-commit-config.yaml` in each repo
- [x] 7.2 Verify Dockerfile base images (`jira-skill`, `agent-core`, `tdt-observability`, `claude-code-provider-adapter`) are aligned with Python 3.14+; verify with `grep FROM */Dockerfile`
- [x] 7.3 Verify LaunchAgent jobs under `~/Library/LaunchAgents/` (`com.developer.index-refresh`, `com.tdt.ai-review`, `com.workspace.claude-code-provider-adapter`); verify executable paths resolve against updated environments

## 8. Workspace-Wide Verification, Modernization Codemod & Sync

- [x] 8.1 Execute automated syntax modernization sweep across all 22 repositories: `uv run ruff check --fix --select UP,B,I,TCH src/ tests/`; verify 0 lint or formatting errors remaining
- [x] 8.2 Run workspace-wide test runner across all repositories with test suites; verify 100% test pass rate with 0 regressions against baseline
- [x] 8.3 Commit atomic, scoped Git commits per repository on `feature/python-deps-clean-break` referencing the OpenSpec change
- [x] 8.4 Execute GDrive synchronization: `rclone bisync` across all 19 Python repos to `gdrive-tdt` and verify exit code 0
