# Proposal

## Why

The `gemini-4-argon` parent combo and its tier sub-combos (`gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`) only included **2** explicit connection-scoped model steps for Google AI Ultra Antigravity accounts (`vinhvumobile@gmail.com` and `vinhghtk1908@gmail.com`), even though `vicgnome19094@gmail.com` (`connectionId: 62af823b-f3d7-4e6b-87a9-98069167d4f6`, `subscriptionTier: "Google AI Ultra"`) is also an active Ultra account with `gemini-4-argon-*` access. Since only Google AI Ultra accounts have `gemini-4-argon` access, each of the four argon combos should route across all **3** Ultra accounts to maximize capacity, quota availability, and failover resilience.

## What Changes

- Update `gemini-4-argon` (parent), `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` combos via `GET /api/combos/{id}` -> merge existing `config` -> `PUT /api/combos/{id}` to include all 3 Ultra-tier Antigravity accounts (`62af823b-f3d7-4e6b-87a9-98069167d4f6`, `0532bad4-2486-4286-8f06-510e9c678620`, `338764b8-1cd7-4946-b789-ee5dad4c5073`) with `context_cache_protection: false` and preserved `auto` routing settings.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `omniroute-compression-and-routing`: Add requirement for three-Ultra-account `gemini-4-argon*` combo routing and failover verification.

## Impact

- OmniRoute live combos in `/app/data/storage.sqlite` (`combos` table).
- No upstream source file changes in `/Users/androidteam/Omniroute/`.
