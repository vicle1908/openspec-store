# Implementation Evidence: `optimize-omniroute-storage-retention-and-tool-safe-stack`

## 1. Database Retention, Usage Rollup Aggregation & Call-Log Artifact Caps Verification (Tasks 1.1–1.2)

- **`PATCH /api/settings/database` & `GET /api/settings/database`**:
  ```json
  {
    "retention": {
      "quotaSnapshots": 3,
      "compressionAnalytics": 7,
      "callLogs": 7,
      "conversationTurnNodes": 2,
      "usageHistory": 30,
      "domainCostHistory": 14,
      "compressionCacheStats": 7,
      "xpAuditLog": 7,
      "autoCleanupEnabled": true
    },
    "aggregation": {
      "enabled": true,
      "rawDataRetentionDays": 7,
      "granularity": "daily"
    },
    "backup": {
      "autoBackupEnabled": true,
      "autoBackupFrequency": "daily",
      "keepLastNBackups": 2
    }
  }
  ```
- **Volume & SQLite Footprint Reclamation Inside `omniroute` Container**:
  - `/app/data/storage.sqlite`: shrunk from **`692.74 MB` (`660.6 MiB`) $\rightarrow$ `263 MB`** (**`-430 MB` / `62%` reduction** via `runAutoCleanup()` + `reclaimFreedPages()`).
  - `/app/data/call_logs/`: shrunk from **`10,000` files (`1.38 GB`) $\rightarrow$ `2,000` files (`269 MB`)** (**`-1.11 GB` / `80.5%` reduction**).
  - Total disk space reclaimed in `omniroute-data`: **`~1.54 GB`**.

## 2. Server-Side Tool-Safe Default Compression Stack Verification (Tasks 2.1–2.2)

- **`PUT /api/context/combos/default-caveman` & `/api/context/combos/default-caveman/assignments`**:
  ```json
  {
    "id": "default-caveman",
    "name": "Tool-Safe Default Stack",
    "pipeline": [
      { "engine": "session-dedup" },
      { "engine": "lite" },
      { "engine": "rtk", "intensity": "minimal" },
      { "engine": "codex-responses" },
      { "engine": "headroom" }
    ],
    "outputMode": false,
    "isDefault": true,
    "assignmentsCount": 16
  }
  ```
- **`PUT /api/settings/compression` & `GET /api/settings/compression`**:
  ```json
  {
    "compressionComboId": "default-caveman",
    "stackedPipeline": [
      { "engine": "session-dedup" },
      { "engine": "lite" },
      { "engine": "rtk", "intensity": "minimal" },
      { "engine": "codex-responses" },
      { "engine": "headroom" }
    ],
    "cavemanEngine": { "enabled": false, "level": "lite" },
    "cavemanConfigEnabled": false
  }
  ```

## 3. Predictive TTFT Circuit Breaker, Unleased 2-Account Pool Concurrency & Subscription-Scoped Ban Auto-Disable Verification (Tasks 3.1–3.2)

- **`PATCH /api/settings/combo-defaults` & `PATCH /api/combos/{id}`**:
  - `comboDefaults`: `{"zeroLatencyOptimizationsEnabled": true, "predictiveTtftMs": 25000, "hedging": false, "fallbackCompressionMode": "off"}`
  - All 7 `agy` combos (`gemini-3.8-flash-high` with `models=15`, `gemini-4-argon{,-high,-medium,-low}` with `models=2`, `claude-opus-5.5` with `models=9`, `muse-spark-1.3` with `models=2`) verified with `zeroLatencyOptimizationsEnabled: true`, `predictiveTtftMs: 25000`, `targetTimeoutMs: 25000`, `hedging: false`, and `fallbackCompressionMode: "off"`.
- **`PUT /api/settings/feature-flags` (`ANTIGRAVITY_ACCOUNT_LEASE_ENABLED`) & `PUT /api/settings/auto-disable-accounts`**:
  ```json
  {
    "ANTIGRAVITY_ACCOUNT_LEASE_ENABLED": ["false", "db"],
    "autoDisableAccounts": {
      "enabled": true,
      "threshold": 3,
      "scope": "subscription"
    }
  }
  ```

## 4. Headerless Multi-Turn End-to-End Verification Across `/v1/chat/completions` & `/v1/responses` (Tasks 4.1–4.2)

- **Test 1 — Headerless `/v1/chat/completions` (`extra_headers=None`, `2,925`-char `Read` tool output + 35-suite `vitest run` tool output)**:
  - Response Header: `x-omniroute-compression: stacked; source=routing-override; tokens=1319->956; rules: test-vitest:collapsex1, test-vitest:keepx1, test-vitest:stripx1`
  - Latency: `1,683.4 ms`
  - Result: `200 OK`, `reply: "SENTINEL=VERIFIED_INTACT and FAILED_TEST=tests/auth.test.ts"` (proving `rtk` ran automatically without any client header while `Read` output at char `2,880` and user prose remained 100% intact).
- **Test 2 — Headerless `/v1/responses` (`extra_headers=None`, `2,925`-char `Read` `function_call_output` + 42-line `npm run build` `function_call_output`)**:
  - Response Header: `x-omniroute-compression: stacked; source=routing-override; tokens=1180->118; rules: docker-logs:collapsex1, docker-logs:keepx1, rtk:dedupx1` (**90.0% token reduction** on headerless `/v1/responses`!).
  - Latency: `3,447.8 ms`
  - Result: `200 OK`, `reply: "SENTINEL=VERIFIED_INTACT\nFAILED_MODULE=40"`.
