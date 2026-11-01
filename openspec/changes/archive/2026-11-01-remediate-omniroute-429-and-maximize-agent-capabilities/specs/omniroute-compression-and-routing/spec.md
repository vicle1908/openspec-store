# omniroute-compression-and-routing Spec Delta

## MODIFIED Requirements

### Requirement: Multi-Account Claude Opus and Sonnet Combo Pooling across Antigravity Accounts
OmniRoute SHALL configure `claude-opus-5.5` and `claude-sonnet-5.5` combos to pool all 13 active Antigravity connections (`10` Pro and `3` Ultra, excluding banned `47f334b1`, `d5c3465f`, and `20369f65`) across 13 `kind: "model"` steps matching each account's `syncedAvailableModels` catalog with `0` `combo-ref` steps, `context_length: 1000000`, `strategy: "auto"`, and `context_cache_protection: false`.

#### Scenario: Claude Opus 5.5 combo pools all 15 Antigravity accounts
- **WHEN** `GET /api/combos/{id}` is queried for `claude-opus-5.5` (`4b2430da-0b3b-4b0e-9773-ec0f97adc252`)
- **THEN** OmniRoute SHALL return a combo with 13 explicit `kind: "model"` steps matching each active connection's `syncedAvailableModels` entry (`agy/claude-opus-5-5-high` on migrated connection `38782750-7a60-46d4-ae3f-e8c13cda296b` and `agy/claude-opus-4-6-thinking` on the remaining 12 active `agy` connections, excluding banned `47f334b1`, `d5c3465f`, and `20369f65`, with `0` `combo-ref` steps), `context_length: 1000000`, `strategy: "auto"`, `candidatePool: ["agy"]`, `context_cache_protection: false`, `config.targetTimeoutMs: 180000`, and `config.predictiveTtftMs: 60000`

#### Scenario: Claude Sonnet 5.5 combo pools all 15 Antigravity accounts
- **WHEN** `GET /api/combos/{id}` is queried for `claude-sonnet-5.5` (`9447399c-856b-4f52-8820-b3bf3dc3f132`)
- **THEN** OmniRoute SHALL return a combo with 13 explicit `kind: "model"` steps matching each active connection's `syncedAvailableModels` entry (`agy/claude-sonnet-5-5-high` on migrated connection `38782750-7a60-46d4-ae3f-e8c13cda296b` and `agy/claude-sonnet-4-6` on the remaining 12 active `agy` connections, excluding banned `47f334b1`, `d5c3465f`, and `20369f65`), `context_length: 1000000`, `strategy: "auto"`, `candidatePool: ["agy"]`, `context_cache_protection: false`, `config.targetTimeoutMs: 120000`, and `config.predictiveTtftMs: 45000`

#### Scenario: Live chat completions route through multi-account Claude combos to authentic Claude models
- **WHEN** `POST /v1/chat/completions` is called with `model: "claude-opus-5.5"` or `model: "claude-sonnet-5.5"`
- **THEN** OmniRoute SHALL return HTTP 200 with a completion served by `claude-opus-5-5-high`/`claude-opus-4-6-thinking` or `claude-sonnet-5-5-high`/`claude-sonnet-4-6` on one of the 13 active Antigravity accounts with zero synthetic deprecation responses or banned-account 403 dispatches

#### Scenario: Upstream Claude 5.5 model cutover contract
- **WHEN** upstream Google Antigravity provisions and advertises `claude-opus-5-5-*` or `claude-sonnet-5-5-*` in its live discovery catalog
- **THEN** OmniRoute SHALL update the explicit model steps in `claude-opus-5.5` and `claude-sonnet-5.5` combos from 4.6 to the corresponding 5.5 identifiers while preserving all active connection mappings

### Requirement: Dedicated 11-Pro-Account Auto Pool for `gemini-3.8-flash-high` and Ultra Quota Isolation
OmniRoute SHALL configure `gemini-3.8-flash-high` (`7555d851-b4f3-44c6-b1fb-c6fdceabf388`) with `strategy: "auto"`, `context_cache_protection: false`, `targetTimeoutMs: 25000`, and 9 `kind: "model"` steps scoped exclusively to active `g1-pro-tier` `agy` connections with remaining quota (excluding the 3 Ultra accounts, quota-exhausted `ce95e1cb`, and banned `47f334b1`, `d5c3465f`, `20369f65`).

#### Scenario: `gemini-3.8-flash-high` routes across the 11 Pro accounts without consuming Ultra Gemini quota
- **WHEN** `GET /api/combos/7555d851-b4f3-44c6-b1fb-c6fdceabf388` (`gemini-3.8-flash-high`) is inspected or invoked
- **THEN** `strategy` SHALL be `"auto"`, `context_cache_protection` SHALL be `false`, and `models` SHALL contain 9 `agy/gemini-3.8-flash-high` steps mapped to healthy `g1-pro-tier` connections (excluding exhausted `ce95e1cb` and banned `47f334b1`, `d5c3465f`, `20369f65`) with non-empty email `label`s
- **AND** none of the 3 `g1-ultra-tier` `connectionId`s SHALL appear in `gemini-3.8-flash-high`

#### Scenario: All 3 Ultra accounts and 11 Pro accounts enforce `rateLimitProtection: true`
- **WHEN** `GET /api/rate-limits` is queried
- **THEN** all 3 `g1-ultra-tier` `agy` accounts and active `g1-pro-tier` `agy` accounts SHALL report `rateLimitProtection: true` and `enabled: true`
