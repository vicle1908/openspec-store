# Spec Delta: omniroute-compression-and-routing

## MODIFIED Requirements

### Requirement: Bounded Quota Park, Early-EOF Sibling Failover, Refusal Cooldown Skip, and Terminal Safety Stops
OmniRoute SHALL persist 24 enabled v3.8.52 resilience, routing, catalog, and compaction feature flags as "true" and ANTIGRAVITY_ACCOUNT_LEASE_ENABLED and COMBO_AUTO_PRUNE_STALE_STEPS as "false" in SQLite key_value (namespace='feature_flags'), set mcpDescriptionCompressionEnabled to true, set sessionAffinityTtlMs to 300000, and keep FLUSH_EMPTY_RETRY_ENABLED and OMNIROUTE_ALLOW_PRIVATE_PROVIDER_URLS disabled ("false") while OMNIROUTE_ALLOW_LOCAL_PROVIDER_URLS remains "true".

#### Scenario: Pre-first-frame SSE early EOF fails over once to a sibling connection
- **WHEN** `STREAM_EARLY_EOF_SIBLING_FAILOVER_ENABLED` is `true` and an upstream SSE stream closes with `STREAM_EARLY_EOF` before emitting any useful frame
- **THEN** OmniRoute SHALL exclude the failed connection and retry once on an eligible sibling connection

#### Scenario: Content-policy safety refusal stops combo retry loop
- **WHEN** `PROVIDER_SAFETY_STOPS_TERMINAL` and `CONTENT_POLICY_REFUSAL_COMBO_STOP_ENABLED` are `true` and an upstream target returns HTTP 400 or 403 with `content_policy_violation`, `cyber_policy`, or `misalignment_policy_violation`
- **THEN** OmniRoute SHALL treat the refusal as terminal for the request and SHALL NOT retry the refused prompt across remaining combo targets

#### Scenario: Expanded v3.8.52 coding-agent feature flags and MCP description compression resolve from authoritative SQLite tables
- **WHEN** `GET /api/settings/feature-flags` and `GET /api/settings/compression` are queried with management authentication
- **THEN** all 24 enabled flags (`QUOTA_WINDOW_BOUNDED_PARK`, `STREAM_EARLY_EOF_SIBLING_FAILOVER_ENABLED`, `COOLDOWN_RETRY_SKIP_REFUSALS_ENABLED`, `PROVIDER_SAFETY_STOPS_TERMINAL`, `EMPTY_STREAM_SIBLING_RECOVERY_ENABLED`, `STREAM_READINESS_STALL_RETRY`, `DB_HEALTHCHECK_STARTUP_DEFERRED_ENABLED`, `STREAM_LATE_OUTPUT_PROBE_ENABLED`, `RETRY_AFTER_PROVENANCE_ENABLED`, `COMBO_EMPTY_POOL_NO_ELIGIBLE_TARGETS_ENABLED`, `CREDENTIAL_GATE_AUTH_DIAGNOSES_ONLY`, `AUTO_REQUEST_RESOLVED_CAPABILITIES`, `AUTO_COMBO_KEYLESS_TRANSPORT_GATE`, `MODELS_DEV_EFFORT_TIERS_ENABLED`, `CATALOG_MIRROR_REFINEMENTS_ENABLED`, `ANTHROPIC_COMPATIBLE_MID_CONVERSATION_SYSTEM`, `CONTENT_POLICY_REFUSAL_COMBO_STOP_ENABLED`, `CREDENTIAL_HEALTH_RETEST_AUTO_DISABLED`, `MODEL_ENDPOINT_CAPABILITY_GATE_ENABLED`, `OPENCODE_FULL_TEXT_ERROR_RULES_ENABLED`, `CLOUDFLARE_AI_FULL_TEXT_ERROR_RULES_ENABLED`, `PROTECTED_PRIORITY_INFRA_502_ENABLED`, `NATIVE_CODEX_REACTIVE_COMPACTION_ENABLED`, `CLAUDE_OAUTH_SUMMARIZED_THINKING_UNREDACTED`) SHALL report `effectiveValue: "true"` and `source: "db"`, `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED` and `COMBO_AUTO_PRUNE_STALE_STEPS` SHALL report `effectiveValue: "false"` and `source: "db"`, and `GET /api/settings/compression` SHALL report `mcpDescriptionCompressionEnabled: true`

#### Scenario: Outbound provider URL guard blocks cloud metadata while permitting Host Ollama
- **WHEN** `OMNIROUTE_ALLOW_PRIVATE_PROVIDER_URLS` is `"false"` and `OMNIROUTE_ALLOW_LOCAL_PROVIDER_URLS` is `"true"`
- **THEN** `getProviderOutboundGuard()`, `getProviderValidationGuard()`, and `embeddingUrlGuard()` SHALL operate in `"block-metadata"` mode—rejecting cloud metadata endpoints (`169.254.169.254`, `fd00:ec2::254`, `metadata.google.internal`) before any network request is dispatched while permitting Host Ollama (`http://host.docker.internal:11434/v1/embeddings`)—and `/v1/search` SHALL independently skip unconfigured default SearXNG (`http://localhost:8888/search`) via `isUnconfiguredLoopbackSearchProvider`

#### Scenario: Stale combo step auto-prune snapshots combos and prunes only on authoritative catalog syncs
- **WHEN** `COMBO_AUTO_PRUNE_STALE_STEPS` is `"true"` after a pre-deployment combo and SQLite backup snapshot has been recorded
- **THEN** OmniRoute SHALL remove explicit combo model steps only when an authoritative live catalog sync confirms the model is delisted, SHALL NOT prune steps on failed, degraded, or free-only syncs, and SHALL NEVER empty a combo whose every step is flagged stale

#### Scenario: Session affinity pins multi-turn connections with cross-session isolation and unhealthy failover
- **WHEN** `sessionAffinityTtlMs` is configured to `300000` (5 minutes)
- **THEN** subsequent turns within the same session window SHALL prefer the pinned connection, distinct session IDs SHALL route independently without sharing affinity pins, and OmniRoute SHALL immediately fail over to a healthy sibling connection if the pinned connection errors or enters cooldown

### Requirement: Predictive TTFT Circuit Breaker, Unleased 3-Ultra-Account Pool Concurrency, and Subscription-Scoped Ban Auto-Disable
OmniRoute SHALL enable `zeroLatencyOptimizationsEnabled: true` (`predictiveTtftMs: 25000`, `targetTimeoutMs: 25000`, `hedging: false`, `fallbackCompressionMode: "off"`) in `/api/settings/combo-defaults` and as the default baseline for `agy` combos while preserving explicit higher-latency tier overrides, SHALL isolate per-attempt target latency across direct metrics and retry helpers, and SHALL scope predictive TTFT to individual targets with bounded recovery and starvation guards.

#### Scenario: Stalled target exceeding 25-second average latency skipped on attempt 0 without fallback re-truncation
- **GIVEN** `zeroLatencyOptimizationsEnabled` is `true` (`predictiveTtftMs: 25000`, `targetTimeoutMs: 25000`, `hedging: false`, `fallbackCompressionMode: "off"`, or the combo's tier-matched `predictiveTtftMs` and `targetTimeoutMs` override) and a connection target's `avgLatencyMs` in `getComboMetrics` (`byTarget[executionKey]`) exceeds the combo's configured `predictiveTtftMs` threshold over at least 5 requests within an active 120,000-millisecond predictive cooldown window
- **WHEN** a new combo request evaluates that target while at least one other eligible unreserved candidate remains in the combo
- **THEN** OmniRoute SHALL skip that target on primary attempt `0` (`predictive_ttft`) and dispatch to the next eligible candidate without issuing duplicate speculative hedged requests or running unconfigured fallback `lite` truncation

#### Scenario: Failover target latency isolated from prior target timeouts and empty-content helper retries
- **GIVEN** target `0` in a combo fails or times out (for example after 25,000 milliseconds) and the combo fails over to target `1`
- **WHEN** target `1` completes in `L` milliseconds, either directly or through helper retry paths including `handleEmptyContentRetry`
- **THEN** OmniRoute SHALL record target `1`'s latency in `byTarget` and `byModel` (and evaluate any helper retry elapsed time for target `1`) from target `1`'s own attempt start timestamp (`L` milliseconds) rather than cumulative combo elapsed time since target `0` started, while preserving whole-request elapsed timing at the outer combo loop

#### Scenario: Connection-scoped predictive evaluation isolates untried sibling accounts from shared model averages
- **GIVEN** a multi-account combo where connection-scoped targets (`executionKey !== modelStr`) share a common `modelStr` and shared `byModel[modelStr].avgLatencyMs` exceeds the combo's `predictiveTtftMs` threshold
- **WHEN** OmniRoute evaluates `predictiveTtftMs` for a sibling connection whose `byTarget[executionKey]` is absent or has fewer than 5 recorded requests
- **THEN** OmniRoute SHALL evaluate `predictiveTtftMs` strictly against `byTarget[executionKey]` without falling back to `byModel[modelStr]` and SHALL NOT skip the untried or under-sampled sibling connection on account of another connection's latency

#### Scenario: Post-cooldown single-probe reservation, latency window re-seed, and terminal release
- **GIVEN** a connection target whose `byTarget[executionKey]` has at least 5 requests with `avgLatencyMs` exceeding `predictiveTtftMs` and whose 120,000-millisecond predictive cooldown window has elapsed
- **WHEN** concurrent requests arrive for that combo
- **THEN** OmniRoute SHALL atomically reserve at most one in-flight recovery probe for that `(comboName, executionKey)` in authoritative metrics state before upstream dispatch while concurrent requests skip that target until the reservation settles
- **AND** if the recovery probe fails, aborts, times out, or succeeds above the predictive threshold, OmniRoute SHALL retain the 90,000-millisecond single-flight reservation lock in `__omniProbeAt` to prevent concurrent probe stampedes and maintain predictive cooldown protection
- **AND** if the recovery probe succeeds with latency at or below `predictiveTtftMs`, OmniRoute SHALL release the reservation and re-seed that target's predictive latency window from the probe duration so cumulative pre-cooldown timeouts do not immediately re-trip `predictive_ttft`, while preserving lifetime request and failure counters

#### Scenario: Eligible-candidate starvation guard respects independent eligibility gates
- **GIVEN** a combo request where all candidates except one otherwise-eligible unreserved candidate have been skipped by `predictive_ttft`, including when the final raw index in `orderedTargets` is independently blocked by auth, quota, model lockout, provider cooldown, or concurrency gates
- **WHEN** OmniRoute evaluates predictive latency for the last remaining candidate that passed all independent eligibility gates (`recordedAttempts === 0`)
- **THEN** OmniRoute SHALL dispatch to that last eligible unreserved candidate rather than returning a zero-attempt `503` from predictive filtering alone, and SHALL NEVER bypass auth, quota, model lockout, cooldown, or concurrency gates on an ineligible target

#### Scenario: Per-target auto candidate scoring and coherent scoped combo metrics state
- **GIVEN** a multi-account `auto` combo with per-target runtime history in `byTarget[executionKey]`
- **WHEN** `buildAutoCandidates` scores candidate targets or an operator queries or resets metrics for an affected combo (`GET /api/combos/metrics` or `DELETE /api/combos/metrics?combo=<name>`)
- **THEN** `buildAutoCandidates` SHALL prefer `byTarget[executionKey]` latency and success rate whenever `byTarget[executionKey].requests > 0` (using `byModel[modelStr]` or 24-hour model aggregates only as fallback when target history is absent)
- **AND** routing, metrics inspection, and scoped combo resets (`DELETE /api/combos/metrics?combo=<name>`) SHALL operate on the same active in-memory metrics state without clearing unrelated combo metrics or stopping the periodic metrics cleanup timer

#### Scenario: Concurrent subagent streams on 3-Ultra-account `gemini-4-argon` pool proceed without lease saturation 503
- **WHEN** `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED` is `"false"` and concurrent streaming requests target `gemini-4-argon*` across the three entitled `Ultra` `agy` accounts
- **THEN** OmniRoute SHALL allow concurrent streams on the three entitled `Ultra` `agy` accounts without returning `503 All eligible Antigravity accounts are currently handling a request for this model`

#### Scenario: Permanently banned OAuth subscription account automatically quarantined
- **WHEN** an OAuth/subscription connection (`agy`, `github`, `muse-code`) receives a permanent ban classification (`permanent: true`) while `auto-disable-accounts` is enabled with `scope: "subscription"`
- **THEN** OmniRoute SHALL set `isActive: false` and stamp `banDisabledAt` on that connection while leaving `apikey`-authenticated connections unaffected

### Requirement: Three-Ultra-Account Gemini-4-Argon Combo Routing
OmniRoute SHALL configure `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` combos with explicit connection-scoped model steps for all 3 active Google AI Ultra Antigravity accounts (`62af823b-f3d7-4e6b-87a9-98069167d4f6`, `0532bad4-2486-4286-8f06-510e9c678620`, `338764b8-1cd7-4946-b789-ee5dad4c5073`), preserving `strategy: "auto"` and setting `context_cache_protection: false`.

#### Scenario: All three Ultra accounts present in every gemini-4-argon* combo
- **WHEN** `GET /api/combos/{id}` is queried for `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, or `gemini-4-argon-low`
- **THEN** `models` SHALL contain 3 steps mapped to `connectionId` values `62af823b-f3d7-4e6b-87a9-98069167d4f6` (`label: "vicgnome19094@gmail.com"`), `0532bad4-2486-4286-8f06-510e9c678620` (`label: "vinhvumobile@gmail.com"`), and `338764b8-1cd7-4946-b789-ee5dad4c5073` (`label: "vinhghtk1908@gmail.com"`)
- **AND** `strategy` SHALL be `"auto"`, `context_cache_protection` SHALL be `false`, `config.targetTimeoutMs` SHALL be `180000`, and `config.predictiveTtftMs` SHALL be `60000`

#### Scenario: Live gemini-4-argon inference succeeds with 3 Ultra accounts
- **WHEN** a completion request is sent to `gemini-4-argon` or `gemini-4-argon-high` (or when one Ultra account returns `HTTP 429`)
- **THEN** OmniRoute SHALL route across the 3 Ultra accounts with `HTTP 200` and bound any single stalled upstream target attempt to `180,000 ms`

### Requirement: Multi-Agent Heavyweight Chat Admission Concurrency and Composite-Combo Prune Protection
OmniRoute SHALL configure `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=16` and `OMNIROUTE_CHAT_ADMISSION_QUEUE_MS=15000` in `/Users/androidteam/Omniroute/.env` and SHALL persist `COMBO_AUTO_PRUNE_STALE_STEPS` as `"false"` in SQLite `feature_flags` so concurrent tool-bearing subagent streams do not shed with `HTTP 503 chat_admission_busy` and composite combos containing a `combo-ref` fallback retain their explicit model steps across catalog syncs.

#### Scenario: Concurrent tool-bearing subagent turns admit without 503 chat_admission_busy
- **WHEN** up to 16 concurrent tool-bearing coding-agent requests (`tools.length >= 64` or `content-length >= 256 KB`) arrive at `/v1/chat/completions` or `/v1/responses` while total `inflightBytes` is below `137,363,456` bytes
- **THEN** `ChatAdmissionController` SHALL admit the requests to the combo router without returning `HTTP 503 chat_admission_busy`

#### Scenario: Composite combo with trailing `combo-ref` retains explicit model steps across catalog syncs
- **WHEN** `COMBO_AUTO_PRUNE_STALE_STEPS` is `"false"` in `GET /api/settings/feature-flags` and scheduled provider model sync runs
- **THEN** OmniRoute SHALL preserve all explicit `kind: "model"` steps in composite combos containing a `combo-ref` step (such as `muse-spark-1.3`) alongside all 15 explicit `kind: "model"` steps in `claude-opus-5.5`

### Requirement: Multi-Account Claude Opus and Sonnet Combo Pooling across Antigravity Accounts
OmniRoute SHALL configure `claude-opus-5.5` and `claude-sonnet-5.5` combos to pool all 15 active Antigravity OAuth connections (`12` active `g1-pro-tier` and `3` `g1-ultra-tier`, excluding banned `47f334b1-b801-41f6-a709-4ebabb7a86d6`) across 15 connection-scoped `kind: "model"` steps (`agy/claude-opus-4-6-thinking` and `agy/claude-sonnet-4-6`) without `combo-ref` sub-combos, using `strategy: "auto"`, `candidatePool: ["agy"]`, and `context_cache_protection: false`.

#### Scenario: Claude Opus 5.5 combo pools all 15 Antigravity accounts
- **WHEN** `GET /api/combos/{id}` is queried for `claude-opus-5.5` (`4b2430da-0b3b-4b0e-9773-ec0f97adc252`)
- **THEN** OmniRoute SHALL return a combo with 15 explicit `kind: "model"` steps targeting `agy/claude-opus-4-6-thinking` across the 15 active `agy` connections (`12` Pro and `3` Ultra, excluding banned `47f334b1-b801-41f6-a709-4ebabb7a86d6` and with `0` `combo-ref` steps), with `strategy: "auto"`, `candidatePool: ["agy"]`, `context_cache_protection: false`, `config.targetTimeoutMs: 180000`, and `config.predictiveTtftMs: 60000`

#### Scenario: Claude Sonnet 5.5 combo pools all 15 Antigravity accounts
- **WHEN** `GET /api/combos/{id}` is queried for `claude-sonnet-5.5` (`9447399c-856b-4f52-8820-b3bf3dc3f132`)
- **THEN** OmniRoute SHALL return a combo with 15 explicit `kind: "model"` steps targeting `agy/claude-sonnet-4-6` across the 15 active `agy` connections (`12` Pro and `3` Ultra, excluding banned `47f334b1-b801-41f6-a709-4ebabb7a86d6`), with `strategy: "auto"`, `candidatePool: ["agy"]`, `context_cache_protection: false`, `config.targetTimeoutMs: 120000`, and `config.predictiveTtftMs: 45000`

#### Scenario: Live chat completions route through multi-account Claude combos to authentic Claude models
- **WHEN** `POST /v1/chat/completions` is called with `model: "claude-opus-5.5"` or `model: "claude-sonnet-5.5"`
- **THEN** OmniRoute SHALL return HTTP 200 with a completion served by `claude-opus-4-6-thinking` or `claude-sonnet-4-6` on one of the 15 active Antigravity accounts

#### Scenario: Upstream Claude 5.5 model cutover contract
- **WHEN** upstream Google Antigravity provisions and advertises `claude-opus-5-5-*` or `claude-sonnet-5-5-*` in its live discovery catalog
- **THEN** OmniRoute SHALL update the explicit model steps in `claude-opus-5.5` and `claude-sonnet-5-5` combos from 4.6 to the corresponding 5.5 identifiers while preserving all 15 connection mappings

### Requirement: Dedicated 11-Pro-Account Auto Pool for `gemini-3.8-flash-high` and Ultra Quota Isolation
OmniRoute SHALL configure `gemini-3.8-flash-high` (`7555d851-b4f3-44c6-b1fb-c6fdceabf388`) with `strategy: "auto"`, `context_cache_protection: false` persisted in `combos.data`, `targetTimeoutMs: 25000`, `predictiveTtftMs: 25000`, and 12 `kind: "model"` steps scoped exclusively to the 12 active `g1-pro-tier` `agy` connections (excluding the 3 Ultra accounts and banned `47f334b1`), and SHALL enable `rateLimitProtection: true` on all 15 active `agy` accounts.

#### Scenario: `gemini-3.8-flash-high` routes across the 11 Pro accounts without consuming Ultra Gemini quota
- **WHEN** `GET /api/combos/7555d851-b4f3-44c6-b1fb-c6fdceabf388` (`gemini-3.8-flash-high`) is inspected or invoked
- **THEN** `strategy` SHALL be `"auto"`, `context_cache_protection` SHALL be `false`, and `models` SHALL contain 12 `agy/gemini-3.8-flash-high` steps mapped to all 12 active `g1-pro-tier` connections (including `ce95e1cb-27a4-433f-9c50-bdb6ad0b6b6b`) with non-empty email `label`s
- **AND** none of the 3 `g1-ultra-tier` `connectionId`s (`62af823b-f3d7-4e6b-87a9-98069167d4f6`, `0532bad4-2486-4286-8f06-510e9c678620`, `338764b8-1cd7-4946-b789-ee5dad4c5073`) SHALL appear in `gemini-3.8-flash-high`

#### Scenario: All 3 Ultra accounts and 11 Pro accounts enforce `rateLimitProtection: true`
- **WHEN** `GET /api/rate-limits` is queried
- **THEN** all 3 `g1-ultra-tier` `agy` accounts (`62af823b`, `0532bad4`, `338764b8`) and all 12 active `g1-pro-tier` `agy` accounts SHALL report `rateLimitProtection: true` and `enabled: true`

### Requirement: Tier-Matched Combo Timeouts, Cold-Start Semantic Cache Bridge, and Fail-Closed Entrypoint Guard
OmniRoute SHALL configure `targetTimeoutMs: 180000` and `predictiveTtftMs: 60000` on deep-reasoning combos (`gemini-4-argon*` and `claude-opus-5.5`), SHALL configure `targetTimeoutMs: 120000`, `predictiveTtftMs: 45000`, and `maxRetries: 1` on `claude-sonnet-5.5`, `kimi-k3.1-pro`, and `deepseek-v4.1-flash`, SHALL auto-invoke `ensureSemanticCacheDbBridge()` on semantic cache initialization, and SHALL assert all runtime patch markers fail-closed in `container-entrypoint-compat.sh`.

#### Scenario: Deep-reasoning and high-TTFT combos enforce tier-matched timeouts without premature 25s aborts
- **WHEN** `GET /api/combos` is queried
- **THEN** `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, and `claude-opus-5.5` SHALL each have `config.targetTimeoutMs === 180000` and `config.predictiveTtftMs === 60000`
- **AND** `claude-sonnet-5.5`, `kimi-k3.1-pro`, and `deepseek-v4.1-flash` SHALL each have `config.targetTimeoutMs === 120000`, `config.predictiveTtftMs === 45000`, and `config.maxRetries === 1`

#### Scenario: Entrypoint verification fails closed across all runtime markers and semantic cache bridge initializes on cold start
- **WHEN** `container-entrypoint-compat.sh` runs on container startup
- **THEN** it SHALL verify all patch markers across the compiled server chunks without skipping missing chunk filenames (`process.exit(1)` on any missing marker)
- **AND** `OMNIROUTE_SEMANTIC_CACHE_EMBEDDING_TIMEOUT_MS=3000` and `OMNIROUTE_SEMANTIC_CACHE_TTL_MS=18000000` SHALL be set in `/Users/androidteam/Omniroute/.env` with `ensureSemanticCacheDbBridge()` auto-invoked on `/v1/responses` and `/v1/messages` cold starts
