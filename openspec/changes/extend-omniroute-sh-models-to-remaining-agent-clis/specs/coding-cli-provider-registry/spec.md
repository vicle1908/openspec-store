## ADDED Requirements

### Requirement: Remaining consumer CLIs SHALL register the live sh models with credential indirection

Each of the consumer CLIs opencode, grok, and droid that is mutated by this change SHALL register the model IDs `sh/gpt-5.6-sol` and `sh/Claude-Fable` against the OmniRoute endpoint `http://localhost:20128/v1`, SHALL reference `OMNIROUTE_API_KEY` through environment indirection, and SHALL NOT change any default model selection.

#### Scenario: opencode omniroute provider uses env indirection

- **WHEN** ~/.config/opencode/opencode.json is inspected
- **THEN** an `omniroute` provider entry SHALL exist with baseURL `http://localhost:20128/v1` and apiKey `{env:OMNIROUTE_API_KEY}`
- **AND** its model map SHALL contain `sh/gpt-5.6-sol` and `sh/Claude-Fable`

#### Scenario: grok omniroute provider and aliases use env-backed credentials

- **WHEN** ~/.grok/config.toml is inspected
- **THEN** `model_providers.omniroute` SHALL exist with base_url `http://localhost:20128/v1` and env_key `OMNIROUTE_API_KEY`
- **AND** model aliases SHALL map to `sh/gpt-5.6-sol` and `sh/Claude-Fable`
- **AND** the default model selection SHALL remain `cockpit-sol`

#### Scenario: droid omniroute custom models use BYOK env references

- **WHEN** ~/.factory/settings.json customModels is inspected
- **THEN** omniroute entries SHALL have baseUrl `http://localhost:20128/v1`, apiKey `${OMNIROUTE_API_KEY}`, provider type `openai`, and the model IDs `sh/gpt-5.6-sol` and `sh/Claude-Fable`
- **AND** session and mission default settings SHALL be unchanged

#### Scenario: existing providers and defaults are preserved

- **WHEN** any consumer CLI configuration mutated by this change is inspected after mutation
- **THEN** every provider present before mutation SHALL remain present
- **AND** default model selections SHALL be byte-identical unless a default change was explicitly approved for that CLI
