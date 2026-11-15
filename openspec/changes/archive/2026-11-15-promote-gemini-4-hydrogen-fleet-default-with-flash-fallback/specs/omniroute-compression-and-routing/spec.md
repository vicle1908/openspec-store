# Spec Delta: omniroute-compression-and-routing

## MODIFIED Requirements

### Requirement: Subset-Account Stickiness, Nested Combo Execution, and Active Target Hygiene

OmniRoute combos targeting Antigravity (`agy`) connection subsets SHALL set `context_cache_protection: false`, `muse-spark-1.3` SHALL set `strategy: "priority"`, `config.nestedComboMode: "execute"`, and `config.targetTimeoutMs: 180000` referencing `gemini-4-hydrogen-high` ahead of `combo-ref: gemini-3.8-flash-high` fallback, `claude-opus-5.5` and `claude-sonnet-5.5` SHALL set `strategy: "quota-weighted"` across active non-banned Pro `agy` accounts, and combos SHALL NOT retain banned (`38782750`, `ea0d6c23`) or zero-active-connection targets.

#### Scenario: Multi-turn conversation on subset-account combo
- **WHEN** a client executes Turn 2 or later against `gemini-4-hydrogen*`, `gemini-3.8-flash-high`, `gemini-4-argon*`, `muse-spark-1.3`, or `claude-opus-5.5`
- **THEN** OmniRoute SHALL route the request using connection-level session stickiness (`applySessionStickiness`) without logging false `provider durably unhealthy — dropping pin` warnings or escaping the combo's configured connections

#### Scenario: Nested combo-ref execution on `muse-spark-1.3` and auto-scored pool on `claude-opus-5.5`
- **WHEN** `muse-spark-1.3` dispatches to its primary `combo-ref` target (`gemini-4-hydrogen-high`)
- **THEN** OmniRoute SHALL execute `gemini-4-hydrogen-high` as an encapsulated runtime unit (`nestedComboMode: "execute"`, `targetTimeoutMs: 180000`) before falling back to `combo-ref: gemini-3.8-flash-high` (with banned `ea0d6c23` absent), while `claude-opus-5.5` (`strategy: "quota-weighted"`, `targetTimeoutMs: 180000`, `predictiveTtftMs: 0`) SHALL balance across the 10 active non-banned Pro Antigravity accounts (excluding banned `38782750`) and preserve `applySessionStickiness`

### Requirement: Dedicated 11-Pro-Account Auto Pool for `gemini-3.8-flash-high` and Ultra Quota Isolation
OmniRoute SHALL configure `gemini-3.8-flash-high` (`7555d851-b4f3-44c6-b1fb-c6fdceabf388`) with `strategy: "quota-weighted"`, `context_cache_protection: false`, `targetTimeoutMs: 120000`, `predictiveTtftMs: 0`, and 10 `kind: "model"` steps scoped exclusively to active non-banned `g1-pro-tier` `agy` connections with remaining quota (excluding Ultra `62af823b` and banned `38782750`, `ea0d6c23`, `47f334b1`, `d5c3465f`, `20369f65`).

#### Scenario: `gemini-3.8-flash-high` routes across the 11 Pro accounts without consuming Ultra Gemini quota
- **WHEN** `GET /api/combos/7555d851-b4f3-44c6-b1fb-c6fdceabf388` (`gemini-3.8-flash-high`) is inspected or invoked as a fallback pool
- **THEN** `strategy` SHALL be `"quota-weighted"`, `context_cache_protection` SHALL be `false`, and `models` SHALL contain 10 `agy/gemini-3.8-flash-high` steps mapped to active non-banned Pro `agy` connections (`9d66311f`, `ce95e1cb`, `9c033d6f`, `37f9924d`, `573e3f41`, `3f3085b1`, `a94216f4`, `a7580e21`, `f511d061`, `9ad0a196`)
- **AND** banned `38782750` and active Ultra `62af823b` SHALL NOT appear in `gemini-3.8-flash-high`

#### Scenario: All 3 Ultra accounts and 11 Pro accounts enforce `rateLimitProtection: true`
- **WHEN** `GET /api/rate-limits` is queried
- **THEN** active `g1-ultra-tier` and `g1-pro-tier` `agy` accounts SHALL report valid rate-limit state without dispatching to banned `38782750` or `ea0d6c23`

### Requirement: Quota-Weighted Concurrency Balancing, Ultra Pool Isolation, and Rate-Limit Queue Scaling Across Antigravity Combos
OmniRoute SHALL configure multi-account Antigravity (`agy`) combos (`gemini-4-argon*`, `gemini-3.8-flash-high`, `claude-opus-5.5`, `claude-sonnet-5.5`) with `strategy: "quota-weighted"`, isolate `gemini-3.8-flash-high`, `claude-opus-5.5`, and `claude-sonnet-5.5` to the 10 active non-banned Pro `agy` accounts (excluding banned `38782750` and Ultra `62af823b`), disable `rateLimitProtection` on active `agy` connections, and scale `settings.requestQueue` to 64 concurrent requests with zero inter-request pacing delay (`minTimeBetweenRequestsMs: 0`).

#### Scenario: Argon combos prune unentitled Pro accounts and balance across the 3 Ultra accounts via quota-weighted routing
- **WHEN** `GET /api/combos` is queried for `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low`
- **THEN** each combo SHALL have `strategy: "quota-weighted"`, `context_cache_protection: false`, `config.targetTimeoutMs: 180000`, `config.predictiveTtftMs: 0`, `config.quotaWeightedFloorPercent: 5`, and 3 `kind: "model"` steps (`0532bad4`, `338764b8`, `62af823b`)

#### Scenario: `gemini-3.8-flash-high` routes exclusively across the 11 active Pro accounts without Ultra quota bleed
- **WHEN** `GET /api/combos/7555d851-b4f3-44c6-b1fb-c6fdceabf388` (`gemini-3.8-flash-high`) is queried or invoked under concurrent subagent load
- **THEN** `strategy` SHALL be `"quota-weighted"`, `config.targetTimeoutMs` SHALL be `120000`, `config.predictiveTtftMs` SHALL be `0`, and `models` SHALL contain 10 `agy/gemini-3.8-flash-high` steps pinned to the 10 active non-banned Pro `agy` connections (`9c033d6f`, `37f9924d`, `573e3f41`, `3f3085b1`, `a94216f4`, `a7580e21`, `f511d061`, `9ad0a196`, `9d66311f`, `ce95e1cb`), with banned `38782750` and Ultra `62af823b` absent

#### Scenario: `claude-opus-5.5` and `claude-sonnet-5.5` route exclusively across the 11 active Pro Antigravity accounts with native 5.5 tiers on the 9 entitled accounts
- **WHEN** `GET /api/combos` is queried for `claude-opus-5.5` (`4b2430da-0b3b-4b0e-9773-ec0f97adc252`) and `claude-sonnet-5.5` (`9447399c-856b-4f52-8820-b3bf3dc3f132`)
- **THEN** both combos SHALL configure `strategy: "quota-weighted"`, `context_length: 1000000`, `context_cache_protection: false`, `config.quotaWeightedFloorPercent: 1`, and 10 `kind: "model"` steps covering the 10 active non-banned Pro `agy` connections (excluding banned `38782750` and Ultra `62af823b`)
- **AND** the 8 active Pro connections advertising native 5.5 (`9c033d6f`, `37f9924d`, `573e3f41`, `3f3085b1`, `a94216f4`, `a7580e21`, `f511d061`, `9ad0a196`) SHALL use `agy/claude-opus-5-5-high` and `agy/claude-sonnet-5-5-high`, while `9d66311f` and `ce95e1cb` SHALL use `agy/claude-opus-4-6-thinking` and `agy/claude-sonnet-4-6`

#### Scenario: All 14 active Antigravity connections disable local rateLimitProtection and requestQueue scales to 64 concurrent requests
- **WHEN** `provider_connections` (`provider = 'agy' AND is_active = 1`) and `GET /api/settings` are inspected
- **THEN** active `agy` connections SHALL have `rate_limit_protection = 0` (`rateLimitProtection: false`) and `settings.requestQueue` SHALL configure `concurrentRequests: 64`, `requestsPerMinute: 600`, `minTimeBetweenRequestsMs: 0`, and `maxWaitMs: 15000`

### Requirement: Gemini 4 Hydrogen Capability Overrides and Priority Tier Combos
OmniRoute SHALL persist capability and context overrides (`1,048,576` context, `262,144` max output tokens, and `low,medium,high,xhigh` reasoning efforts) for the four Antigravity `gemini-4-hydrogen-{low,medium,high,xhigh}` models and SHALL configure 5 priority-strategy Hydrogen combos across the 6 active entitled Google AI accounts (`5` WTU Pro + `1` Ultra `62af823b`, excluding banned `38782750`) without embedding `gemini-3.8-flash-high` steps inside `gemini-4-hydrogen*`.

#### Scenario: Model synchronization and 16 single-key capability overrides unlock Hydrogen 262,144 max output tokens and reasoning efforts
- **WHEN** `GET /api/model-capability-overrides` and `GET /v1/models` (`Accept-Encoding: gzip`) are queried
- **THEN** `antigravity/gemini-4-hydrogen-{low,medium,high,xhigh}` overrides SHALL persist `context_length: "1048576"`, `max_input_tokens: "1048576"`, `max_output_tokens: "262144"`, and `reasoning_efforts: "low,medium,high,xhigh"`
- **AND** `GET /v1/models` SHALL advertise `max_output_tokens: 262144` on all 5 `gemini-4-hydrogen*` combos (preserved because no `65536`-capped Flash step is nested inside Hydrogen combos) while total gzipped download payload remains `<= 35,000` bytes

#### Scenario: Five Gemini 4 Hydrogen priority combos route WTU-Pro-first ahead of Ultra account 62af823b
- **WHEN** `GET /api/combos` is queried for `gemini-4-hydrogen{,-xhigh,-high,-medium,-low}`
- **THEN** homogeneous tier combos `gemini-4-hydrogen-xhigh`, `gemini-4-hydrogen-high`, `gemini-4-hydrogen-medium`, and `gemini-4-hydrogen-low` SHALL configure `strategy: "priority"`, `context_length: 1000000`, `context_cache_protection: false`, `config.failoverBeforeRetry: true`, `config.retryDelayMs: 500`, `config.fallbackDelayMs: 0`, `config.targetTimeoutMs: 180000`, `config.predictiveTtftMs: 0`, `config.hedging: false`, `config.fallbackCompressionMode: "off"`, `config.candidatePool: ["agy"]`, and all four `reset*QuotaCache*` keys (`300000` ms TTL, `3600000` ms max-stale)
- **AND** each tier combo SHALL contain the 6 active `kind: "model"` steps targeting `agy/gemini-4-hydrogen-{xhigh,high,medium,low}` in WTU-Pro-first order `[9c033d6f-ec87-42f7-9e8a-e42858a7644c, 62af823b-f3d7-4e6b-87a9-98069167d4f6, 37f9924d-7480-44e5-9c2e-f04b10cc2de1, 573e3f41-5d58-4e3f-9af3-4cb4efffb721, 3f3085b1-a0f3-4771-b500-c3747bea3bd1, a94216f4-907f-4aec-a38d-e5250697f258]`, excluding banned `38782750`
- **AND** top-level combo `gemini-4-hydrogen` SHALL reference `comboName: "gemini-4-hydrogen-high"` with the identical `config` object and zero Flash steps
