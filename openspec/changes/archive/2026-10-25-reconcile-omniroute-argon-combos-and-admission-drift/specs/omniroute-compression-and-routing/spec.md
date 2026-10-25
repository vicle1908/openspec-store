## MODIFIED Requirements

### Requirement: Predictive TTFT Circuit Breaker, Unleased 2-Account Pool Concurrency, and Subscription-Scoped Ban Auto-Disable

OmniRoute SHALL enable `zeroLatencyOptimizationsEnabled: true` (`predictiveTtftMs: 25000`, `targetTimeoutMs: 25000`, `hedging: false`, `fallbackCompressionMode: "off"`) in `/api/settings/combo-defaults` and `agy` combos (`gemini-3.8-flash-high`, `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, `gemini-4-argon-low`, `claude-opus-5.5`, `muse-spark-1.3`), set `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED` to `"false"`, and configure `/api/settings/auto-disable-accounts` (`enabled: true`, `scope: "subscription"`, `threshold: 3`).

#### Scenario: Stalled target exceeding 25-second average latency skipped on attempt 0 without fallback re-truncation
- **WHEN** `zeroLatencyOptimizationsEnabled` is `true` (`predictiveTtftMs: 25000`, `targetTimeoutMs: 25000`, `hedging: false`, `fallbackCompressionMode: "off"`) and a target's historical `avgLatencyMs` in `getComboMetrics` exceeds 25,000 milliseconds
- **THEN** OmniRoute SHALL skip that target on primary attempt `0` (`predictive_ttft`) and dispatch to the next healthy candidate without issuing duplicate speculative hedged requests or running unconfigured fallback `lite` truncation

#### Scenario: Concurrent subagent streams on 2-account `gemini-4-argon` pool proceed without lease saturation 503
- **WHEN** `ANTIGRAVITY_ACCOUNT_LEASE_ENABLED` is `"false"` and concurrent streaming requests target `gemini-4-argon*` across the three entitled `Ultra` `agy` accounts
- **THEN** OmniRoute SHALL allow concurrent streams on the three entitled `Ultra` `agy` accounts without returning `503 All eligible Antigravity accounts are currently handling a request for this model`

#### Scenario: Permanently banned OAuth subscription account automatically quarantined
- **WHEN** an OAuth/subscription connection (`agy`, `github`, `muse-code`) receives a permanent ban classification (`permanent: true`) while `auto-disable-accounts` is enabled with `scope: "subscription"`
- **THEN** OmniRoute SHALL set `isActive: false` and stamp `banDisabledAt` on that connection while leaving `apikey`-authenticated connections unaffected

### Requirement: Three-Ultra-Account Gemini-4-Argon Combo Routing

OmniRoute SHALL configure `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` combos with explicit connection-scoped model steps (`kind: "model"`, `providerId: "agy"`, `weight: 0`, and non-empty account email `label`) for all 3 active Google AI Ultra Antigravity accounts (`62af823b-f3d7-4e6b-87a9-98069167d4f6` / `vicgnome19094@gmail.com`, `0532bad4-2486-4286-8f06-510e9c678620` / `vinhvumobile@gmail.com`, `338764b8-1cd7-4946-b789-ee5dad4c5073` / `vinhghtk1908@gmail.com`), preserving `strategy: "auto"`, `context_cache_protection: false`, and `config.targetTimeoutMs: 25000`.

#### Scenario: All three Ultra accounts present in every gemini-4-argon* combo
- **WHEN** `GET /api/combos/{id}` is queried for `gemini-4-argon`, `gemini-4-argon-high`, `gemini-4-argon-medium`, or `gemini-4-argon-low`
- **THEN** `models` SHALL contain 3 steps mapped to `connectionId` values `62af823b-f3d7-4e6b-87a9-98069167d4f6` (`label: "vicgnome19094@gmail.com"`), `0532bad4-2486-4286-8f06-510e9c678620` (`label: "vinhvumobile@gmail.com"`), and `338764b8-1cd7-4946-b789-ee5dad4c5073` (`label: "vinhghtk1908@gmail.com"`)
- **AND** `strategy` SHALL be `"auto"`, `context_cache_protection` SHALL be `false`, and `config.targetTimeoutMs` SHALL be `25000`

#### Scenario: Live gemini-4-argon inference succeeds with 3 Ultra accounts
- **WHEN** a completion request is sent to `gemini-4-argon` or `gemini-4-argon-high` (or when one Ultra account returns `HTTP 429`)
- **THEN** OmniRoute SHALL route across the 3 Ultra accounts with `HTTP 200` and bound any single stalled upstream target attempt to `25,000 ms`

## ADDED Requirements

### Requirement: Multi-Agent Heavyweight Chat Admission Concurrency and Composite-Combo Prune Protection

OmniRoute SHALL configure `OMNIROUTE_CHAT_MAX_HEAVY_IN_FLIGHT=16` and `OMNIROUTE_CHAT_ADMISSION_QUEUE_MS=15000` in `/Users/androidteam/Omniroute/.env` and SHALL persist `COMBO_AUTO_PRUNE_STALE_STEPS` as `"false"` in SQLite `feature_flags` so concurrent tool-bearing subagent streams do not shed with `HTTP 503 chat_admission_busy` and composite combos containing a `combo-ref` fallback retain their explicit model steps across catalog syncs.

#### Scenario: Concurrent tool-bearing subagent turns admit without 503 chat_admission_busy
- **WHEN** up to 16 concurrent tool-bearing coding-agent requests (`tools.length >= 64` or `content-length >= 256 KB`) arrive at `/v1/chat/completions` or `/v1/responses` while total `inflightBytes` is below `137,363,456` bytes
- **THEN** `ChatAdmissionController` SHALL admit the requests to the combo router without returning `HTTP 503 chat_admission_busy`

#### Scenario: Composite combo with trailing `combo-ref` retains explicit model steps across catalog syncs
- **WHEN** `COMBO_AUTO_PRUNE_STALE_STEPS` is `"false"` in `GET /api/settings/feature-flags` and scheduled provider model sync runs
- **THEN** OmniRoute SHALL preserve all explicit `kind: "model"` steps in `claude-opus-5.5` ahead of its `combo-ref: gemini-3.8-flash-high` fallback
