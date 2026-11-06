# Proposal: Modernize Workspace Dependencies (Q4 2026)

## Why
Workspace repositories across `shb/`, `tdt/`, and `platform/` accumulated dependency drift and pin divergence against recent upstream security patches and major releases. Upgrading foundational runtimes—including Pydantic-AI 2.66 (remediating 4 high/medium GHSAs and adding sticky model fallbacks), FastAPI 0.162 (strict boolean form field semantics and httpx2 testing), DBOS 3.4 (asynchronous data sources and payload table separation), DuckDB 2.0 LTS (async I/O and agent mode), Redis 8.1 (default RESP3 wire protocol), Go 1.27.3 compiler alignment, Temporal Go SDK v1.50.0, and Model Context Protocol SDK 1.32.2—ensures supply-chain security, eliminates obsolete deprecated patterns, and accelerates agent orchestration performance under a strict clean-break standard.

## What Changes
- **Python Autonomous Agent Ecosystem (`shb/`, `tdt/`)**:
  - **BREAKING (Security & Model Fallback)**: Upgraded `pydantic-ai` to `>=2.66.0` (from `>=2.59.0`), `pydantic-ai-harness` to `>=0.66.0`, and `pydantic-evals` to `>=2.66.0`. Resolves 4 GHSAs (GHSA-m5vj-8mcw-82qx JSON expansion DoS, GHSA-mfx5-pc32-32m8 harness regex ReDoS, GHSA-jp94-mmr3-2pvv OTel credential leakage, GHSA-4cj4-hgwf-4hc4 durable execution file re-inflation). Adopts `ModelFallback(sticky=True)` and `DetectLoops` capabilities.
  - **BREAKING (Web Framework & Lifespan)**: Upgraded `fastapi` to `>=0.162.0` (from `>=0.159.1`) and `starlette` to `>=1.10.0`. Enforces explicit default semantics on boolean form fields (FastAPI no longer coercively infers `False` for omitted booleans). Declares `httpx2>=2.16.0` in dev dependency groups across FastAPI services to eliminate Starlette TestClient deprecation warnings.
  - **Durable Scheduling & State Engine (`shb/shb-schedule`, `tdt/tdt-core`)**: Upgraded `dbos` to `>=3.4.0` (from `>=3.3.0`). Adopts pluggable asynchronous data sources and payload separation tables. Purges references to retired in-memory schedulers/queues.
  - **Analytics & Observability (`tdt/tdt-observability`, `ops-automation-suite`)**: Upgraded `duckdb` to `>=2.0.0` LTS (from `>=1.5.5`). Adopts asynchronous I/O and native agent mode. Upgraded `langfuse` to `>=5.1.0` (from `>=4.14.0`) aligned with Langfuse Server v4, adopting compressed span export and typed metadata filters.
  - **Data Rails & Caching (`shb/shb-core`, `tdt/agent-core`)**: Upgraded `redis` to `>=8.1.0` (from `>=5.0.0`) adopting the native RESP3 protocol on the wire by default. Upgraded `psycopg[binary,pool]` to `>=3.3.8` and `asyncpg` to `>=0.32.0` for PostgreSQL 18.4 connection pool resilience.
  - **Tooling & Cryptography**: Upgraded `playwright` to `>=1.64.1` (Chrome CDP 135+ engine parity), `cryptography` to `>=50.0.2`, `pillow` to `>=13.0.0`, and `pypdf` to `>=6.21.4`.
- **Go Monorepo & Microservices (`platform/go-microservices`)**:
  - **Toolchain Alignment**: Synchronized root `.go-version`, Makefile `GO_VERSION`, and all `go.mod` files to `1.27.3` matching the host workstation Go compiler (`go1.27.3 darwin/arm64`).
  - **Temporal & Messaging**: Upgraded `go.temporal.io/sdk` to `v1.50.0` and `go.temporal.io/api` to `v1.64.1`. Upgraded `github.com/twmb/franz-go` to `v1.22.2`.
  - **Dev Tools Directive**: Upgraded `honnef.co/go/tools` (staticcheck) to `v0.8.2`, `buf.build/buf` to `v1.75.0`, `mvdan.cc/gofumpt` to `v0.12.0`, and `connectrpc.com/otelconnect` to `v0.12.0`.
- **Node & TypeScript Monorepo (`platform/mcp-router`)**:
  - **Protocol Parity**: Upgraded `@modelcontextprotocol/sdk` to `1.32.2` in `apps/cli` and `apps/electron` for reliable SSE reconnection and JSON-RPC notification handling.
  - **Compiler Normalization**: Unified `typescript` to `^7.0.2` across `apps/cli`, `packages/shared`, `packages/ui`, and `packages/remote-api-types` (matching root `devDependencies`).
  - **Build Engine**: Upgraded `turbo` to `^2.11.10`.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `python-dependency-clean-break`: Extend requirements to mandate `pydantic-ai>=2.66.0` (with `pydantic-ai-harness>=0.66.0`), `fastapi>=0.162.0` (with strict boolean form defaults and `httpx2` clean test client), `dbos>=3.4.0` (asynchronous data sources and payload separation), `duckdb>=2.0.0` LTS (async I/O), `redis>=8.1.0` (default RESP3 wire protocol), and `langfuse>=5.1.0`.
- `platform-go-runtime`: Upgrade Go toolchain requirement to `go 1.27.3` aligned with root `.go-version` `1.27.3`, `go.temporal.io/sdk v1.50.0`, and modern tool directives (`staticcheck v0.8.2`, `buf v1.75.0`).

## Impact
- **Python Services**: `shb/shb-agent-core`, `shb/shb-agent-harness`, `shb/shb-schedule`, `shb/shb-core`, `shb/shb-webhook-receiver`, `shb/shb-observability`, `tdt/agent-core`, `tdt/agent-harness`, `tdt/tdt-observability`, `tdt/webhook-receiver`, `tdt/ops-automation-suite`.
- **Go Services & Platform**: `platform/go-microservices` (platform module, 8 microservices, tests, tools, root Makefile, `.go-version`).
- **Node / Electron Platform**: `platform/mcp-router` (`apps/cli`, `packages/shared`, `packages/ui`, `packages/remote-api-types`, root `package.json`).

## Non-Goals
- Introducing backward-compatibility shims, polyfills, or fallback wrappers for deprecated APIs.
- Premature major upgrade of `electron` to `45.x` or `better-sqlite3` to `13.x` in `mcp-router` within this change (deferring native binary recompile to a dedicated Electron lifecycle change).
- Modifying intentional negative compliance test fixtures in `shb-agent-skills` (`python-noncompliant/`).
