# register-custom-provider-credentials Delta

## REMOVED Requirements

### Requirement: Custom provider credentials SHALL be registered

**Reason**: The registered credential set changes from (shopapikey, giaoduc,
cockpit) to (shopapikey, phanmemvip, cockpit) because the giaoduc provider is
retired and replaced by phanmemvip. The requirement is rebuilt below with the
new provider set; the giaoduc scenario is intentionally dropped.

**Migration**: The rebuilt requirement is re-added in this same delta under
ADDED Requirements with the phanmemvip entry replacing the giaoduc entry.
Consumers resolving credentials SHALL use `HERMES_CUSTOM_PHANMEMVIP_API_KEY`
bound to provider `phanmemvip` in place of the removed giaoduc binding.

## ADDED Requirements

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

## MODIFIED Requirements

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
