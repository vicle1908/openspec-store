# Spec Delta

## ADDED Requirements

### Requirement: OMP Base Interactive Default Role Cutover to OmniRoute Gemini 4 Neon
In `~/.omp/agent/config.yml` on `iosteam-mac-mini`, `modelRoles.default` SHALL be assigned to `omniroute/gemini-4-neon`, and `~/.omp/agent/models.yml` SHALL add `headers.x-omniroute-no-memory: "true"` under `providers.omniroute`, register `gemini-4-neon` under `providers.omniroute.models` (`contextWindow: 512000`, `maxTokens: 262144`), and create `providers.omp` (`baseUrl: http://127.0.0.1:4000/v1`) registering `gemini-4-neon` (`contextWindow: 1048576`, `maxTokens: 262144`).

#### Scenario: OMP default role resolves to OmniRoute Gemini 4 Neon
- **WHEN** `~/.omp/agent/config.yml` is parsed with a YAML loader
- **THEN** `modelRoles.default` SHALL equal `'omniroute/gemini-4-neon'`
- **AND** `modelRoles.task`, `modelRoles.slow`, and `modelRoles.advisor` SHALL preserve their existing validated assignments
- **AND** `omp models --json` SHALL resolve `omniroute/gemini-4-neon` with `contextWindow: 512000` and `supportsTools: true`

#### Scenario: Local OMP provider registers active Gemini 4 Neon mirror
- **WHEN** `~/.omp/agent/models.yml` is parsed with a YAML loader
- **THEN** `providers.omp.models` SHALL include `gemini-4-neon` with `contextWindow: 1048576`, `maxTokens: 262144`, and `thinking.efforts: [low, medium, high]`
- **AND** `omp/gemini-4-carbon` SHALL be absent from `providers.omp.models`

### Requirement: Fail-Closed Fallback Chain for OmniRoute Gemini 4 Neon
The `retry.fallbackChains` configuration in `~/.omp/agent/config.yml` on `iosteam-mac-mini` SHALL define an explicit fail-closed fallback chain for `omniroute/gemini-4-neon` routing through local `omp/gemini-4-neon:high`, `omniroute/gemini-4-hydrogen:high`, `omp/gemini-4-hydrogen:high`, and `google-antigravity/gemini-4-hydrogen:high` ahead of `omniroute/gemini-3.8-flash-high:high` and `google-antigravity/gemini-3.8-flash:high`.

#### Scenario: Neon fallback chain covers local and remote failover paths
- **WHEN** `retry.fallbackChains` in `~/.omp/agent/config.yml` is inspected
- **THEN** `retry.fallbackChains['omniroute/gemini-4-neon']` SHALL equal:
  ```yaml
  - omp/gemini-4-neon:high
  - omniroute/gemini-4-hydrogen:high
  - omp/gemini-4-hydrogen:high
  - google-antigravity/gemini-4-hydrogen:high
  - omniroute/gemini-3.8-flash-high:high
  - google-antigravity/gemini-3.8-flash:high
  ```
- **AND** `gemini-4-carbon` SHALL NOT appear in any fallback chain entry
- **AND** `omp models --kind all` SHALL start with zero `Fallback chain` warning diagnostics
