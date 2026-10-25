# Design: Reconcile OmniRoute Argon Combos, Heavyweight Admission & Auto-Prune Drift

## Context

Following the archival of `2026-10-25-consolidate-omniroute-three-tier-config-and-max-features` and `2026-10-25-expand-gemini-4-argon-three-ultra-accounts`, a comprehensive behavioral audit of `/app/data/storage.sqlite` (`combos`, `call_logs`, `key_value`) and workstation client configs surfaced four concrete discrepancies:

1. **Missing Step `label`s and `targetTimeoutMs: 25000` on `gemini-4-argon*` Combos**:
   - All 4 `gemini-4-argon*` combos (`gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`) now contain the 3 Google AI Ultra (`g1-ultra-tier`) `agy` connections (`62af823b-f3d7-4e6b-87a9-98069167d4f6` / `vicgnome19094@gmail.com`, `0532bad4-2486-4286-8f06-510e9c678620` / `vinhvumobile@gmail.com`, `338764b8-1cd7-4946-b789-ee5dad4c5073` / `vinhghtk1908@gmail.com`).
   - However, the `PUT /api/combos/{id}` update in `2026-10-25-expand-gemini-4-argon-three-ultra-accounts` omitted `"label"` on all 12 steps and omitted `"targetTimeoutMs": 25000` in `config` (which is also absent from `muse-spark-1.3` and `/api/settings/combo-defaults`). Without `targetTimeoutMs: 25000`, a rate-limited step on `62af823b` hung for `99,132 ms` at `2026-10-25T09:34:51Z` before failing over.
2. **Gateway-Wide `503 chat_admission_busy` Shedding from `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=1`**:
   - In `chunks/37338.js` (module `637338`), `admitChatRequest` classifies any request with `content-length >= 256 KB` as heavy, and `admitChatStructure` classifies any request with `tools.length >= 64` (every coding agent wired to MCP Router carries 84+ tools) or `estimatedTokens >= 32,000` as heavy.
   - Setting `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=1` with default `OMNIROUTE_CHAT_ADMISSION_QUEUE_MS=0` limits the entire 15-account / 3-Ultra-account gateway to `1` active heavy slot + `1` healthy headroom slot = **2 concurrent requests total**, rejecting 242+ requests today (`18` on `gemini-4-argon`, `35` on `gemini-3.8-flash-high`) in `0 ms` while `inflightBytes` was at `1.6%` (`2.18 MB / 137.36 MB`).
3. **Destructive Composite-Combo Auto-Pruning (`COMBO_AUTO_PRUNE_STALE_STEPS="true"`)**:
   - In `src/lib/combos/staleModelRefs.ts`, `pruneStaleComboSteps` only aborts when `kept.length === 0`. Because `claude-opus-5.5` has a trailing `combo-ref: gemini-3.8-flash-high` step (`kept.length === 1`), scheduled sync at `2026-10-25T08:11:40Z` deleted all 8 explicit `agy/claude-opus-5-5-high` steps, silently turning `claude-opus-5.5` into a 100% alias for `gemini-3.8-flash-high`.
4. **Codex Catalog & Canonical Spec/Wiki Drift**:
   - `~/.codex/cockpit-model-catalog.json` drifted to `context_window: 272000`, `prefer_websockets: true`, and `default_reasoning_level: "medium"` on all 4 `gemini-4-argon*` entries, and `omniroute-agent-cli-routing/spec.md:638-647,718` plus `wiki/concepts/omniroute-gemini-4-argon-fleet-routing.md:18,44` still state 2 Ultra accounts instead of 3.

## Goals / Non-Goals

- **Goals**:
  - Restore `"label"` (`vicgnome19094@gmail.com`, `vinhvumobile@gmail.com`, `vinhghtk1908@gmail.com`) and `"targetTimeoutMs": 25000` across all 4 `gemini-4-argon*` combos, add `"targetTimeoutMs": 25000` to `muse-spark-1.3` and `/api/settings/combo-defaults`, and remove the stale `gemini-4-argon` alias from `/api/models/alias`.
  - Raise `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=16` and set `OMNIROUTE_CHAT_ADMISSION_QUEUE_MS=15000` in `/Users/androidteam/Omniroute/.env` so concurrent subagent turns across the 3 Ultra accounts and 15 Flash accounts never shed while V8 heap byte budget (`maxInflightBytes: 137363456`) has headroom.
  - Set `COMBO_AUTO_PRUNE_STALE_STEPS` to `"false"` via `PUT /api/settings/feature-flags` and restore `claude-opus-5.5` (`context_length: 1000000`).
  - Restore the 1M-context `gemini-4-argon*` definitions in `~/.codex/cockpit-model-catalog.json` (and mode `0600` on `~/.codex/config.toml`) and synchronize canonical specs and wiki pages.
- **Non-Goals**:
  - Editing any git-tracked file inside `/Users/androidteam/Omniroute/`.
  - Adding Pro or Free `agy` accounts to `gemini-4-argon*` combos.

## Architecture & Transaction Boundaries

```
+--------------------------------------------------------------------------------------------------+
|                         OmniRoute Admission -> Combo Dispatch Pipeline                           |
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
|  [Coding Agent Request (tools >= 64)]                                                            |
|         |                                                                                        |
|         v                                                                                        |
|  1. ChatAdmissionController (.env: OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=16, QUEUE_MS=15000)        |
|     - Byte ceiling: maxInflightBytes = 137,363,456 (3.1% of 4.09 GiB V8 heap)                    |
|     - Concurrency ceiling: 16 activeHeavy + 1 healthyHeadroom = 17 concurrent tool streams       |
|         |                                                                                        |
|         v                                                                                        |
|  2. Combo Router (gemini-4-argon{,-high,-medium,-low}, strategy="auto", targetTimeoutMs=25000)   |
|     - Step [0]: 62af823b-f3d7-4e6b-87a9-98069167d4f6 (label: "vicgnome19094@gmail.com")          |
|     - Step [1]: 0532bad4-2486-4286-8f06-510e9c678620 (label: "vinhvumobile@gmail.com")           |
|     - Step [2]: 338764b8-1cd7-4946-b789-ee5dad4c5073 (label: "vinhghtk1908@gmail.com")           |
+--------------------------------------------------------------------------------------------------+
```

- **SQLite Combo Update Boundary (`sqliteComboRepository.ts`)**: Always read the full combo via `GET /api/combos/{id}`, merge `config` (`targetTimeoutMs: 25000`) and `models` (preserving all existing `config` fields), and submit via `PUT /api/combos/{id}` so `sqliteComboRepository.ts` shallow-merge semantics never drop `resetWindowQuotaCacheTtlMs` or `predictiveTtftMs`.
- **Feature Flag Boundary (`PUT /api/settings/feature-flags`)**: Must be invoked with a single `{ "key": "COMBO_AUTO_PRUNE_STALE_STEPS", "value": "false" }` payload per request (`src/app/api/settings/feature-flags/route.ts:101-129`).
