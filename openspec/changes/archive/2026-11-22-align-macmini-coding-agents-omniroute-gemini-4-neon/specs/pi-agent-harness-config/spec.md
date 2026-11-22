# Spec Delta

## ADDED Requirements

### Requirement: Pi Default Model Cutover to Gemini 4 Neon
In `~/.pi/agent/settings.json` on `iosteam-mac-mini`, `defaultModel` and `subagents.defaultModel` SHALL be configured as `"gemini-4-neon"`, `~/.pi/agent/models.json` SHALL declare `gemini-4-neon` under both `omniroute-responses` (`contextWindow: 512000`, `maxTokens: 262144`) and `omp` (`contextWindow: 1048576`, `maxTokens: 262144`), and role-based `subagents.agentOverrides` SHALL route primary subagents to `gemini-4-neon`.

#### Scenario: Pi startup and interactive sessions default to Gemini 4 Neon
- **WHEN** `~/.pi/agent/settings.json` is inspected
- **THEN** `defaultProvider` SHALL be `"omniroute-responses"`
- **AND** `defaultModel` SHALL be `"gemini-4-neon"`
- **AND** `modelThinkingLevels["omniroute-responses/gemini-4-neon"]` SHALL be `"high"`
- **AND** `gemini-4-hydrogen` and `gemini-3.8-flash-high` SHALL remain available in `models.json` as selectable and fallback options

#### Scenario: Pi subagent overrides route to Gemini 4 Neon
- **WHEN** `subagents.agentOverrides` in `~/.pi/agent/settings.json` is inspected
- **THEN** `scout`, `researcher`, and `worker` SHALL declare `"model": "omniroute-responses/gemini-4-neon"`
- **AND** `oracle` SHALL preserve `"model": "omniroute-responses/gemini-4-argon-high"` and `reviewer` SHALL preserve `"model": "omniroute-responses/gemini-4-hydrogen-xhigh"`
