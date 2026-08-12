# Migration Semantics Decision Ledger

Resolved 2026-08-12 during v2 implementation scoping.

## Schema Modes

### 1. Legacy-only configuration

```yaml
model:
  primary: openai-chat:fable-5
  fallback: [anthropic:Advance]
providers:
  giaoduc:
    base_url: https://api.giaoduc.online
    api_key_env: HERMES_CUSTOM_GIAODUC_API_KEY
```

**Behavior:** Accepted without error. Existing resolution path unchanged. Provenance records `legacy_model_path`. Registry validates credential binding.

### 2. New-only configuration

```yaml
defaults:
  model: shopapikey-fable-5
providers:
  shopapikey:
    base_url: https://api.phanmemvip.shop/v1
    protocol: messages
    auth_env: HERMES_CUSTOM_SHOPAPIKEY_API_KEY
models:
  shopapikey-fable-5:
    provider: shopapikey
    model: fable-5
```

**Behavior:** Accepted. New resolution path. Provenance records `new_schema_path`. Registry NOT used for provider binding.

### 3. Mixed configuration — equivalent values

```yaml
model:
  primary: shopapikey:fable-5        # legacy
defaults:
  model: shopapikey-fable-5           # new
providers:
  shopapikey:
    base_url: https://api.phanmemvip.shop/v1
    protocol: messages
    auth_env: HERMES_CUSTOM_SHOPAPIKEY_API_KEY
```

**Behavior:** REJECTED with explicit conflict error. Spec requires fail-closed: "validation SHALL fail with an explicit conflict error." No implicit "new wins."

### 4. Mixed configuration — partially migrated

Some providers use legacy `api_key_env`, others use new `auth_env`.

**Behavior:** REJECTED. All-or-nothing migration. A single config file cannot have both patterns simultaneously.

## Registry Role During Transition

- **Keep the registry** for legacy compatibility (`environment-key-registry.json` remains).
- New `auth_env` in provider definitions IS the authoritative credential declaration.
- The registry does NOT override YAML-defined provider binding.
- The registry validates env var name syntax and secret classification.
- Registry retirement is a later, explicit migration gate (Phase 5).

## Identifier Behavior

The resolved profile exposes:

| Field | Legacy Path | New Path | Description |
|---|---|---|---|
| `model_alias` | `primary` raw value | `defaults.model` key | User-facing name |
| `provider_name` | parsed from `{provider}:{model}` | `models.*.provider` | Provider identity |
| `wire_model` | parsed from `{provider}:{model}` | `models.*.model` | What provider receives |
| `canonical_id` | `primary` raw | `{provider}:{wire_model}` | Direct identifier |
| `protocol` | inferred from `api_mode` | `providers.*.protocol` | Wire protocol |
| `auth_env_name` | `api_key_env` value | `providers.*.auth_env` | Env var name (not value) |
| `credential_available` | `bool(os.environ.get(...))` | same | Never the value itself |
| `provenance` | records legacy fields | records new fields | Redacted source map |

Consumers MUST NOT confuse a model alias (`shopapikey-fable-5`) with a wire identifier (`fable-5`) or a canonical identifier (`shopapikey:fable-5`).
