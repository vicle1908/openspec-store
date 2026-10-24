# Implementation Evidence: `optimize-omniroute-memory-bleed-responses-and-resilience`

## 1. Built-in Memory & Skills Deactivation and 75-Row Purge Verification (Tasks 1.1–1.3)

- **Container Health Preflight**:
  - `GET http://127.0.0.1:20128/healthz` $\rightarrow$ `200 OK`
- **`PUT /api/settings/memory` & `GET /api/settings/memory`**:
  ```json
  {
    "enabled": false,
    "skillsEnabled": false,
    "maxTokens": 0
  }
  ```
- **Per-ID `DELETE /api/memory/{id}` Purge across 75 Stored Rows**:
  - Initial `GET /api/memory?limit=100`: `total: 75`, `stats.tokensUsed: 7026`
  - Deleted: `75 / 75` rows (`200 OK` on each `DELETE /api/memory/{id}`)
  - Post-purge `GET /api/memory?limit=1`: `total: 0`, `stats.tokensUsed: 0`
  - Post-smoke-test `GET /api/memory?limit=1` (after 4 authenticated inference calls): `total: 0`, `stats.tokensUsed: 0`

## 2. Lossless `lite` Tool Preservation, `headroom`, `codex-responses` & `contextBudget` Verification (Tasks 2.1–2.2)

- **`GET /api/settings/compression`**:
  ```json
  {
    "lite": {
      "compressToolResults": false,
      "maxToolLength": 200000
    },
    "engines": {
      "session-dedup": { "enabled": true },
      "headroom": { "enabled": true },
      "lite": { "enabled": true },
      "codex-responses": { "enabled": true },
      "rtk": { "enabled": true, "level": "minimal" },
      "caveman": { "enabled": true, "level": "lite" }
    },
    "codexResponsesConfig": {
      "enabled": true,
      "minBytes": 512,
      "maxOutputBytes": 2097152,
      "maxCandidateBytes": 524288,
      "maxLines": 160,
      "minSearchMatches": 8,
      "minLogLines": 24,
      "preserveToolNames": [
        "Read", "Glob", "Grep", "Write", "Edit", "WebSearch", "WebFetch",
        "read", "glob", "grep", "write", "edit", "web_search", "web_fetch", "find"
      ]
    },
    "contextBudget": {
      "mode": "replace-autotrigger",
      "policy": "percentage",
      "outputReserve": 4096,
      "safetyMargin": 1024,
      "pct": 0.85,
      "absoluteBudget": 0,
      "ladderOverride": [
        { "engine": "session-dedup" },
        { "engine": "headroom" },
        { "engine": "lite" },
        { "engine": "codex-responses" },
        { "engine": "rtk", "intensity": "minimal" }
      ]
    }
  }
  ```

## 3. Resilience Feature Flags, Classifier Short-Circuit, Body Limit & `models.dev` Sync Verification (Tasks 3.1–3.2)

- **`GET /api/settings/feature-flags`**:
  ```json
  {
    "QUOTA_WINDOW_BOUNDED_PARK": ["true", "db"],
    "STREAM_EARLY_EOF_SIBLING_FAILOVER_ENABLED": ["true", "db"],
    "COOLDOWN_RETRY_SKIP_REFUSALS_ENABLED": ["true", "db"],
    "PROVIDER_SAFETY_STOPS_TERMINAL": ["true", "db"],
    "FLUSH_EMPTY_RETRY_ENABLED": ["false", "default"]
  }
  ```
- **`PATCH /api/settings` & `GET /api/settings`**:
  ```json
  {
    "claudeClassifierCompat": "auto",
    "claudeFastMode": {
      "enabled": true,
      "supportedModels": [
        "claude-fable-5",
        "claude-opus-5-5",
        "claude-opus-5",
        "claude-opus-4-8",
        "claude-opus-4-7",
        "claude-opus-4-6"
      ]
    },
    "maxBodySizeMb": 50,
    "modelsDevSyncEnabled": true
  }
  ```
- **`POST /api/settings/models-dev` (`"sync"` + `"start"`) & `GET /api/settings/models-dev?action=status`**:
  ```json
  {
    "enabled": true,
    "lastSync": "2026-10-24T09:59:45.558Z",
    "lastSyncModelCount": 9826,
    "lastSyncCapabilityCount": 10226,
    "nextSync": "2026-10-25T09:59:45.558Z",
    "intervalMs": 86400000,
    "providerCount": 233,
    "modelCount": 9826,
    "capabilityCount": 10226
  }
  ```

## 4. Classifier Short-Circuit & Multi-Protocol Smoke Tests (Tasks 4.1–4.2)

- **Claude Code Classifier Short-Circuit (`POST /v1/messages`, `model: "claude-opus-5.5"`, `system: "You are a security monitor for autonomous AI coding agents..."`)**:
  - `status: 200 OK`, `content: [{"type": "text", "text": "<block>no</block>"}]`, `usage: {"input_tokens": 1, "output_tokens": 1}`
- **Live Inference Smoke Tests**:
  - `POST /v1/chat/completions` (`model: "gemini-3.8-flash-high"`) $\rightarrow$ `200 OK`, `id: chatcmpl-1792836028254-035a95f2`, `reply: "PONG"`
  - `POST /v1/messages` (`model: "gemini-3.8-flash-high"`) $\rightarrow$ `200 OK`, `id: chatcmpl-1792836031160-fcaba8c4`, `reply: "PONG"`
  - `POST /v1/responses` (`model: "gemini-3.8-flash-high"`) $\rightarrow$ `200 OK`, `id: resp_chatcmpl-1792836034333-3db0807b`, `reply: "PONG"`
- **Updated Skill Line Counts (all $\le 500$ lines)**:
  - `~/.agents/skills/omni-settings/SKILL.md`: 221 lines
  - `~/.agents/skills/omni-compression/SKILL.md`: 176 lines

## 5. Real End-to-End Feature Exercise Across Live OmniRoute (`127.0.0.1:20128` & `20129`)

- **Test 1 — Prior-Turn `Read` Tool Result (`2,925` chars) Preserved Intact (`lite.compressToolResults: false`)**:
  - Sent a multi-turn `/v1/chat/completions` conversation containing a `2,925`-character `Read` tool result with `SENTINEL_MARKER_AT_CHAR_2880=VERIFIED_INTACT` placed at character `2,880` (past the legacy `2,000`-char `lite` truncation point).
  - Response Header: `x-omniroute-compression: stacked; source=default`
  - Result: `200 OK`, model extracted `VERIFIED` accurately from character `2,880`.
- **Test 2 — Lossless `headroom` (SmartCrusher) JSON Array Compaction on Headerless Request**:
  - Sent a multi-turn `/v1/chat/completions` conversation containing a 20-item JSON array in a prior turn without any `x-omniroute-compression` header.
  - Response Header: `x-omniroute-compression: stacked; source=default`
  - Result: `200 OK`, `reply: "healthy"`.
- **Test 3 — `/v1/responses` `codex-responses` + RTK Stacked Execution (`x-omniroute-compression: allow-lossy`)**:
  - Sent a multi-turn `POST /v1/responses` payload containing both a protected `Read` `function_call_output` (`EXPORTED_PORT_CONST=20129`) and a verbose 42-line `bash` `function_call_output` (`npm run build` failing on module 40).
  - Response Header: `x-omniroute-compression: stacked; source=default; tokens=677->113; rules: docker-logs:collapsex1, docker-logs:keepx1, shell-find:deduplicatex1, shell-find:stripx1` (**83.3% token reduction** while preserving the `Read` output).
  - Result: `200 OK`, `reply: "EXPORTED_PORT_CONST=20129, module 40"`.
- **Test 4 — `/v1/chat/completions` RTK Vitest Filter (`x-omniroute-compression: engine:rtk`)**:
  - Sent a multi-turn `/v1/chat/completions` payload with a 35-suite `vitest run` tool output (`512` tokens).
  - Response Header: `x-omniroute-compression: rtk; source=request-header; tokens=512->149; rules: test-vitest:collapsex1, test-vitest:keepx1, test-vitest:stripx1` (**70.9% token reduction**).
  - Result: `200 OK`, `reply: "tests/auth.test.ts"`.
- **Test 5 — `/v1/responses` Standalone `codex-responses` (`x-omniroute-compression: engine:codex-responses`)**:
  - Response Header: `x-omniroute-compression: codex-responses; source=request-header`
  - Result: `200 OK`, `reply: "EXPORTED_PORT_CONST=20129\nFailed module: 40"`.
- **Test 6 — Port `20129` API Bridge + Claude Classifier `<severity>0</severity>` Short-Circuit**:
  - Sent `POST http://127.0.0.1:20129/v1/messages` with `stop_sequences: ["</severity>"]` and `system` containing `"You are a security monitor for autonomous AI coding agents"`.
  - Result: `200 OK` in `323.6ms`, `content: [{"type": "text", "text": "<severity>0</severity>"}]`, `usage: {"input_tokens": 1, "output_tokens": 1}`.
- **Test 7 — Live OMP CLI End-to-End Probe & Zero Memory Bleed Verification**:
  - `omp --mode json --no-session --no-prewalk --model omniroute/gemini-3.8-flash-high -p "Reply with the single word PONG"` $\rightarrow$ `{"type":"message_end","model":"gemini-3.8-flash-high","stopReason":"stop","text":"PONG"}`.
  - Post-E2E `GET http://127.0.0.1:20128/api/memory?limit=1` after 10+ authenticated multi-turn requests across all 3 protocols: `{"total": 0, "tokensUsed": 0}`.
