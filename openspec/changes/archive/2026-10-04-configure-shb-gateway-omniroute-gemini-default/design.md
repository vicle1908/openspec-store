# Design

## Context

The SHB agent ecosystem relies on `shb-core` for unified environment loading and client factories, and `shb-agent-core` for the ReAct autonomous loop and tool integration.
Models are resolved dynamically via `resolve_model()` and `create_default_chain()`, backed by Pydantic AI's `OpenAIChatModel` pointing to an OpenAI-compatible gateway (`SHB_MODEL_GATEWAY_URL`, default `http://127.0.0.1:20128/v1`).
OmniRoute runs locally as a Docker container exposing port 20128, keyless on loopback.
Direct testing demonstrated that `gemini-3.8-flash-high` handles chat completions, reasoning tokens, and structured function calling reliably.

## Goals / Non-Goals

**Goals:**
- Transition the default model for SHB agent workloads to `gemini-3.8-flash-high`.
- Maintain full compatibility with `pydantic-ai>=2.51.0` ReAct loops and banking tool calling.
- Ensure all test suites pass without regressions.
- Keep the fallback chain functional (`gemini-3.8-flash-high` -> `Advance`).

**Non-Goals:**
- Reconfiguring OmniRoute routing profiles or upstream gateway keys.
- Changing model providers for other organizations (TDT, VDS).
- Modifying banking security policies (maker-checker, PAN masking, HMAC).

## Decisions

1. **Default Model Identification**:
   - Set `SHB_DEFAULT_MODEL=gemini-3.8-flash-high`.
   - Keep `SHB_MODEL_GATEWAY_URL=http://127.0.0.1:20128/v1`.
   - Keep `SHB_FALLBACK_MODEL=Advance`.

2. **Configuration Hierarchy**:
   - Code-level default in `shb_core.config.ShbSettings` changed from `fable-5` to `gemini-3.8-flash-high`.
   - Environment file `~/.shb/.env` updated to `SHB_DEFAULT_MODEL=gemini-3.8-flash-high`.
   - Template `~/.shb/.env.example` synchronized.

3. **Validation & Verification Strategy**:
   - `shb-core` unit tests updated to assert `gemini-3.8-flash-high`.
   - `shb-agent-core` model resolution and CLI inspected.
   - Pydantic AI live tool execution tested against OmniRoute.
