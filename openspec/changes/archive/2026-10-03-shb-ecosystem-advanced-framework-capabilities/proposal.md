# Proposal: SHB Ecosystem Advanced Framework Capabilities Integration

## Why
While dependencies across the 12 repositories in the Saigon - Hanoi Bank (`shb`) autonomous agent ecosystem have been upgraded to their latest stable releases (`pydantic-ai>=2.53.0`, `langgraph>=1.2.12`, `fastapi>=0.142.2`, `mcp>=2.3.0`), several core modules still rely on simplified shims or underutilize framework capabilities:
- `shb-agent-core` binds only 2 of 10 registered banking tools and uses keyword routing rather than dynamic model tool selection and `ModelRetry` self-correction.
- `shb-agent-harness` uses volatile in-memory checkpointing (`MemorySaver`) and lacks an operator CLI resume command for human-in-the-loop gates.
- `shb-mcp-servers` hand-rolls custom JSON-RPC request dispatching rather than using the official `FastMCP` SDK.
- `shb-observability` lacks distributed OpenTelemetry trace context propagation across the agent execution chain.
- `shb-core` uses flat settings without secret masking.

Integrating these native framework capabilities elevates runtime resilience, audit compliance, and multi-agent coordination.

## What Changes
- **Pydantic AI Full Toolset & Self-Correction**: Dynamically register all 10 banking tools (balance, statement, VietQR generation/parsing, biller presentment/payment, beneficiary verification, maker-checker transfer, AML sanction screening) to `@self._agent.tool`. Implement `ModelRetry` in domain tools to trigger model retry with validation feedback when transfer rules or parameters are violated. Separate cacheable static instructions from per-turn runtime dependencies (`@agent.instructions`). Add streaming execution (`run_stream`).
- **Durable Harness Checkpointing & Resume**: Implement file-backed `SqliteSaver` in `~/.shb/harness.db` (with graceful fallback to `MemorySaver`), enabling tickets to be resumed across sessions. Add `shb-harness resume <ticket_id> --action approve/reject` CLI command leveraging LangGraph `Command(resume=...)`.
- **FastMCP SDK Adoption**: Refactor `shb-mcp-servers` to use official `mcp.server.fastmcp.FastMCP`, exposing automatic Pydantic schema validation, resource templates (`shb://accounts/{id}/summary`), and compliance prompts (`audit-ticket-compliance`).
- **Distributed Tracing & Metrics**: Instrument `shb-core` and `shb-agent-core` with OpenTelemetry trace context propagation and domain metrics (`shb_agent_tool_calls_total`).
- **Structured Config & Secret Masking**: Enhance `shb-core` configuration with `pydantic.SecretStr` for sensitive keys and tokens.

## Capabilities

### Modified Capabilities
- `shb-agent-runtime`: Update agent runtime requirements to mandate dynamic registration of all domain banking tools, `ModelRetry` feedback loops, prompt caching separation, and streaming output generation.
- `shb-planning-harness`: Update harness requirements to enforce durable SQLite checkpointing and human-in-the-loop graph resumption.
- `shb-mcp-servers`: Update MCP server requirements to mandate official FastMCP implementation with resource and prompt templates.
- `shb-observability-telemetry`: Update observability requirements to enforce OpenTelemetry distributed trace propagation and domain metric tracking.
- `shb-core-foundation`: Update configuration foundation requirements to require secret masking (`SecretStr`) and structured settings models.

## Impact
- **Repositories**: `shb-core`, `shb-agent-core`, `shb-agent-harness`, `shb-mcp-servers`, `shb-observability`, `shb-tools`.
- **APIs & Runtime**: All existing CLI flags and external contracts remain backwards-compatible, while gaining streaming, durable resume, and standard MCP resource/prompt endpoints.
