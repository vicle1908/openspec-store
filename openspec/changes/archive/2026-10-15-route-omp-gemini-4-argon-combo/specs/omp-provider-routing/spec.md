# Spec Delta: omp-provider-routing

## ADDED Requirements

### Requirement: OmniRoute Gemini 4 Argon Combo Model Declaration

The OmniRoute provider block in `~/.omp/agent/models.yml` SHALL declare the top-level combo model `gemini-4-argon` without provider prefix, matching OmniRoute's native combo catalog. The entry SHALL declare `reasoning: true`, effort-based thinking tiers (`low`, `medium`, `high`), tool support, and `input: [text, image]`.

#### Scenario: Combo model registered in OMP catalog
- **WHEN** `omp models --json` is executed
- **THEN** model entry `omniroute/gemini-4-argon` SHALL be present
- **AND** it SHALL declare `reasoning: true` and `contextWindow: 1000000`.

### Requirement: Default Role Allocation to Gemini 4 Argon Combo

The `modelRoles.default` role in `~/.omp/agent/config.yml` SHALL be assigned to `omniroute/gemini-4-argon:high`. Unrelated roles (`commit`, `task`, `plan`, `slow`, `advisor`, `smol`, `tiny`, `vision`) SHALL preserve their active assignments.

#### Scenario: Default turn execution via combo
- **WHEN** OMP executes a turn without an explicit `--model` flag
- **THEN** the request SHALL route to `omniroute/gemini-4-argon`
- **AND** the response SHALL be served without unmonitored fallback errors.

### Requirement: Explicit Fail-Closed Fallback for Gemini 4 Argon Combo

The `retry.fallbackChains` configuration in `~/.omp/agent/config.yml` SHALL define an explicit fallback chain for `omniroute/gemini-4-argon` pointing to `omniroute/gemini-3.8-flash-high` as primary fallback and `google-antigravity/gemini-3.8-flash:high` as secondary fallback.

#### Scenario: Fallback chain configuration
- **WHEN** `~/.omp/agent/config.yml` is inspected programmatically
- **THEN** `retry.fallbackChains['omniroute/gemini-4-argon']` SHALL equal `['omniroute/gemini-3.8-flash-high', 'google-antigravity/gemini-3.8-flash:high']`.
