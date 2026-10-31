# Spec Delta: omniroute-compression-and-routing

## MODIFIED Requirements

### Requirement: Multi-Account Claude Opus and Sonnet Combo Pooling across Antigravity Accounts
OmniRoute SHALL configure `claude-opus-5.5` and `claude-sonnet-5.5` combos to pool all 15 active Antigravity connections (`12` Pro and `3` Ultra, excluding banned `47f334b1`) across 15 `kind: "model"` steps matching each account's `syncedAvailableModels` catalog (`agy/claude-opus-5-5-high` or `agy/claude-opus-4-6-thinking`, and `agy/claude-sonnet-5-5-high` or `agy/claude-sonnet-4-6`) with `0` `combo-ref` steps, `strategy: "auto"`, and `context_cache_protection: false`.

#### Scenario: Claude Opus 5.5 combo pools all 15 Antigravity accounts
- **WHEN** `GET /api/combos/{id}` is queried for `claude-opus-5.5` (`4b2430da-0b3b-4b0e-9773-ec0f97adc252`)
- **THEN** OmniRoute SHALL return a combo with 15 explicit `kind: "model"` steps matching each active connection's `syncedAvailableModels` entry (`agy/claude-opus-5-5-high` on migrated connection `38782750-7a60-46d4-ae3f-e8c13cda296b` and `agy/claude-opus-4-6-thinking` on the remaining 14 active `agy` connections) (`12` Pro and `3` Ultra, excluding banned `47f334b1-b801-41f6-a709-4ebabb7a86d6` and with `0` `combo-ref` steps), with `strategy: "auto"`, `candidatePool: ["agy"]`, `context_cache_protection: false`, `config.targetTimeoutMs: 180000`, and `config.predictiveTtftMs: 60000`

#### Scenario: Claude Sonnet 5.5 combo pools all 15 Antigravity accounts
- **WHEN** `GET /api/combos/{id}` is queried for `claude-sonnet-5.5` (`9447399c-856b-4f52-8820-b3bf3dc3f132`)
- **THEN** OmniRoute SHALL return a combo with 15 explicit `kind: "model"` steps matching each active connection's `syncedAvailableModels` entry (`agy/claude-sonnet-5-5-high` on migrated connection `38782750-7a60-46d4-ae3f-e8c13cda296b` and `agy/claude-sonnet-4-6` on the remaining 14 active `agy` connections) (`12` Pro and `3` Ultra, excluding banned `47f334b1-b801-41f6-a709-4ebabb7a86d6`), with `strategy: "auto"`, `candidatePool: ["agy"]`, `context_cache_protection: false`, `config.targetTimeoutMs: 120000`, and `config.predictiveTtftMs: 45000`

#### Scenario: Live chat completions route through multi-account Claude combos to authentic Claude models
- **WHEN** `POST /v1/chat/completions` is called with `model: "claude-opus-5.5"` or `model: "claude-sonnet-5.5"`
- **THEN** OmniRoute SHALL return HTTP 200 with a completion served by `claude-opus-5-5-high`/`claude-opus-4-6-thinking` or `claude-sonnet-5-5-high`/`claude-sonnet-4-6` on one of the 15 active Antigravity accounts with zero synthetic deprecation responses

#### Scenario: Upstream Claude 5.5 model cutover contract
- **WHEN** upstream Google Antigravity provisions and advertises `claude-opus-5-5-*` or `claude-sonnet-5-5-*` in its live discovery catalog
- **THEN** OmniRoute SHALL update the explicit model steps in `claude-opus-5.5` and `claude-sonnet-5-5` combos from 4.6 to the corresponding 5.5 identifiers while preserving all 15 connection mappings
