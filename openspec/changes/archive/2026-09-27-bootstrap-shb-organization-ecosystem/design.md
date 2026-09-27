# Design: Bootstrap SHB Organization Ecosystem

## Context

The workspace follows a multi-repo pattern under `~/Developer/` with first-class organizational namespaces (`tdt/`, `platform/`, `vds/`, `ascend/`, `ghtk/`, `fpt/`). The user has designated `shb` (Saigon - Hanoi Commercial Joint Stock Bank) as the primary ongoing development organization, with an explicit governance mandate to prioritize **Python, agent runtimes, developer CLI tools, and engineering skills first**, deferring heavyweight Java microservices.

Rather than starting from scratch, the team is bringing over, adapting, and synthesizing the best-of-breed agent, CLI, and operational tooling ecosystems from existing organizations (`tdt`, `vds`, `platform`) into `~/Developer/shb/`.

See `proposal.md` for executive motivation, the Wave 1 repository matrix, and scope boundaries.

## Goals / Non-Goals

**Goals:**
- Establish `~/Developer/shb/` containing independent, production-grade Git repositories for the **Python Agentic, CLI, and Engineering Skills Platform**:
  1. `shb-core` (SDK, auth, client factories, DBOS scheduler)
  2. `shb-agent-core` (Pydantic AI v2 runtime, ReAct, tool registry, memory)
  3. `shb-agent-harness` (12-stage LangGraph ticket planning harness)
  4. `shb-ai-harness-skills` (Harness-13 schemas & stage contracts)
  5. `shb-agent-skills` (38+ engineering skills from `vds/WHO-project/vds-skills`: hexagonal architecture audit, circular dependency, migration detection, etc.)
  6. `shb-ai-review` (Automated GitLab MR review, multi-provider review dispatch, coverage gating)
  7. `shb-browser-cli` (Playwright CDP browser automation, document extraction)
  8. `shb-webhook-receiver` (FastAPI event webhook ingress, DLQ replay, health monitoring)
  9. `shb-jira-tools` (Jira project tracking, ADF comments, sprint & epic reporting)
  10. `shb-observability` (OTel collector, Streamlit/DuckDB telemetry dashboard)
  11. `shb-tools` (Operational automation, Docker Compose stacks, Nginx reverse proxy)
- Ingest and sanitize core capabilities from `tdt` and `vds`, establishing a clean repository lifecycle for `shb`.
- Guarantee strict credential and configuration isolation via `~/.shb/` (mode 0700) and `~/.shb/.env` (mode 0600).
- Standardize all Python repositories on Python `>=3.14`, `uv` packaging, `hatchling` build backend, Ruff (line length 100), and strict Mypy.
- Configure seamless inter-repository development via `[tool.uv.sources]` editable paths.
- Register all repositories in workspace code intelligence (`knowledge-refresh-inventory.tsv` for GitNexus and Graphify).

**Non-Goals:**
- Ingesting, porting, or deploying Java Spring Boot microservices (`EKYC-project`, `SAVING-project`, `LEP-project`, `PAR-project` from `vds`) during Wave 1 — **we will NOT bring Java microservices in yet** (explicitly deferred to a dedicated Wave 2 change).
- Creating a Git submodule hierarchy or monorepo wrapper inside `shb/` (each must remain an independent Git repository).
- Sharing secrets, runtime environments, or cache directories between `~/.tdt/`, `~/.vds/`, and `~/.shb/`.
- Mutating or breaking existing repositories in `tdt/`, `platform/`, or `vds/`.
- Connecting to live production banking networks during initial bootstrap.

## Technical Decisions

### Decision 0: Explicit Deferral of Java Microservices (Not Bringing Java Microservices In Yet)
- **Mandate**: Java microservices from `vds` (`SAVING-project`, `EKYC-project`, `LEP-project`, `PAR-project`) and any other legacy enterprise stacks are explicitly out of scope for the current change. We will **NOT** bring Java microservices in yet.
- **Architectural Rationale**:
  1. *Toolchain & Runtime Isolation*: Heavy JVM runtimes, Gradle daemons, Maven repository bloat, and Nexus proxy friction compete with the lightweight, sub-second Python agent workflows.
  2. *Agent & Verification First Precedence*: Establishing the autonomous ReAct agent runtime (`shb-agent-core`), ticket planning harness (`shb-agent-harness`), schema contracts (`shb-ai-harness-skills`), automated code reviewer (`shb-ai-review`), and Model Context Protocol servers (`shb-mcp-servers`) equips the engineering team with the AI apparatus necessary to inspect, refactor, and test Java microservices later.
  3. *Clean-Break Governance*: Wave 1 remains 100% Python `>=3.14`, `uv`, and cloud-native observability. A future dedicated OpenSpec change will govern the ingestion of Java microservices once autonomous agent verification gates are established in production.

### Decision 1: Python-First Agentic Architecture
- **Choice**: Focus Wave 1 strictly on the 11 Python, Agent, CLI, and Skill repositories:
  - **Foundational Runtime**: Core SDK (`shb-core`) and Agent Runtime (`shb-agent-core`) delivering Pydantic AI v2 loop, multi-provider model fallback (`infer_model`), and DBOS durable execution.
  - **Planning & Skills**: `shb-agent-harness` (12-stage ticket lifecycle), `shb-ai-harness-skills` (harness-13 schemas), and `shb-agent-skills` (harvested 38+ engineering skills from VDS).
  - **Ingress & Quality**: `shb-ai-review` (automated MR review), `shb-webhook-receiver` (FastAPI event ingress), and `shb-jira-tools` (Jira delivery tracking).
  - **Tools & Infra**: `shb-browser-cli` (CDP attach & document extraction), `shb-observability` (OTel dashboard & pollers), and `shb-tools` (operational Docker orchestration).
- **Rationale**: Setting up the Python agent and review tooling first provides the autonomous agents necessary to subsequently inspect, refactor, and test Java microservices when they are brought in during Wave 2.

### Decision 2: Sourcing, Ingestion, and Decoupling Pipeline
- **Choice**: Clean-slate repository initialization with selective file ingestion from upstream counterparts.
- **Refactoring & Sanitization Pipeline**:
  - **Git History**: Initialize each repository with `git init -b main` to start a clean repository lifecycle without carrying forward legacy commit histories, stale branches, or old author metadata.
  - **Namespace Transformation**:
    - `tdt_core` / `vds_*` → `shb_core`
    - `agent_core` → `shb_agent_core` (or `shb_agent`)
    - `agent_harness` → `shb_agent_harness`
    - `ai_harness` → `shb_ai_harness`
    - `ai_review` → `shb_ai_review`
    - `webhook_receiver` → `shb_webhook_receiver`
  - **Config & Secret Isolation**:
    - Global config: `~/.shb/config.yaml`
    - Secrets file: `~/.shb/.env` (mode 0600)
    - Environment prefixes: `TDT_*` / `VDS_*` → `SHB_*`
    - Zero fallback or loading of `~/.tdt/` or `~/.vds/`.
  - **Skill Harvesting from VDS**:
    - Ingest 38 canonical skills from `vds/WHO-project/vds-skills` (hexagonal architecture audit, circular dependency detection, code review graph, migration script detection) into `shb-agent-skills`, sanitizing prompt paths to `~/.shb/` standards.
  - **Dependency Decoupling**:
    - Wire internal dependencies using `uv` workspace source tables in each `pyproject.toml`:
      ```toml
      [tool.uv.sources]
      shb-core = { path = "../shb-core", editable = true }
      shb-agent-core = { path = "../shb-agent-core", editable = true }
      ```
  - **Exclusion Filters**:
    - Strictly exclude `.git/`, `.venv/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `dist/`, `build/`, `*.egg-info/`, `.DS_Store`.

### Decision 3: Python Toolchain & Quality Standards
- **Choice**: Standardize all repositories on Python `>=3.14` with unconstrained upper bounds, `hatchling` build backend, `uv` packaging, Ruff (line length 100), and Mypy strict.
- **Rationale**: Guarantees consistency across all repositories, avoids virtualenv drift, and enables sub-second dependency syncing.

### Decision 4: Centralized OpenSpec Specification Architecture
- **Choice**: All specifications live centrally under `~/Developer/platform/openspec-store/openspec/specs/shb-*/`.
- **Rationale**: Follows workspace invariant that no individual repo contains an `openspec/` directory. All changes validate against central schemas and tooling via `--store openspec-store`.

## Risks / Trade-offs

- **[Risk] Upstream import leakage (dangling imports to `tdt_core`, `agent_core`, or `vds_*`)** → **Mitigation**: Automated grep sweeps in test suites asserting zero occurrences of `tdt_` or `vds_` across all `src/` and `tests/` directories.
- **[Risk] Credential contamination across organizations** → **Mitigation**: Strict permissions on `~/.shb/.env` (mode 0600) and automated tests asserting `shb-core` fails closed when `~/.shb/.env` is absent.
- **[Risk] Workspace test cache pollution** → **Mitigation**: All `pyproject.toml` files include `addopts = "-ra -q --tb=short --strict-markers -p no:cacheprovider"`.

## Migration & Execution Plan

1. **Phase 1: Environment & Directory Scaffolding**
   - Create `~/Developer/shb/` and `~/.shb/` with templates.
2. **Phase 2: Core SDK Ingestion (`shb-core`)**
   - Ingest `tdt/tdt-core` foundation, config loader, client factories, and DBOS scheduler.
3. **Phase 3: Agent Runtime & Planning Harness (`shb-agent-core`, `shb-agent-harness`, `shb-ai-harness-skills`, `shb-agent-skills`)**
   - Ingest Pydantic AI v2 runtime, 12-stage LangGraph harness, schema-backed verification skills, and 38+ engineering skills from `vds-skills`.
4. **Phase 4: Developer Tools, Review & Ingress Automation (`shb-browser-cli`, `shb-ai-review`, `shb-webhook-receiver`, `shb-jira-tools`)**
   - Ingest Playwright browser automation, automated MR code review, event webhook ingress, and Jira delivery tools.
5. **Phase 5: Observability & Operational Infrastructure (`shb-observability`, `shb-tools`)**
   - Ingest OTel telemetry stack, Streamlit/DuckDB dashboard, Docker Compose stacks, and CLI script routing.
6. **Phase 6: Integration, Code Intelligence & Knowledge Refresh**
   - Register all repositories in `knowledge-refresh-inventory.tsv`, author per-repo `SPEC_INDEX.md` and `README.md`, and verify clean `uv run pytest` runs across all repositories.
