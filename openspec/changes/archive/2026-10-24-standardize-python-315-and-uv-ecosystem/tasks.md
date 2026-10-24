# Tasks

## 1. Toolchain & Workspace Runtime Environment (Wave 0)

- [x] 1.1 Install `cpython-3.15.1-macos-aarch64-none` via `uv python install 3.15` and verify installation under `~/.local/share/uv/python/`.
  - Check: `uv python list --only-installed | grep '3.15.1'`
- [x] 1.2 Upgrade global `uv tools` (`browser-use`, `graphifyy`, `infinity-emb`, `tavily-cli`) to Python 3.15 environments using `uv tool upgrade --all`.
  - Check: `uv tool list` reports Python 3.15 runtimes for all tools.
- [x] 1.3 Update reference template `ai-tooling/workspace-python-template/pyproject.toml` to Python 3.15 (`requires-python = ">=3.15"`, `target-version = "py315"`, `python_version = "3.15"`).
  - Check: `git -C ai-tooling/workspace-python-template diff pyproject.toml`
- [x] 1.4 Update `platform/openspec-store/pyproject.toml` and `.python-version` to Python 3.15, refresh `uv.lock`, and verify `uv run pytest -p no:cacheprovider`.
  - Check: `uv run --directory platform/openspec-store pytest -p no:cacheprovider` exits 0.

## 2. Core SDK Foundation Wave (Wave 1: shb-core & tdt-core)

- [x] 2.1 Update `shb/shb-core/pyproject.toml` to Python 3.15, create `.python-version` with `"3.15"`, upgrade dependencies via `uv lock --upgrade`, and verify `pytest`, `ruff`, and `mypy`.
  - Check: `cd shb/shb-core && uv run ruff check . && uv run mypy src && uv run pytest -p no:cacheprovider`
- [x] 2.2 Fix `dbos 3.3.0` API typing and runtime queue registration in `tdt/tdt-core` (`system_database_url` in `dbos_client.py` and `engine.py`, `DBOS.register_queue` in `scheduling.py:177` and tests).
  - Check: `uv run --directory tdt/tdt-core mypy src/tdt_core/scheduler` reports zero errors.
- [x] 2.3 Rename shadowed `sentinel` variables in `tdt/tdt-core` (`registry_loader.py:501,546`, `tests/test_http_session.py:146`, and `tests/scheduler/test_registry_loader.py:191,199`) to `reload_sentinel` / `mock_sentinel` to resolve Ruff `A001`.
  - Check: `uv run --directory tdt/tdt-core ruff check src/ tests/ --select A001` reports 0 violations.
- [x] 2.4 Update `tdt/tdt-core/pyproject.toml` to Python 3.15 (`requires-python = ">=3.15"`, `target-version = "py315"`, `python_version = "3.15"`), update `.python-version` to `"3.15"`, run `uv lock --upgrade`, and verify `uv run pytest -p no:cacheprovider` and `uv run ruff check .`.
  - Check: `cd tdt/tdt-core && uv run ruff check . && uv run pytest -p no:cacheprovider`

## 3. Framework & Agent Runtime Wave (Wave 2: shb-schedule, agent-core, agent-harness)

- [x] 3.1 Rename shadowed `sentinel` variables in `shb/shb-schedule` (`src/shb_schedule/cli.py:279`, `tests/test_server.py:848`) to `reload_sentinel` / `mock_sentinel` and restore missing `TC` and `TCH` rules to `[tool.ruff.lint.select]`.
  - Check: `uv run --directory shb/shb-schedule ruff check src/ tests/ --select A001,TC,TCH`
- [x] 3.2 Update `shb/shb-schedule/pyproject.toml` and create `.python-version` with `"3.15"`, run `uv lock --upgrade`, and verify all scheduler tests pass.
  - Check: `cd shb/shb-schedule && uv run pytest -p no:cacheprovider`
- [x] 3.3 Purge `<1.45.0` upper bounds on OpenTelemetry in `tdt/agent-core/pyproject.toml:28-29` and rename shadowed `sentinel` variable in `tests/_ai/test_streaming_responses.py:354`.
  - Check: `grep -n '<' tdt/agent-core/pyproject.toml` reports 0 matches.
- [x] 3.4 Update `tdt/agent-core/pyproject.toml` to Python 3.15 and `.python-version` to `"3.15"`, run `uv lock --upgrade`, and verify `pytest` and `ruff`.
  - Check: `cd tdt/agent-core && uv run ruff check . && uv run pytest -p no:cacheprovider`
- [x] 3.5 Purge `<1.45.0` upper bounds in `tdt/agent-harness/pyproject.toml:30`, rename shadowed `sentinel` variables in `tests/test_harness_capability_forwarding.py` and `tests/test_model_context_composition.py`, migrate the 7 `(str, Enum)` classes to `StrEnum` (`UP042`), update `pyproject.toml` and `.python-version` to `"3.15"`, and verify tests.
  - Check: `cd tdt/agent-harness && uv run ruff check . --select UP042,A001 && uv run pytest -p no:cacheprovider`

## 4. SHB Ecosystem Wave (Wave 3A: Remaining 11 Repositories)

- [x] 4.1 Update `shb-agent-core`, `shb-agent-harness`, `shb-agent-skills`, `shb-ai-harness-skills`, and `shb-ai-review` to Python 3.15 (`pyproject.toml`, create `.python-version = "3.15"`), upgrade lockfiles via `uv lock --upgrade`, and verify test suites.
  - Check: `for r in shb-agent-core shb-agent-harness shb-agent-skills shb-ai-harness-skills shb-ai-review; do uv run --directory shb/$r pytest -p no:cacheprovider; done`
- [x] 4.2 Restore canonical 19-rule `[tool.ruff.lint.select]` and `target-version = "py315"` in `shb-jira-tools` and `shb-webhook-receiver`, update `pyproject.toml`, create `.python-version = "3.15"`, and verify checks.
  - Check: `for r in shb-jira-tools shb-webhook-receiver; do uv run --directory shb/$r ruff check .; done`
- [x] 4.3 Update `shb-browser-cli`, `shb-mcp-servers`, `shb-observability`, and `shb-tools` to Python 3.15 (`pyproject.toml`, create `.python-version = "3.15"`), upgrade lockfiles, and verify test suites.
  - Check: `for r in shb-browser-cli shb-mcp-servers shb-observability shb-tools; do uv run --directory shb/$r pytest -p no:cacheprovider; done`

## 5. TDT Ecosystem, Platform & VDS Wave (Wave 3B: Remaining 16 Repositories)

- [x] 5.1 Rename shadowed `sentinel` variables in `tdt/agent-docs-sync` (`tests/test_canonical_model_operation_contract.py:134,171`), update `pyproject.toml` and `.python-version = "3.15"`, and verify tests.
  - Check: `cd tdt/agent-docs-sync && uv run ruff check . && uv run pytest -p no:cacheprovider`
- [x] 5.2 Migrate `tdt/code-daily-scan` string enum `CoverageLevel` to `StrEnum` (`UP042`), ensure explicit `package = true`, update `pyproject.toml` and `.python-version = "3.15"`, and run `uv lock --upgrade`.
  - Check: `cd tdt/code-daily-scan && uv run ruff check . && uv run pytest -p no:cacheprovider`
- [x] 5.3 Purge `<1.45.0` upper bounds in `tdt/ai-review/pyproject.toml:29` and `tdt/webhook-receiver/pyproject.toml:34`, update both to Python 3.15 and `.python-version = "3.15"`, and run `uv lock --upgrade`.
  - Check: `grep -n '<' tdt/ai-review/pyproject.toml tdt/webhook-receiver/pyproject.toml` reports 0 matches.
- [x] 5.4 Update remaining TDT repos (`ai-harness-skills`, `browser-cli`, `jira-daily-reports`, `jira-epic-report`, `jira-kanban-from-spreadsheet`, `jira-skill`, `ops-automation-suite`, `tdt-observability`, `tdt-sheets`) to Python 3.15, make `package = true` explicit under `[tool.uv]`, update `.python-version = "3.15"`, remove redundant optional-dependencies dev from `tdt-observability`, and run `uv lock --upgrade`.
  - Check: `for r in ai-harness-skills browser-cli jira-daily-reports jira-epic-report jira-kanban-from-spreadsheet jira-skill ops-automation-suite tdt-observability tdt-sheets; do uv run --directory tdt/$r pytest -p no:cacheprovider; done`
- [x] 5.5 Migrate `platform/claude-code-provider-adapter` from `[project.optional-dependencies] dev` to PEP 735 `[dependency-groups] dev`, add canonical Ruff section and `.python-version = "3.15"`, and verify tests.
  - Check: `cd platform/claude-code-provider-adapter && uv run pytest -p no:cacheprovider`
- [x] 5.6 Add canonical `[tool.uv]`, `[tool.ruff]`, strict `[tool.mypy]` (with full type annotations and no blanket `ignore_errors`), and `[tool.pytest.ini_options]` sections to `ai-tooling/wiki-mcp-server` and `vds/viettel-excel-updater`, delete empty duplicate `config 2.py`, update `.python-version = "3.15"`, and run `uv lock --upgrade`.
  - Check: `for r in ai-tooling/wiki-mcp-server vds/viettel-excel-updater; do uv run --directory $r pytest -p no:cacheprovider; done`

## 6. Workspace-Wide Verification & Syntax Modernization Audit (Wave 4)

- [x] 6.1 Run workspace-wide lint validation `ruff check --target-version py315` across all 34 repositories to confirm zero `A001` (sentinel), zero `UP042` (StrEnum), and zero canonical rule violations.
  - Check: `ruff check --target-version py315 tdt/ shb/ platform/ ai-tooling/ vds/` exits 0.
- [x] 6.2 Execute full test suites across all 34 repositories with `-p no:cacheprovider` to verify hermetic 100% test pass on Python 3.15.
  - Check: All 34 repositories report clean passing test suites.
- [x] 6.3 Verify lockfile freshness across the ecosystem via `uv lock --check` on all repositories.
  - Check: Zero stale lockfile reports across all 34 repositories.
