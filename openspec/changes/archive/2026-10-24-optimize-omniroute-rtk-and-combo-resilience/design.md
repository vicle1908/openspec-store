# Design

## Context

See `proposal.md` for motivation. Following our 3-agent review and `ponytail-review`, we verified five additional runtime behaviors in OmniRoute `v3.8.52`:
1. `src/lib/apiBridgeServer.ts:310` binds `API_PORT` (`20129`) to `process.env.API_HOST || "127.0.0.1"` inside the container namespace; without `API_HOST=0.0.0.0` in `docker-compose.override.yml`, Docker's host port forward (`127.0.0.1:20129->20129/tcp`) hits container `eth0` and immediately resets/closes the socket.
2. `open-sse/services/combo/dispatchPrelude.ts:763-820` (`tryRuntimeUnitDispatch`) intercepts any combo with `nestedComboMode: "execute"` and a `combo-ref` step, walking top-level `models[]` via `executeRuntimeUnitCombo` without calling `targetResolution.ts` (`applySessionStickiness` / `resolveAutoStrategyOrder`). While ideal for `muse-spark-1.3` (whose step `[0]` IS `combo-ref: gemini-3.8-flash-high`), setting `strategy: "priority"` + `nestedComboMode: "execute"` on `claude-opus-5.5` (which has 8 individual `agy/claude-opus-5-5-high` steps before `combo-ref: gemini-3.8-flash-high`) bypasses `applySessionStickiness` and quota scoring across the 8 Opus accounts, hammering account `[0]`. Setting `claude-opus-5.5` to `strategy: "auto"` with `nestedComboMode: "flatten"` runs full 16-factor `auto` scoring (`tierPriority: Ultra=1.0, Pro=0.67`, `quota`, `health`, `latencyInv`) plus `applySessionStickiness` across all 8 Opus accounts and the 15 Flash fallback targets.
3. In `omniroute-agent-cli-routing/spec.md:637-648` (and archived change `2026-10-19-configure-omniroute-gemini-4-argon-tier-combos`), only two `agy` accounts (`338764b8-1cd7-4946-b789-ee5dad4c5073` and `0532bad4-2486-4286-8f06-510e9c678620`) are entitled to `agy/gemini-4-argon-{high,medium,low}`; `62af823b-f3d7-4e6b-87a9-98069167d4f6` (`vicgnome19094@gmail.com`) was explicitly excluded because upstream Cloud Code returns `gemini-4-argon-disabled` (`HTTP 429`) on it.
4. In `src/app/api/v1/muse-code/models/route.ts:98-100` (and `2026-10-22-minimize-omniroute-customizations-and-env-drift/design.md:46`), `/v1/muse-code/models` requires the `muse-code` connection (`51795cf9-4c03-4c22-af9d-9ce4de975dc1`) to stay `isActive: true` so `getProviderModels(request, { provider: "muse-code" })` returns the 40-model catalog (`muse-spark-1.3` first) instead of `data: []`.
5. In `open-sse/services/compression/strategySelector.ts:173,240-250`, headerless requests are downgraded by `applyLossyRequestPolicy` to `SAFE_DEFAULT_PIPELINE` (`session-dedup` + `lite`) *before* `resolveAdaptivePlan` runs. Enabling `contextBudget: { mode: "replace-autotrigger", policy: "reserve-output", outputReserve: 4096, safetyMargin: 1024, pct: 0.85, absoluteBudget: 0 }` causes `resolveAdaptivePlan` (`resolveAdaptivePlan.ts:65-79`) to automatically escalate along `DEFAULT_LADDER` (`session-dedup` $\rightarrow$ `rtk` $\rightarrow$ `headroom` $\rightarrow$ `lite` $\rightarrow$ `caveman`) whenever a headerless request's estimated tokens exceed 85% of the model's context window, while smaller headerless requests stay on lossless `SAFE_DEFAULT_PIPELINE` (and explicit `x-omniroute-compression: allow-lossy` or `engine:rtk` requests run RTK immediately).

## Goals / Non-Goals

**Goals:**
- Authenticate all programmatic management `PUT`/`PATCH`/`POST` mutations via `Authorization: Bearer $OMNIROUTE_KEY` (`id: "server-env"`, `manage` scope).
- Activate RTK (`intensity: "minimal"`, `applyToToolResults: true`, 55 built-in filters), `contextBudget` (`mode: "replace-autotrigger"`, `pct: 0.85`), and Claude delegated `contextEditing` (`enabled: true`).
- Set **both** `resetWindowQuotaCache*` and `resetAwareQuotaCache*` (`300000` / `3600000`) across all `agy`-backed combos while preserving existing `config` fields.
- Reconcile `gemini-4-argon{,-high,-medium,-low}` to strictly the **2** entitled Ultra accounts (`338764b8`, `0532bad4`) with `strategy: "auto"` and `context_cache_protection: false`.
- Configure `muse-spark-1.3` with `strategy: "priority"`, `context_cache_protection: false`, and `config.nestedComboMode: "execute"`; configure `claude-opus-5.5` with `strategy: "auto"`, `context_cache_protection: false`, and `config.nestedComboMode: "flatten"`; prune dead step #2 from `phanmemvip`; and deactivate expired `codex` connection `0ee99889-6643-4fe8-a68a-6c4350de961f` (preserving `muse-code` `51795cf9` active for catalog discovery).
- Add `API_HOST=0.0.0.0` to `~/Omniroute/docker-compose.override.yml` and recreate `omniroute-base` under `/usr/bin/lockf` on `~/.omniroute/update.lock` so host port `20129` (`cockpit` launcher and API bridge) responds alongside port `20128`.
- Switch `thinkingBudget.mode` to `"passthrough"`, configure active `voyage-ai` (`voyage-code-3`, 1024d) via `PUT /api/settings/cache-config`, enable daily SQLite auto-backups via `PATCH /api/settings/database`, enable 5 resilience feature flags, enhance `~/.agents/skills/` ($\le 500$ lines), and unlink the 13 symlinks in `~/Developer/data/skills`.

**Non-Goals:**
- Running `PRAGMA wal_checkpoint(TRUNCATE)` on a live server (`#13973`).
- Modifying tracked files in `/Users/androidteam/Omniroute`.
- Deactivating `muse-code` connection `51795cf9-4c03-4c22-af9d-9ce4de975dc1` (required by `/v1/muse-code/models` and `update.sh` Gate 8).

## Decisions

1. **`API_HOST=0.0.0.0` in `~/Omniroute/docker-compose.override.yml` (`src/lib/apiBridgeServer.ts:310`)**
   - *Rationale*: `docker-compose.yml:46` defaults `API_HOST` to `127.0.0.1` inside the container, whereas `standalone-server-ws.mjs` (`runtime-env.mjs:177`) binds `DASHBOARD_PORT` (`20128`) to `HOSTNAME="0.0.0.0"`. Setting `- API_HOST=0.0.0.0` in `docker-compose.override.yml` while keeping `ports: !override` mapped to `"127.0.0.1:${API_PORT:-20129}:${API_PORT:-20129}"` exposes `20129` on host loopback only while allowing Docker's port forwarder to reach `apiBridgeServer` inside the container.

2. **`claude-opus-5.5` on `strategy: "auto"` (`nestedComboMode: "flatten"`) vs `muse-spark-1.3` on `strategy: "priority"` (`nestedComboMode: "execute"`)**
   - *Rationale*: `muse-spark-1.3` has `[0] combo-ref: gemini-3.8-flash-high` and `[1] model: agy/gemini-3.8-flash-medium`; `priority` + `nestedComboMode: "execute"` runs `gemini-3.8-flash-high`'s `auto` strategy first and only falls back to `[1]` if all 15 accounts fail. Conversely, `claude-opus-5.5` has 8 individual `agy/claude-opus-5-5-high` steps followed by `combo-ref: gemini-3.8-flash-high`; `strategy: "auto"` + `nestedComboMode: "flatten"` scores all targets via 16-factor `auto` routing and applies connection-level `applySessionStickiness` across all 8 Opus accounts instead of hammering step `[0]`.

3. **Strict Two-Account Pool on `gemini-4-argon{,-high,-medium,-low}` (`338764b8` and `0532bad4`)**
   - *Rationale*: Matches `omniroute-agent-cli-routing/spec.md:637-648`. Removing `62af823b-f3d7-4e6b-87a9-98069167d4f6` (`vicgnome19094@gmail.com`) from the four `gemini-4-argon*` combos prevents `429` retry stalls on an account not entitled to `agy/gemini-4-argon-*`.

4. **`contextBudget.mode: "replace-autotrigger"` + `lossyRequestPolicy` (`strategySelector.ts:173,240-250`)**
   - *Rationale*: Headerless requests below 85% context budget run lossless `SAFE_DEFAULT_PIPELINE` (`session-dedup` + `lite`). When estimated tokens exceed 85% of the model context window, `resolveAdaptivePlan` escalates along `DEFAULT_LADDER` (`rtk` $\rightarrow$ `headroom` $\rightarrow$ `caveman`), and requests with `x-omniroute-compression: allow-lossy` or `engine:rtk` invoke RTK directly.

## Risks / Trade-offs

- **Risk**: Recreating `omniroute-base` to apply `API_HOST=0.0.0.0` briefly restarts the container (~5s).
  - *Mitigation*: Acquire `/usr/bin/lockf` on `~/.omniroute/update.lock` before `docker compose --profile base up -d --no-build --pull never --no-deps --force-recreate omniroute-base` and run `~/Omniroute/scripts/ensure-muse-wire-compat.sh omniroute` immediately after healthcheck passes.
