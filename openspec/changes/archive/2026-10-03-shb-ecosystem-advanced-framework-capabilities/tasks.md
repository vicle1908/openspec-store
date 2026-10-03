# Tasks

## 1. Core Foundation and Telemetry Enhancements

- [x] 1.1 Implement `SecretStr` masking and OpenTelemetry tracer propagation in `shb-core`, and verify with `uv run pytest tests/`
- [x] 1.2 Implement OpenTelemetry metric counters (`shb_agent_tool_calls_total`) and tracer integration in `shb-observability`, and verify with `uv run pytest tests/`

## 2. Pydantic AI Agent Core Advanced Capabilities

- [x] 2.1 Dynamically bind all 10 banking tools (balance, statement, VietQR, biller, beneficiary, transfer, AML compliance) to `@self._agent.tool` in `shb-agent-core`
- [x] 2.2 Implement `ModelRetry` in domain transfer tools for maker-checker supervisor token requirement and parameter violations
- [x] 2.3 Separate static instructions from per-turn runtime dependencies using `@agent.instructions` and add streaming execution (`run_stream`)
- [x] 2.4 Verify `shb-agent-core` with `uv run pytest tests/` and `uv run shb-agent tools-list`

## 3. LangGraph Planning Harness Persistence and Resume

- [x] 3.1 Implement file-backed `SqliteSaver` in `shb-agent-harness` targeting `~/.shb/harness.db` with graceful fallback to `MemorySaver`
- [x] 3.2 Implement `shb-harness resume <ticket_id>` CLI command using LangGraph `Command(resume=...)` for human-in-the-loop review gating
- [x] 3.3 Verify `shb-agent-harness` with `uv run pytest tests/` and `uv run shb-harness list-stages`

## 4. FastMCP SDK Migration in MCP Servers

- [x] 4.1 Migrate `shb-mcp-servers` from custom JSON-RPC to official FastMCP (`mcp.server.fastmcp.FastMCP` / `MCPServer`)
- [x] 4.2 Register MCP resource templates (`shb://accounts/{account_number}/summary`) and compliance prompt templates (`audit-ticket-compliance`)
- [x] 4.3 Verify `shb-mcp-servers` with `uv run pytest tests/` and `uv run shb-mcp list-tools`

## 5. Ecosystem Verification and OpenSpec Lifecycle Closure

- [x] 5.1 Run full test suite across all 12 repositories (`uv run pytest -q -p no:cacheprovider`) and assert 100% pass rate
- [x] 5.2 Verify clean lint and type checks across all 12 repositories (`ruff check src/` and `mypy src/`)
- [x] 5.3 Validate OpenSpec change strictly using `openspec validate --all --strict --store openspec-store`
