# Spec Delta: omp-provider-routing

## ADDED Requirements

### Requirement: OmniRoute Nexus Model Catalog Registration

The OmniRoute provider block in `~/.omp/agent/models.yml` SHALL declare entries for verified Nexus provider models: `nx/deepseek-v4.1-flash`, `nx/deepseek-v4-pro`, and `nx/Gemini 4 Argon`. Model entries SHALL declare catalog-verified context windows, reasoning flags, and input modalities. Non-OmniRoute provider blocks SHALL remain unmutated.

#### Scenario: Nexus models registered in OMP catalog
- **WHEN** `omp models --json` is executed
- **THEN** model entries `omniroute/nx/deepseek-v4.1-flash`, `omniroute/nx/deepseek-v4-pro`, and `omniroute/nx/Gemini 4 Argon` SHALL be present
- **AND** `nx/deepseek-v4.1-flash` SHALL declare `reasoning: true` and `contextWindow: 128000`
- **AND** `nx/deepseek-v4-pro` SHALL declare `reasoning: true` and `contextWindow: 1000000`
- **AND** `nx/Gemini 4 Argon` SHALL declare `reasoning: true`, `contextWindow: 1000000`, and `input: [text, image]`.

### Requirement: Fast Commit Role Reallocation

The `modelRoles.commit` role in `~/.omp/agent/config.yml` SHALL be assigned to `omniroute/nx/deepseek-v4.1-flash`. The `default`, `task`, `plan`, `slow`, `advisor`, `tiny`, `smol`, and `vision` roles SHALL preserve their existing primary assignments to `omniroute/gemini-3.8-flash-high` and `google-antigravity/gemini-3.8-flash:high`. `nx/Gemini 4 Argon` SHALL NOT be assigned to automatic execution roles while its upstream relay parameter validation is unstable.

#### Scenario: Commit role resolution
- **WHEN** OMP evaluates the `commit` role selector
- **THEN** it SHALL resolve to `omniroute/nx/deepseek-v4.1-flash`
- **AND** `task` and `default` roles SHALL continue resolving to their existing primary models.

### Requirement: Explicit Fail-Closed Fallback Chains for Nexus Models

The `retry.fallbackChains` configuration in `~/.omp/agent/config.yml` SHALL define explicit fallback chains for both `omniroute/nx/deepseek-v4.1-flash` and `omniroute/nx/Gemini 4 Argon`. Each chain SHALL specify `omniroute/gemini-3.8-flash-high` as primary fallback and `google-antigravity/gemini-3.8-flash:high` as secondary fallback.

#### Scenario: Fallback chain structure
- **WHEN** `~/.omp/agent/config.yml` is inspected programmatically
- **THEN** `retry.fallbackChains['omniroute/nx/deepseek-v4.1-flash']` SHALL contain `omniroute/gemini-3.8-flash-high` followed by `google-antigravity/gemini-3.8-flash:high`
- **AND** `retry.fallbackChains['omniroute/nx/Gemini 4 Argon']` SHALL contain `omniroute/gemini-3.8-flash-high` followed by `google-antigravity/gemini-3.8-flash:high`.

### Requirement: Isolated Profile Smoke Gate Verification

Prior to modifying the live `~/.omp/agent/models.yml` and `~/.omp/agent/config.yml` files, proposed changes SHALL be validated in an isolated throwaway profile with empty fallback chains. The isolated profile SHALL verify that `omniroute/nx/deepseek-v4.1-flash` successfully self-serves a completion with exit code 0 and no fallback or error events.

#### Scenario: Isolated profile smoke test
- **WHEN** `omp --profile <test-profile> --no-session --model 'omniroute/nx/deepseek-v4.1-flash' -p 'reply only: pong'` is executed
- **THEN** the process SHALL exit with code 0
- **AND** the response SHALL contain `pong`
- **AND** no `fallback`, `model_change`, or `error` markers SHALL be emitted.
