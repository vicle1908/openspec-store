# Tasks

## 1. Tier 0 & Tier 1 Foundation SDK Upgrades (Python)

- [ ] 1.1 Update `shb/shb-core` and `tdt/tdt-core` manifests to latest dependencies (`pydantic>=2.14.2`, `psycopg[binary,pool]>=3.3.8`, `httpx>=0.28.1`) and verify `uv lock --upgrade && uv run python -m pytest tests/ -q` passes
- [ ] 1.2 Update Tier 1 shared subsystems (`shb-tools`, `shb-ai-harness-skills`, `shb-agent-skills`, `tdt-sheets`, `jira-skill`) to align with updated Tier 0 SDKs and verify unit tests pass

## 2. Tier 2 Core Agent Orchestration Frameworks (Python)

- [ ] 2.1 Update `shb/shb-agent-core` and `tdt/agent-core` to `pydantic-ai>=2.66.0` and `redis>=8.1.0`; verify `uv lock --upgrade && uv run python -m pytest tests/ -q` passes without legacy fallback shims
- [ ] 2.2 Update `tdt/tdt-observability` to `duckdb>=2.0.0` LTS; verify health poller, log aggregator, and store tests pass using asynchronous I/O
- [ ] 2.3 Update `shb/shb-observability` and `tdt/tdt-observability` to `opentelemetry-sdk>=1.45.2`; verify metric aggregation and OTLP collector tests pass

## 3. Tier 3 Leaf Services, Schedulers & Webhooks (Python)

- [ ] 3.1 Update `shb/shb-schedule` to `dbos>=3.4.0` with separate payload tables and async data sources; verify `uv lock --upgrade && uv run python -m pytest tests/ -q` passes
- [ ] 3.2 Update `shb/shb-agent-harness` and `tdt/agent-harness` to `pydantic-ai-harness>=0.66.0` and `langgraph>=1.2.19`; verify ticket planning state graphs pass all tests
- [ ] 3.3 Update `shb/shb-webhook-receiver` and `tdt/webhook-receiver` to `fastapi>=0.162.0` and `starlette>=1.10.0`, declaring `httpx2>=2.16.0` in dev dependency groups; verify webhook ingress tests pass with zero deprecation warnings
- [ ] 3.4 Update remaining leaf applications (`ops-automation-suite`, `shb-ai-review`, `ai-review`, `browser-cli`, `shb-browser-cli`, `shb-jira-tools`) and verify project test suites pass

## 4. Go Monorepo Toolchain & Dependency Alignment

- [ ] 4.1 Update root `.go-version`, `platform/go-microservices/Makefile` GO_VERSION, and `platform/go.mod` to `1.27.3`; verify toolchain alignment passes `make verify-go-version`
- [ ] 4.2 Update `platform/go.mod` and all 8 service `go.mod` files to `go.temporal.io/sdk v1.50.0`, `go.temporal.io/api v1.64.1`, and `twmb/franz-go v1.22.2`; run `go mod tidy` across all modules
- [ ] 4.3 Update Go tool directives (`staticcheck v0.8.2`, `buf v1.75.0`, `gofumpt v0.12.0`); execute `make test-unit` across the monorepo and verify 100% pass rate

## 5. Node / TypeScript MCP Router Alignment

- [ ] 5.1 Update `@modelcontextprotocol/sdk` to `1.32.2` and `typescript` to `^7.0.2` across `platform/mcp-router` (`apps/cli`, `packages/shared`, `packages/ui`, `packages/remote-api-types`); verify `pnpm -r build` succeeds
- [ ] 5.2 Update root devDependencies (`turbo ^2.11.10`, `prettier ^3.9.10`) in `platform/mcp-router/package.json` and verify `pnpm -r test` passes

## 6. Cross-Workspace Integration Verification & Hygiene

- [ ] 6.1 Execute cross-repo test verification across all updated Python, Go, and Node packages; verify zero root-level cache files (`.pytest_cache`, `.ruff_cache`)
- [ ] 6.2 Validate OpenSpec strict compliance via `openspec validate modernize-workspace-dependencies-q4-2026 --strict` and generate verification summary
