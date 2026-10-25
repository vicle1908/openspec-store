# Design

## Context

See `proposal.md` — Why for motivation. The `combos` table in `/app/data/storage.sqlite` stores combo routing configurations. In OmniRoute `v3.8.52`, `claude-opus-5.5` existed (ID: `4b2430da-0b3b-4b0e-9773-ec0f97adc252`) with only a `combo-ref: gemini-3.8-flash-high` step, and `claude-sonnet-5.5` did not exist.

Live verification uncovered a critical `strategy: "auto"` invariant (`open-sse/services/combo/resolveAutoStrategy.ts:L180-480`): when a `combo-ref: gemini-3.8-flash-high` fallback step is included inside an `auto` combo, `resolveNestedComboTargets` expands all 15 `gemini-3.8-flash-high` targets into the same candidate pool as the 15 Claude targets, and `selectAutoProvider` scores `gemini-3.8-flash-high` (`score=0.682`, lower cost and latency) above `claude-opus-4-6-thinking` / `claude-sonnet-4-6`, hijacking 100% of primary requests to Gemini Flash. Using a pure 15-account homogeneous Claude pool (matching the `gemini-4-argon*` combo architecture) ensures `auto` scoring selects the healthiest, highest-headroom Claude account across all 15 Antigravity connections.

## Goals / Non-Goals

**Goals:**
- Update `claude-opus-5.5` (`4b2430da-0b3b-4b0e-9773-ec0f97adc252`) with 15 explicit model steps for `agy/claude-opus-4-6-thinking` (one per connection).
- Create `claude-sonnet-5.5` (`9447399c-856b-4f52-8820-b3bf3dc3f132`) with 15 explicit model steps for `agy/claude-sonnet-4-6` (one per connection).
- Configure both combos with `strategy: "auto"`, `candidatePool: ["agy"]`, `context_cache_protection: false`, `zeroLatencyOptimizationsEnabled: true`, `predictiveTtftMs: 25000`, `targetTimeoutMs: 25000`, `fallbackCompressionMode: "off"`, and `hedging: false`.
- Establish the operational cutover procedure for future upstream 5.5 model availability.

**Non-Goals:**
- Modifying git-tracked source files inside `/Users/androidteam/Omniroute/`.
- Changing existing `gemini-3.8-flash-high` or `gemini-4-argon*` combos.
- Creating synthetic model aliases that fail with upstream 429 quota errors.

## Decisions

### 1. Connection Inventory for the 15-Account Claude Pool
| # | Account Name | Connection ID | Tier |
|---|---|---|---|
| 1 | `vicgnome19092@gmail.com` | `ea0d6c23-85c0-42c8-abdf-8186effd3371` | `g1-pro-tier` |
| 2 | `vicgnome19096@gmail.com` | `38782750-7a60-46d4-ae3f-e8c13cda296b` | `g1-pro-tier` |
| 3 | `vicgnome19095@gmail.com` | `a59369ac-c8a9-40f7-ad21-fc7c7bc7a4a9` | `g1-pro-tier` |
| 4 | `vicgnome19094@gmail.com` | `62af823b-f3d7-4e6b-87a9-98069167d4f6` | `g1-ultra-tier` |
| 5 | `vicgnome19091@gmail.com` | `47f334b1-b801-41f6-a709-4ebabb7a86d6` | `g1-pro-tier` |
| 6 | `vicgnome19086@gmail.com` | `9d66311f-9db7-49b2-90f5-277c5f311f2a` | `g1-pro-tier` |
| 7 | `vicgnome19088@gmail.com` | `615a4993-68ce-4a6b-be58-ed376be8ae63` | `g1-pro-tier` |
| 8 | `phamkive425@gmail.com` | `20369f65-4fae-4fa0-b02b-4f15047bee79` | `g1-pro-tier` |
| 9 | `ascenddevtwo@gmail.com` | `d5c3465f-9797-4b4b-a937-c3e653e168fb` | `g1-pro-tier` |
| 10 | `vinhvumobile@gmail.com` | `0532bad4-2486-4286-8f06-510e9c678620` | `g1-ultra-tier` |
| 11 | `vicgnome19097@gmail.com` | `ce95e1cb-27a4-433f-9c50-bdb6ad0b6b6b` | `free-tier` |
| 12 | `vicgnome1908@gmail.com` | `d71506bf-5952-4805-82e0-125cef2941ce` | `g1-pro-tier` |
| 13 | `vicle1908@gmail.com` | `cdac4585-b65a-4134-aa11-9544f7e42245` | `g1-pro-tier` |
| 14 | `ghtkmobile@gmail.com` | `d902fb26-520d-4316-9f2c-6e52c5da7b74` | `g1-pro-tier` |
| 15 | `vinhghtk1908@gmail.com` | `338764b8-1cd7-4946-b789-ee5dad4c5073` | `g1-ultra-tier` |

### 2. Pure 15-Step Homogeneous Combo Structure
- **Steps 1 to 15**: Explicit model steps with `kind: "model"`, `connectionId`, `provider: "agy"`, `weight: 0`, and `label` set to the account email:
  - `claude-opus-5.5`: `model: "agy/claude-opus-4-6-thinking"`
  - `claude-sonnet-5.5`: `model: "agy/claude-sonnet-4-6"`
- Why no `combo-ref: gemini-3.8-flash-high` step inside the `auto` combo: Under `strategy: "auto"`, `resolveAutoStrategyOrder` scores all resolved targets simultaneously without tier/step boundaries, causing a cheaper/faster fallback model (`gemini-3.8-flash-high`, `score=0.682`) to outscore the primary Claude models on every request. With 15 independent Antigravity accounts in the pool, account-level failover across 15 connections provides 15x redundancy natively while guaranteeing every response comes from the requested Claude model family.

### 3. Future Upstream 5.5 Cutover Contract
- When Google Antigravity provisions and advertises `claude-opus-5-5-*` or `claude-sonnet-5-5-*` in `GET /api/providers/client` or `POST /api/providers/{id}/sync-models`, update the `model` property on steps 1–15 from `agy/claude-opus-4-6-thinking` / `agy/claude-sonnet-4-6` to the new upstream model IDs via `PUT /api/combos/{id}`, keeping all 15 connection IDs unchanged.

## Risks / Trade-offs

- **Risk**: An upstream Google token expiry or rate-limit on one account could fail an individual attempt.
  - **Mitigation**: `strategy: "auto"` with 15 accounts automatically skips cooling/expired connections and fails over across the remaining 14 accounts.
