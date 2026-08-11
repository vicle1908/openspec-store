# standardize-agent-llm-environment-resolution-v2

## What this change is

Corrective v2 of the agent LLM environment resolution standardization. Aligns the TDT Python agent ecosystem with the provider/model/default configuration pattern proven by Codex, Grok, Kimi, and Pi.

## Status

**Not archive-ready.** Core resolver implementation is on `main`. Interim credential registry fix is integrated (`d63aa08`). The YAML-based provider/model/default schema migration is proposed but not implemented.

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
| `cli-provider-profile-resolution` | MODIFIED | CLI adapter profiles, native format projection, authentication isolation |
| `agent-docs-sync` | MODIFIED | Docs-sync config alignment |
| `provider-model-profile-resolution` | ADDED | YAML schema: providers, models, defaults, auth_env, protocol, referential integrity (PROPOSED, not implemented) |

## Remaining blockers

1. YAML `providers/models/defaults` schema not implemented (Phase 4).
2. CLI consumer integrations not implemented (Phase 6).
3. Isolated `TDT_HOME` fixture validation not completed (Phase 7).
4. Live LLM acceptance not performed (Phase 9).
