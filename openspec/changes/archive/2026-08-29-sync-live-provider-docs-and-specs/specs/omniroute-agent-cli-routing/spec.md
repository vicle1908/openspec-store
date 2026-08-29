## ADDED Requirements

### Requirement: Prime Agent OmniRoute registration SHALL preserve the reviewed allowlist

Prime Agent's `omniroute` provider registration SHALL use its documented custom-provider configuration surface with base URL `http://localhost:20128/v1`, API `openai-responses`, and `OMNIROUTE_API_KEY` environment indirection. Its reviewed model allowlist SHALL be exactly `sh/codex` and `sh/gpt-5.6-sol`. Existing Prime Agent providers and default model selection SHALL remain unchanged.

#### Scenario: Prime Agent provider registration matches the reviewed allowlist

- **WHEN** `~/.prime/agent/models.json` is inspected
- **THEN** the `omniroute` provider SHALL have `baseUrl: http://localhost:20128/v1`, `api: openai-responses`, and `apiKey: OMNIROUTE_API_KEY`
- **AND** its model list SHALL contain exactly `sh/codex` and `sh/gpt-5.6-sol`

#### Scenario: Prime Agent defaults and providers remain preserved

- **WHEN** the Prime Agent configuration is inspected after the OmniRoute registration
- **THEN** the existing `phanmemvip`, `shopapikey`, and `cockpit` providers SHALL remain present
- **AND** the default provider and default model selection SHALL remain unchanged
