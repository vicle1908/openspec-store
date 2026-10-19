# Design

## Context

See `proposal.md` — Why for problem motivation.

OmniRoute (`http://127.0.0.1:20128`, running `diegosouzapw/omniroute:latest` v3.8.51 with SQLite state on the `omniroute-data` Docker named volume) manages 15 active Google Antigravity CLI (`agy`) OAuth connections. Live audit of `/api/usage/provider-limits` and `/api/providers/{id}/models` establishes:

1. **Account Tier Entitlement Boundary**:
   - **2 Google AI `Ultra` accounts** expose callable `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` quotas via `retrieveUserQuota` and `:fetchAvailableModels`:
     - `338764b8-1cd7-4946-b789-ee5dad4c5073` (`vinhghtk1908@gmail.com`)
     - `0532bad4-2486-4286-8f06-510e9c678620` (`vinhvumobile@gmail.com`)
   - **13 Google AI `Pro` accounts** (`vicgnome*`, `phamkive425@gmail.com`, `ascenddevtwo@gmail.com`, `vicle1908@gmail.com`, `ghtkmobile@gmail.com`) only receive `gemini-4-argon-disabled` from `:fetchAvailableModels` and return `HTTP 429: Resource has been exhausted` after ~20s of internal backoff retries if targeted with `agy/gemini-4-argon-*`.
2. **Current `gemini-4-argon` Combo State (`id: f1cefc64-7662-4f0a-9234-84f70603cbe4`)**:
   - `models`: single step targeting `agy/gemini-4-argon-disabled` on `338764b8-1cd7-4946-b789-ee5dad4c5073` (`HTTP 429`).
   - `config.candidatePool`: stale `["openai-compatible-responses-396066d4-c57b-44ab-9683-013cdaa89d49"]` from the former `nx` provider, which causes `selectAutoProvider()` (`open-sse/services/autoCombo/engine.ts:266`) to filter out `agy` targets before falling back.
3. **Existing Pattern Reference**:
   - Combo `gemini-3.8-flash-high` (`id: 7555d851-b4f3-44c6-b1fb-c6fdceabf388`) establishes the canonical `agy` combo structure: `strategy: "auto"`, `context_length: 1000000`, `context_cache_protection: true`, `config.candidatePool: ["agy"]`, and explicit connection-pinned `models[]` steps (`kind: "model"`, `providerId: "agy"`, `connectionId`, `label`, `weight: 0`).
   - Skill `omp-omniroute-catalog-sync` and `omp-isolated-profile-smoke-gate` establish the staged throwaway profile workflow (`~/.omp/profiles/<name>/agent`) with `retry: {fallbackChains: {}}` before atomic promotion to `~/.omp/agent/models.yml` and `~/.omp/agent/config.yml`.

```text
+-----------------------------------------------------------------------------+
|                OMNIROUTE ARGON 4 TIER COMBOS (strategy: "auto")             |
|        context_length: 1000000 | context_cache_protection: false            |
|        candidatePool: ["agy"]  | resetAwareQuotaCacheTtlMs: 300000          |
+-----------------------------------------------------------------------------+
        |                       |                       |                     |
        v                       v                       v                     v
+--------------------+  +--------------------+  +--------------------+  +--------------------+
| gemini-4-argon     |  | gemini-4-argon-    |  | gemini-4-argon-    |  | gemini-4-argon-    |
| (default high)     |  | high               |  | medium             |  | low                |
+--------------------+  +--------------------+  +--------------------+  +--------------------+
| 1. 338764b8 (Ultra)|  | 1. 338764b8 (Ultra)|  | 1. 338764b8 (Ultra)|  | 1. 338764b8 (Ultra)|
|    agy/...-high    |  |    agy/...-high    |  |    agy/...-medium  |  |    agy/...-low     |
| 2. 0532bad4 (Ultra)|  | 2. 0532bad4 (Ultra)|  | 2. 0532bad4 (Ultra)|  | 2. 0532bad4 (Ultra)|
|    agy/...-high    |  |    agy/...-high    |  |    agy/...-medium  |  |    agy/...-low     |
+--------------------+  +--------------------+  +--------------------+  +--------------------+
```

## Goals / Non-Goals

**Goals:**
- Reconcile `gemini-4-argon` (`f1cefc64-7662-4f0a-9234-84f70603cbe4`) and create `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` combos in OmniRoute, each containing strictly 2 steps pinned to the 2 `Ultra` `agy` connections (`338764b8-1cd7-4946-b789-ee5dad4c5073` and `0532bad4-2486-4286-8f06-510e9c678620`).
- Remove the invalid manual `agy/gemini-4-argon` custom model entry from OmniRoute's provider-models table.
- Synchronize `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` into `~/.omp/agent/models.yml` and `~/.omp/agent/config.yml` (`retry.fallbackChains`) using an isolated smoke-test gate.

**Non-Goals:**
- Patching git-tracked files in `/Users/androidteam/Omniroute`.
- Adding the 13 `Pro`-tier `agy` accounts to any Gemini 4 Argon combo.
- Changing active `modelRoles` in `~/.omp/agent/config.yml` or default models in other workstation CLIs.

## Decisions

### 1. Provision Three Explicit Tier Combos Plus Reconciled `gemini-4-argon` Alias Combo
- **Decision**: Maintain `gemini-4-argon` (`id: f1cefc64-7662-4f0a-9234-84f70603cbe4`, targeting `agy/gemini-4-argon-high` on the 2 `Ultra` accounts) and create 3 tier-specific combos (`gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`) via a single shared payload builder calling `POST /api/combos` (or `PATCH /api/combos/{id}` if already present), each with:
  ```json
  {
    "strategy": "auto",
    "context_length": 1000000,
    "context_cache_protection": false,
    "config": {
      "maxRetries": 1,
      "retryDelayMs": 2000,
      "fallbackDelayMs": 0,
      "handoffThreshold": 0.85,
      "handoffModel": "",
      "maxMessagesForSummary": 30,
      "maxComboDepth": 3,
      "trackMetrics": true,
      "reasoningTokenBufferEnabled": true,
      "zeroLatencyOptimizationsEnabled": false,
      "candidatePool": ["agy"],
      "resetAwareQuotaCacheTtlMs": 300000,
      "resetAwareQuotaCacheMaxStaleMs": 3600000
    }
  }
  ```
- **Rationale**:
  - Reusing the top-level combo naming pattern (`src/lib/combos/modelNameCollision.ts` `#6940`/`#8530`) allows callers to select exact upstream thinking tiers (`gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`) as top-level model IDs while preserving backward compatibility for `omniroute/gemini-4-argon`.
  - Setting `context_cache_protection: false` avoids the model-level `tryPinnedModelDispatch` path (`open-sse/services/combo/dispatchPrelude.ts:174-191,320-344`), which otherwise queries `provider = "antigravity"` (0 rows for `agy`), logs a false `provider durably unhealthy` warning every turn, and dispatches `handleSingleModelWithTimeout` without a `connectionId` pin if `antigravity` ever reports healthy. Per-conversation account stickiness to the chosen `Ultra` `connectionId` remains active via `applySessionStickiness` (`open-sse/services/combo/targetResolution.ts:533`).
  - Setting `resetAwareQuotaCacheTtlMs: 300000` (5 minutes) and `resetAwareQuotaCacheMaxStaleMs: 3600000` (1 hour) prevents `buildAutoCandidates` (`open-sse/services/combo.ts:469`) from blocking requests every 60 seconds with synchronous upstream `retrieveUserQuota` HTTP calls.
- **Alternatives Considered**:
  - *Single `gemini-4-argon` combo relying only on `reasoning_effort`*: Rejected because upstream Cloud Code exposes distinct model IDs (`gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`) and the user explicitly requested exposing high, medium, and low as 3 combos with 2 `Ultra` steps each.
  - *Including all 15 `agy` accounts*: Rejected because the 13 `Pro` accounts return `HTTP 429` (`gemini-4-argon-disabled`) and incur ~20s retry latency per failed step.

### 2. Remove Manual `agy/gemini-4-argon` Custom Model Entry
- **Decision**: Execute `~/.local/bin/omniroute models remove agy gemini-4-argon --yes` (which calls `DELETE /api/provider-models` with `resetOverride=true`).
- **Rationale**: Upstream Cloud Code does not serve bare `gemini-4-argon` (`HTTP 400: Model 'gemini-4-argon' is not available in the active live catalog for provider 'antigravity'`). Removing the manual override prevents pure-auto expansion (`expandAutoComboCandidatePool` in `open-sse/services/combo/autoStrategy.ts:514`) from injecting a broken `agy/gemini-4-argon` candidate while keeping the top-level `gemini-4-argon` combo intact.

### 3. Tier-Matched `thinking.defaultLevel` in OMP `models.yml`
- **Decision**: Configure each tier combo in `~/.omp/agent/models.yml` with `thinking: { mode: effort, efforts: [low, medium, high], defaultLevel: <tier> }` where `defaultLevel` is `high` for `gemini-4-argon-high` (and `gemini-4-argon`), `medium` for `gemini-4-argon-medium`, and `low` for `gemini-4-argon-low`.
- **Rationale**: When a user or subagent selects `omniroute/gemini-4-argon-medium` or `omniroute/gemini-4-argon-low` without an explicit `:effort` suffix, OMP transmits `reasoning: { effort: defaultLevel }` on `POST /v1/responses`, aligning the request's reasoning budget with the combo's upstream Antigravity tier.

### 4. Idempotent Transaction Boundaries & Atomic Rollout
- **OmniRoute SQLite State (`/app/data/storage.sqlite`)**:
  - Pre-mutation backup snapshots written to `/tmp/omniroute-combos-pre-argon-tiers.json` and `/tmp/omniroute-agy-models-pre-argon-tiers.json` (mode `0600`).
  - Combo provisioning inspects `GET /api/combos` by `name` first: if the combo already exists, it invokes `PATCH /api/combos/{id}`; otherwise it invokes `POST /api/combos` (avoiding `400 COMBO_004` name collisions on re-runs). Each call executes as an atomic SQLite transaction inside OmniRoute's `updateCombo`/`createCombo` repository layer (`src/lib/db/combos.ts`).
  - `POST /api/combos/test` streams SSE (`stream: true`, `max_tokens: 64`, `X-Internal-Test: combo-health-check`) through `extractComboTestStreamResult` (`src/lib/combos/testHealth.ts:190`), verifying that non-keepalive `content` (`"pong"`) is returned from both `Ultra` `agy` steps within the 60s target deadline.
  - Manual model removal executes as a single atomic SQLite delete on `provider_models` (idempotent if already absent).
- **OMP Configuration (`~/.omp/agent/models.yml`, `~/.omp/agent/config.yml`)**:
  - Pre-mutation SHA-256/MD5 hashes and timestamped backups captured before any edit; `~/.omp/agent/agent.db` MD5 is recorded before and after.
  - Staged first in an isolated profile `~/.omp/profiles/argon-tiers-smoke/agent` with `retry: {fallbackChains: {}}`, seeding `agent.db` `auth_*` tables strictly read-only (`file:/Users/androidteam/.omp/agent/agent.db?mode=ro`) using exact `sqlite_master` DDL (`CREATE TABLE` + `CREATE INDEX` + `INSERT INTO`, never `CREATE TABLE AS SELECT`), and verified from a clean login shell (`zsh -lc`) to prove direct self-served completion without fallback masquerade (`omp-isolated-profile-smoke-gate`).
  - Promoted to `~/.omp/agent/models.yml` and `~/.omp/agent/config.yml` via same-directory temporary files with `fsync`, permission preservation, and `os.replace()` atomic rename, followed by cleanup of the throwaway profile.

## Risks / Trade-offs

- **[Risk] Quota exhaustion on the 2 `Ultra` accounts (`vinhvumobile@gmail.com` currently at 1.17% remaining until `2026-10-23T22:00:08Z`; `vinhghtk1908@gmail.com` at 51.85% resetting `2026-10-19T10:02:20Z`)** → **Mitigation**: `strategy: "auto"` with `candidatePool: ["agy"]` automatically scores remaining quota and health across both `Ultra` steps and fails over between them; in OMP, `retry.fallbackChains` fails over to the 15-account `omniroute/gemini-3.8-flash-high` pool if both `Ultra` accounts are exhausted.
- **[Risk] Tiny `max_tokens <= 256` on `/v1/chat/completions` multi-turn tool continuations without `reasoning_effort`** → **Mitigation**: Documented in verification; OMP and Responses API clients (`/v1/responses`) pass explicit `reasoning.effort` and `maxTokens: 128000`, avoiding the `thinkingBudget <= 128` (`THINKING_LEVEL_MINIMAL`) branch in `openai-to-gemini.ts`.
