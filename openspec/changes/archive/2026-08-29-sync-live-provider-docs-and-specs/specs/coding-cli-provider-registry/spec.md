## MODIFIED Requirements

### Requirement: Consumer CLI OmniRoute registrations SHALL carry the live sh/gpt-5.6-sol and sh/Claude-Fable models

Every consumer CLI governed by this capability that registers an OmniRoute provider SHALL register the model IDs `sh/gpt-5.6-sol` and `sh/Claude-Fable`, using only IDs present in the live `sh/*` registry at apply time, except where an explicitly reviewed provider-specific allowlist defines a different set. Retired `dlg/*` inference routes SHALL NOT remain in any active OmniRoute catalog. The OmniRoute credential SHALL be referenced through `OMNIROUTE_API_KEY` environment indirection wherever the CLI's official mechanism supports it.

#### Scenario: goose catalog contains the live sh models and no retired dlg routes

- **WHEN** `~/.config/goose/custom_providers/custom_omniroute.json` is inspected
- **THEN** the model list SHALL contain `sh/gpt-5.6-sol` and `sh/Claude-Fable`
- **AND** no `dlg/*` model entry SHALL remain
- **AND** `api_key_env` SHALL name `OMNIROUTE_API_KEY`

#### Scenario: pi omniroute provider registers both sh models with env indirection

- **WHEN** `~/.pi/agent/models.json` is inspected
- **THEN** the `omniroute` provider SHALL have `apiKey` set to `${OMNIROUTE_API_KEY}`
- **AND** its model list SHALL contain `sh/gpt-5.6-sol` with `contextWindow` 1050000 and `sh/Claude-Fable` with `contextWindow` 200000

#### Scenario: kimi registers both sh models through the omniroute provider

- **WHEN** `~/.kimi-code/config.toml` is inspected
- **THEN** model aliases `or-gpt-5-6-sol` (model `sh/gpt-5.6-sol`) and `or-claude-fable` (model `sh/Claude-Fable`) SHALL reference the `omniroute` provider
- **AND** the `omniroute` provider SHALL use the `openai` chat-completions dialect against `http://localhost:20128/v1`

#### Scenario: kimi literal-key posture is the documented exception

- **GIVEN** kimi exposes no documented environment indirection for provider `api_key` values
- **WHEN** the kimi `omniroute` provider is inspected
- **THEN** a literal `api_key` value SHALL be permitted for that provider only
- **AND** `~/.kimi-code/config.toml` SHALL remain mode 600

#### Scenario: Prime Agent reviewed allowlist exception

- **WHEN** `~/.prime/agent/models.json` is inspected
- **THEN** the `omniroute` provider SHALL use `api: openai-responses`, `baseUrl: http://localhost:20128/v1`, and `apiKey: OMNIROUTE_API_KEY`
- **AND** its reviewed model allowlist SHALL contain `sh/codex` and `sh/gpt-5.6-sol`
- **AND** it SHALL NOT be required to register `sh/Claude-Fable` because the reviewed Prime Agent allowlist intentionally differs from the generic consumer-CLI set

#### Scenario: existing providers and defaults are preserved

- **WHEN** any consumer CLI configuration mutated by this change is inspected after mutation
- **THEN** every provider present before mutation SHALL remain present
- **AND** default model selections SHALL be byte-identical unless a default change was explicitly approved for that CLI
