# Spec Delta

## ADDED Requirements

### Requirement: OMP OmniRoute Catalog SHALL Declare Tiered Gemini 4 Argon Combo Models

The `providers.omniroute.models` list in `~/.omp/agent/models.yml` SHALL declare top-level combo entries `gemini-4-argon-high`, `gemini-4-argon-medium`, and `gemini-4-argon-low` alongside `gemini-4-argon`. Each entry SHALL configure `reasoning: true`, `thinking` effort mode (`efforts: [low, medium, high]` with tier-matched `defaultLevel`), `supportsTools: true`, `input: [text, image]`, `contextWindow: 1000000`, `maxTokens: 128000`, and `imageCountBudget: 20`.

#### Scenario: Tiered Gemini 4 Argon combo selectors registered in OMP catalog
- **WHEN** `omp models --json` and `~/.omp/agent/models.yml` are inspected
- **THEN** selectors `omniroute/gemini-4-argon-high`, `omniroute/gemini-4-argon-medium`, `omniroute/gemini-4-argon-low`, and `omniroute/gemini-4-argon` SHALL be present
- **AND** each entry SHALL report `reasoning: true`, `contextWindow: 1000000`, and `maxTokens: 128000`
- **AND** `thinking.defaultLevel` SHALL equal `high` for `gemini-4-argon-high` and `gemini-4-argon`, `medium` for `gemini-4-argon-medium`, and `low` for `gemini-4-argon-low`
- **AND** non-OmniRoute provider blocks in `~/.omp/agent/models.yml` SHALL remain byte-identical

#### Scenario: Isolated-profile and live attribution probes succeed without fallback masquerade
- **WHEN** `omp --mode json --no-session --model "<selector>" -p "reply only: pong"` is executed for `omniroute/gemini-4-argon-high`, `omniroute/gemini-4-argon-medium`, `omniroute/gemini-4-argon-low`, and `omniroute/gemini-4-argon`
- **THEN** each invocation SHALL exit with code `0` and emit `"pong"`
- **AND** assistant event metadata SHALL report `provider: "omniroute"` with zero `retry_fallback_applied` or `retry_fallback_succeeded` events

### Requirement: OMP Fallback Chains SHALL Cover All Gemini 4 Argon Tier Combo Selectors

The `retry.fallbackChains` map in `~/.omp/agent/config.yml` SHALL define explicit fail-closed fallback chains for `omniroute/gemini-4-argon-high`, `omniroute/gemini-4-argon-medium`, `omniroute/gemini-4-argon-low`, and `omniroute/gemini-4-argon`, routing failover to `omniroute/gemini-3.8-flash-high` as primary fallback and `google-antigravity/gemini-3.8-flash:high` as secondary fallback while preserving active `modelRoles`.

#### Scenario: Tiered Gemini 4 Argon fallback chains configured in config.yml
- **WHEN** `~/.omp/agent/config.yml` is parsed with a YAML loader
- **THEN** `retry.fallbackChains['omniroute/gemini-4-argon-high']`, `retry.fallbackChains['omniroute/gemini-4-argon-medium']`, `retry.fallbackChains['omniroute/gemini-4-argon-low']`, and `retry.fallbackChains['omniroute/gemini-4-argon']` SHALL each equal `['omniroute/gemini-3.8-flash-high', 'google-antigravity/gemini-3.8-flash:high']`
- **AND** existing `modelRoles` assignments SHALL remain unchanged
