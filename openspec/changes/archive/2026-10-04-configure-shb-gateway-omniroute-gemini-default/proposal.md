# Proposal

## Why

The Saigon - Hanoi Bank (SHB) autonomous agent ecosystem (`shb-core`, `shb-agent-core`) previously defaulted its model gateway routing to `fable-5`. With OmniRoute active on loopback (`http://127.0.0.1:20128/v1`), `gemini-3.8-flash-high` provides superior latency, strong reasoning token emissions, and verified OpenAI-compatible function calling for autonomous banking ReAct loops and domain tools. Configuring OmniRoute with `gemini-3.8-flash-high` as the default provider across the SHB agent ecosystem establishes high-speed execution while retaining `Advance` in the fallback chain.

## What Changes

- Update `shb-core` configuration defaults (`SHB_DEFAULT_MODEL`) from `fable-5` to `gemini-3.8-flash-high` in `shb_core.config.ShbSettings`.
- Update `~/.shb/.env` and `~/.shb/.env.example` templates to reflect `SHB_DEFAULT_MODEL=gemini-3.8-flash-high`.
- Update unit and integration tests in `shb-core` to validate default model resolution to `gemini-3.8-flash-high`.
- Verify `shb-agent-core` model resolution and ReAct execution against the default chain backed by OmniRoute.

## Capabilities

### Modified Capabilities

- `shb-core-foundation`: update environment loading and default model configuration.
- `shb-agent-runtime`: update default model resolution and gateway connection scenarios to specify `gemini-3.8-flash-high`.

## Impact

- Affects `shb-core` default settings and `~/.shb/.env`.
- Affects `shb-agent-core` default agent execution when `chain` or `model` is omitted.
- Dependent on OmniRoute (`http://127.0.0.1:20128/v1`), verified keyless on loopback with active tool calling.
- No changes to banking client credentials or Jira/GitLab tokens.

## Non-Goals

- Modifying OmniRoute upstream configuration or Docker stack.
- Modifying fallback model target (`Advance`) or fallback chain mechanics in `FallbackModelChain`.
- Altering banking domain tool definitions or business logic.
