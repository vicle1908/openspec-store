# Evidence

## Execution Summary

- **Change**: `reconcile-hydrogen-codex-routing-banned-accounts-and-pi-sync`
- **Store**: `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`)
- **Timestamp**: `2026-11-15T05:12:00Z`
- **Host**: `iosteam-mac-mini` (`100.70.16.83`, macOS arm64)
- **Apply Status**: `9/9` tracked tasks complete (`validate-archive-readiness.py` `status: "ready"`, `openspec validate --strict` valid).

## Key Verification Results

### 1. Pre-Flight Backups & Snapshots (Tasks 1.1, 1.2)
- Backup directory created: `/Users/androidteam/.omniroute/backups/reconcile-hydrogen-codex-routing-banned-accounts-and-pi-sync/` (`0700`).
- Backed up 5 host files + `combos-pre.json` (`0600`), verified `PRAGMA quick_check = ok` on `agent.db.bak`, and generated `sha256-manifest.json` (`0600`).
- Captured OmniRoute snapshot `/Users/androidteam/.omniroute/snapshots/pre-reconcile-hydrogen-20261115.sqlite` (`0600`, 288 MB, `PRAGMA quick_check = ok`, 5 snapshots retained).
- Verified `git -C /Users/androidteam/Omniroute status --porcelain --untracked-files=no` is clean.

### 2. OmniRoute Combo Hygiene & Hydrogen Quota-Weighted Routing (Tasks 2.1, 2.2)
- Pruned banned `62af823b` (`vicgnome19094@gmail.com`) from all 8 remaining Argon/Carbon combos (`gemini-4-argon{,-high,-medium,-low}` and `gemini-4-carbon{,-high,-medium,-low}`) via `PUT /api/combos/{id}` (HTTP `200` on all 8), leaving exactly 2 active Ultra steps (`0532bad4`, `338764b8`) and zero occurrences of `62af823b` in `combos`.
- Switched `gemini-4-hydrogen-{xhigh,high,medium,low}` to `strategy: "quota-weighted"` (`predictiveTtftMs: 0`, `quotaWeightedFloorPercent: 5`, `quotaWeightedScoring: "leftover"`) across the 5 active WTU-Pro accounts (`9c033d6f`, `37f9924d`, `573e3f41`, `3f3085b1`, `a94216f4`), keeping top-level `gemini-4-hydrogen` as a flattened `combo-ref` wrapper (`nestedComboMode` unset/`"flatten"` so flattened target execution runs `applyStrategyOrdering("quota-weighted")`).
- Verified `POST /api/settings/reasoning-routing-rules/simulate` routes `low`, `medium`, and `xhigh` to their matching tier combos, and `DELETE /api/resilience/model-cooldowns` cleared all cooldowns (`HTTP 200`).

### 3. OMP Auth DB, Codex Config, and Pi 1.5.2 Alignment (Tasks 3.1, 3.2, 3.3)
- Pruned banned `vicgnome19094@gmail.com` (`id = 3`) from `/Users/androidteam/.omp/agent/agent.db` inside `BEGIN IMMEDIATE;` (mode `0600`, `PRAGMA quick_check = ok`, leaving the 5 active non-banned rows `id IN (2, 6, 10, 14, 15)`).
- Removed unsupported `service_tier = "ultrafast"` from `/Users/androidteam/.codex/config.toml` (`mode 0600`), eliminating `unsupported_service_tier_warning`.
- **Codex Exec Root-Cause Finding**: Bisection proved that native `codex exec` sends an unconfigurable hardcoded system prompt `You are Codex, an agent based on GPT-5.` which Google Antigravity upstream rejects with content-level `429 RESOURCE_EXHAUSTED` (regardless of account quota), whereas identical `/v1/responses` requests with that single identity line replaced by `You are an AI coding assistant.` succeed in `2.5s–4.6s` (`HTTP 200` `pong`).
- Updated `"lastChangelogVersion": "1.5.2"` in `/Users/androidteam/.pi/agent/settings.json` (`mode 0600`), verified `pi --version == 1.5.2` and `current-version == 1.5.2`, updated `wiki/entities/pi.md` (documenting `releases/{1.5.1,1.5.2}/` `N-1` retention) and `pi/SKILL.md` from `1.4.0` to `1.5.2`, and verified `pi -p "reply only: pong"` returned `pong`.

### 4. Verification, Knowledge Index Refresh & Readiness (Tasks 4.1, 4.2)
- Verified `stat -L` permissions (`0600` on credentials/configs, `0644` on public catalog), confirmed zero secret leaks in markdown/spec files, and verified `setup-macbook-omniroute-client.sh --check` exited `0` (`SUCCESS`).
- Verified 4 concurrent `/v1/responses` completions on `quota-weighted` `gemini-4-hydrogen` (`pong 0` through `pong 3` in `3.7s`), distributing across multiple accounts in `call_logs`.
- Synchronized Notion `wiki/entities/pi.md` (`3efc4b21-deb4-8129-b9c3-d7c22a453212`).
- Saved decision memory to AgentMemory (`POST http://127.0.0.1:3111/agentmemory/remember`) and published mesh sync (`local_mesh` pushed `1`, `peer_mesh` success `true`).
- Force-refreshed `openspec-store` GitNexus index at `1332b88d7cc7` (`70,389 nodes | 73,782 edges | 18.9s`).
- Passed `openspec validate --strict --store openspec-store` and `validate-archive-readiness.py`.
