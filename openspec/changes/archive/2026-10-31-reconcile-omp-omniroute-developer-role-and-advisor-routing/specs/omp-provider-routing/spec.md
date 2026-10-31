# omp-provider-routing Specification Delta

## MODIFIED Requirements

### Requirement: Default Role Allocation to Gemini 4 Argon Combo

In `~/.omp/agent/config.yml`, `modelRoles.default` SHALL be assigned to `omniroute/gemini-4-argon`, `modelRoles.plan` to `google-antigravity/gemini-4-argon:high`, and `modelRoles.advisor` to `google-antigravity/gemini-3.8-flash:high`, while `modelRoles.smol`, `tiny`, `vision`, `slow`, `commit`, and `task` SHALL resolve to `omniroute/gemini-3.8-flash-high:high`.

#### Scenario: Default turn execution via combo
- **WHEN** OMP executes a turn without an explicit `--model` flag under `default` role selection
- **THEN** the request SHALL route to `omniroute/gemini-4-argon` with `retry.fallbackChains` preserving failover to `omniroute/gemini-3.8-flash-high:high` and `google-antigravity/gemini-3.8-flash:high`
- **AND** the response SHALL be served without unmonitored fallback errors

#### Scenario: Live config role alignment with specification
- **WHEN** `~/.omp/agent/config.yml` is inspected
- **THEN** `modelRoles.default` SHALL equal `'omniroute/gemini-4-argon'`, `modelRoles.plan` SHALL equal `'google-antigravity/gemini-4-argon:high'`, `modelRoles.advisor` SHALL equal `'google-antigravity/gemini-3.8-flash:high'`, and `modelRoles.smol` SHALL equal `'omniroute/gemini-3.8-flash-high:high'`
- **AND** `retry.fallbackChains['omniroute/gemini-4-argon']` SHALL equal `['omniroute/gemini-3.8-flash-high:high', 'google-antigravity/gemini-3.8-flash:high']`

### Requirement: OmniRoute No-Memory Headers, Reasoning Compat, and Root Key Hygiene

In `~/.omp/agent/models.yml`, `providers.omniroute` and `providers.omniroute-anthropic` SHALL declare `headers: { "x-omniroute-no-memory": "true" }`, `providers.omniroute` SHALL declare `compat: { supportsReasoningEffort: true, supportsDeveloperRole: false }`, and the unused root `equivalence` key and `promptCache` fields SHALL be absent.

#### Scenario: OmniRoute models retain thinking effort ladder and opt out of gateway memory injection
- **WHEN** `~/.omp/agent/models.yml` and `omp models --json` are inspected
- **THEN** `providers.omniroute.headers['x-omniroute-no-memory']` and `providers.omniroute-anthropic.headers['x-omniroute-no-memory']` SHALL both equal `'true'`
- **AND** `providers.omniroute.compat` SHALL set `supportsReasoningEffort: true` and `supportsDeveloperRole: false` so `omniroute/gemini-4-argon`, `omniroute/gemini-4-argon-high`, `omniroute/gemini-4-argon-medium`, `omniroute/gemini-4-argon-low`, and `omniroute/nx/gemini-4-argon` report `thinking: ["low", "medium", "high"]` instead of `null` in `omp models --json` while sending system prompts with `role: "system"`
- **AND** root key `equivalence` and model-level `promptCache` keys SHALL be absent from `~/.omp/agent/models.yml`
