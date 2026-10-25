# Proposal

## Why

Live OmniRoute (`v3.8.52`) currently drops concurrent coding-agent turns with `HTTP 503 chat_admission_busy`, stalls `gemini-4-argon*` failover on upstream `429` errors for up to 99 seconds, and silently stripped all 8 Claude Opus steps from `claude-opus-5.5` due to post-archive configuration drift across today's OmniRoute changes. Specifically: (1) `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=1` caps the entire 15-account / 3-Ultra-account gateway to 1 heavy in-flight request + 1 headroom slot (`queueMs = 0`), shedding 229+ requests (`18` on `gemini-4-argon` and `35` on `gemini-3.8-flash-high`) while V8 heap inflight memory is at only 1.6% (`2.18 MB / 137.36 MB`); (2) `2026-10-25-expand-gemini-4-argon-three-ultra-accounts` added the 3rd Google AI Ultra account (`vicgnome19094@gmail.com` / `62af823b-f3d7-4e6b-87a9-98069167d4f6`) to all four `gemini-4-argon*` combos but omitted `"label"` on all 12 steps and omitted `"targetTimeoutMs": 25000` (which is also missing from `muse-spark-1.3` and `/api/settings/combo-defaults`); (3) enabling `COMBO_AUTO_PRUNE_STALE_STEPS="true"` caused scheduled catalog sync to prune all 8 `agy/claude-opus-5-5-high` steps from `claude-opus-5.5` because its trailing `combo-ref: gemini-3.8-flash-high` bypassed the empty-combo guard; and (4) canonical specs (`omniroute-agent-cli-routing`, `omniroute-compression-and-routing`), `/api/models/alias`, `~/.codex/cockpit-model-catalog.json`, and `wiki/concepts/omniroute-gemini-4-argon-fleet-routing.md` still carry stale 2-Ultra-account or 272k-context definitions.

## What Changes

- **Complete 3-Ultra-Account `gemini-4-argon*` & `muse-spark-1.3` Combo Configuration**:
  - Update `gemini-4-argon` (`f1cefc64-7662-4f0a-9234-84f70603cbe4`), `gemini-4-argon-high` (`f7a7ff33-44bd-427a-957f-0774227e12ed`), `gemini-4-argon-medium` (`4dc53616-dad7-4c51-8d09-067fec4d51d8`), and `gemini-4-argon-low` (`bafa3f44-dc5f-4bf3-8d0f-13a2fe078e5c`) via `GET /api/combos/{id}` -> merge `config` -> `PUT /api/combos/{id}` so all 3 Google AI Ultra steps carry explicit `"label"` values (`"vicgnome19094@gmail.com"`, `"vinhvumobile@gmail.com"`, `"vinhghtk1908@gmail.com"`) and `config.targetTimeoutMs: 25000` alongside `predictiveTtftMs: 25000`, `zeroLatencyOptimizationsEnabled: true`, `hedging: false`, `fallbackCompressionMode: "off"`, and dual 5-minute quota-cache TTLs.
  - Add `config.targetTimeoutMs: 25000` to `muse-spark-1.3` (`453c5dd3-f7f4-4c44-bd4b-6c3c1d0f4e5b`) and `PATCH /api/settings/combo-defaults`, set `context_length: 1000000` and `context_cache_protection: false` on `kimi-k3.1-pro` and `deepseek-v4.1-flash`, and remove the stale `gemini-4-argon` alias pointing to Nexus (`nx`) from `/api/models/alias`.
- **Eliminate `503 chat_admission_busy` Multi-Agent Starvation**:
  - Update `/Users/androidteam/Omniroute/.env` to raise `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=16` (matching the 15-account Flash / 3-Ultra-account Argon concurrency while the `137.36 MB` V8 heap byte budget `maxInflightBytes` and `5g` container cgroup ceiling enforce hard memory safety) and set `OMNIROUTE_CHAT_ADMISSION_QUEUE_MS=15000` so bursts queue cleanly rather than shedding immediately in 0ms.
- **Disable Destructive Composite-Combo Auto-Pruning & Restore `claude-opus-5.5`**:
  - Set `COMBO_AUTO_PRUNE_STALE_STEPS` to `"false"` via `PUT /api/settings/feature-flags` (`{"key": "COMBO_AUTO_PRUNE_STALE_STEPS", "value": "false"}`) so scheduled catalog syncs never strip explicit model steps from hybrid combos that end with a `combo-ref` fallback, and restore `claude-opus-5.5` (`4b2430da-0b3b-4b0e-9773-ec0f97adc252`, `context_length: 1000000`) with its 8 active `agy` accounts + `combo-ref: gemini-3.8-flash-high`.
- **Reconcile Codex CLI Catalog, Main Specs & Wiki Documentation**:
  - Restore `context_window: 1000000`, `max_context_window: 1000000`, `auto_compact_token_limit: 800000`, `prefer_websockets: false`, neutral `base_instructions`, and tier-matched `default_reasoning_level` (`high`, `medium`, `low`) on the 4 `gemini-4-argon*` entries in `~/.codex/cockpit-model-catalog.json` (and mode `0600` on `~/.codex/config.toml`).
  - Synchronize `omniroute-agent-cli-routing/spec.md`, `omniroute-compression-and-routing/spec.md`, `wiki/entities/omniroute.md`, and `wiki/concepts/omniroute-gemini-4-argon-fleet-routing.md` to reflect all 3 Google AI Ultra accounts (`62af823b-f3d7-4e6b-87a9-98069167d4f6`, `0532bad4-2486-4286-8f06-510e9c678620`, `338764b8-1cd7-4946-b789-ee5dad4c5073`), `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=16`, and `COMBO_AUTO_PRUNE_STALE_STEPS="false"`.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `omniroute-compression-and-routing`: Update the 3-Ultra-account `gemini-4-argon*` combo requirement to mandate step `label`s and `targetTimeoutMs: 25000`, update the heavyweight admission requirement from `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=1` to `16` with `OMNIROUTE_CHAT_ADMISSION_QUEUE_MS=15000`, and set `COMBO_AUTO_PRUNE_STALE_STEPS` to `"false"` (24 `"true"` + 2 `"false"` SQLite feature flags) to protect composite combos containing `combo-ref` steps.
- `omniroute-agent-cli-routing`: Update the Gemini 4 Argon tier combo requirement from 2 Ultra `agy` CLI connections to all 3 entitled Google AI Ultra `agy` CLI connections (`62af823b-f3d7-4e6b-87a9-98069167d4f6`, `0532bad4-2486-4286-8f06-510e9c678620`, `338764b8-1cd7-4946-b789-ee5dad4c5073`) with explicit step `label`s and `targetTimeoutMs: 25000`.

## Non-Goals

- Modifying any git-tracked source files inside `/Users/androidteam/Omniroute/`.
- Adding non-Ultra (`g1-pro-tier` or `free-tier`) `agy` accounts to `gemini-4-argon*` combos.
- Mutating archived OpenSpec change directories under `openspec/changes/archive/`.

## Ownership Boundaries

- **External Managed Service (`/Users/androidteam/Omniroute/`)**: Untracked `.env` and SQLite state in named Docker volume `omniroute-data` (`/app/data/storage.sqlite` via REST API on `http://127.0.0.1:20128`).
- **Workstation Client Config (`~/.codex/`)**: `~/.codex/cockpit-model-catalog.json` and `~/.codex/config.toml`.
- **Central OpenSpec Store & Wiki (`/Users/androidteam/Developer/platform/openspec-store/`, `/Users/androidteam/Developer/wiki/`)**: Main specs and curated wiki pages.

## Impact

- Eliminates `HTTP 503 chat_admission_busy` rejections on concurrent multi-agent `gemini-4-argon*` and `gemini-3.8-flash-high` turns.
- Caps per-step stalled target attempts at `25,000 ms` across all `gemini-4-argon*` and `muse-spark-1.3` combos (preventing 99s retry hangs) and restores account email labels in the OmniRoute dashboard.
- Prevents scheduled catalog syncs from stripping explicit model steps out of composite combos that include a `combo-ref` fallback.
