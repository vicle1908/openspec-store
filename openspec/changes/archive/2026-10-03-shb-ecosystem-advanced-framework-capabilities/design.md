# Design: SHB Ecosystem Advanced Framework Capabilities Integration

## Context
See `proposal.md` for motivation and scope. The SHB ecosystem runs on Python 3.14 with dependencies standardized to latest PyPI releases (`pydantic-ai>=2.53.0`, `langgraph>=1.2.12`, `fastapi>=0.142.2`, `mcp>=2.3.0`, `opentelemetry-api>=1.45.0`). The test baseline across all 12 repositories is 116/116 passing tests. This design details the architectural integration of advanced upstream framework features across 5 core repositories.

## Goals / Non-Goals

**Goals:**
- Expose all 10 registered banking tools to `shb-agent-core`'s Pydantic AI agent with dynamic parameter validation and schema generation.
- Implement self-correction using Pydantic AI `ModelRetry` for threshold violations (>50M VND maker-checker requirement).
- Separate prompt caching static instructions from per-turn dynamic dependencies via `@agent.instructions`.
- Add streaming execution (`run_stream`) producing partial completions.
- Implement file-backed `SqliteSaver` in `shb-agent-harness` at `~/.shb/harness.db` with graceful fallback to `MemorySaver`, plus an operator CLI resume command (`shb-harness resume`).
- Refactor `shb-mcp-servers` to use official `FastMCP` with resource templates (`shb://accounts/{id}/summary`) and compliance prompt templates.
- Add OpenTelemetry distributed trace context propagation and metric instruments in `shb-core` and `shb-observability`.
- Enhance `shb-core` configuration with `pydantic.SecretStr` for credentials.

**Non-Goals:**
- Introducing external non-loopback network calls.
- Modifying underlying NAPAS247 CRC or bank routing schemas.
- Deprecating existing CLI flags or test suites.

## Decisions

### 1. Unified Toolset Binding with ModelRetry Feedback
- **Decision**: In `shb_agent.agent.ShbAgent`, dynamically iterate over all tools in `ToolRegistry` (`banking_tools`, `vietqr_tools`, `biller_tools`) and bind them to `@self._agent.tool`. In tools requiring supervisor authorization (e.g. transfer >50M VND), raise `ModelRetry` when the token is missing, prompting the model to request supervisor authorization rather than aborting.
- **Rationale**: Elevates agent reasoning from hardcoded keyword heuristics to authentic ReAct tool selection with conversational error recovery.
- **Alternatives Considered**: Retaining manual `if "balance" in user_prompt` matching (rejected: defeats ReAct agent capabilities).

### 2. Dual Checkpointer Pattern in LangGraph Harness
- **Decision**: In `shb_harness.workflow.build_harness_graph`, initialize `SqliteSaver` pointing to `~/.shb/harness.db` when available, falling back to in-memory `MemorySaver` during unit test runs or when the directory is unwritable. Expose a CLI `resume` command using `graph.invoke(Command(resume=...), config={"configurable": {"thread_id": ticket_id}})`.
- **Rationale**: Enables human operators to inspect paused tickets at `PLAN_REVIEW` and resume execution seamlessly in subsequent terminal sessions.
- **Alternatives Considered**: In-memory only (rejected: loses state between CLI invocations).

### 3. Native FastMCP Migration
- **Decision**: Migrate `shb_mcp.server.ShbMcpServer` from hand-rolled JSON-RPC 2.0 to `mcp.server.fastmcp.FastMCP`. Expose tools via `@mcp.tool()`, resources via `@mcp.resource("shb://...")`, and prompts via `@mcp.prompt()`.
- **Rationale**: Leverages the official MCP Python SDK v2.3.0 for standard transport negotiation and auto-generated tool/resource/prompt schemas.
- **Alternatives Considered**: Custom JSON-RPC dictionary parser (rejected: high maintenance, non-standard error codes).

### 4. OpenTelemetry Trace Context Propagation
- **Decision**: Use `opentelemetry-api` to provide standard trace context injection (`traceparent`) on outgoing banking client requests and expose tracer spans around ReAct cycles and harness stage execution.
- **Rationale**: Ensures complete distributed visibility when tracing across webhook ingress, planning harness, and agent tool execution.

## Risks / Trade-offs

- **[Risk: FastMCP async event loop conflicts in synchronous CLI commands]** → FastMCP provides both synchronous helper methods and async runners; ensure Typer CLI executes within proper `anyio` or `asyncio.run` boundaries.
- **[Risk: SqliteSaver lock contention during concurrent test runs]** → Use `:memory:` or temporary databases during unit tests, using `~/.shb/harness.db` strictly for operator CLI execution.
- **[Risk: Pydantic SecretStr serialization in CLI tables]** → Explicitly use `.get_secret_value()` when masked display is needed or print `********` for security.

## Migration Plan

1. **Phase 1: Core Foundation & Telemetry**: Add `SecretStr` masking and OpenTelemetry tracer helpers in `shb-core` and metric instruments in `shb-observability`.
2. **Phase 2: Agent Core Modernization**: Implement dynamic toolset binding, `ModelRetry`, `@agent.instructions`, and streaming in `shb-agent-core`.
3. **Phase 3: Planning Harness Persistence**: Add `SqliteSaver`, `Command` dynamic routing, and `shb-harness resume` in `shb-agent-harness`.
4. **Phase 4: FastMCP Server Integration**: Refactor `shb-mcp-servers` to `FastMCP` with tools, resources, and prompt templates.
5. **Phase 5: Ecosystem Verification**: Run full test suites across all 12 repos, verify CLI commands, validate strictly with OpenSpec.
