## Why

The agentmemory session-end hook was reported failing with `Hook cancelled`, and provider logs show repeated 502 gateway errors plus long timeouts against the configured LLM endpoint. The runtime already targets the shopapikey provider, but its timeout posture allows unstable upstream work to occupy the iii engine for too long.

## Decisions

### 1. Keep the OpenAI-compatible shopapikey endpoint

The runtime SHALL continue using `https://api.phanmemvip.shop/v1` and the existing credential source. An Ollama fallback is not selected because it changes model behavior and introduces a new local availability prerequisite.

### 2. Normalize the model alias at the runtime boundary

Set `OPENAI_MODEL=fable-5` and validate it with a small non-sensitive chat probe. The probe checks HTTP status, latency, and response shape only; it does not persist prompts or print credentials.

### 3. Use explicit bounded timeouts

Set both `OPENAI_TIMEOUT_MS` and `AGENTMEMORY_LLM_TIMEOUT_MS` to `60000`. Set `workers[iii-http].config.default_timeout` in `/Users/androidteam/Library/Application Support/agentmemory/iii-config.yaml` to `75000` ms, the path passed by the launchd-managed iii process. Keep `~/.agentmemory/iii-config.yaml` aligned as a legacy reference. The provider request therefore expires before the engine invocation ceiling, while the engine remains bounded and does not retain work for the previous 180-second period. Retries are not added because repeated retries amplify upstream 502/rate-limit pressure.

### 4. Preserve asynchronous failure isolation

Session-end persistence remains independent from summarization and consolidation. Provider failure is logged and returned as a failed background operation; it must not prevent the session-end endpoint from acknowledging persisted session state.

### 5. Apply changes transactionally with rollback

Before editing runtime configuration, copy `~/.agentmemory/.env` to a timestamped backup and update `~/.agentmemory/.env.bak`, preserving existing `.env.pre-change`. Write configuration atomically, restart the launchd-managed server, and run probes. If startup or probes fail, restore the backup and restart again. No state database migration is required.

## Runtime ownership boundary

OpenSpec artifacts are stored in `openspec-store`; runtime configuration is user-managed under `~/.agentmemory`. Applying this change requires the operator to execute the tasks against the runtime. Runtime files, credentials, memory payloads, and raw probe bodies SHALL NOT be committed to the store.

## Risks / Trade-offs

- Provider remains unavailable: session summaries may fail, but observation capture and session completion remain available; logs provide the failure reason.
- Timeout too short for large summaries: prefer later reprocessing over increasing the synchronous hook budget.
- LaunchAgent restart interrupts in-flight work: perform backup and probes before restart, and rely on persisted observations plus the rollback copy.
- Existing config is user-managed: preserve feature flags, embeddings, credential source, and unrelated keys; never print or rewrite secret values.

## Migration Plan

1. Capture a redacted current configuration and create a timestamped `.env` backup.
2. Update only endpoint/model/timeout settings covered by the delta spec.
3. Update iii `default_timeout` to `75000` ms and validate YAML.
4. Restart `com.agentmemory.server` through launchd; do not kill unrelated MCP clients.
5. Probe `v1/chat/completions` using the existing key helper without logging the key.
6. Probe `POST http://127.0.0.1:3111/agentmemory/session/end` with `Content-Type: application/json` and body `{"sessionId":"openspec-probe-<timestamp>"}`; add the bearer secret only when configured, and verify HTTP 200 plus `success=true`.
7. Run a provider-failure isolation test and review fresh logs for successful observation capture/session completion.
8. Roll back the timestamped backup and restart if any gate fails.
