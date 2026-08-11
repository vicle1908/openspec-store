# standardize-agent-llm-environment-resolution-v2

## What this change is

Corrective v2 of the agent LLM environment resolution standardization. Aligns the TDT Python agent ecosystem with the provider/model/default configuration pattern proven by Codex, Grok Build, fable-5, and Pi.

## Status

**Not archive-ready.** Core resolver implementation is on `main`; the YAML-based provider/model/default schema migration is proposed but not implemented.

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
| `provider-model-profile-resolution` | ADDED | YAML schema: providers, models, defaults, auth_env, protocol, referential integrity |

## Current blockers

1. Three custom provider credentials unregistered in `environment-key-registry.json` (Phase 3).
2. New YAML schema not implemented (Phase 4).
3. CLI consumer integrations not implemented (Phase 6).
