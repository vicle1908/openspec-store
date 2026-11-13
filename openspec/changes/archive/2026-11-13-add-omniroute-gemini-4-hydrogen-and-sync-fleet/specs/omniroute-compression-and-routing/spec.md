# Spec Delta

## ADDED Requirements

### Requirement: Gemini 4 Hydrogen Capability Overrides and Priority Tier Combos
OmniRoute SHALL persist capability and context overrides (`1,048,576` context, `262,144` max output tokens, and `low,medium,high,xhigh` reasoning efforts) for the four Antigravity Gemini 4 Hydrogen tier models and SHALL expose five top-level Hydrogen combos routed via `strategy: "priority"` across the seven entitled Antigravity connections in WTU-Pro-first order.

#### Scenario: Ultra inventory sync and capability overrides unlock 262,144 output tokens across all four Hydrogen tiers
- **WHEN** Bearer-authenticated (`Authorization: Bearer $OMNIROUTE_API_KEY`) `POST /api/providers/62af823b-f3d7-4e6b-87a9-98069167d4f6/sync-models`, `DELETE /api/resilience/model-cooldowns` with body `{"all": true}`, and 16 single-key `PATCH /api/model-capability-overrides` requests (`4 models × 4 keys` with comma-separated `"low,medium,high,xhigh"` for `reasoning_efforts`) are applied and `GET /api/providers/62af823b-f3d7-4e6b-87a9-98069167d4f6/models`, `GET /api/model-capability-overrides`, and `GET /v1/models` are queried
- **THEN** `GET /api/providers/62af823b-f3d7-4e6b-87a9-98069167d4f6/models` SHALL list `gemini-4-hydrogen-{low,medium,high,xhigh}`, `gemini-4-argon-{low,medium,high}`, and `gemini-4-carbon-{low,medium,high}` without `-disabled` suffixes
- **AND** `GET /api/model-capability-overrides` SHALL report persisted `antigravity/gemini-4-hydrogen-{low,medium,high,xhigh}` overrides for `context_length: "1048576"`, `max_input_tokens: "1048576"`, `max_output_tokens: "262144"`, and `reasoning_efforts: "low,medium,high,xhigh"`
- **AND** `/v1/models` (`Accept-Encoding: gzip`, compressed payload `<= 35,000` bytes) SHALL advertise all five `gemini-4-hydrogen*` combos (`owned_by: "combo"`) with `context_length: 1000000` and `max_output_tokens: 262144`

#### Scenario: Five Hydrogen combos upsert idempotently in WTU-Pro-first priority order with a top-level combo-ref alias
- **WHEN** Bearer-authenticated `GET /api/combos` is queried after idempotent combo provisioning (matching by `name` before creating or updating so repeat or peer execution never fails with `HTTP 400 "Combo name already exists"`)
- **THEN** homogeneous tier combos `gemini-4-hydrogen-xhigh`, `gemini-4-hydrogen-high`, `gemini-4-hydrogen-medium`, and `gemini-4-hydrogen-low` SHALL be provisioned ahead of `gemini-4-hydrogen` with `strategy: "priority"`, `context_length: 1000000`, `context_cache_protection: false`, `config.failoverBeforeRetry: true`, `config.retryDelayMs: 500`, `config.fallbackDelayMs: 0`, `config.targetTimeoutMs: 180000`, `config.predictiveTtftMs: 0`, `config.hedging: false`, `config.fallbackCompressionMode: "off"`, `config.candidatePool: ["agy"]`, `config.resetAwareQuotaCacheTtlMs: 300000`, `config.resetAwareQuotaCacheMaxStaleMs: 3600000`, `config.resetWindowQuotaCacheTtlMs: 300000`, and `config.resetWindowQuotaCacheMaxStaleMs: 3600000`
- **AND** each tier combo SHALL contain 7 `kind: "model"` steps targeting `agy/gemini-4-hydrogen-{xhigh,high,medium,low}` in order `[38782750-7a60-46d4-ae3f-e8c13cda296b, 9c033d6f-ec87-42f7-9e8a-e42858a7644c, 62af823b-f3d7-4e6b-87a9-98069167d4f6, 37f9924d-7480-44e5-9c2e-f04b10cc2de1, 573e3f41-5d58-4e3f-9af3-4cb4efffb721, 3f3085b1-a0f3-4771-b500-c3747bea3bd1, a94216f4-907f-4aec-a38d-e5250697f258]`, failing over immediately (`0 ms`) to the next sibling on `HTTP 429` under concurrent bursts
- **AND** top-level combo `gemini-4-hydrogen` SHALL configure `strategy: "priority"`, `context_length: 1000000`, `context_cache_protection: false`, the identical `config` object (`failoverBeforeRetry: true`, `targetTimeoutMs: 180000`, `predictiveTtftMs: 0`, `candidatePool: ["agy"]`, and all four `reset*QuotaCache*` keys), and a single `kind: "combo-ref"` step referencing `comboName: "gemini-4-hydrogen-high"`

### Requirement: Combo-Scoped Reasoning Effort Routing for Top-Level Gemini 4 Hydrogen
OmniRoute SHALL configure three named combo-scoped reasoning-routing rules on `gemini-4-hydrogen` so requests specifying effort `low`, `medium`, or `xhigh` dispatch to `gemini-4-hydrogen-{low,medium,xhigh}` while effort `high` resolves through its `combo-ref` target `gemini-4-hydrogen-high`.

#### Scenario: Reasoning-routing simulation and live inference route each effort level to its matching Hydrogen tier
- **WHEN** `POST /api/settings/reasoning-routing-rules/simulate` is called for `model: "gemini-4-hydrogen"` across `effort` values `"low"`, `"medium"`, `"high"`, and `"xhigh"`
- **THEN** efforts `"low"`, `"medium"`, and `"xhigh"` SHALL each match their named `scope: "combo"` rule (`name: "gemini-4-hydrogen-{low,medium,xhigh}"`, upserted via `POST /api/settings/reasoning-routing-rules` or `PATCH /api/settings/reasoning-routing-rules/{id}`, `effortMode: "inherit"`, `targetKind: "combo"`) resolving to `gemini-4-hydrogen-{low,medium,xhigh}` with zero transport or capability rejection errors, while `"high"` SHALL fall through unmatched to `gemini-4-hydrogen-high`
- **AND** live `POST /v1/responses` (`max_output_tokens: 32768`, `reasoning.effort`), `POST /v1/chat/completions` (`max_completion_tokens: 32768`, `reasoning_effort`), and `POST /v1/messages` (`max_tokens: 32768`, `output_config.effort`) probes against `gemini-4-hydrogen` (`"high"`) and `gemini-4-hydrogen-xhigh` (`"xhigh"`) SHALL return `HTTP 200` with completed output attributed to the matching upstream Hydrogen tier model

## MODIFIED Requirements

### Requirement: Gemini 4 Carbon Tier Combos and SQLite Capability Overrides Without Source Modifications
OmniRoute SHALL expose four top-level Google Gemini 4 Carbon combos (`gemini-4-carbon`, `gemini-4-carbon-high`, `gemini-4-carbon-medium`, and `gemini-4-carbon-low`) routed via `strategy: "quota-weighted"` across the three configured Ultra-slot `agy` connections and SHALL persist SQLite capability and context overrides (`1,048,576` context, `262,144` max output tokens, `["low", "medium", "high"]` efforts) without modifying git-tracked source code.

#### Scenario: SQLite capability and context overrides unlock 262,144 output tokens and 1M context for Carbon tiers
- **WHEN** 12 single-key `PATCH http://127.0.0.1:20128/api/model-capability-overrides` requests (`3 models × 4 keys`, passing `"low,medium,high"` as a comma-separated string for `reasoning_efforts`) are applied and `GET /api/model-capability-overrides` + `GET /v1/models` are queried
- **THEN** `antigravity/gemini-4-carbon-high`, `antigravity/gemini-4-carbon-medium`, and `antigravity/gemini-4-carbon-low` SHALL each report persisted overrides for `context_length: 1048576`, `max_input_tokens: 1048576`, `max_output_tokens: 262144`, and `reasoning_efforts: ["low", "medium", "high"]`
- **AND** top-level combos `gemini-4-carbon`, `gemini-4-carbon-high`, `gemini-4-carbon-medium`, and `gemini-4-carbon-low` in `/v1/models` (`owned_by: "combo"`) SHALL advertise `context_length: 1000000` and `max_output_tokens: 262144` without rejecting requests carrying `max_tokens > 65536` up to `262144`

#### Scenario: Four Gemini 4 Carbon combos route exclusively across the three Ultra Antigravity accounts via quota-weighted strategy
- **WHEN** `GET http://127.0.0.1:20128/api/combos` is queried
- **THEN** combos `gemini-4-carbon`, `gemini-4-carbon-high`, `gemini-4-carbon-medium`, and `gemini-4-carbon-low` SHALL each be active with `strategy: "quota-weighted"`, `context_length: 1000000`, `context_cache_protection: false`, `config.targetTimeoutMs: 180000`, `config.predictiveTtftMs: 0`, `config.quotaWeightedFloorPercent: 5`, `config.quotaWeightedScoring: "leftover"`, `config.resetAwareQuotaCacheTtlMs: 300000`, `config.resetWindowQuotaCacheTtlMs: 300000`, and `config.resetAwareQuotaCacheMaxStaleMs: 3600000`
- **AND** `gemini-4-carbon` and `gemini-4-carbon-high` SHALL each contain 3 `kind: "model"` steps with `model: "agy/gemini-4-carbon-high"` mapped to `0532bad4-2486-4286-8f06-510e9c678620` (`vinhvumobile@gmail.com`), `338764b8-1cd7-4946-b789-ee5dad4c5073` (`vinhghtk1908@gmail.com`), and `62af823b-f3d7-4e6b-87a9-98069167d4f6` (`vicgnome19094@gmail.com`) (with `0532bad4` and `338764b8` bypassed via `excludedModels` / `-disabled` catalog filtering while downgraded to `g1-pro-tier` ahead of active `g1-ultra-tier` `62af823b`), while `gemini-4-carbon-medium` and `gemini-4-carbon-low` SHALL map those same 3 connections to `agy/gemini-4-carbon-medium` and `agy/gemini-4-carbon-low` respectively
- **AND** zero other `g1-pro-tier` `connectionId` values SHALL appear in any `gemini-4-carbon*` combo

#### Scenario: Concurrent Carbon inference distributes load by remaining quota and in-flight count
- **WHEN** concurrent `POST /v1/chat/completions` or `POST /v1/responses` requests target `gemini-4-carbon` or `gemini-4-carbon-high`
- **THEN** OmniRoute SHALL skip any step excluded by per-account catalog or `excludedModels` filtering, weight eligible Ultra candidates by `score / (1 + inflight)`, and return `HTTP 200` completions with zero `429` dispatches to unentitled Pro accounts

### Requirement: Invalid Provider Quarantine, 14-Combo Assignment Reconciliation, and Banned Account Blocklist Preservation
OmniRoute SHALL deactivate invalid API-key provider connection `f3aaa87c-4af7-4a83-a636-98983119b9bc` (`pm`) and remove unused combo `phanmemvip` (`ad4dace4-9072-42a8-8503-e6188e325890`), SHALL reconcile `compression_combo_assignments` exclusively to the 19 active workstation combo UUIDs, and SHALL preserve inactive banned `agy` rows (`is_active = 0`, `test_status = 'banned'`) as an import-deduplication safety blocklist.

#### Scenario: Invalid `pm` connection deactivated and unused `phanmemvip` combo removed
- **WHEN** `GET /api/providers` and `GET /api/combos` are queried
- **THEN** connection `f3aaa87c-4af7-4a83-a636-98983119b9bc` (`anthropic-compatible-6408e370-2373-4ae0-9942-7f4095ba976c`, prefix `pm`) SHALL have `isActive: false` (`is_active = 0`) and `healthCheckInterval: 0` so validation sweeps never emit `HTTP 401 ("Invalid API key")` errors
- **AND** unused combo `phanmemvip` (`ad4dace4-9072-42a8-8503-e6188e325890`) SHALL be absent from `combos`, leaving the exact 19 active workstation combos (`gemini-4-hydrogen{,-xhigh,-high,-medium,-low}`, `gemini-4-carbon{,-high,-medium,-low}`, `gemini-4-argon{,-high,-medium,-low}`, `gemini-3.8-flash-high`, `claude-opus-5.5`, `claude-sonnet-5.5`, `deepseek-v4.1-flash`, `kimi-k3.1-pro`, `muse-spark-1.3`)

#### Scenario: `compression_combo_assignments` reconciled to the 14 active combo UUIDs without orphaned or duplicate rows
- **WHEN** `PUT /api/context/combos/default-caveman/assignments` is applied with body `{"routingComboIds": [<19 active combo UUIDs>]}` and `compression_combo_assignments` is inspected
- **THEN** `compression_combo_assignments` SHALL contain exactly 19 rows matching the 19 active `combos.id` UUIDs (`0` plain-name duplicates and `0` orphaned rows referencing deleted combos)

#### Scenario: Inactive banned Antigravity connections retained as import blocklist with zero sweep overhead
- **WHEN** `provider_connections` (`provider = 'agy' AND is_active = 0 AND test_status = 'banned'`) is inspected or `findExistingAgyConnection` runs during bulk/CLI OAuth import
- **THEN** all 9 banned `agy` rows SHALL remain present with `is_active = 0` so duplicate-account detection rejects accidental re-import with `409 duplicate_account` while token health sweeps skip them with zero outbound network requests
