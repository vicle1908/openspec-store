# Verification Evidence: `align-omniroute-official-runtime-standards`

**Date**: 2026-10-24
**Store**: `/Users/androidteam/Developer/platform/openspec-store`

## 1. Root-Cause Forensic Evidence (`call_logs` & Live Lockouts Before Fix)

- **Failed Call 1 (`338764b8-1cd7-4946-b789-ee5dad4c5073`)**:
  - `call_logs.id`: `d1284bad-2a92-47d8-8999-0c650395e3c8` (`2026-10-24T11:28:21.690Z`, `POST /v1/responses`, `gemini-4-argon`, 419 items ending on `role: "model"`)
  - Upstream Error: `[400]: Antigravity upstream error (400): Requests ending with a model turn are not supported.`
- **Failed Call 2 (`0532bad4-2486-4286-8f06-510e9c678620`)**:
  - `call_logs.id`: `c05ad91f-6975-4c09-ad9c-e095d29f5376` (`2026-10-24T11:28:26.045Z`, fallback retry on 2nd Ultra account)
  - Upstream Error: `[400]: Antigravity upstream error (400): Requests ending with a model turn are not supported.`
- **Resulting Pre-Fix 1-Hour Lockouts (`GET /api/rate-limits`)**:
  - `{"provider":"agy","connectionId":"338764b8-1cd7-4946-b789-ee5dad4c5073","model":"family:gemini","reason":"model_capacity","failureCount":1,"lockedAt":"2026-10-24T11:28:21.700Z","until":1792844901700}`
  - `{"provider":"agy","connectionId":"0532bad4-2486-4286-8f06-510e9c678620","model":"family:gemini","reason":"model_capacity","failureCount":1,"lockedAt":"2026-10-24T11:28:26.053Z","until":1792844906053}`

## 2. Task 1.1 & 1.2 Verification (Compose Override & Entrypoint Chunk Normalization)

- **Clean Upstream Git Working Tree**:
  - Command: `git -C /Users/androidteam/Omniroute status --untracked-files=no`
  - Output: `On branch main / Your branch is up to date with 'origin/main'. / nothing to commit`
- **Container Runtime Inspection**:
  - Command: `docker inspect omniroute --format 'StopTimeout={{.Config.StopTimeout}} SlowMs={{range .Config.Env}}{{if eq . "OMNIROUTE_SQLITE_SLOW_MS=200"}}{{.}}{{end}}{{end}}'`
  - Output: `StopTimeout=40 SlowMs=OMNIROUTE_SQLITE_SLOW_MS=200`
- **Idempotent Entrypoint Normalization (`--patch-only`)**:
  - Command: `docker exec omniroute /app/container-entrypoint-compat.sh --patch-only`
  - Output: `already_ok`
  - In-container chunk verification:
    - `7449.js PATCH_VERIFIED /^gemini-(?:[34](?:\.\d+)?(?:-[a-z0-9-]+)?|pro-agent)$/`
    - `37174.js PATCH_VERIFIED /^gemini-(?:[34](?:\.\d+)?(?:-[a-z0-9-]+)?|pro-agent)$/`
    - `32946.js PATCH_VERIFIED /\bmodel(?!\s+turn\b).*not.*(?:available|found|supported|accessible)\b/i`
    - `32946.js PATCH_VERIFIED /\bmodel(?!\s+turn\b)\b[\s\S]{0,80}?\b(?:not\s+supported|unsupported|unknown|unavailable)\b/i`
    - `32946.js PATCH_VERIFIED ("antigravity"===ag(a)||"agy"===ag(a)?bz:ap)(a,b,c,d,e)`
    - `55661.js PATCH_VERIFIED /\bmodel(?!\s+turn\b).*not.*(?:available|found|supported|accessible)\b/i`

## 3. Task 2.1 & 2.2 Verification (Database Semantic Cache Alignment & Live Multi-Turn Probes)

- **Database Semantic Cache Alignment (`PATCH /api/settings/database`)**:
  - Output: `{"semanticCacheMaxSize":1000,"semanticCacheTTL":18000000}`
- **Multi-Turn Trailing-Assistant-Turn Inference Probes (All 4 Model x Endpoint Combinations)**:
  1. `POST http://127.0.0.1:20128/v1/chat/completions` (`model: "gemini-4-argon"`, ending on `role: "assistant"`):
     `{"id":"chatcmpl-1792844877627-e0784c98","model":"gemini-4-argon-high","reply":"PONG"}` (`HTTP 200`)
  2. `POST http://127.0.0.1:20128/v1/responses` (`model: "gemini-4-argon-high"`, ending on `role: "assistant"`):
     `{"id":"resp_chatcmpl-1792844886197-ab08c4a6","model":"gemini-4-argon-high","status":"completed","output_types":["message"]}` (`HTTP 200`)
  3. `POST http://127.0.0.1:20128/v1/chat/completions` (`model: "gemini-4-argon-high"`, ending on `role: "assistant"`):
     `{"endpoint":"chat/completions","model":"gemini-4-argon-high","reply":"PONG"}` (`HTTP 200`)
  4. `POST http://127.0.0.1:20128/v1/responses` (`model: "gemini-4-argon"`, ending on `role: "assistant"`):
     `{"endpoint":"responses","model":"gemini-4-argon-high","status":"completed"}` (`HTTP 200`)
- **Automated Unit & Integration Test Suites (`22/22` tests passing)**:
  - Command: `python3 -m unittest tests/test_omniroute_lock_and_watchdog.py tests/test_omniroute_cli_bridge.py tests/test_omniroute_typesafe_provider.py`
  - Output: `Ran 22 tests ... OK` (including fixture verification of all 4 `gemini-[34]` / `\bmodel(?!\s+turn\b)` / `("antigravity"===ag(a)||"agy"===ag(a)?bz:ap)` chunk replacements and `patched` $\rightarrow$ `already_ok` idempotency in `test_v3852_muse_wire_compat_and_updater_muse_catalog_and_backup_cleanup`).
- **Post-Probe Lockout & CLI Health Verification**:
  - `GET http://127.0.0.1:20128/api/resilience/model-cooldowns` $\rightarrow$ `{"items":[]}`
  - `GET http://127.0.0.1:20128/api/rate-limits` (`.lockouts`) $\rightarrow$ `[]`
  - `~/.local/bin/omniroute health --json` $\rightarrow$ `{"status":"healthy"}`
