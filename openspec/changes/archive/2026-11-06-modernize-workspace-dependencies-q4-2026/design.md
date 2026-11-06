# Design: Modernize Workspace Dependencies (Q4 2026)

## Context
See `proposal.md` for background and motivation. The workspace spans multi-language polyrepo domains:
- 12 Python repositories in `shb/` and 19 in `tdt/` managed via `uv` with editable workspace sources (`[tool.uv.sources]`).
- Greenfield Go monorepo in `platform/go-microservices` (8 deployable services, shared platform module, Temporal Go SDK, Kafka franz-go).
- TypeScript monorepo in `platform/mcp-router` (Electron app, CLI, shared libraries, `@modelcontextprotocol/sdk`).

Upgrades must satisfy the clean-break standard: zero legacy shims, zero deprecation wrappers, and direct adoption of upstream APIs.

## Goals / Non-Goals

**Goals:**
- Eliminate security vulnerabilities across Python runtimes (4 GHSAs in Pydantic-AI/Harness).
- Upgrade foundational Python dependencies (`pydantic-ai>=2.66.0`, `fastapi>=0.162.0`, `dbos>=3.4.0`, `duckdb>=2.0.0`, `redis>=8.1.0`, `langfuse>=5.1.0`).
- Align Go toolchain across all modules to `1.27.3` (matching the host workstation Go compiler), upgrading `go.temporal.io/sdk` to `v1.50.0`.
- Unify TypeScript compiler to `^7.0.2` and MCP SDK to `1.32.2` across `mcp-router`.
- Ensure 100% test pass rate across all modified packages without deprecation warnings.

**Non-Goals:**
- Upgrading `electron` to 45.x or `better-sqlite3` to 13.x in `mcp-router` (which requires native Mach-O binary rebuilds and notarization, reserved for an isolated desktop app change).
- Rewriting database schemas or touching historical migration files.
- Modifying intentional negative test fixtures under `shb-agent-skills/skills/hexagonal-compliance-skill/tests/fixtures/python-noncompliant/`.

## Decisions

### Decision 1: Topological Tier Phasing for Python Monorepo Upgrades
- **Rationale**: Repositories declare editable path dependencies on siblings (`shb-agent-core` depends on `shb-core`, `agent-harness` depends on `agent-core` and `tdt-core`). Updating downstream manifests before upstream dependencies triggers solver backtracking deadlocks.
- **Order**:
  - Tier 0: Foundation SDKs (`shb-core`, `tdt-core`).
  - Tier 1: Shared Subsystems & Skills (`tdt-sheets`, `jira-skill`, `shb-tools`, `shb-ai-harness-skills`, `shb-agent-skills`).
  - Tier 2: Core Orchestration Frameworks (`shb-agent-core`, `agent-core`, `shb-observability`, `tdt-observability`).
  - Tier 3: Leaf Services & Schedulers (`shb-agent-harness`, `agent-harness`, `shb-schedule`, `shb-webhook-receiver`, `webhook-receiver`, `ops-automation-suite`, `ai-review`, `shb-ai-review`).
- **Alternative Considered**: Updating all manifests simultaneously with `uv lock --upgrade`. Rejected because scratch simulations showed solver instability when leaf dependencies lock before base SDK versions propagate.

### Decision 2: Native Pydantic-AI 2.66 Capabilities vs Custom Retry Logic
- **Rationale**: Pydantic-AI 2.66 introduces `ModelFallback(sticky=True)`, `DetectLoops`, and native handling for `ContentFilterError` and provider refusals. Adopting upstream `sticky=True` prevents oscillatory model flapping in `FallbackModelChain` without custom state tracking.
- **Alternative Considered**: Maintaining custom wrapper logic in `shb_agent_core.models.fallback`. Rejected under clean-break standard.

### Decision 3: Explicit Boolean Defaults & Dev Group `httpx2` for FastAPI Services
- **Rationale**: FastAPI 0.162 fixes boolean form field handling to eliminate coercive `False` inference on omitted fields. All boolean form parameters must declare explicit defaults (`Field(default=False)`). Additionally, declaring `httpx2>=2.16.0` in dev dependency groups eliminates Starlette 1.10 `TestClient` deprecation warnings.
- **Alternative Considered**: Suppressing `StarletteDeprecationWarning` in `pytest.ini`. Rejected because clean-break standard forbids warning suppressions.

### Decision 4: DBOS 3.4 Asynchronous Data Sources and Table Separation
- **Rationale**: DBOS 3.4 separates workflow execution payloads from metadata tables, preventing database table bloat in `shb-schedule`. All retired in-memory queues and schedulers are purged in favor of SQLite/PostgreSQL storage.
- **Alternative Considered**: Retaining DBOS 3.3.0. Rejected due to performance improvements and memory cleanup during process shutdown.

### Decision 5: Go Compiler Alignment to 1.27.3 and Temporal SDK v1.50.0
- **Rationale**: Host Go compiler is `go1.27.3 darwin/arm64`. Aligning `.go-version`, root `Makefile`, and service `go.mod` files avoids toolchain mismatch warnings in CI and local developer workflows. Temporal Go SDK v1.50.0 provides improved memory management during workflow replay verification.
- **Alternative Considered**: Leaving `.go-version` at `1.27.1`. Rejected because of compiler version drift.

### Decision 6: MCP SDK 1.32.2 & TypeScript 7 Unification in `mcp-router`
- **Rationale**: Upgrading `@modelcontextprotocol/sdk` to 1.32.2 addresses SSE reconnection drops. Unifying `typescript` to `^7.0.2` across all subpackages eliminates multi-version compiler variance in Turbo monorepo builds.
- **Alternative Considered**: Leaving CLI on TS 5.9.3. Rejected to keep workspace devDependencies aligned.

## Risks / Trade-offs

- **[Risk] Redis 8.1 RESP3 wire protocol changes return types**: In RESP3, Redis returns sets as Python `set` instead of `list`, and map entries as `dict`.
  - **Mitigation**: Audit callers in `agent-core` and `shb-agent-core` that parse Redis responses to ensure compatibility with native Python types.
- **[Risk] DuckDB 2.0 storage file compatibility**: Upgrading DuckDB to 2.0 LTS may affect local `.duckdb` state files if storage format versions differ.
  - **Mitigation**: `tdt-observability` uses DuckDB for transient metric caching and event logs; tests use isolated temporary databases (`test.duckdb`).
- **[Risk] FastAPI 0.162 form parameter parsing**: Omitted booleans now raise validation errors if no default was declared.
  - **Mitigation**: Inspect all webhook receiver request models in `shb-webhook-receiver` and `tdt/webhook-receiver` to guarantee explicit defaults on all boolean attributes.
- **[Risk] Solver backtracking in multi-repo uv workspaces**: Transitive pins in editable packages could cause lockfile conflicts.
  - **Mitigation**: Tested in sandboxed scratch (`~/.hermes/cache/scratch/dep-sim/`) before modifying repository trees.

## Migration Plan

1. **Phase 1: Python Foundation (Tier 0 & Tier 1)**:
   - Update `shb-core` and `tdt-core` manifests; run `uv lock --upgrade` and test suites.
   - Update shared subsystems (`tdt-sheets`, `jira-skill`, `shb-tools`, `shb-ai-harness-skills`, `shb-agent-skills`).
2. **Phase 2: Python Core & Schedulers (Tier 2 & Tier 3)**:
   - Update `shb-agent-core` and `agent-core` (`pydantic-ai>=2.66.0`, `redis>=8.1.0`).
   - Update `shb-schedule` (`dbos>=3.4.0`), `tdt-observability` (`duckdb>=2.0.0`), `shb-webhook-receiver` and `webhook-receiver` (`fastapi>=0.162.0`, `httpx2`).
   - Run full unit and integration test suites.
3. **Phase 3: Go Monorepo Alignment**:
   - Update root `.go-version` and `platform/go-microservices/Makefile` to `1.27.3`.
   - Update `platform/go.mod` and service `go.mod` files to `go 1.27.3`, `go.temporal.io/sdk v1.50.0`, `franz-go v1.22.2`.
   - Run `go mod tidy` and `make test-unit`.
4. **Phase 4: Node / MCP Router Alignment**:
   - Update `@modelcontextprotocol/sdk` to `1.32.2` and `typescript` to `^7.0.2` in `platform/mcp-router`.
   - Run `pnpm -r build` and `pnpm -r test`.
5. **Rollback Strategy**:
   - Manifest edits are committed atomically per repository. If any tier fails post-upgrade verification, revert the specific Git commit and re-lock.
