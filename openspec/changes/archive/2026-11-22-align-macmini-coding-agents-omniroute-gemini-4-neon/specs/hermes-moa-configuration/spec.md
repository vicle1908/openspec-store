# Spec Delta

## ADDED Requirements

### Requirement: Hermes OmniRoute Gemini 4 Neon Model Catalog Exposure
In `~/.hermes/config.yaml` on `iosteam-mac-mini`, `providers.omniroute.models` SHALL include `gemini-4-neon`, `agent.reasoning_overrides` SHALL map `gemini-4-neon: high`, and the primary default preset SHALL remain `moa:default`.

#### Scenario: Hermes exposes Gemini 4 Neon under OmniRoute without altering MoA defaults
- **WHEN** `~/.hermes/config.yaml` is parsed with a YAML loader
- **THEN** `providers.omniroute.models` SHALL contain `'gemini-4-neon'`
- **AND** `agent.reasoning_overrides['gemini-4-neon']` SHALL equal `'high'`
- **AND** `model.provider` SHALL remain `'moa'` and `model.default` SHALL remain `'default'`
- **AND** `fallback_providers` SHALL remain `[{provider: 'omniroute', model: 'gemini-3.8-flash-high'}]`
