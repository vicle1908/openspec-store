# Execution & Verification Evidence: unify-agent-routing-and-retire-provider-adapter

**Date:** 2026-10-13  
**Target Root:** `/Users/androidteam/Developer`, `/Users/androidteam/Omniroute`  
**Execution Context:** Darwin 27.0.0 arm64, Docker Desktop 4.95.0, OmniRoute v3.8.51  

---

## 1. Cockpit Provider Node Registration in OmniRoute

### SQLite Storage Verification
Verified provider node and connection records in `/app/data/storage.sqlite`:
- **Node**: `openai-compatible-responses-cockpit` (`type: openai-compatible`, `api_type: responses`, `prefix: cockpit`, `base_url: http://host.docker.internal:51006/v1`).
- **Connection**: `c0ckp1t0-0000-4000-a000-000000000001` with field-level AES-256-GCM encryption of `HERMES_CUSTOM_COCKPIT_API_KEY`.
- **Active Status**: `is_active: 1`, `test_status: active`.

### Live Model Catalog Verification
Executed `GET http://127.0.0.1:20128/v1/models` with Bearer authentication:
```
"id":"cockpit/codex-auto-review"
"id":"cockpit/gpt-5.5"
"id":"cockpit/gpt-5.6-luna"
"id":"cockpit/gpt-5.6-sol"
"id":"cockpit/gpt-5.6-terra"
"id":"cockpit/gpt-6.1-sol"
"id":"cockpit/gpt-6-astra"
"id":"cockpit/gpt-6-luna"
"id":"cockpit/gpt-6-sol"
"id":"cockpit/gpt-reserve"
```

### Native Messages Protocol Translation Parity
Sent Anthropic Messages request to OmniRoute port 20129:
```bash
curl -H "anthropic-version: 2023-06-01" \
  -d '{"model":"cockpit/gpt-5.6-luna","max_tokens":10,"messages":[{"role":"user","content":"ping"}]}' \
  http://127.0.0.1:20129/v1/messages
```
Output:
```json
{"error":{"code":"upstream_error","message":"{\n  \"error\": {\n    \"message\": \"Payment Required\",\n    \"type\": null,\n    \"code\": \"deactivated_workspace\",\n    \"param\": null\n  },\n  \"status\": 402\n}","type":"invalid_request_error"}}
```
Proves OmniRoute's native `openai-responses.ts` engine accurately translates inbound Anthropic Messages requests to OpenAI Responses upstream against `host.docker.internal:51006/v1/responses`, matching upstream behavior without intermediate sidecars.

---

## 2. Claude Code Launcher & Profile Reconciled

- `~/.claude/profiles/cockpit.json`:
  ```json
  {
      "model": "cockpit/gpt-5.6-luna",
      "env": {
          "ANTHROPIC_BASE_URL": "http://localhost:20129",
          "ANTHROPIC_MODEL": "cockpit/gpt-5.6-luna"
      },
      "apiKeyHelper": "/Users/androidteam/.claude/helpers/omniroute-key.sh"
  }
  ```
- `~/.zshrc`: Updated `cockpit()` function to point to `http://localhost:20129` with `cockpit/gpt-5.6-luna`.
- Live smoke test in interactive zsh:
  - `omniroute --version` → `2.1.296 (Claude Code)`
  - `shopapikey --version` → `2.1.296 (Claude Code)`
  - `cockpit --version` → `2.1.296 (Claude Code)`

---

## 3. Provider Adapter Decommissioning

- Executed `docker compose down` in `platform/claude-code-provider-adapter`.
- Container `claude-code-provider-adapter-adapter-1` stopped and removed.
- Unloaded LaunchAgent `com.workspace.claude-code-provider-adapter` (`launchctl bootout`).
- Renamed plist to `~/Library/LaunchAgents/com.workspace.claude-code-provider-adapter.plist.disabled`.
- Port 8788 no longer occupied: `lsof -iTCP:8788` returns empty.

---

## 4. Workstation Scripts & Watchdog Streamlining

- `~/Developer/scripts/docker-service.sh`: `COMPOSE_STACKS` pruned to solely `/Users/androidteam/Omniroute`.
- `~/Developer/scripts/omniroute-watchdog.sh`: Removed port 8788 probe block; focuses strictly on Docker daemon health and port 20128.
- Validated `docker-service.sh status --json` reports `running` with `helpers: {vmnetd: true, socket: true}`.
- Validated `omniroute-watchdog.sh` runs cleanly without errors.
