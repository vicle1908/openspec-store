# coding-cli-provider-registry Specification

## Purpose
Define the expected provider registration state for the nine consumer coding
CLIs (omp, goose, pi, prime-agent, opencode, droid, cline, kimi, grok) after the giaoduc
retirement: giaoduc absent everywhere, phanmemvip present via the OpenAI
Responses API, and the shopapikey Claude model named `Claude-Fable`.

## Requirements

### Requirement: No consumer CLI SHALL reference giaoduc

None of the nine consumer CLI configurations SHALL contain a giaoduc provider, model, or credential reference.

#### Scenario: giaoduc absent from all consumer configs

- **WHEN** `~/.omp/agent/{models,config}.yml`, `~/.config/goose/{config.yaml,custom_providers/}`, `~/.pi/agent/{models,settings}.json`, `~/.prime/agent/{models,settings}.json`, `~/.config/opencode/opencode.json`, `~/.factory/settings.json`, `~/.cline/data/settings/providers.json`, `~/.kimi-code/config.toml`, and `~/.grok/config.toml` are inspected
- **THEN** no file SHALL contain `giaoduc` or the model name `Advance`

#### Scenario: opencode default is not giaoduc

- **WHEN** `~/.config/opencode/opencode.json` is inspected
- **THEN** `model` and `small_model` SHALL NOT reference giaoduc
- **AND** no `giaoduc` provider block SHALL exist

#### Scenario: kimi has no dead OmniRoute dlg models

- **WHEN** `~/.kimi-code/config.toml` is inspected
- **THEN** no model entry SHALL reference a `dlg/*` OmniRoute model ID

### Requirement: phanmemvip SHALL be registered in every consumer CLI via the Responses API

Each of the nine consumer CLIs SHALL register the phanmemvip provider (`https://api.phanmemvip.shop/v1`, key `HERMES_CUSTOM_PHANMEMVIP_API_KEY`, model `gpt-5.6-sol`) using its OpenAI Responses dialect.

#### Scenario: opencode phanmemvip uses Responses

- **WHEN** `~/.config/opencode/opencode.json` is inspected
- **THEN** the `phanmemvip` provider SHALL have `baseURL: https://api.phanmemvip.shop/v1` and `api: "responses"`
- **AND** its model list SHALL include `gpt-5.6-sol`

#### Scenario: droid phanmemvip custom model exists

- **WHEN** `~/.factory/settings.json` `customModels` is inspected
- **THEN** an entry with model `gpt-5.6-sol` SHALL exist with `baseUrl: https://api.phanmemvip.shop/v1` and provider type `openai`

#### Scenario: cline phanmemvip registered

- **WHEN** `~/.cline/data/settings/providers.json` is inspected
- **THEN** an `openai-native` provider entry SHALL reference model `gpt-5.6-sol` with base URL `https://api.phanmemvip.shop/v1`
- **AND** no `giaoduc` provider entry SHALL exist

#### Scenario: omp, goose, pi, prime-agent phanmemvip state preserved

- **WHEN** the omp, goose, pi, and prime-agent configurations are inspected
- **THEN** each SHALL retain its phanmemvip registration (`openai-responses` / `engine: openai` dialect, model `gpt-5.6-sol`) established by `replace-giaoduc-with-phanmemvip`

#### Scenario: kimi phanmemvip uses Responses

- **WHEN** `~/.kimi-code/config.toml` is inspected
- **THEN** a `phanmemvip` provider SHALL exist with `type = "openai_responses"` and `base_url = "https://api.phanmemvip.shop/v1"`
- **AND** model entries `phanmemvip-sol` (model `gpt-5.6-sol`) and `phanmemvip-claude-fable` (model `Claude-Fable`) SHALL reference it
- **AND** `default_model` SHALL be `phanmemvip-sol`

#### Scenario: grok phanmemvip uses Responses

- **WHEN** `~/.grok/config.toml` is inspected
- **THEN** the `phanmemvip` provider SHALL have `api_backend = "responses"` and `base_url = "https://api.phanmemvip.shop/v1"`
- **AND** `default` model SHALL be `phanmemvip-sol`

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

### Requirement: Consumer CLI migrations SHALL be smoke-verified

Each migrated consumer CLI SHALL pass a non-interactive smoke test against its phanmemvip registration before the change is archived.

#### Scenario: opencode smoke

- **WHEN** `opencode run -m phanmemvip/gpt-5.6-sol "reply only: pong"` is executed
- **THEN** the response SHALL contain `pong` with exit code 0

#### Scenario: droid smoke

- **WHEN** `droid exec` is run against the phanmemvip `gpt-5.6-sol` custom model with prompt "reply only: pong"
- **THEN** the response SHALL contain `pong` with exit code 0

#### Scenario: kimi smoke

- **WHEN** `kimi -p "reply only: pong" --model phanmemvip-sol` is executed
- **THEN** the response SHALL contain `pong` with exit code 0

#### Scenario: grok smoke

- **WHEN** `grok -p "reply only: pong"` (default phanmemvip-sol) and `grok --model shopapikey-claude-fable -p "reply only: pong"` are executed
- **THEN** both responses SHALL contain `pong` with exit code 0

### Requirement: Consumer CLI OmniRoute registrations SHALL carry the live sh/gpt-5.6-sol and sh/Claude-Fable models

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

### Requirement: Remaining consumer CLIs SHALL register the live sh models with credential indirection

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
