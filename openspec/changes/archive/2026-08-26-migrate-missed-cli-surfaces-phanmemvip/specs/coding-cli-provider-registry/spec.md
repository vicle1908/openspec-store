# coding-cli-provider-registry Delta

## Purpose

Define the expected provider registration state for the seven consumer coding
CLIs (omp, goose, pi, prime-agent, opencode, droid, cline) after the giaoduc
retirement: giaoduc absent everywhere, phanmemvip present via the OpenAI
Responses API, and the shopapikey Claude model named `Claude-Fable`.

## ADDED Requirements

### Requirement: No consumer CLI SHALL reference giaoduc

None of the seven consumer CLI configurations SHALL contain a giaoduc provider, model, or credential reference.

#### Scenario: giaoduc absent from all consumer configs

- **WHEN** `~/.omp/agent/{models,config}.yml`, `~/.config/goose/{config.yaml,custom_providers/}`, `~/.pi/agent/{models,settings}.json`, `~/.prime/agent/{models,settings}.json`, `~/.config/opencode/opencode.json`, `~/.factory/settings.json`, and `~/.cline/data/settings/providers.json` are inspected
- **THEN** no file SHALL contain `giaoduc` or the model name `Advance`

#### Scenario: opencode default is not giaoduc

- **WHEN** `~/.config/opencode/opencode.json` is inspected
- **THEN** `model` and `small_model` SHALL NOT reference giaoduc
- **AND** no `giaoduc` provider block SHALL exist

### Requirement: phanmemvip SHALL be registered in every consumer CLI via the Responses API

Each of the seven consumer CLIs SHALL register the phanmemvip provider (`https://api.phanmemvip.shop/v1`, key `HERMES_CUSTOM_PHANMEMVIP_API_KEY`, model `gpt-5.6-sol`) using its OpenAI Responses dialect.

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

### Requirement: The shopapikey Claude model SHALL be named Claude-Fable in every consumer CLI

Where a consumer CLI registers the shopapikey Claude model, its model ID SHALL be `Claude-Fable`, not `fable-5`.

#### Scenario: opencode shopapikey model renamed

- **WHEN** `~/.config/opencode/opencode.json` is inspected
- **THEN** the shopapikey provider's model list SHALL contain `Claude-Fable` and SHALL NOT contain `fable-5`

#### Scenario: droid shopapikey model renamed

- **WHEN** `~/.factory/settings.json` `customModels` is inspected
- **THEN** the phanmemvip.shop anthropic entry SHALL have model `Claude-Fable` and SHALL NOT have model `fable-5`

### Requirement: Consumer CLI migrations SHALL be smoke-verified

Each migrated consumer CLI SHALL pass a non-interactive smoke test against its phanmemvip registration before the change is archived.

#### Scenario: opencode smoke

- **WHEN** `opencode run -m phanmemvip/gpt-5.6-sol "reply only: pong"` is executed
- **THEN** the response SHALL contain `pong` with exit code 0

#### Scenario: droid smoke

- **WHEN** `droid exec` is run against the phanmemvip `gpt-5.6-sol` custom model with prompt "reply only: pong"
- **THEN** the response SHALL contain `pong` with exit code 0
