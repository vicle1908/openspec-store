# Spec Delta

## ADDED Requirements

### Requirement: Multi-Account Claude Opus and Sonnet Combo Pooling across Antigravity Accounts

OmniRoute SHALL configure `claude-opus-5.5` and `claude-sonnet-5.5` combos to pool all 15 active Antigravity OAuth connections across explicit connection-scoped model steps (`agy/claude-opus-4-6-thinking` and `agy/claude-sonnet-4-6`) with `strategy: "auto"`, `candidatePool: ["agy"]`, and `context_cache_protection: false`, and SHALL preserve the 15-account topology for upstream 5.5 model cutover.

#### Scenario: Claude Opus 5.5 combo pools all 15 Antigravity accounts
- **WHEN** `GET /api/combos/{id}` is queried for `claude-opus-5.5` (`4b2430da-0b3b-4b0e-9773-ec0f97adc252`)
- **THEN** OmniRoute SHALL return a combo with 15 explicit model steps targeting `agy/claude-opus-4-6-thinking` (one for each active `agy` connection), with `strategy: "auto"`, `candidatePool: ["agy"]`, and `context_cache_protection: false`

#### Scenario: Claude Sonnet 5.5 combo pools all 15 Antigravity accounts
- **WHEN** `GET /api/combos/{id}` is queried for `claude-sonnet-5.5` (`9447399c-856b-4f52-8820-b3bf3dc3f132`)
- **THEN** OmniRoute SHALL return a combo with 15 explicit model steps targeting `agy/claude-sonnet-4-6` (one for each active `agy` connection), with `strategy: "auto"`, `candidatePool: ["agy"]`, and `context_cache_protection: false`

#### Scenario: Live chat completions route through multi-account Claude combos to authentic Claude models
- **WHEN** `POST /v1/chat/completions` is called with `model: "claude-opus-5.5"` or `model: "claude-sonnet-5.5"`
- **THEN** OmniRoute SHALL return HTTP 200 with a completion served by `claude-opus-4-6-thinking` or `claude-sonnet-4-6` on one of the 15 active Antigravity accounts

#### Scenario: Upstream Claude 5.5 model cutover contract
- **WHEN** upstream Google Antigravity provisions and advertises `claude-opus-5-5-*` or `claude-sonnet-5-5-*` in its live discovery catalog
- **THEN** OmniRoute SHALL update the explicit model steps in `claude-opus-5.5` and `claude-sonnet-5.5` combos from 4.6 to the corresponding 5.5 identifiers while preserving all 15 connection mappings
