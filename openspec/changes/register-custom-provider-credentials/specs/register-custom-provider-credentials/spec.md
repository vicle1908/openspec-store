# Specs: register-custom-provider-credentials

## ADDED Requirements

### Requirement: Custom provider credentials SHALL be registered

Three custom provider credential keys that appear in the production `~/.tdt/config.yaml` as `providers.*.api_key_env` values SHALL be registered in the canonical `environment-key-registry.json` with `secret: true` and an explicit provider binding.

#### Scenario: giaoduc credential accepted

- **WHEN** the registry is loaded and `resolve_agent_profile()` encounters `providers.giaoduc.api_key_env: HERMES_CUSTOM_GIAODUC_API_KEY`
- **THEN** `credential_entry()` SHALL accept the key bound to provider `giaoduc`
- **AND** the resolved profile SHALL record `CredentialAvailability(key_name="HERMES_CUSTOM_GIAODUC_API_KEY", available=<bool>, provider="giaoduc")`

#### Scenario: shopapikey credential accepted

- **WHEN** the registry is loaded and `resolve_agent_profile()` encounters `providers.shopapikey.api_key_env: HERMES_CUSTOM_SHOPAPIKEY_API_KEY`
- **THEN** `credential_entry()` SHALL accept the key bound to provider `shopapikey`
- **AND** the resolved profile SHALL record `CredentialAvailability(key_name="HERMES_CUSTOM_SHOPAPIKEY_API_KEY", available=<bool>, provider="shopapikey")`

#### Scenario: cockpit credential accepted

- **WHEN** the registry is loaded and `resolve_agent_profile()` encounters `providers.cockpit.api_key_env: HERMES_CUSTOM_COCKPIT_API_KEY`
- **THEN** `credential_entry()` SHALL accept the key bound to provider `cockpit`
- **AND** the resolved profile SHALL record `CredentialAvailability(key_name="HERMES_CUSTOM_COCKPIT_API_KEY", available=<bool>, provider="cockpit")`

### Requirement: Credential entries SHALL be provider-bound

Each registered custom credential entry SHALL have an explicit `provider` field matching the YAML provider name. `credential_entry()` SHALL reject cross-provider assignments.

#### Scenario: Wrong-provider assignment rejected

- **GIVEN** `HERMES_CUSTOM_GIAODUC_API_KEY` is registered with `provider: "giaoduc"`
- **WHEN** a provider entry for `shopapikey` references `api_key_env: HERMES_CUSTOM_GIAODUC_API_KEY`
- **THEN** `credential_entry()` SHALL raise `ProfileResolutionError`
- **AND** the error SHALL not reveal credential values

#### Scenario: Unknown credential key rejected

- **WHEN** a provider entry references an `api_key_env` value not present in the registry
- **THEN** `credential_entry()` SHALL raise `ProfileResolutionError`
- **AND** the error SHALL name the missing key

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
