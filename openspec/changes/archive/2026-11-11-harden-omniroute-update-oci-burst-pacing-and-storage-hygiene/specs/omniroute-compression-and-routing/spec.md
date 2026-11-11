# omniroute-compression-and-routing Spec Delta

## MODIFIED Requirements

### Requirement: Quota-Weighted Concurrency Balancing, Ultra Pool Isolation, and Rate-Limit Queue Scaling Across Antigravity Combos
OmniRoute SHALL configure multi-account Antigravity (`agy`) combos (`gemini-4-argon*`, `gemini-3.8-flash-high`, `claude-opus-5.5`, `claude-sonnet-5.5`) with `strategy: "quota-weighted"`, isolate `gemini-3.8-flash-high`, `claude-opus-5.5`, and `claude-sonnet-5.5` to the 11 active Pro `agy` accounts, disable `rateLimitProtection` on active `agy` connections, and scale `settings.requestQueue` to 64 concurrent requests with zero inter-request pacing delay (`minTimeBetweenRequestsMs: 0`).

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
- **WHEN** `provider_connections` (`provider = 'agy' AND is_active = 1`) and `GET /api/resilience` (`GET /api/settings`) are inspected
- **THEN** all 14 active `agy` connections SHALL have `rate_limit_protection = 0` (`rateLimitProtection: false`) so individual connections are not locally serialized at 20 concurrent requests
- **AND** `settings.requestQueue` SHALL be configured with `concurrentRequests: 64`, `requestsPerMinute: 600`, `minTimeBetweenRequestsMs: 0`, and `maxWaitMs: 15000` so Bottleneck limiters (`resolveMinTime(0) === 0`) dispatch simultaneous subagent bursts immediately without `200 ms` (`5 req/s`) inter-arrival serialization, while `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED` and `COMBO_AUTO_PRUNE_STALE_STEPS` remain `"false"` in `feature_flags`

## ADDED Requirements

### Requirement: Invalid Provider Quarantine, 14-Combo Assignment Reconciliation, and Banned Account Blocklist Preservation
OmniRoute SHALL deactivate invalid API-key provider connection `f3aaa87c-4af7-4a83-a636-98983119b9bc` (`pm`) and remove unused combo `phanmemvip` (`ad4dace4-9072-42a8-8503-e6188e325890`), SHALL reconcile `compression_combo_assignments` exclusively to the 14 active workstation combo UUIDs, and SHALL preserve inactive banned `agy` rows (`is_active = 0`, `test_status = 'banned'`) as an import-deduplication safety blocklist.

#### Scenario: Invalid `pm` connection deactivated and unused `phanmemvip` combo removed
- **WHEN** `GET /api/providers` and `GET /api/combos` are queried
- **THEN** connection `f3aaa87c-4af7-4a83-a636-98983119b9bc` (`anthropic-compatible-6408e370-2373-4ae0-9942-7f4095ba976c`, prefix `pm`) SHALL have `isActive: false` (`is_active = 0`) and `healthCheckInterval: 0` so validation sweeps never emit `HTTP 401 ("Invalid API key")` errors
- **AND** unused combo `phanmemvip` (`ad4dace4-9072-42a8-8503-e6188e325890`) SHALL be absent from `combos`, leaving the exact 14 active workstation combos (`gemini-4-carbon{,-high,-medium,-low}`, `gemini-4-argon{,-high,-medium,-low}`, `gemini-3.8-flash-high`, `claude-opus-5.5`, `claude-sonnet-5.5`, `deepseek-v4.1-flash`, `kimi-k3.1-pro`, `muse-spark-1.3`)

#### Scenario: `compression_combo_assignments` reconciled to the 14 active combo UUIDs without orphaned or duplicate rows
- **WHEN** `PUT /api/context/combos/default-caveman/assignments` is applied with the 14 active combo UUIDs and `compression_combo_assignments` is inspected
- **THEN** `compression_combo_assignments` SHALL contain exactly 14 rows matching the 14 active `combos.id` UUIDs (`0` plain-name duplicates and `0` orphaned rows referencing deleted combos such as `phanmemvip`)

#### Scenario: Inactive banned Antigravity connections retained as import blocklist with zero sweep overhead
- **WHEN** `provider_connections` (`provider = 'agy' AND is_active = 0 AND test_status = 'banned'`) is inspected or `findExistingAgyConnection` runs during bulk/CLI OAuth import
- **THEN** all 9 banned `agy` rows SHALL remain present with `is_active = 0` so `findExistingAgyConnection` rejects accidental re-import with `409 duplicate_account` while `tokenHealthCheck` (`!conn.isActive`) skips them with zero outbound network requests
