# omp-provider-routing Specification Delta

## MODIFIED Requirements

### Requirement: OmniRoute Nexus Model Catalog Registration

The OmniRoute provider block in `~/.omp/agent/models.yml` SHALL declare entries for verified Nexus provider models: `nx/deepseek-v4.1-flash`, `nx/deepseek-v4-pro`, and `nx/gemini-4-argon`. Model entries SHALL declare catalog-verified context windows (`900000` for `nx/deepseek-v4.1-flash` and `1000000` for `nx/deepseek-v4-pro` and `nx/gemini-4-argon`), reasoning flags, and input modalities. Non-OmniRoute provider blocks SHALL remain unmutated.

#### Scenario: Nexus models registered in OMP catalog
- **WHEN** `omp models --json` or `~/.omp/agent/models.yml` is inspected
- **THEN** model entries `omniroute/nx/deepseek-v4.1-flash`, `omniroute/nx/deepseek-v4-pro`, and `omniroute/nx/gemini-4-argon` SHALL be present
- **AND** `nx/deepseek-v4.1-flash` SHALL declare `reasoning: true` and `contextWindow: 900000`
- **AND** `nx/deepseek-v4-pro` SHALL declare `reasoning: true` and `contextWindow: 1000000`
- **AND** `nx/gemini-4-argon` SHALL declare `reasoning: true`, `contextWindow: 1000000`, and `input: [text, image]`.

### Requirement: Default Role Allocation to Gemini 4 Argon Combo

The `modelRoles.default` and `modelRoles.smol` roles in `~/.omp/agent/config.yml` SHALL be assigned to `google-antigravity/gemini-4-argon`, while `modelRoles.commit` SHALL resolve to `omniroute/nx/deepseek-v4.1-flash` and `tiny`, `vision`, `slow`, `plan`, and `task` roles SHALL resolve to `omniroute/gemini-3.8-flash-high`.

#### Scenario: Default turn execution via combo
- **WHEN** OMP executes a turn without an explicit `--model` flag under `default` or `smol` role selection
- **THEN** the request SHALL route to `google-antigravity/gemini-4-argon` with `retry.fallbackChains` preserving failover to `omniroute/gemini-3.8-flash-high`
- **AND** the response SHALL be served without unmonitored fallback errors.

#### Scenario: Live config role alignment with specification
- **WHEN** `~/.omp/agent/config.yml` is inspected
- **THEN** `modelRoles.default` and `modelRoles.smol` SHALL match the documented `gemini-4-argon` assignment
- **AND** `retry.fallbackChains['omniroute/gemini-4-argon']` SHALL remain `['omniroute/gemini-3.8-flash-high', 'google-antigravity/gemini-3.8-flash:high']`

## ADDED Requirements

### Requirement: OMP 18.11.3 prewalk, image budget, and shell completion integration

OMP workstation configuration SHALL support `18.11.3` capabilities including custom gateway `imageCountBudget` declarations in `~/.omp/agent/models.yml`, `prewalk.auto` configuration in `~/.omp/agent/config.yml`, and dynamic Zsh completions via `eval "$(omp completions zsh)"` in `~/.zshrc`.

#### Scenario: OMP 18.11.3 features are active in shell and agent config
- **WHEN** `~/.omp/agent/config.yml`, `~/.omp/agent/models.yml`, and `~/.zshrc` are inspected
- **THEN** `config.yml` SHALL configure `prewalk.auto` (`"suggest"`)
- **AND** `models.yml` SHALL declare `imageCountBudget` on custom multimodal gateway models where supported
- **AND** interactive Zsh shells SHALL load `omp completions zsh`
