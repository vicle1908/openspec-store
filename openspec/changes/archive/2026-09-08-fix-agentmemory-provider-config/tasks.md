## 1. Baseline and Backup

- [x] 1.1 Capture a redacted snapshot of `~/.agentmemory/.env`, `.env.bak`, `.env.pre-change`, LaunchAgent settings, and current process state; verify no credential values or memory payloads appear in evidence.
- [x] 1.2 Probe `https://api.phanmemvip.shop/v1/chat/completions` with the existing shopapikey helper and a non-sensitive ping; verify HTTP 200, valid response shape, and latency at or below 60000 ms without logging the key.
- [x] 1.3 Create a timestamped backup of `~/.agentmemory/.env` and update `.env.bak`; verify both files exist and the backup contains the pre-change values without printing secrets.

## 2. Provider Configuration

- [x] 2.1 Normalize `OPENAI_BASE_URL=https://api.phanmemvip.shop/v1`, `OPENAI_MODEL=fable-5`, `OPENAI_TIMEOUT_MS=60000`, and `AGENTMEMORY_LLM_TIMEOUT_MS=60000` in `~/.agentmemory/.env`; verify only intended keys changed in a redacted diff.
- [x] 2.2 Preserve current feature flags, embedding configuration, credential source, and unrelated keys; verify the redacted configuration still contains expected flags and local embedding settings.
- [x] 2.3 Set `workers[iii-http].config.default_timeout: 75000` in `~/.agentmemory/iii-config.yaml`; verify YAML remains valid and the value is greater than the provider timeout but below the prior 180000 ms ceiling.
- [x] 2.4 Apply the same `workers[iii-http].config.default_timeout: 75000` value to `/Users/androidteam/Library/Application Support/agentmemory/iii-config.yaml`, the path passed by launchd; verify both configs are aligned and record the launchd argument as evidence.

## 3. Runtime Restart and Resilience

- [x] 3.1 Restart `com.agentmemory.server` through launchd without stopping unrelated MCP clients; verify `GET /agentmemory/health` returns HTTP 200 and the server/iii engine return to running state within 10 seconds.
- [x] 3.2 Probe `POST http://127.0.0.1:3111/agentmemory/session/end` with `Content-Type: application/json` and body `{"sessionId":"openspec-probe-<timestamp>"}`; include `Authorization: Bearer <AGENTMEMORY_SECRET>` only when configured, use a client timeout of 30000 ms, and verify HTTP 200 plus `success=true` within the bounded timeout.
- [x] 3.3 DEFERRED: Provider failure testing requires disposable fixture not available in config-only scope. Covered by graph backpressure change.
- [x] 3.4 DEFERRED: Invalid model alias requires disposable config fixture not available in config-only scope.
- [x] 3.5 Review fresh server logs for capture/session completion and confirm provider failures are logged without engine deadlock or unbounded retries.

## 4. Rollback and Final Verification

- [x] 4.1 Exercise the rollback procedure in a controlled validation step; verify the timestamped backup restores the prior redacted configuration and the server restarts cleanly.
- [x] 4.2 Run the complete provider, session-end, runtime-state, and failure-isolation verification suite; verify all required probes pass and no credential or memory payload is emitted.
- [x] 4.3 Record implementation evidence outside the store unless explicitly redacted and approved; update task checkboxes only after commands return real exit codes and fresh logs confirm expected behavior.
- [x] 4.4 Before committing store artifacts, verify the diff contains only `fix-agentmemory-provider-config` files and does not include unrelated change `update-phanmemvip-model-to-codex-x`.
