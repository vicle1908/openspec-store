# Design

## Context

1. **Per-Account Upstream Catalog Migration (`38782750-7a60-46d4-ae3f-e8c13cda296b` / `vicgnome19096@gmail.com`)**:
   - In `key_value` (`namespace = 'syncedAvailableModels'`), connection `agy:38782750-7a60-46d4-ae3f-e8c13cda296b` advertises `["claude-opus-5-5-high", "claude-opus-5-5-medium", "claude-opus-5-5-low", "claude-sonnet-5-5-high", "claude-sonnet-5-5-medium", "claude-sonnet-5-5-low"]` (128K output limit) and has dropped `claude-opus-4-6-thinking` and `claude-sonnet-4-6`.
   - Because Google Cloud Code returns a synthetic HTTP `200` stream (`"Claude Opus 4.6 is no longer available. Please switch to Claude Opus 5.5."`, `tokens_in: 0, tokens_out: 0`) when a migrated account requests `4-6`, and `validateResponseQuality` (`open-sse/services/combo/validateQuality.ts:94-118`) does not inspect assistant text on HTTP `200`, pinning each combo step to its connection's `syncedAvailableModels` model ID (`agy/claude-opus-5-5-high` and `agy/claude-sonnet-5-5-high` on `38782750-7a60-46d4-ae3f-e8c13cda296b`; `agy/claude-opus-4-6-thinking` and `agy/claude-sonnet-4-6` on the remaining 14 active accounts) ensures all 15 steps return genuine completions.
   - In `ANTIGRAVITY_PRICING` (`src/shared/constants/pricing/oauth-subscriptions.ts:75-95`), both `claude-opus-5-5-high` (`$4/$20` blended `$10.4/M`) and `claude-opus-4-6-thinking` (`$5/$25` blended `$13.0/M`) are `"premium"` tier in `classifyTier` and `model_capabilities`, so `resolveAutoStrategyOrder` scores all 15 steps harmoniously without `ScoreTierRotator` starvation.
2. **Compatibility Script Inventory (`51` modifications / `60` fail-closed markers across `24` compiled files)**:
   - `/Users/androidteam/Omniroute/scripts/container-entrypoint-compat.sh` (`43,267` bytes, SHA-256 `d8658728fc0e96cc3502ba133270081e69bb29b3167db6b2a3f252caf7a96ee1`, `nlink=1` on both host and container) applies `3` non-chunk patches (`N1`–`N3`) + `48` chunk/route replacements (`R1`–`R48`) = `51` modifications, guarded by `3` `requiredNonChunkMarkers` + `57` `requiredMarkers` across `21` unique server chunk files = `60` fail-closed markers across `24` compiled files.

## Goals / Non-Goals

- **Goals**:
  1. Ensure 100% of active steps in `claude-opus-5.5` and `claude-sonnet-5.5` target their connection's `syncedAvailableModels` identifier (`5-5-high` on `38782750`, `4-6` on the remaining 14 active accounts).
  2. Synchronize the `51`-modification / `60`-marker counts across `ensure-muse-wire-compat.sh:6,15`, `wiki/entities/omniroute.md:44,67,73`, and the 3 OpenSpec specifications (`omniroute-runtime-customization`, `omniroute-compression-and-routing`, `omniroute-agent-cli-routing`).
- **Non-Goals**:
  - Modifying `container-entrypoint-compat.sh` (`60/60` markers are already active on disk in `omniroute`).

## Decisions

- **Decision 1**: Map each connection step in `claude-opus-5.5` and `claude-sonnet-5.5` to its connection's `syncedAvailableModels` entry (`agy/claude-opus-5-5-high` and `agy/claude-sonnet-5-5-high` on `38782750-7a60-46d4-ae3f-e8c13cda296b`, `agy/claude-opus-4-6-thinking` and `agy/claude-sonnet-4-6` on the remaining 14 active `agy` connections).
- **Decision 2**: Record the exact AST-verified `container-entrypoint-compat.sh` counts (`3` non-chunk + `48` chunk/route replacements = `51` modifications; `3` non-chunk + `57` chunk markers across `21` server chunk files = `60` fail-closed markers across `24` compiled files) across all specs and documentation.
