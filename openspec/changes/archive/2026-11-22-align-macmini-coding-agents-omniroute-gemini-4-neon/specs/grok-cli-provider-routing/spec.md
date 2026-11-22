# Spec Delta

## ADDED Requirements

### Requirement: Grok Default Model Cutover to OmniRoute Gemini 4 Neon
In `~/.grok/config.toml` on `iosteam-mac-mini`, `[models] default` SHALL be configured as `"omniroute-gemini-4-neon"`, `[model_providers.omp]` and `[subagents]` SHALL be added, and Gemini 4 reasoning efforts SHALL be constrained to `["high", "medium", "low"]`.

#### Scenario: Grok starts with OmniRoute Gemini 4 Neon default
- **WHEN** `~/.grok/config.toml` is parsed with a TOML loader
- **THEN** `[models] default` SHALL equal `"omniroute-gemini-4-neon"`
- **AND** `[model.omniroute-gemini-4-neon]` SHALL declare `model = "gemini-4-neon"`, `context_window = 512000`, and `reasoning_effort = "high"`
- **AND** `session_summary` SHALL preserve `"omniroute-gemini-flash"` and `[subagents.models]` SHALL set `default = "omniroute-gemini-flash"` and `explore = "omp-gemini-flash"`
- **AND** all Gemini 4 model entries SHALL declare reasoning efforts restricted to `["high", "medium", "low"]` without `minimal` or `max`
