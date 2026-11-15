# Spec Delta

## MODIFIED Requirements

### Requirement: Gemini 4 Carbon Tier Combos and SQLite Capability Overrides Without Source Modifications
OmniRoute SHALL expose four top-level Google Gemini 4 Carbon combos (`gemini-4-carbon`, `gemini-4-carbon-high`, `gemini-4-carbon-medium`, and `gemini-4-carbon-low`) routed via `strategy: "quota-weighted"` across the active non-banned Google AI Ultra `agy` connections (`0532bad4`, `338764b8`, excluding banned `62af823b`) and SHALL persist SQLite capability and context overrides (`1,048,576` context, `262,144` max output tokens, `["low", "medium", "high"]` efforts) without modifying git-tracked source code.

#### Scenario: SQLite capability and context overrides unlock 262,144 output tokens and 1M context for Carbon tiers
- **WHEN** 12 single-key `PATCH http://127.0.0.1:20128/api/model-capability-overrides` requests (`3 models × 4 keys`, passing `"low,medium,high"` as a comma-separated string for `reasoning_efforts`) are applied and `GET /api/model-capability-overrides` + `GET /v1/models` are queried
- **THEN** `antigravity/gemini-4-carbon-high`, `antigravity/gemini-4-carbon-medium`, and `antigravity/gemini-4-carbon-low` SHALL each report persisted overrides for `context_length: 1048576`, `max_input_tokens: 1048576`, `max_output_tokens: 262144`, and `reasoning_efforts: ["low", "medium", "high"]`
- **AND** top-level combos `gemini-4-carbon`, `gemini-4-carbon-high`, `gemini-4-carbon-medium`, and `gemini-4-carbon-low` in `/v1/models` (`owned_by: "combo"`) SHALL advertise `context_length: 1000000` and `max_output_tokens: 262144` without rejecting requests carrying `max_tokens > 65536` up to `262144`

#### Scenario: Four Gemini 4 Carbon combos route exclusively across the three Ultra Antigravity accounts via quota-weighted strategy
- **WHEN** `GET http://127.0.0.1:20128/api/combos` is queried
- **THEN** combos `gemini-4-carbon`, `gemini-4-carbon-high`, `gemini-4-carbon-medium`, and `gemini-4-carbon-low` SHALL each be active with `strategy: "quota-weighted"`, `context_length: 1000000`, `context_cache_protection: false`, `config.targetTimeoutMs: 180000`, `config.predictiveTtftMs: 0`, `config.quotaWeightedFloorPercent: 5`, `config.quotaWeightedScoring: "leftover"`, `config.resetAwareQuotaCacheTtlMs: 300000`, `config.resetWindowQuotaCacheTtlMs: 300000`, and `config.resetAwareQuotaCacheMaxStaleMs: 3600000`
- **AND** `gemini-4-carbon` and `gemini-4-carbon-high` SHALL each contain exactly 2 `kind: "model"` steps with `model: "agy/gemini-4-carbon-high"` pinned to `0532bad4-2486-4286-8f06-510e9c678620` (`vinhvumobile@gmail.com`) and `338764b8-1cd7-4946-b789-ee5dad4c5073` (`vinhghtk1908@gmail.com`), while `gemini-4-carbon-medium` and `gemini-4-carbon-low` SHALL map those same 2 active Ultra connections to `agy/gemini-4-carbon-medium` and `agy/gemini-4-carbon-low` respectively
- **AND** banned Ultra connection `62af823b-f3d7-4e6b-87a9-98069167d4f6` (`vicgnome19094@gmail.com`) and all non-Ultra (`g1-pro-tier`) `connectionId` values SHALL be absent from every `gemini-4-carbon*` combo

#### Scenario: Concurrent Carbon inference distributes load by remaining quota and in-flight count
- **WHEN** concurrent `POST /v1/chat/completions` or `POST /v1/responses` requests target `gemini-4-carbon` or `gemini-4-carbon-high`
- **THEN** OmniRoute SHALL weight candidate selection by `score / (1 + inflight)` across the 2 active Ultra accounts, reserve `inflight` synchronously in the same event-loop turn before yielding, and return `HTTP 200` completions with zero `429` dispatches to unentitled Pro accounts or banned `62af823b`

### Requirement: Quota-Weighted Concurrency Balancing, Ultra Pool Isolation, and Rate-Limit Queue Scaling Across Antigravity Combos
OmniRoute SHALL configure multi-account Antigravity (`agy`) combos (`gemini-4-argon*`, `gemini-4-hydrogen*`, `gemini-3.8-flash-high`, `claude-opus-5.5`, `claude-sonnet-5.5`) with `strategy: "quota-weighted"`, isolate `gemini-3.8-flash-high`, `claude-opus-5.5`, and `claude-sonnet-5.5` to the 10 active non-banned Pro `agy` accounts (excluding banned `38782750` and `62af823b`), disable `rateLimitProtection` on active `agy` connections, and scale `settings.requestQueue` to 64 concurrent requests with zero inter-request pacing delay (`minTimeBetweenRequestsMs: 0`).

#### Scenario: Argon combos prune unentitled Pro accounts and balance across the 3 Ultra accounts via quota-weighted routing
- **WHEN** `GET /api/combos` is queried for `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low`
- **THEN** each combo SHALL have `strategy: "quota-weighted"`, `context_cache_protection: false`, `config.targetTimeoutMs: 180000`, `config.predictiveTtftMs: 0`, `config.quotaWeightedFloorPercent: 5`, and 2 `kind: "model"` steps (`0532bad4`, `338764b8`), with banned `62af823b` absent

#### Scenario: `gemini-3.8-flash-high` routes exclusively across the 11 active Pro accounts without Ultra quota bleed
- **WHEN** `GET /api/combos/7555d851-b4f3-44c6-b1fb-c6fdceabf388` (`gemini-3.8-flash-high`) is queried or invoked under concurrent subagent load
- **THEN** `strategy` SHALL be `"quota-weighted"`, `config.targetTimeoutMs` SHALL be `120000`, `config.predictiveTtftMs` SHALL be `0`, and `models` SHALL contain 10 `agy/gemini-3.8-flash-high` steps pinned to the 10 active non-banned Pro `agy` connections (`9c033d6f`, `37f9924d`, `573e3f41`, `3f3085b1`, `a94216f4`, `a7580e21`, `f511d061`, `9ad0a196`, `9d66311f`, `ce95e1cb`), with banned `38782750` and `62af823b` absent

#### Scenario: `claude-opus-5.5` and `claude-sonnet-5.5` route exclusively across the 11 active Pro Antigravity accounts with native 5.5 tiers on the 9 entitled accounts
- **WHEN** `GET /api/combos` is queried for `claude-opus-5.5` (`4b2430da-0b3b-4b0e-9773-ec0f97adc252`) and `claude-sonnet-5.5` (`9447399c-856b-4f52-8820-b3bf3dc3f132`)
- **THEN** both combos SHALL configure `strategy: "quota-weighted"`, `context_length: 1000000`, `context_cache_protection: false`, `config.quotaWeightedFloorPercent: 1`, and 10 `kind: "model"` steps covering the 10 active non-banned Pro `agy` connections (excluding banned `38782750` and `62af823b`)
- **AND** the 8 active Pro connections advertising native 5.5 (`9c033d6f`, `37f9924d`, `573e3f41`, `3f3085b1`, `a94216f4`, `a7580e21`, `f511d061`, `9ad0a196`) SHALL use `agy/claude-opus-5-5-high` and `agy/claude-sonnet-5-5-high`, while `9d66311f` and `ce95e1cb` SHALL use `agy/claude-opus-4-6-thinking` and `agy/claude-sonnet-4-6`

#### Scenario: All 14 active Antigravity connections disable local rateLimitProtection and requestQueue scales to 64 concurrent requests
- **WHEN** `provider_connections` (`provider = 'agy' AND is_active = 1`) and `GET /api/settings` are inspected
- **THEN** active `agy` connections SHALL have `rate_limit_protection = 0` (`rateLimitProtection: false`) and `settings.requestQueue` SHALL configure `concurrentRequests: 64`, `requestsPerMinute: 600`, `minTimeBetweenRequestsMs: 0`, and `maxWaitMs: 15000`

### Requirement: Gemini 4 Hydrogen Capability Overrides and Priority Tier Combos
OmniRoute SHALL persist capability and context overrides (`1,048,576` context, `262,144` max output tokens, and `low,medium,high,xhigh` reasoning efforts) for the four Antigravity `gemini-4-hydrogen-{low,medium,high,xhigh}` models and SHALL configure the 4 Hydrogen tier combos (`gemini-4-hydrogen-{xhigh,high,medium,low}`) with `strategy: "quota-weighted"` across the 5 active entitled WTU-Pro Google AI accounts (`9c033d6f`, `37f9924d`, `573e3f41`, `3f3085b1`, `a94216f4`, excluding banned `38782750` and `62af823b`) without embedding `gemini-3.8-flash-high` steps inside `gemini-4-hydrogen*`.

#### Scenario: Model synchronization and 16 single-key capability overrides unlock Hydrogen 262,144 max output tokens and reasoning efforts
- **WHEN** `GET /api/model-capability-overrides` and `GET /v1/models` (`Accept-Encoding: gzip`) are queried
- **THEN** `antigravity/gemini-4-hydrogen-{low,medium,high,xhigh}` overrides SHALL persist `context_length: "1048576"`, `max_input_tokens: "1048576"`, `max_output_tokens: "262144"`, and `reasoning_efforts: "low,medium,high,xhigh"`
- **AND** `GET /v1/models` SHALL advertise `max_output_tokens: 262144` on all 5 `gemini-4-hydrogen*` combos (preserved because no `65536`-capped Flash step is nested inside Hydrogen combos) while total gzipped download payload remains `<= 35,000` bytes

#### Scenario: Five Gemini 4 Hydrogen priority combos route WTU-Pro-first ahead of Ultra account 62af823b
- **WHEN** `GET /api/combos` is queried for `gemini-4-hydrogen{,-xhigh,-high,-medium,-low}`
- **THEN** homogeneous tier combos `gemini-4-hydrogen-xhigh`, `gemini-4-hydrogen-high`, `gemini-4-hydrogen-medium`, and `gemini-4-hydrogen-low` SHALL configure `strategy: "quota-weighted"`, `context_length: 1000000`, `context_cache_protection: false`, `config.failoverBeforeRetry: true`, `config.retryDelayMs: 500`, `config.fallbackDelayMs: 0`, `config.targetTimeoutMs: 180000`, `config.predictiveTtftMs: 0`, `config.quotaWeightedFloorPercent: 5`, `config.quotaWeightedScoring: "leftover"`, `config.hedging: false`, `config.fallbackCompressionMode: "off"`, `config.candidatePool: ["agy"]`, and all four `reset*QuotaCache*` keys (`300000` ms TTL, `3600000` ms max-stale)
- **AND** each tier combo SHALL contain the 5 active `kind: "model"` steps targeting `agy/gemini-4-hydrogen-{xhigh,high,medium,low}` (`9c033d6f-ec87-42f7-9e8a-e42858a7644c`, `37f9924d-7480-44e5-9c2e-f04b10cc2de1`, `573e3f41-5d58-4e3f-9af3-4cb4efffb721`, `3f3085b1-a0f3-4771-b500-c3747bea3bd1`, `a94216f4-907f-4aec-a38d-e5250697f258`), excluding banned `38782750` and `62af823b`
- **AND** top-level combo `gemini-4-hydrogen` SHALL use `strategy: "quota-weighted"` (`nestedComboMode` unset/`"flatten"`, `config.quotaWeightedFloorPercent: 5`, `config.quotaWeightedScoring: "leftover"`, `config.predictiveTtftMs: 0`) referencing `comboName: "gemini-4-hydrogen-high"` with zero Flash steps so flattened target execution runs `orderTargetsByQuotaWeighted`
