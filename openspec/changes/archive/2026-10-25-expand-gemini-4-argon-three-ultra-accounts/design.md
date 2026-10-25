# Design

## Context

Live `provider_connections` in `/app/data/storage.sqlite` shows 15 active `agy` OAuth accounts, of which exactly **3** have `tier: "g1-ultra-tier"` / `subscriptionTier: "Google AI Ultra"` (the only tier with `gemini-4-argon` access).

## Goals / Non-Goals

**Goals:**
- Configure `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` combos to route across all 3 Ultra accounts with per-connection model steps.
- Preserve existing `auto` routing config (`zeroLatencyOptimizationsEnabled: true`, `predictiveTtftMs: 25000`, `hedging: false`, `fallbackCompressionMode: "off"`, `candidatePool: ["agy"]`) and set `context_cache_protection: false`.

**Non-Goals:**
- Modifying upstream git-tracked files in `/Users/androidteam/Omniroute/`.
- Adding non-Ultra (`g1-pro-tier` or `free-tier`) accounts to `gemini-4-argon*` combos.

## Decisions

### 1. Three Ultra Account Connections
| Ultra Account | `connectionId` |
|---|---|
| `vicgnome19094@gmail.com` | `62af823b-f3d7-4e6b-87a9-98069167d4f6` |
| `vinhvumobile@gmail.com` | `0532bad4-2486-4286-8f06-510e9c678620` |
| `vinhghtk1908@gmail.com` | `338764b8-1cd7-4946-b789-ee5dad4c5073` |

### 2. Combo Update Mechanics
- `GET /api/combos/{id}` first, merge `config` without dropping existing keys (`sqliteComboRepository` replaces `config` on partial update), and call `PUT /api/combos/{id}` with `models: [...]` where each step is `{ id, model: "agy/gemini-4-argon-{tier}", connectionId, provider: "agy", weight: 0 }`.
- Parent `gemini-4-argon` (`id: f1cefc64-7662-4f0a-9234-84f70603cbe4`) routes to `agy/gemini-4-argon-high` across all 3 Ultra connections.

## Risks / Trade-offs

- **Risk**: Dropping existing combo `config` keys on `PUT /api/combos/{id}` would lose predictive TTFT, candidate pool, and fallback compression settings.
  - **Mitigation**: Fetch current combo and merge `config` before each PUT.
