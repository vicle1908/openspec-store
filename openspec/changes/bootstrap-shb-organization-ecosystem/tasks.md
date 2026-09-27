# Tasks: Bootstrap SHB Organization Ecosystem

## 1. Environment and Directory Scaffolding

- [x] 1.1 Create `~/Developer/shb` organizational directory and verify directory exists with zero parent git collisions via `test -d ~/Developer/shb`
- [x] 1.2 Author template credential file at `~/.shb/.env.example` with isolated banking environment variables and verify permissions are mode 0600
- [x] 1.3 Update `openspec-store/openspec/config.yaml` to document the `shb` organization layout and Python-first agentic context

## 2. Core SDK and Agent Runtime (shb-core, shb-agent-core)

- [x] 2.1 Initialize `shb-core` repository with `pyproject.toml` using `hatchling` and `uv`, create `src/shb_core`, and verify `git status` reports clean initial repo
- [x] 2.2 Ingest and adapt configuration loader in `src/shb_core/config.py` resolving `~/.shb/.env` and verify unit tests assert zero leakage of `~/.tdt/.env`
- [x] 2.3 Implement client factories for Jira, GitLab, and banking HTTP APIs in `src/shb_core/clients/` and verify unit tests pass with `uv run pytest tests/test_clients.py`
- [x] 2.4 Implement `shb` CLI in `src/shb_core/cli.py` with `doctor` and `config-show` commands and verify `uv run shb --help` outputs registered commands
- [x] 2.5 Verify `shb-core` test suite passes cleanly via `uv run pytest`
- [x] 2.6 Initialize `shb-agent-core` repository with `pyproject.toml` depending on `shb-core` and verify `uv sync` resolves dependencies
- [x] 2.7 Ingest model resolution and provider fallback chain into `src/shb_agent/model.py` and verify unit tests with `uv run pytest tests/test_model.py`
- [x] 2.8 Implement ReAct agent execution loop and banking tool registry in `src/shb_agent/agent.py` and verify execution tests pass with `uv run pytest tests/test_agent.py`
- [x] 2.9 Implement `shb-agent` CLI entrypoint in `src/shb_agent/cli.py` and verify `uv run shb-agent --help` succeeds
- [x] 2.10 Verify `shb-agent-core` test suite passes cleanly via `uv run pytest`

## 3. Planning Harness and Engineering Skills (shb-agent-harness, shb-ai-harness-skills, shb-agent-skills)

- [x] 3.1 Ingest 12-stage ticket planning engine from `tdt/agent-harness` into `shb-agent-harness` and verify `shb-harness --help` succeeds
- [x] 3.2 Ingest schema validation contracts from `tdt/ai-harness-skills` into `shb-ai-harness-skills` and verify schema loading tests pass
- [x] 3.3 Ingest 38+ engineering skills from `vds/WHO-project/vds-skills` into `shb-agent-skills`, sanitizing prompt paths to `~/.shb/` standards and adding banking compliance guidelines

## 4. Developer CLI, Review, and Ingress Automation (shb-browser-cli, shb-ai-review, shb-webhook-receiver, shb-jira-tools)

- [x] 4.1 Ingest `tdt/browser-cli` patterns into `shb-browser-cli` repository with `pyproject.toml` and Playwright dependencies, verifying `git status` reports clean repo
- [x] 4.2 Port CDP attach and document extraction pipeline in `src/shb_browser_cli/` and verify unit tests pass with `uv run pytest`
- [x] 4.3 Verify `shb-browser-cli` test suite passes cleanly via `uv run pytest`
- [x] 4.4 Ingest MR review intake and multi-provider reviewer orchestration from `tdt/ai-review` into `shb-ai-review` and verify CLI help
- [x] 4.5 Ingest event webhook receiver, HMAC validation, and Dead Letter Queue from `tdt/webhook-receiver` into `shb-webhook-receiver`
- [x] 4.6 Ingest Jira integration, ADF formatting, and delivery reporting from `tdt/jira-skill` and `jira-daily-reports` into `shb-jira-tools`
- [x] 4.7 Implement Model Context Protocol (MCP) server endpoints in `shb-mcp-servers` exposing stdio/SSE transports for banking, Jira, and GitLab tools, and verify `shb-mcp --help`

## 5. Telemetry, Observability, and Operational Infrastructure (shb-observability, shb-tools)

- [x] 5.1 Initialize `shb-tools` repository with operational shell and Python automation scripts, verifying script executability with `bash -n`
- [x] 5.2 Ingest OTel collector and telemetry dashboard from `tdt/tdt-observability` into `shb-observability` and verify CLI help
- [x] 5.3 Provision Docker Compose service stacks (PostgreSQL 18, Redis, OTel Collector) and Nginx proxy in `shb-tools/docker/`

## 6. Workspace Integration and Verification

- [x] 6.1 Register active SHB repositories in `~/Developer/scripts/knowledge-refresh/knowledge-refresh-inventory.tsv` and verify via `~/Developer/scripts/knowledge-refresh/knowledge-status.sh --json`
- [x] 6.2 Author `SPEC_INDEX.md` and `README.md` for active repositories and verify links resolve to central OpenSpec store
- [x] 6.3 Run full test suites across active SHB repositories via `uv run pytest` and verify zero failures, zero import leaks of `tdt_` or `vds_`, and zero test cache pollution in workspace root

## 7. Scope Boundaries and Deferral Verification

- [x] 7.1 Verify zero Java microservices (`.java` files, Maven `pom.xml`, Gradle wrappers, Spring Boot services) are created under `~/Developer/shb/` (all 12 active repositories remain strictly Python, agent runtimes, CLI tools, skills, and operational infrastructure)
