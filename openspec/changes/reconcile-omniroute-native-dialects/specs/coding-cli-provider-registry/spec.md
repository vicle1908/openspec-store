## MODIFIED Requirements

### Requirement: Consumer CLI OmniRoute registrations SHALL carry the live requested namespace/model pairs

Every consumer CLI governed by this capability that registers an OmniRoute provider SHALL register `sh/gpt-5.6-sol` for the OpenAI Responses route when its native SH probe passes, or SHALL register the exact model through the versionless Chat Completions fallback when a named compatibility failure is captured. It SHALL register `pm/Claude-Fable` for the Anthropic Messages route when that CLI supports the corresponding native protocol. The exact IDs SHALL be present in the live registry at apply time. Retired `dlg/*` inference routes SHALL NOT remain in any active OmniRoute catalog. A client-specific Chat Completions fallback MAY retain the exact requested model only after a native decoder/provider failure is captured and the versionless fallback is independently proven.

#### Scenario: goose catalog separates native and fallback routes

- **WHEN** goose custom providers are inspected
- **THEN** the native Anthropic provider, if enabled, SHALL contain `pm/Claude-Fable`
- **AND** the Responses provider, if enabled, SHALL contain `sh/gpt-5.6-sol`
- **AND** a chat fallback SHALL be explicitly identified and SHALL not be mistaken for native Responses or Messages
- **AND** no `dlg/*` model entry SHALL remain in an active provider owned by this capability

#### Scenario: pi uses separate native providers

- **WHEN** `~/.pi/agent/models.json` is inspected
- **THEN** an `anthropic-messages` provider SHALL contain `pm/Claude-Fable`
- **AND** an `openai-responses` provider SHALL contain `sh/gpt-5.6-sol`
- **AND** both providers SHALL use the documented environment reference for `OMNIROUTE_API_KEY`

#### Scenario: Kimi Code uses separate native or proven fallback providers

- **WHEN** `~/.kimi-code/config.toml` is inspected
- **THEN** the PM alias SHALL reference a provider with `type = "anthropic"` and model `pm/Claude-Fable`
- **AND** the SH alias SHALL reference a provider with `type = "openai_responses"` and model `sh/gpt-5.6-sol` when the native probe passes
- **AND** when FBC-2 is recorded, the SH alias SHALL instead reference a Chat Completions provider with root `base_url = "http://localhost:20128"` and the exact model `sh/gpt-5.6-sol`
- **AND** the existing mode-600 credential exception SHALL be recorded without printing or rotating its value

#### Scenario: existing providers and defaults are preserved

- **WHEN** a consumer CLI configuration is corrected
- **THEN** every provider present before the mutation SHALL remain present unless the provider is an explicitly replaced stale OmniRoute dialect block
- **AND** default model selections SHALL be byte-identical unless a separate default change was explicitly approved

### Requirement: Remaining consumer CLIs SHALL register live OmniRoute models with the protocol each client supports

Each consumer CLI that is mutated by this capability SHALL expose the requested models through the most faithful documented protocol available to that client: Anthropic Messages for `pm/Claude-Fable`, OpenAI Responses for `sh/gpt-5.6-sol`, or the empirically proven versionless Chat Completions fallback when the installed client cannot decode the native stream. The configuration SHALL reference `OMNIROUTE_API_KEY` through the client's documented environment mechanism wherever available and SHALL not change defaults implicitly.

#### Scenario: OpenCode, Kilo, Prime Agent, and Droid use native provider APIs

- **WHEN** these CLIs expose their OmniRoute model entries
- **THEN** their PM entries SHALL use an Anthropic-compatible provider and model `pm/Claude-Fable`
- **AND** their SH entries SHALL use a Responses-compatible provider and model `sh/gpt-5.6-sol`
- **AND** thinking settings SHALL use the provider-specific field for the selected API

#### Scenario: Grok uses a proven per-client fallback when required

- **WHEN** Grok's native SH Responses probe reports the captured `serialization error: missing field sequence_number` failure
- **THEN** the SH registration MAY use Chat Completions at the versionless route
- **AND** the PM registration SHALL use the native Messages route if its probe passes
- **AND** the evidence SHALL retain both the native failure and fallback success

#### Scenario: no implicit default change

- **WHEN** a new or corrected OmniRoute entry is written
- **THEN** session/default settings SHALL remain unchanged unless an explicit default approval is recorded
