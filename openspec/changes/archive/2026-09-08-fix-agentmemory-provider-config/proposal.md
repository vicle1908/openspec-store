## Context

The agentmemory runtime uses the shopapikey-backed OpenAI-compatible endpoint `https://api.phanmemvip.shop/v1`, model alias `fable-5`, and 90-second LLM timeouts. The server is launchd-managed and uses the iii engine with a 180-second invocation timeout. Recent 502 responses and engine timeouts have caused repeated summarization and consolidation failures, while observation capture and session completion must remain available.

## Goals / Non-Goals

**Goals:**

- Make provider endpoint/model configuration explicit and internally consistent.
- Bound LLM and engine work so provider failures cannot exhaust the local memory runtime.
- Keep session-end persistence and observation capture available when LLM work fails.
- Provide a reversible, backup-first rollout with direct provider and session-end probes.

**Non-Goals:**

- Do not change Claude Code, Hermes, Codex, pi, or MCP client ownership boundaries.
- Do not replace the shopapikey provider with another provider in this change.
- Do not modify agentmemory source code or the persistent state database.
- Do not expose API keys in logs, diagnostics, specs, or verification artifacts.
- Do not commit `~/.agentmemory` runtime files or probe payloads to this store.

## What Changes

This is an operational configuration change. Implementation acts on the user-managed agentmemory runtime configuration outside the store; this change records the contract, rollout, rollback, and evidence requirements only.

- Normalize `OPENAI_BASE_URL`, `OPENAI_MODEL`, `OPENAI_TIMEOUT_MS`, and `AGENTMEMORY_LLM_TIMEOUT_MS` in `~/.agentmemory/.env`.
- Set `workers[iii-http].config.default_timeout` in `/Users/androidteam/Library/Application Support/agentmemory/iii-config.yaml` to 75000 ms, which is the config path passed by the launchd-managed iii process. Keep `~/.agentmemory/iii-config.yaml` aligned as a legacy reference.
- Preserve feature flags, local embeddings, credential source, and persistent state.
- Restart only `com.agentmemory.server` through launchd and verify session-end resilience.

## Capabilities

### New Capabilities

- `agentmemory/provider-stability`: runtime provider settings and timeout behavior that protect summarization and consolidation under unstable LLM conditions.

### Modified Capabilities

- `developer-memory`: align the installed agentmemory runtime behavior with the documented Hermes/shopapikey provider path so local developer memory remains functional and consistent.

## Impact

- User-managed runtime files: `~/.agentmemory/.env` and `~/.agentmemory/iii-config.yaml`.
- Rollback references: `~/.agentmemory/.env.bak` and timestamped pre-change backup.
- Launchd service `com.agentmemory.server` and iii runtime behavior.
- Session memory summarization behavior for configured clients.
- OpenSpec delta specs and redacted verification evidence in the operator's local evidence location.

## Verification

- Review a redacted configuration diff against the pre-change backup.
- Probe `https://api.phanmemvip.shop/v1/chat/completions` using the existing key helper without logging the key.
- Restart `com.agentmemory.server`, confirm health, and verify `POST /agentmemory/session/end` returns HTTP 200 with `success=true`.
- Exercise provider failure isolation and verify observation capture/session completion remain available.
