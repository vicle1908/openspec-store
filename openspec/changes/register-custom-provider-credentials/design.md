# Design: register-custom-provider-credentials

## Current Behavior

`resolve_agent_profile()` iterates `providers.*` from the global YAML and calls `registry.credential_entry(api_key_env, provider_id)` for each provider that declares an `api_key_env` string. The registry validates that the key is registered, classified as `secret`, and bound to the correct provider.

The credential resolution path in `resolve_agent_profile()` (line 865):

```
global YAML providers.*.api_key_env
  → registry.credential_entry(key_name, provider_id)
    → match by canonical_key or aliases, filter by secret=true
    → reject if provider mismatch
    → return EnvironmentKey with canonical_key, secret, provider
  → CredentialAvailability(key_name=canonical_key, available=bool(os.environ.get(...)), provider=provider_id)
```

`credential_entry()` at `agent_profile.py:395-402` already correctly rejects:
- Unknown credential keys (no match in registry)
- Wrong-provider assignments (key registered for different provider)

## What This Change Does

Add exactly three entries to `environment-key-registry.json`. No schema changes, no code changes, no consumer modifications.

## Entry Shape (matches existing entries)

```json
{
  "logical_key": "credential.giaoduc.api_key",
  "canonical_key": "HERMES_CUSTOM_GIAODUC_API_KEY",
  "owner": "tdt-core",
  "value_type": "string",
  "precedence": "shared",
  "secret": true,
  "provider": "giaoduc",
  "allow_clearing": false
}
```

Three entries with this shape for giaoduc, shopapikey, and cockpit.

## Impact

- Blast radius: cross-repository — agent-core, agent-harness, agent-docs-sync all call the shared loader.
- Risk: LOW — this is additive data, no schema change, no code path change. The resolver already handles these keys correctly; they simply weren't registered.
- Focused tests confirm accepted/wrong-provider/rejected behavior.

## What Is NOT Changed

- No consumer repositories modified.
- No new YAML schema introduced.
- No `providers/models/defaults` migration.
- No credential values stored.
- Existing anthropic/openai/model credential entries unchanged.
