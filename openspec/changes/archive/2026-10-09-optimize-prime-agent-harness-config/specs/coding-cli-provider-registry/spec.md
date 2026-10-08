# Spec Delta

## MODIFIED Requirements

### Requirement: The shopapikey Claude model SHALL be named Claude-Fable in every consumer CLI

Where a consumer CLI registers the shopapikey Claude model, its model ID SHALL be `Claude-Fable`, not `fable-5`, and it SHALL be routed through a transport the endpoint supports for that model.

#### Scenario: opencode shopapikey model renamed

- **WHEN** `~/.config/opencode/opencode.json` is inspected
- **THEN** the shopapikey provider's model list SHALL contain `Claude-Fable` and SHALL NOT contain `fable-5`

#### Scenario: droid shopapikey model renamed

- **WHEN** `~/.factory/settings.json` `customModels` is inspected
- **THEN** the phanmemvip.shop anthropic entry SHALL have model `Claude-Fable` and SHALL NOT have model `fable-5`

#### Scenario: grok shopapikey Claude-Fable uses the Responses backend

- **WHEN** `~/.grok/config.toml` is inspected
- **THEN** the `shopapikey` provider SHALL have `api_backend = "responses"`
- **AND** it SHALL NOT carry an Anthropic-only `extra_headers` block
- **AND** the `shopapikey-claude-fable` model entry SHALL have `model = "Claude-Fable"`

#### Scenario: Prime Agent SHALL NOT default to a non-delivering shopapikey selection

- **WHEN** `~/.prime/agent/settings.json` is inspected
- **THEN** `defaultProvider`/`defaultModel` SHALL NOT name a shopapikey model registration whose endpoint returns a constant prompt-token count independent of the assembled system prompt
- **AND** the corrected default SHALL be a registration verified to deliver the harness system prompt
- **AND** the other eight consumer CLIs' shopapikey registrations SHALL be unchanged by that correction
