## Why

`resolve_agent_profile()` calls `registry.credential_entry(key_name, provider_id)` for each `providers.*.api_key_env` value in the global YAML. When the key is not registered in the environment-key registry, the call raises `ProfileResolutionError`, blocking every downstream consumer test suite.

Three custom provider credential keys in production `~/.tdt/config.yaml` are not registered:
- `HERMES_CUSTOM_GIAODUC_API_KEY` (giaoduc)
- `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` (shopapikey)
- `HERMES_CUSTOM_COCKPIT_API_KEY` (cockpit)

## What Changes

1. Add three credential entries to `tdt-core`'s `environment-key-registry.json`.
2. Bind each key to exactly one provider.
3. Preserve `secret: true` classification.
4. Add focused tests: accepted, wrong-provider rejected, unregistered rejected.
5. Do not introduce the new `providers/models/defaults` YAML schema.
6. Do not modify consumer repositories.
7. Do not store credential values.

This is an interim compatibility fix. The YAML-based provider/model migration (defined in the v2 change `provider-model-profile-resolution`) will eventually supersede the registry for credential validation.

## Boundary

This change modifies only `tdt-core` source and test files. Consumer repositories remain untouched. The registry remains the credential validation gate until the YAML schema migration is implemented.
