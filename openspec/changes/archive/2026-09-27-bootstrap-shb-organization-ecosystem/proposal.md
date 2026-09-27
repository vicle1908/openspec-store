# Proposal: Bootstrap SHB Organization Ecosystem

## Why

The workspace is establishing Saigon - Hanoi Commercial Joint Stock Bank (SHB) as the primary ongoing engineering, AI agent, and banking software development organization. Rather than developing isolated ad-hoc tools, the team is bringing over, adapting, and synthesizing the best-of-breed agent, CLI, and operational tooling ecosystems from existing organizations (`tdt`, `vds`, `platform`) into `~/Developer/shb/`. This creates a self-contained, enterprise-grade banking AI ecosystem with strict credential isolation (`~/.shb/`), standardized Python 3.14 toolchains (`uv`), and full code intelligence.

## Sourcing & Phased Prioritization: Python, Agent, CLI Tools & Skills First

Following detailed audits of `~/Developer/tdt/` (23 repositories) and `~/Developer/vds/` (10 banking project suites and 38 agent skills), the rollout strictly follows a **Python-First Agentic Precedence**:

### Python Autonomous Agent & Tooling Architecture

The ecosystem establishes the autonomous toolchain, agent execution runtimes, developer CLIs, and engineering skills catalog necessary to inspect, plan, write, and review codebases. All 12 repositories are standardized on Python `>=3.14` and `uv`:

| Target SHB Repository | Source Organization & Repo | Content Brought In / Ingested | Key Adaptations & Sanitizations |
|---|---|---|---|
| **`shb-core`** | `tdt/tdt-core` | Foundation SDK, Pydantic settings, DBOS scheduler primitives, Jira & GitLab client factories. | Isolated config loader targeting `~/.shb/.env` and `~/.shb/config.yaml`. Added `BankingApiClientFactory` for SHB internal banking APIs. Rebranded to `shb_core`. |
| **`shb-agent-core`** | `tdt/agent-core` | Pydantic AI v2 foundation, ReAct execution loop, model fallback resolver (`infer_model`), tool registry, memory systems, Langfuse/MLflow telemetry. | Decoupled from `tdt_core` to depend exclusively on `shb_core`. Removed brokerage trading logic. Rebranded CLI to `shb-agent`. |
| **`shb-agent-harness`** | `tdt/agent-harness` | 12-stage LangGraph engineering ticket planning harness, durable state checkpointing, evidence publication, and human gates. | Re-targeted planning stages to commercial banking systems, compliance checks, and microservice APIs. Rebranded CLI to `shb-harness`. |
| **`shb-ai-harness-skills`** | `tdt/ai-harness-skills` | JSON schema specifications (`resources/harness-13`), stage validation contracts, claim diagnostics, traceability verification, and audit tools. | Decoupled from TDT legacy schemas. Tailored verification contracts for banking compliance and data safety. Rebranded CLI to `shb-harness-skills`. |
| **`shb-agent-skills`** | `vds/WHO-project/vds-skills` | Curated catalog of 38+ engineering skills (hexagonal architecture audit, migration script detection, GitNexus code review, circular dependency analysis, spec creation). | Sanitized all prompt paths to `~/.shb/` conventions, removed VDS-specific prefixes, added banking data protection rules (PCI-DSS / SBV regulations). |
| **`shb-ai-review`** | `tdt/ai-review` | Automated GitLab MR review intake, multi-provider review dispatch (Claude, Codex, Antigravity, Kimi), MR note publication, coverage calculation. | Scoped to SHB GitLab instance and banking service repositories. Stripped mobile Swift/Kotlin rules. Rebranded CLIs to `shb-ai-review` and `shb-mr-coverage`. |
| **`shb-browser-cli`** | `tdt/browser-cli` | Playwright browser automation, Chrome DevTools Protocol (CDP) session attach, persistent storage states, PDF/DOCX/table document extraction (bank statements, credit agreements). | Dedicated cookie store for SHB intranet portals. Extractor pipelines tailored for bank statements and credit agreements. Rebranded CLI to `shb-browser-cli`. |
| **`shb-webhook-receiver`** | `tdt/webhook-receiver` | FastAPI webhook ingress, HMAC signature verification, GitLab/Jira event triggers, Dead Letter Queue (DLQ) replay, health monitoring. | Scoped to SHB event webhooks. Rebranded CLIs to `shb-webhook-receiver` and `shb-replay-dlq`. |
| **`shb-jira-tools`** | `tdt/jira-skill` + `tdt/jira-daily-reports` | Jira Cloud/Server API integration, ADF comment formatting, JQL search helpers, sprint tracking, and epic progress reporting. | Consolidated Jira tools into single focused repository for SHB project tracking. Rebranded CLI to `shb-jira`. |
| **`shb-mcp-servers`** | Greenfield | Model Context Protocol JSON-RPC 2.0 stdio & SSE servers for banking tools. | Exposes accounts, transactions, MR diff inspection, and Jira issue lookups. |
| **`shb-observability`** | `tdt/tdt-observability` | Centralized OTel observability stack, telemetry dashboard, log collectors, and service health pollers. | Parameterized for SHB local port allocations and agent telemetry tracking. |
| **`shb-tools`** | `tdt/tdt-tools` + `tdt/bootstrap-nexus` + `vds/WHO-project/vds-scripts` | Operational automation scripts, incident reporting utilities, Docker Compose service stacks (Postgres, Redis, OTel), Nginx reverse proxy configs. | Parameterized for SHB local development environments and multi-repo script dispatching. |

### Scope Boundary: Fully Decoupled Python Engineering Platform

The SHB engineering ecosystem is completely self-contained in a single unified Python and tooling architecture. All legacy Java microservices are completely excluded:
- **Zero Java Dependencies**: No JVM, JDK, Gradle wrappers, or Maven `pom.xml` dependencies exist in this ecosystem.
- **Unified Architecture**: The rollout focuses exclusively on the autonomous Python agent runtime, planning harness, schema contracts, engineering skills, review engines, developer CLIs, event webhooks, Jira tools, MCP servers, and operational observability across 12 independent repositories.
- **Zero Additional Waves**: There are no additional waves, secondary phases, or pending Java migrations.

## What Changes

- Provision `~/Developer/shb/` as an independent organizational namespace holding decoupled Git repositories.
- Ingest and sanitize source trees from `tdt` and `vds`, removing legacy git commit histories to start clean repository lifecycles in `shb`.
- Standardize all repositories on Python `>=3.14`, `uv` package management, `hatchling` build backends, Ruff (line length 100), and strict Mypy.
- Enforce strict credential and configuration isolation in `~/.shb/` (mode 0700) and `~/.shb/.env` (mode 0600), asserting zero leakage from `~/.tdt/` or `~/.vds/`.
- Wire inter-repository dependencies locally via `[tool.uv.sources]` editable paths.
- Register all repositories in `~/Developer/scripts/knowledge-refresh/knowledge-refresh-inventory.tsv` for nightly GitNexus and Graphify code intelligence.
- Update central OpenSpec store contexts and workspace `AGENTS.md` to establish SHB as a core active organization.

### Non-Goals
- Ingesting, porting, or deploying Java Spring Boot/Gradle/Maven microservices (`EKYC-project`, `SAVING-project`, `LEP-project`, `PAR-project`) — completely out of scope.
- Modifying or breaking existing active repositories in `tdt/`, `platform/`, `vds/`, or `ascend/`.
- Creating a Git submodule hierarchy or monorepo wrapper under `~/Developer/shb/` (each must remain an independent Git repository).
- Sharing runtime secret files between `~/.tdt/`, `~/.vds/`, and `~/.shb/`.
- Connecting to live production banking networks during initial bootstrap.

## Capabilities

### New Capabilities
- `shb-core-foundation`: Shared SDK providing unified environment loading (`~/.shb/.env`), configuration models, banking/collaboration client factories, and the `shb` base CLI.
- `shb-agent-runtime`: Pydantic AI v2 foundation, provider-agnostic model resolution (`infer_model`), ReAct execution engine, tool registry, and `shb-agent` CLI.
- `shb-planning-harness`: Multi-stage ticket planning workflows, schema-backed verification, durable checkpoints, and `shb-harness` CLI.
- `shb-agent-skills`: Catalog of 38+ specialized engineering skills, architectural audit evaluators, and banking compliance prompts.
- `shb-review-and-quality`: Automated GitLab MR reviews, multi-provider review orchestration, test coverage gating, and `shb-ai-review` CLI.
- `shb-browser-cli`: Authenticated browser automation CLI using Playwright CDP attach and document extraction pipelines.
- `shb-webhook-ingress`: Event webhook ingress, Dead Letter Queue (DLQ) replay, and Jira project delivery reporting.
- `shb-observability-telemetry`: Centralized OpenTelemetry collection, service health polling, and telemetry dashboards.
- `shb-ecosystem-tooling`: Multi-repo directory topology, packaging standardization with `uv`, quality gates, and code intelligence integration.

### Modified Capabilities
<!-- None -->

## Impact

- **Workspace Topology**: Adds `~/Developer/shb/` containing independent Git repositories to `AGENTS.md`.
- **Environment & Secrets**: Introduces `~/.shb/` directory with `~/.shb/.env` (mode 0600) strictly isolated from other organizations.
- **Knowledge Refresh**: Registers SHB repositories into `~/Developer/scripts/knowledge-refresh/knowledge-refresh-inventory.tsv`.
- **Tooling & Development**: Standardizes on Python `>=3.14` and `uv` for package management and local inter-repo linking across the entire banking ecosystem.
