# standardize-agent-llm-environment-resolution-v2

## What this change is

Corrective v2 of the agent LLM environment resolution standardization. Aligns the TDT Python agent ecosystem with the provider/model/default configuration pattern proven by Codex, Grok, Kimi, and Pi.

## Status

**Core implementation complete. Phase 6 (CLI consumer wiring) deferred to successor change `integrate-canonical-cli-projections-v1`.**

## What's done

| Artifact | SHA | Tests | Status |
|----------|-----|-------|--------|
| YAML provider/model/default schema parser | `21dcd5b` | 46 parser tests | ✅ |
| Resolver integration (`_NewSchemaProjection` → `_choose()`) | `21dcd5b` | 39 resolver tests | ✅ |
| Strict Codex acceptance | `4c277c4` | Nonce `TDT_8ef49e53`, exit 0 | ✅ |
| Credential registry fix | `d63aa08` | 12 focused tests | ✅ |
| Full tdt-core suite | `21dcd5b` | 687/681/0/6 | ✅ |
| agent-core downstream | `e5fb49d` | 746/746 | ✅ |
| agent-harness downstream | `0ad49d2` | 343/343 | ✅ |
| agent-docs-sync downstream | `e0ba600` | 245/245 | ✅ |
| Six-layer precedence tests | `21dcd5b` | 19 tests | ✅ |
| Missing-credential proof | `21dcd5b` | Both auth_env + api_key_env | ✅ |

## What's deferred

- **Phase 5** (registry retirement decision) → successor change
- **Phase 6** (CLI projections for ai-harness-skills and ai-review) → successor change
- **Phase 9.2** (re-run consumers with new YAML schema) → successor change
- **Phase 9.4** (redacted diagnostics verification) → successor change

## Interim fix: credential registry (RESOLVED)

Three custom provider credentials were registered in `tdt-core`'s `environment-key-registry.json` via the separate `register-custom-provider-credentials` change. This was an interim compatibility fix; the YAML-based provider/model migration will eventually supersede the registry.

## Specs (10)

| Spec | Status | Description |
|---|---|---|
| `agent-config-resolution` | MODIFIED | Six-layer precedence, single resolution boundary |
| `agent-core-model-resolution` | MODIFIED | Config-driven fallback, model layer is config-input only |
| `agent-harness-runner` | MODIFIED | Two-plane config, domain provenance, artifact containment |
| `consumer-config-composition` | MODIFIED | Settings projection, env/YAML loading, shortcuts |
| `consumer-pattern` | MODIFIED | Harness composition, public SDK usage |
| `ecosystem-config-loading` | MODIFIED | Typed settings + agent profile sharing |
| `tdt-env-loader-tdt-home` | MODIFIED | Canonical dotenv authority, idempotency, path containment, registry |
| `cli-provider-profile-resolution` | ADDED | CLI adapter profiles, native format projection, authentication isolation |
| `agent-docs-sync` | MODIFIED | Docs-sync config alignment |
| `provider-model-profile-resolution` | ADDED | YAML schema: providers, models, defaults, auth_env, protocol, referential integrity |

## Successor change

Phase 6 crosses two independent repositories (`ai-harness-skills`, `ai-review`) and introduces runtime dependency/package changes. It is isolated into a dedicated successor change: `integrate-canonical-cli-projections-v1`.
