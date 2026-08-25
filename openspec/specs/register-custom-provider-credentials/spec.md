# register-custom-provider-credentials Specification

## Purpose

Define registration of the three custom provider credential keys
(shopapikey, giaoduc, cockpit) in the canonical environment-key-registry
with secret classification, provider binding, cross-provider rejection,
and preservation of existing credential entries.

## Requirements

### Requirement: Credential entries SHALL be provider-bound

Each registered custom credential entry SHALL have an explicit `provider` field matching the canonical provider name. `CredentialResolver.resolve()` SHALL reject a resolve request whose provider does not match the route's provider binding.

#### Scenario: Wrong-provider assignment rejected

- **GIVEN** a resolved route carries `CredentialAvailability(key_name="HERMES_CUSTOM_PHANMEMVIP_API_KEY", provider="phanmemvip")`
- **WHEN** `CredentialResolver.resolve()` is called with `provider="shopapikey"`
- **THEN** it SHALL raise `ProfileResolutionError`
- **AND** the error SHALL not reveal credential values

#### Scenario: Unknown credential key rejected

- **WHEN** a resolve request names a key not present in the resolver's provider-bound references
- **THEN** it SHALL raise `ProfileResolutionError`
- **AND** the error SHALL NOT reveal credential values

### Requirement: Credential values SHALL NOT appear in registry or profiles

The registry entries MUST NOT contain literal credential values. Resolved profiles MUST record only `key_name`, `available` (boolean), and `provider` — never the secret itself.

#### Scenario: No secret in registry

- **WHEN** the registry JSON is inspected
- **THEN** no entry SHALL contain a literal API key, token, or password value
- **AND** all credential entries SHALL have `"secret": true`

#### Scenario: No secret in resolved profile

- **WHEN** a resolved profile is serialized or diagnosed
- **THEN** credential entries SHALL contain only `key_name`, `available`, and `provider`
- **AND** no `value` or `secret_value` field SHALL appear

### Requirement: Existing credential entries remain unchanged

The three existing credential entries (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `MODEL_API_KEY`) SHALL NOT be modified by this change.

#### Scenario: Anthropic entry preserved

- **WHEN** the registry is loaded after the change
- **THEN** `credential.anthropic.api_key` SHALL remain registered with `provider: "anthropic"` and `secret: true`

#### Scenario: OpenAI entry preserved

- **WHEN** the registry is loaded after the change
- **THEN** `credential.openai.api_key` SHALL remain registered with `provider: "openai-chat"` and `secret: true`

#### Scenario: Model entry preserved

- **WHEN** the registry is loaded after the change
- **THEN** `credential.model.api_key` SHALL remain registered with `provider: null` and `secret: true`

### Requirement: Custom provider credentials SHALL be registered for the active provider set

Three custom provider credential keys that appear in the production `~/.tdt/config.yaml` as `providers.*.auth_env` values SHALL be registered in the canonical `environment-key-registry.json` with `secret: true` and an explicit provider binding. The registered set SHALL be `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` (shopapikey), `HERMES_CUSTOM_PHANMEMVIP_API_KEY` (phanmemvip), and `HERMES_CUSTOM_COCKPIT_API_KEY` (cockpit); no `HERMES_CUSTOM_GIAODUC_API_KEY` entry SHALL remain. The registry entries record credential metadata; the runtime credential validation is performed by `CredentialResolver.resolve()` using the provider-bound references projected from resolved routes, not by a registry lookup at resolution time.

#### Scenario: phanmemvip credential accepted

- **GIVEN** the registry contains an entry for `HERMES_CUSTOM_PHANMEMVIP_API_KEY` with `secret: true` and `provider: "phanmemvip"`
- **AND** a canonical provider declares `auth_env: HERMES_CUSTOM_PHANMEMVIP_API_KEY`
- **WHEN** `resolve_agent_profile()` resolves that provider
- **THEN** the resolved route SHALL record `CredentialAvailability(key_name="HERMES_CUSTOM_PHANMEMVIP_API_KEY", available=<bool>, provider="phanmemvip")`

#### Scenario: shopapikey credential accepted

- **GIVEN** the registry contains an entry for `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` with `secret: true` and `provider: "shopapikey"`
- **AND** a canonical provider declares `auth_env: HERMES_CUSTOM_SHOPAPIKEY_API_KEY`
- **WHEN** `resolve_agent_profile()` resolves that provider
- **THEN** the resolved route SHALL record `CredentialAvailability(key_name="HERMES_CUSTOM_SHOPAPIKEY_API_KEY", available=<bool>, provider="shopapikey")`

#### Scenario: cockpit credential accepted

- **GIVEN** the registry contains an entry for `HERMES_CUSTOM_COCKPIT_API_KEY` with `secret: true` and `provider: "cockpit"`
- **AND** a canonical provider declares `auth_env: HERMES_CUSTOM_COCKPIT_API_KEY`
- **WHEN** `resolve_agent_profile()` resolves that provider
- **THEN** the resolved route SHALL record `CredentialAvailability(key_name="HERMES_CUSTOM_COCKPIT_API_KEY", available=<bool>, provider="cockpit")`

#### Scenario: giaoduc credential entry removed

- **WHEN** the registry JSON is inspected after the change
- **THEN** no entry for `HERMES_CUSTOM_GIAODUC_API_KEY` SHALL exist
- **AND** no registry entry SHALL carry `provider: "giaoduc"`
