## MODIFIED Requirements

### Requirement: Custom provider credentials SHALL be registered

Three custom provider credential keys that appear in the production `~/.tdt/config.yaml` as `providers.*.auth_env` values SHALL be registered in the canonical `environment-key-registry.json` with `secret: true` and an explicit provider binding. The registry entries record credential metadata; the runtime credential validation is performed by `CredentialResolver.resolve()` using the provider-bound references projected from resolved routes, not by a registry lookup at resolution time.

#### Scenario: giaoduc credential accepted

- **GIVEN** the registry contains an entry for `HERMES_CUSTOM_GIAODUC_API_KEY` with `secret: true` and `provider: "giaoduc"`
- **AND** a canonical provider declares `auth_env: HERMES_CUSTOM_GIAODUC_API_KEY`
- **WHEN** `resolve_agent_profile()` resolves that provider
- **THEN** the resolved route SHALL record `CredentialAvailability(key_name="HERMES_CUSTOM_GIAODUC_API_KEY", available=<bool>, provider="giaoduc")`

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

### Requirement: Credential entries SHALL be provider-bound

Each registered custom credential entry SHALL have an explicit `provider` field matching the canonical provider name. `CredentialResolver.resolve()` SHALL reject a resolve request whose provider does not match the route's provider binding.

#### Scenario: Wrong-provider assignment rejected

- **GIVEN** a resolved route carries `CredentialAvailability(key_name="HERMES_CUSTOM_GIAODUC_API_KEY", provider="giaoduc")`
- **WHEN** `CredentialResolver.resolve()` is called with `provider="shopapikey"`
- **THEN** it SHALL raise `ProfileResolutionError`
- **AND** the error SHALL not reveal credential values

#### Scenario: Unknown credential key rejected

- **GIVEN** a resolve request names a key not present in the resolver's provider-bound references
- **WHEN** `CredentialResolver.resolve()` is called
- **THEN** it SHALL raise `ProfileResolutionError`
- **AND** the error SHALL NOT reveal credential values
