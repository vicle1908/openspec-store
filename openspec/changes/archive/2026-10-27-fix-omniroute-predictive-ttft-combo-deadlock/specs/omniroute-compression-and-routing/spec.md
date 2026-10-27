# Spec Delta

## MODIFIED Requirements

### Requirement: Predictive TTFT Circuit Breaker, Unleased 2-Account Pool Concurrency, and Subscription-Scoped Ban Auto-Disable

OmniRoute SHALL enable `zeroLatencyOptimizationsEnabled: true` (`predictiveTtftMs: 25000`, `targetTimeoutMs: 25000`, `hedging: false`, `fallbackCompressionMode: "off"`) in `/api/settings/combo-defaults` and as the default baseline for `agy` combos while preserving the explicit higher-latency tier overrides defined in the `Tier-Matched Combo Timeouts, Cold-Start Semantic Cache Bridge, and Fail-Closed Entrypoint Guard` requirement (`targetTimeoutMs: 180000` and `predictiveTtftMs: 60000` on `gemini-4-argon*` and `claude-opus-5.5`; `targetTimeoutMs: 120000`, `predictiveTtftMs: 45000`, and `maxRetries: 1` on `claude-sonnet-5.5`, `kimi-k3.1-pro`, and `deepseek-v4.1-flash`), SHALL isolate per-attempt target latency from whole-request elapsed time across all direct metric writers and helper retry paths, SHALL evaluate predictive latency per connection target with a bounded single-probe 120-second recovery window and eligible-target starvation guard, SHALL prioritize fresh per-target metrics in `auto` candidate ranking, SHALL serve routing, metrics inspection, and scoped combo resets from the same active in-memory metrics state, set `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED` to `"false"`, and configure `/api/settings/auto-disable-accounts` (`enabled: true`, `scope: "subscription"`, `threshold: 3`).

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
- **AND** if the recovery probe fails, aborts, times out, or succeeds above the predictive threshold, OmniRoute SHALL release the in-flight reservation and start a fresh 120,000-millisecond predictive cooldown window
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

#### Scenario: Concurrent subagent streams on 2-account `gemini-4-argon` pool proceed without lease saturation 503
- **WHEN** `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED` is `"false"` and concurrent streaming requests target `gemini-4-argon*` across the three entitled `Ultra` `agy` accounts
- **THEN** OmniRoute SHALL allow concurrent streams on the three entitled `Ultra` `agy` accounts without returning `503 All eligible Antigravity accounts are currently handling a request for this model`

#### Scenario: Permanently banned OAuth subscription account automatically quarantined
- **WHEN** an OAuth/subscription connection (`agy`, `github`, `muse-code`) receives a permanent ban classification (`permanent: true`) while `auto-disable-accounts` is enabled with `scope: "subscription"`
- **THEN** OmniRoute SHALL set `isActive: false` and stamp `banDisabledAt` on that connection while leaving `apikey`-authenticated connections unaffected

### Requirement: Gemini 4 Trailing Model Turn Stripping, Exact-Model Lockout Scoping on agy, Slow SQLite Telemetry, and Unified Database Semantic Cache Config

The OmniRoute gateway SHALL strip trailing `role: "model"` turns on `gemini-4-*` requests, SHALL exclude `"model turn"` HTTP 400 responses from model-access-denied lockout classifiers, SHALL enable `settings.modelLockout` (`enabled: true`, `errorCodes: [403, 404, 429, 502, 503, 504]`, `baseCooldownMs: 120000`, `maxCooldownMs: 1800000`, `maxBackoffSteps: 10`, `useExponentialBackoff: true`) and scope all `agy` and `antigravity` model lockouts to the exact model, SHALL enforce file-scoped startup patch replacement and per-file marker verification in `/app/container-entrypoint-compat.sh`, and SHALL configure `OMNIROUTE_SQLITE_SLOW_MS=200` with unified `database_settings.cache` limits.

#### Scenario: Trailing model turn stripped on gemini-4-argon requests
- **WHEN** a coding client or advisor submits a request targeting `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, or `gemini-4-argon-low` whose translated Gemini `contents` array ends with one or more `role: "model"` entries (and `contents.length > 1`)
- **THEN** OmniRoute SHALL strip the trailing `role: "model"` entries before sending the payload to Cloud Code so upstream does not reject the turn with HTTP 400

#### Scenario: Request-shape model-turn 400 does not trigger 1-hour model_capacity lockout
- **WHEN** an upstream target returns HTTP 400 with `"Requests ending with a model turn are not supported"`
- **THEN** both `isModelScoped400` and `isProviderModelUnsupported400` SHALL return `false` and OmniRoute SHALL NOT lock the model or `family:gemini` for 1 hour (`model_capacity`)

#### Scenario: Per-model lockouts on agy connections scope to the exact model
- **GIVEN** `settings.modelLockout.enabled` is `true` (`errorCodes: [403, 404, 429, 502, 503, 504]`, `baseCooldownMs: 120000`, `maxCooldownMs: 1800000`, `maxBackoffSteps: 10`, `useExponentialBackoff: true`)
- **WHEN** `lockModelIfPerModelQuota` or `recordModelLockoutFailure` records a per-model lockout (such as HTTP 429 or synthetic HTTP 504 `combo_target_timeout`) for provider `"agy"` or `"antigravity"`, including when invoked from combo failure handling without an explicit `options.scope` override
- **THEN** OmniRoute SHALL resolve the lockout scope to `"exact"` and invoke `lockExactModel` for the specific `<provider>:<connectionId>:exact:<model>` tuple so subsequent requests skip that timed-out or rate-limited connection for that exact model during its cooldown window rather than locking the entire `family:gemini` or `family:claude` quota family across the connection

#### Scenario: File-scoped startup patch execution and per-file marker verification fail closed
- **GIVEN** `/app/container-entrypoint-compat.sh` applies runtime compatibility replacements and validates `requiredMarkers` on container startup
- **WHEN** any replacement rule is executed or `requiredMarkers` are checked across target server bundles
- **THEN** each replacement rule SHALL execute only against its explicitly scoped target file or unique surrounding context (preventing cross-chunk helper identifier collisions), repeated runs SHALL be idempotent, and startup verification SHALL enforce `fileMatch` suffix matching for every required marker and exit non-zero (`1`) if any target file is missing its expected patched state

#### Scenario: Synchronous SQLite stall telemetry and unified database semantic cache settings
- **WHEN** `OMNIROUTE_SQLITE_SLOW_MS=200` is configured and `/api/settings/database` is queried
- **THEN** OmniRoute SHALL emit a diagnostic `[SQLITE-SLOW]` warning (without query parameters or prompt content) whenever a synchronous SQLite operation exceeds 200 milliseconds, and `GET /api/settings/database` SHALL report `cache.semanticCacheMaxSize: 1000` and `cache.semanticCacheTTL: 18000000` matching `GET /api/settings`
