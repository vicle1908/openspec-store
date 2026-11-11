# omniroute-compression-and-routing Spec Delta

## ADDED Requirements

### Requirement: Gemini 4 Carbon Tier Combos and SQLite Capability Overrides Without Source Modifications
OmniRoute SHALL expose four top-level Google Gemini 4 Carbon combos (`gemini-4-carbon`, `gemini-4-carbon-high`, `gemini-4-carbon-medium`, and `gemini-4-carbon-low`) routed via `strategy: "quota-weighted"` across the three entitled Google AI Ultra `agy` connections and SHALL persist SQLite capability and context overrides (`1,048,576` context, `262,144` max output tokens, `["low", "medium", "high"]` efforts) without modifying git-tracked source code.

#### Scenario: SQLite capability and context overrides unlock 262,144 output tokens and 1M context for Carbon tiers
- **WHEN** 12 single-key `PATCH http://127.0.0.1:20128/api/model-capability-overrides` requests (`3 models × 4 keys`, passing `"low,medium,high"` as a comma-separated string for `reasoning_efforts`) are applied and `GET /api/model-capability-overrides` + `GET /v1/models` are queried
- **THEN** `antigravity/gemini-4-carbon-high`, `antigravity/gemini-4-carbon-medium`, and `antigravity/gemini-4-carbon-low` SHALL each report persisted overrides for `context_length: 1048576`, `max_input_tokens: 1048576`, `max_output_tokens: 262144`, and `reasoning_efforts: ["low", "medium", "high"]`
- **AND** top-level combos `gemini-4-carbon`, `gemini-4-carbon-high`, `gemini-4-carbon-medium`, and `gemini-4-carbon-low` in `/v1/models` (`owned_by: "combo"`) SHALL advertise `context_length: 1000000` and `max_output_tokens: 262144` without rejecting requests carrying `max_tokens > 65536` up to `262144`

#### Scenario: Four Gemini 4 Carbon combos route exclusively across the three Ultra Antigravity accounts via quota-weighted strategy
- **WHEN** `GET http://127.0.0.1:20128/api/combos` is queried
- **THEN** combos `gemini-4-carbon`, `gemini-4-carbon-high`, `gemini-4-carbon-medium`, and `gemini-4-carbon-low` SHALL each be active with `strategy: "quota-weighted"`, `context_length: 1000000`, `context_cache_protection: false`, `config.targetTimeoutMs: 180000`, `config.predictiveTtftMs: 0`, `config.quotaWeightedFloorPercent: 5`, `config.quotaWeightedScoring: "leftover"`, `config.resetAwareQuotaCacheTtlMs: 300000`, `config.resetWindowQuotaCacheTtlMs: 300000`, and `config.resetAwareQuotaCacheMaxStaleMs: 3600000`
- **AND** `gemini-4-carbon` and `gemini-4-carbon-high` SHALL each contain exactly 3 `kind: "model"` steps with `model: "agy/gemini-4-carbon-high"` pinned to `0532bad4-2486-4286-8f06-510e9c678620` (`vinhvumobile@gmail.com`), `338764b8-1cd7-4946-b789-ee5dad4c5073` (`vinhghtk1908@gmail.com`), and `62af823b-f3d7-4e6b-87a9-98069167d4f6` (`vicgnome19094@gmail.com`), while `gemini-4-carbon-medium` and `gemini-4-carbon-low` SHALL map those same 3 Ultra connections to `agy/gemini-4-carbon-medium` and `agy/gemini-4-carbon-low` respectively
- **AND** zero non-Ultra (`g1-pro-tier`) `connectionId` values SHALL appear in any `gemini-4-carbon*` combo

#### Scenario: Concurrent Carbon inference distributes load by remaining quota and in-flight count
- **WHEN** concurrent `POST /v1/chat/completions` or `POST /v1/responses` requests target `gemini-4-carbon` or `gemini-4-carbon-high`
- **THEN** OmniRoute SHALL weight candidate selection by `score / (1 + inflight)` across the 3 Ultra accounts, reserve `inflight` synchronously in the same event-loop turn before yielding, and return `HTTP 200` completions with zero `429` dispatches to unentitled Pro accounts

### Requirement: Quota-Weighted Concurrency Balancing, Ultra Pool Isolation, and Rate-Limit Queue Scaling Across Antigravity Combos
OmniRoute SHALL configure multi-account Antigravity (`agy`) combos (`gemini-4-argon*`, `gemini-3.8-flash-high`, `claude-opus-5.5`, `claude-sonnet-5.5`) with `strategy: "quota-weighted"`, isolate `gemini-3.8-flash-high`, `claude-opus-5.5`, and `claude-sonnet-5.5` to the 11 active Pro `agy` accounts, disable `rateLimitProtection` on active `agy` connections, and scale `settings.requestQueue` to 64 concurrent requests.

#### Scenario: Argon combos prune unentitled Pro accounts and balance across the 3 Ultra accounts via quota-weighted routing
- **WHEN** `GET /api/combos` is queried for `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low`
- **THEN** each combo SHALL have `strategy: "quota-weighted"`, `context_cache_protection: false`, `config.targetTimeoutMs: 180000`, `config.predictiveTtftMs: 0`, `config.quotaWeightedFloorPercent: 5`, and exactly 3 `kind: "model"` steps pinned to the 3 Ultra `agy` accounts (`0532bad4`, `338764b8`, `62af823b`), with all 7 exhausted/unentitled Pro `agy` steps removed

#### Scenario: `gemini-3.8-flash-high` routes exclusively across the 11 active Pro accounts without Ultra quota bleed
- **WHEN** `GET /api/combos/7555d851-b4f3-44c6-b1fb-c6fdceabf388` (`gemini-3.8-flash-high`) is queried or invoked under concurrent subagent load
- **THEN** `strategy` SHALL be `"quota-weighted"`, `config.targetTimeoutMs` SHALL be `120000`, `config.predictiveTtftMs` SHALL be `0`, and `models` SHALL contain 11 `agy/gemini-3.8-flash-high` steps pinned to the 11 active Google AI Pro `agy` connections (`38782750`, `9d66311f`, `ce95e1cb`, `9c033d6f`, `37f9924d`, `573e3f41`, `3f3085b1`, `a94216f4`, `a7580e21`, `f511d061`, `9ad0a196`)
- **AND** none of the 3 Ultra `agy` accounts (`62af823b`, `0532bad4`, `338764b8`) SHALL appear in `gemini-3.8-flash-high`, preserving Ultra weekly quota exclusively for `gemini-4-argon*` and `gemini-4-carbon*`

#### Scenario: `claude-opus-5.5` and `claude-sonnet-5.5` route exclusively across the 11 active Pro Antigravity accounts with native 5.5 tiers on the 9 entitled accounts
- **WHEN** `GET /api/combos` is queried for `claude-opus-5.5` (`4b2430da-0b3b-4b0e-9773-ec0f97adc252`) and `claude-sonnet-5.5` (`9447399c-856b-4f52-8820-b3bf3dc3f132`)
- **THEN** both combos SHALL configure `strategy: "quota-weighted"`, `context_length: 1000000`, `context_cache_protection: false`, `config.quotaWeightedFloorPercent: 1`, and 11 `kind: "model"` steps covering the 11 active Google AI Pro `agy` connections (excluding the 3 Ultra accounts `0532bad4`, `338764b8`, and `62af823b` so Claude usage cannot trigger `genericQuotaFetcher.ts`'s unscoped `argon` family quota aggregation)
- **AND** the 9 Pro connections advertising native 5.5 in `syncedAvailableModels` (`38782750`, `9c033d6f`, `37f9924d`, `573e3f41`, `3f3085b1`, `a94216f4`, `a7580e21`, `f511d061`, `9ad0a196`) SHALL use `agy/claude-opus-5-5-high` and `agy/claude-sonnet-5-5-high`, while the remaining 2 active Pro connections (`9d66311f`, `ce95e1cb`) SHALL use `agy/claude-opus-4-6-thinking` and `agy/claude-sonnet-4-6`

#### Scenario: All 14 active Antigravity connections disable local rateLimitProtection and requestQueue scales to 64 concurrent requests
- **WHEN** `provider_connections` (`provider = 'agy' AND is_active = 1`) and `GET /api/settings` are inspected
- **THEN** all 14 active `agy` connections SHALL have `rate_limit_protection = 0` (`rateLimitProtection: false`) so individual connections are not locally serialized at 20 concurrent requests
- **AND** `settings.requestQueue` SHALL be configured with `concurrentRequests: 64`, `requestsPerMinute: 600`, and `maxWaitMs: 15000`, while `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED` and `COMBO_AUTO_PRUNE_STALE_STEPS` remain `"false"` in `feature_flags`
