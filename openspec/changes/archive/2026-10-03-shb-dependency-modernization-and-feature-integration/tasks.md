# Tasks

## 1. Toolchain and Developer Dependencies

- [x] 1.1 Update `mypy>=2.4.0`, `ruff>=0.16.10`, and `pytest-mock>=3.16.0` across all 12 SHB `pyproject.toml` files and verify with `uv sync`
- [x] 1.2 Run `uv run ruff check` and `uv run mypy src/` across all 12 repositories to verify clean lint and type checks under the updated toolchain

## 2. Core Foundation and Webhook Modernization

- [x] 2.1 Upgrade `shb-core` dependencies (`python-dotenv>=1.2.4`, `pyyaml>=6.0.3`, `pydantic>=2.13.5`) and verify `uv run pytest tests/` passes with 21/21 tests
- [x] 2.2 Modernize `shb-webhook-receiver` to `fastapi>=0.142.2` and `uvicorn>=0.54.0`, update async lifespan event handlers in `src/shb_webhook/app.py`, and verify `uv run pytest tests/` passes with 0 deprecation warnings

## 3. Agent Runtime and Planning Ecosystem Upgrade

- [x] 3.1 Upgrade `shb-agent-core` to `pydantic-ai>=2.53.0` and standardize `pydantic>=2.13.5`, verifying agent reasoning and banking tools with `uv run pytest tests/` (27/27 tests)
- [x] 3.2 Standardize dependency constraints across `shb-agent-harness`, `shb-mcp-servers`, `shb-jira-tools`, `shb-agent-skills`, `shb-ai-harness-skills`, `shb-ai-review`, `shb-browser-cli`, `shb-observability`, and `shb-tools`
- [x] 3.3 Run `uv sync --upgrade` across all 12 repositories to generate fresh, synchronized `uv.lock` files

## 4. End-to-End Verification and Validation

- [x] 4.1 Execute full test suite across all 12 repositories (`uv run pytest -q -p no:cacheprovider`) and verify 100% pass rate
- [x] 4.2 Verify all CLI entrypoints (`shb doctor`, `shb-agent tools-list`, `shb-harness list-stages`, `shb-mcp list-tools`, `shb-skills list-available-skills`) execute with exit code 0
- [x] 4.3 Validate OpenSpec change strictly using `openspec validate --all --strict --store openspec-store`
