# Evidence: Modernize Workspace Dependencies Q4 2026

## 1. Upstream Major Versions & Ecosystem Upgrades

### 1.1 Python Ecosystem (`shb/` and `tdt/`)
- **Pydantic & Pydantic AI Core**:
  - `pydantic`: upgraded to `>=2.14.2` (resolved `2.14.3`).
  - `pydantic-settings[yaml]`: upgraded to `>=2.16.2`.
  - `pydantic-ai`: upgraded to `>=2.66.0` (resolved `2.66.0`), addressing GHSAs:
    - GHSA-m5vj-8mcw-82qx (memory exhaustion in `web_fetch_tool`)
    - GHSA-mfx5-pc32-32m8 (ReDoS in harness private key validation)
    - GHSA-jp94-mmr3-2pvv (credential leakage in OTel spans)
    - GHSA-4cj4-hgwf-4hc4 (privilege escalation in history serialization)
  - `pydantic-ai-harness`: upgraded to `>=0.66.0`.
  - `pydantic-evals`: upgraded to `>=2.66.0`.
  - `pydantic-monty`: upgraded to `1.4.0`.
- **Database, Durable Execution & Analytics**:
  - `dbos`: upgraded to `>=3.4.0` (resolved `3.4.0`) with async data sources and split payload tables.
  - `duckdb`: upgraded to `>=2.0.0` (LTS baseline) with native async I/O.
  - `redis`: upgraded to `>=8.1.0` (RESP3 protocol support).
  - `psycopg[binary,pool]`: upgraded to `>=3.3.8`.
  - `asyncpg`: upgraded to `>=0.32.0`.
- **Web & Observability**:
  - `fastapi`: upgraded to `>=0.162.0` (resolved `0.162.0`) with strict form field defaults.
  - `starlette`: upgraded to `>=1.10.0`.
  - `uvicorn`: upgraded to `>=0.54.0`.
  - `httpx`: upgraded to `>=0.28.1`.
  - `httpx2`: added to test dependencies at `>=2.16.0`.
  - `opentelemetry-sdk`: upgraded to `>=1.45.2`.
  - `langfuse`: upgraded to `>=5.1.0`.
  - `langgraph`: upgraded to `>=1.2.19` (resolved `1.2.20`).
  - `langgraph-checkpoint`: upgraded to `4.3.1`.
  - `langgraph-checkpoint-postgres`: upgraded to `3.2.0`.
  - `playwright`: upgraded to `>=1.64.1`.

### 1.2 Go Monorepo (`platform/go-microservices`)
- **Compiler Toolchain**:
  - Aligned `.go-version` and `Makefile` `GO_VERSION` to `1.27.3` (host toolchain: `go1.27.3 darwin/arm64`).
- **Distributed Workflow & Messaging**:
  - `go.temporal.io/sdk`: upgraded from `v1.49.0` to `v1.50.0`.
  - `go.temporal.io/api`: upgraded from `v1.63.7` to `v1.64.1`.
  - `github.com/twmb/franz-go`: upgraded from `v1.22.1` to `v1.22.2`.
  - Go directives: `buf v1.75.0`, `staticcheck v0.8.2`, `gofumpt v0.12.0`.

### 1.3 Node & TypeScript Ecosystem (`platform/mcp-router`)
- `@modelcontextprotocol/sdk`: upgraded to `^1.32.2` across `apps/cli` and `apps/electron`.
- `typescript`: upgraded to `^7.0.2` across `packages/shared`, `packages/ui`, and `apps/cli`.
- `turbo`: upgraded to `^2.11.10`.
- `prettier`: upgraded to `^3.9.10`.

---

## 2. Bug Fixes & Deprecation Remediations

1. **Agent Dependency Baseline Assertion Contracts**:
   - In `tdt/agent-core`, `tdt/agent-harness`, and `tdt/agent-docs-sync`, fixed regression assertion tests in `tests/test_dependency_baseline.py` to match the newly locked version tuples (`2.66.0`, `0.66.0`, `1.4.0`, `1.2.20`) and (`4.3.1`, `3.2.0`).
2. **Pytest-Asyncio Loop Scope Configuration**:
   - Resolved `PytestDeprecationWarning: The configuration option 'asyncio_default_fixture_loop_scope' is unset` in `shb/shb-schedule` and `tdt/agent-docs-sync` by explicitly declaring `asyncio_default_fixture_loop_scope = "function"` in `pyproject.toml`.
3. **TypeScript 7 Compiler Option Compatibility**:
   - Resolved TS5102 error in `platform/mcp-router` (`Option 'baseUrl' has been removed`) by removing deprecated `baseUrl: "."` from `apps/cli/tsconfig.json` and `packages/remote-api-types/tsconfig.json`.
   - Pinned `typescript` in `packages/remote-api-types` to `^5.9.3` to maintain compatibility with `tsup 8.5.0`'s bundled rollup DTS generator.

---

## 3. End-to-End Verification Evidence

### 3.1 Go Platform Module & Temporal Replay
```bash
cd /Users/androidteam/Developer/platform/go-microservices && make platform-verify
```
- Platform unit tests, vet checks, and package builds passed: `platform-verify: ok`.

```bash
cd /Users/androidteam/Developer/platform/go-microservices && make temporal-verify
```
- Temporal inventory validation passed (8 services, 9 task queues).
- 5 negative controls verified.
- 8 services workflowaudit passed.
- 8 services workflowcheck passed.
- Clean-slate and determinism controls passed.
- All service event histories replayed successfully without mutation (`temporal-replay: all current-code histories replayed without fixture mutation`).

### 3.2 MCP Router Monorepo Build & Tests
```bash
cd /Users/androidteam/Developer/platform/mcp-router && pnpm -r build && pnpm -r test
```
- Packages `@mcp_router/shared`, `@mcp_router/ui`, `@mcp_router/remote-api-types`, and `@mcp_router/cli` built cleanly.
- 64 unit/integration tests passed across the monorepo packages.

### 3.3 Python Multi-Repo Verification Baselines
- `shb/shb-core`: 46 passed, 1 skipped.
- `shb/shb-tools`: 34 passed.
- `shb/shb-ai-harness-skills`: 27 passed.
- `shb/shb-agent-skills`: 31 passed.
- `shb/shb-agent-core`: 48 passed.
- `shb/shb-observability`: 22 passed.
- `shb/shb-schedule`: 122 passed in 141.94s.
- `shb/shb-agent-harness`: 14 passed.
- `shb/shb-webhook-receiver`: 7 passed.
- `shb/shb-ai-review`: 6 passed.
- `shb/shb-browser-cli`: 10 passed.
- `shb/shb-jira-tools`: 10 passed.
- `shb/shb-mcp-servers`: 18 passed.
- `tdt/tdt-core`: 45 passed.
- `tdt/tdt-sheets`: 31 passed.
- `tdt/jira-skill`: 47 passed.
- `tdt/agent-core`: 648 passed.
- `tdt/tdt-observability`: 231 passed.
- `tdt/agent-harness`: 418 passed.
- `tdt/agent-docs-sync`: 342 passed (with OTEL_SDK_DISABLED=true).
- `tdt/webhook-receiver`: 60 passed.
- `tdt/ops-automation-suite`: 13 passed.
- `tdt/ai-review`: 40 passed.
- `tdt/browser-cli`: 19 passed.
- `tdt/jira-epic-report`: 650 passed (83.90% coverage).
- `tdt/jira-kanban-from-spreadsheet`: 152 passed.
- `tdt/jira-daily-reports`: 643 passed.
- `tdt/code-daily-scan`: 510 passed, 2 skipped.
- `tdt/ai-harness-skills`: 633 passed, 4 skipped (87.45% coverage).

### 3.4 OpenSpec Strict Validation
```bash
openspec validate modernize-workspace-dependencies-q4-2026 --strict --store openspec-store
```
- Result: `Change 'modernize-workspace-dependencies-q4-2026' is valid` (exit 0).

```bash
openspec validate --all --store openspec-store
```
- Result: `Totals: 460 passed, 0 failed (460 items)` (exit 0).
