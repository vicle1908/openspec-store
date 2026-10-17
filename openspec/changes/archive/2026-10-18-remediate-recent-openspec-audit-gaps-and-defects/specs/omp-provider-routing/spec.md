# omp-provider-routing Specification Delta

## ADDED Requirements

### Requirement: Supersession of Pre-OmniRoute Role and Fallback Prohibitions

Canonical OMP routing in `~/.omp/agent/config.yml` SHALL permit validated `omniroute/*` selectors in `modelRoles` and `retry.fallbackChains` whenever backed by explicit fallback chains and isolated-profile smoke verification, superseding earlier bootstrap prohibitions against `omniroute` strings in `config.yml`.

#### Scenario: Validated OmniRoute selectors permitted in fallback chains and roles
- **WHEN** `~/.omp/agent/config.yml` is validated against `omp-provider-routing`
- **THEN** `retry.fallbackChains` entries for `omniroute/gemini-4-argon` and `omniroute/nx/*` pointing to `omniroute/gemini-3.8-flash-high` and `google-antigravity/gemini-3.8-flash:high` SHALL be recognized as compliant
- **AND** `modelRoles` assignments to either `google-antigravity/gemini-4-argon` or `omniroute/gemini-4-argon:high` SHALL be valid when backed by `models.yml` and `retry.fallbackChains`

## MODIFIED Requirements

### Requirement: Default Role Allocation to Gemini 4 Argon Combo

The `modelRoles.default` and `modelRoles.smol` roles in `~/.omp/agent/config.yml` SHALL be assigned to `google-antigravity/gemini-4-argon` (or `omniroute/gemini-4-argon:high` when routed via the gateway combo), while `omniroute/gemini-4-argon` and its explicit fallback chain remain declared in `models.yml` and `config.yml`.

#### Scenario: Default turn execution via combo
- **WHEN** OMP executes a turn without an explicit `--model` flag
- **THEN** the request SHALL route to the configured `gemini-4-argon` selector (`google-antigravity/gemini-4-argon` or `omniroute/gemini-4-argon:high`)
- **AND** the response SHALL be served without unmonitored fallback errors.

#### Scenario: Live config role alignment with specification
- **WHEN** `~/.omp/agent/config.yml` is inspected
- **THEN** `modelRoles.default` and `modelRoles.smol` SHALL match the documented `gemini-4-argon` assignment
- **AND** `retry.fallbackChains['omniroute/gemini-4-argon']` SHALL remain `['omniroute/gemini-3.8-flash-high', 'google-antigravity/gemini-3.8-flash:high']`
