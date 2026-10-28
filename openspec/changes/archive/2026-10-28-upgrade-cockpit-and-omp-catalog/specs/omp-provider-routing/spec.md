# Spec Delta: omp-provider-routing

## MODIFIED Requirements

### Requirement: Cockpit Reasoning Metadata and Wildcard Fallback Chain Coverage
`~/.omp/agent/models.yml` SHALL declare exact native model identifiers for all 10 Cockpit text and coding models, accurate 272,000-token context windows, 128,000-token maximum output limits, `supportsTools: true`, `input: [text]`, and supported thinking effort modes matching the local Cockpit Tools backend (`http://localhost:51006/v1`), and `~/.omp/agent/config.yml` SHALL use `retry.fallbackChains['cockpit/*']` to guarantee fail-closed failover resilience during Cockpit downtime.

#### Scenario: Cockpit models declare reasoning efforts and wildcard fallback chain
- **WHEN** `~/.omp/agent/models.yml` and `~/.omp/agent/config.yml` are loaded on OMP start
- **THEN** every model under `providers.cockpit.models` SHALL declare `reasoning: true`, `supportsTools: true`, `imageCountBudget: 20`, and `thinking.efforts` containing `['low', 'medium', 'high', 'xhigh']`
- **AND** `retry.fallbackChains['cockpit/*']` SHALL equal `['google-antigravity/gemini-4-argon:high', 'omniroute/gemini-3.8-flash-high:high', 'google-antigravity/gemini-3.8-flash:high']` without duplicate `cockpit/gpt-6-astra` or `cockpit/gpt-6.1-sol` keys
- **AND** `retry.fallbackChains['google-antigravity/*']` SHALL equal `['omniroute/gemini-3.8-flash-high:high', 'google-antigravity/gemini-3.8-flash:high']`

#### Scenario: Full Native Model Catalog Declared
- **WHEN** OMP parses `models.yml` for the `cockpit` provider
- **THEN** it SHALL resolve exactly 10 distinct native chat and coding models: `gpt-6.1-sol`, `gpt-6.1-terra`, `gpt-6-astra`, `gpt-6-sol`, `gpt-6-luna`, `gpt-5.6-sol`, `gpt-5.6-terra`, `gpt-5.6-luna`, `codex-auto-review`, and `gpt-reserve`
- **AND** every model SHALL declare `contextWindow: 272000`, `maxTokens: 128000`, `supportsTools: true`, and `input: [text]`
- **AND** all 10 models SHALL declare `efforts: [low, medium, high, xhigh, max]` capped at `max` per OMP schema validation constraints
- **AND** non-chat image generator endpoint `gpt-image-2.5` SHALL be omitted from `providers.cockpit.models`

#### Scenario: Context Window Compaction Protection
- **WHEN** an agent conversation reaches large token volumes on a Cockpit model
- **THEN** OMP's client-side compaction threshold SHALL trigger at or before 244,800 tokens ($90\%$ of 272,000)
- **AND** OMP SHALL NOT send requests exceeding 272,000 tokens to the Cockpit endpoint

#### Scenario: Service Downtime Fallback Delegation
- **WHEN** Cockpit Tools is restarting or unavailable on `127.0.0.1:51006` and returns `ECONNREFUSED`
- **THEN** OMP SHALL automatically fail over via the `cockpit/*` fallback chain to `google-antigravity/gemini-4-argon:high` without terminating the agent session
