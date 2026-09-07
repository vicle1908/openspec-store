## Why

The agentmemory session-end hook was reported failing with `Hook cancelled`, and the provider logs show repeated 502 gateway errors plus long timeouts against the configured LLM endpoint. Investigation showed the underlying `OPENAI_BASE_URL`, model alias, and timeout settings could be tightened so summarization, consolidation, and graph extraction stop collapsing during provider instability.

## What Changes

- Normalize the LLM provider configuration used by agentmemory so the provider name, base URL, and model alias match the intended shopapikey-backed endpoint.
- Adjust provider timeout and job-throttling posture so long-running summarization or consolidation tasks do not hold server resources while the upstream provider is unstable.
- Preserve current feature flags and embeddings settings unless a change is required to stop the active failure mode.

## Capabilities

### New Capabilities

- `agentmemory/provider-stability`: runtime provider settings and timeout behavior that protect summarization and consolidation under unstable LLM conditions.

### Modified Capabilities

- `developer-memory`: align the installed agentmemory runtime behavior with the documented Hermes/shopapikey provider path so local developer memory remains functional and consistent.

## Impact

- `~/.agentmemory/.env`
- `~/.agentmemory/.env.bak` / `.env.pre-change` as reference/current configs
- `iii-config.yaml` timeout defaults
- agentmemory server (`iii`) runtime behavior
- Claude Code / Hermes / Codex / pi session memory summarization behavior
- OpenSpec delta spec for the modified capability

## Verification

- Config diff reviewed against existing backup files
- Direct provider probe against the configured `v1/chat/completions` endpoint
- After implementation: restart `com.agentmemory.server`, confirm `POST /agentmemory/session/end` succeeds, and fresh logs show successful summarization attempts
