## Context

See `proposal.md` for motivation and scope. The implementation starts from these verified constraints:

- `tdt-core` owns dynamic TDT-root helpers, dotenv profile loading, global typed settings, and a cached global-plus-agent mapping loader. The canonical `resolve_agent_profile()` and `load_agent_config()` are committed to `main` (`d90283f`).
- `agent-core` routes per-agent model config through `build_agent()` → `load_agent_config()`. Model construction consumes already-resolved values (`e5fb49d`).
- `agent-docs-sync` uses `load_agent_config("agent-docs-sync")` for merged model/fallback/providers. Settings and generation derive from the same profile (`e0ba600`).
- `agent-harness` implements two-plane config: `load_agent_config("agent-harness")` for LLM, domain overlay for harness-specific fields. `HarnessConfig` composes the resolved profile (`0ad49d2`).
- `ai-harness-skills` and `ai-review` invoke provider CLIs rather than Pydantic-AI. The `project_cli_profile()` API exists in `tdt-core` (`agent_profile.py:912`) but no consumer repo imports it.
- The current `environment-key-registry.json` contains 17 entries (3 credential, 7 shared model, 7 consumer). Three custom provider credentials (`HERMES_CUSTOM_GIAODUC_API_KEY`, `HERMES_CUSTOM_SHOPAPIKEY_API_KEY`, `HERMES_CUSTOM_COCKPIT_API_KEY`) are NOT registered, blocking all downstream consumer test suites.
- Codex (`config.toml`), Grok Build (`config.toml`), Kimi (`config.toml`), and Pi (`mcp.json`) all converge on the same configuration pattern: provider definitions with endpoint + protocol + credential reference, named model aliases with provider + wire model + behavior, and default alias selection. TDT duplicates this information across `config.yaml`, the packaged registry, and per-agent YAML.

## Runtime Transaction Boundary

One profile-resolution call captures all selected file identities, registered environment inputs, explicit overrides, and source provenance into an immutable snapshot. Agent or CLI construction consumes that snapshot without reopening configuration sources. Provider invocation and credential access occur after this transaction and remain provider-specific.

## Native CLI Convergence Model

All four installed provider CLIs converge on the same abstract structure:

```text
provider definition: endpoint + wire protocol + credential reference + capabilities
model profile:       provider reference + wire model ID + alias + context limit + behavior
default:             selected model profile
```

Concrete examples from installed CLIs:

| CLI | Provider section | Model section | Default |
|---|---|---|---|
| Codex (`~/.codex/config.toml`) | `[model_providers.X]` — `base_url`, `wire_api`, auth | `model = "..."` | top-level `model` |
| Grok Build (`~/.grok/config.toml`) | `[model_providers.X]` — `base_url`, `api_backend`, `context_window` | `[model.X]` — `model`, `model_provider`, `reasoning_effort` | `[models].default` |
| Kimi (`~/.kimi/config.toml`) | `[providers.X]` — `type`, `base_url`, `api_key` | `[models.X]` — `provider`, `model`, `max_context_size` | `default_model` |
| Pi (`~/.pi/agent/mcp.json`) | Transport/MCP delegation | Inherited from parent runtime | N/A |

**Key distinction:** Credentials are never in the config file for Codex (`auth.json`) or Grok (`auth.json`). Kimi is the exception — it stores API keys inline in `config.toml`. TDT follows the Codex/Grok pattern: credentials in `.env`, never in YAML.

## Current State vs Target Architecture

### Current state

```yaml
# ~/.tdt/config.yaml
model:
  primary: openai-chat:fable-5
  fallback: [anthropic:Advance]
providers:
  giaoduc:
    base_url: https://api.giaoduc.online
    api_key_env: HERMES_CUSTOM_GIAODUC_API_KEY    # ← unregistered in registry
  shopapikey:
    *** https://api.phanmemvip.shop/v1
    api_key_env: HERMES_CUSTOM_SHOPAPIKEY_API_KEY  # ← unregistered in registry
  cockpit:
    base_url: http://localhost:51006/v1
    api_key_env: HERMES_CUSTOM_COCKPIT_API_KEY     # ← unregistered in registry
```

Plus a separate `environment-key-registry.json` with 17 entries. The registry is the validation gate, but it is out of sync with the YAML.

### Target architecture (aligned with native CLIs)

```yaml
defaults:
  model: shopapikey-fable-5
  reasoning_effort: xhigh

providers:
  shopapikey:
    *** https://api.phanmemvip.shop/v1
    protocol: messages
    auth_env: HERMES_CUSTOM_SHOPAPIKEY_API_KEY

  giaoduc:
    base_url: https://api.giaoduc.online/v1
    protocol: messages
    auth_env: HERMES_CUSTOM_GIAODUC_API_KEY

  cockpit:
    base_url: http://localhost:51006/v1
    protocol: responses
    auth_env: HERMES_CUSTOM_COCKPIT_API_KEY

models:
  shopapikey-fable-5:
    provider: shopapikey
    model: fable-5

  giaoduc-advance:
    provider: giaoduc
    model: Advance

  cockpit-terra:
    provider: cockpit
    model: gpt-5.6-terra

  cockpit-luna:
    provider: cockpit
    model: fable-5.6-luna
    reasoning_effort: max
```

### Migration path

1. **Current state** (`providers.*.api_key_env` + packaged registry): registry is the validation gate, three custom keys unregistered.
2. **Interim unblocker**: register the three custom credentials in the registry. This is a tdt-core source change, separate from this OpenSpec change.
3. **Transitional state**: add `auth_env` support to YAML and validate against environment-name grammar. Provider binding comes from YAML; registry becomes a compatibility/validation shim.
4. **Target state**: provider binding is entirely YAML-driven; registry is reduced to generic schema validation or removed. Credentials remain in `.env` and never in serializable profiles.

**Do not state that step 3 or 4 is complete.**

## Goals / Non-Goals

**Goals:**

- Produce one internally consistent, redacted effective LLM profile for every participating consumer.
- Make precedence, provenance, failure behavior, and cache invalidation directly testable.
- Reuse tdt-core's existing root, environment, secret classification, and containment patterns.
- Preserve consumer domain ownership and provider CLI authentication isolation.
- Converge TDT provider/model configuration toward the proven native CLI pattern.
- Stage migration so the four direct Python participants stabilize before CLI-provider consumers.

**Non-Goals:**

- Replace every field in `agent_core.foundation.Settings` with `TDTSettings`.
- Normalize all provider model names to one ecosystem-wide model version.
- Change provider credentials, copy them, or expose them in a resolved profile.
- Refresh dirty Graphify or GitNexus indexes.
- Remove or archive concurrent untracked OpenSpec drafts.
- Modify Claude Code's `~/.claude/settings.json` — that is governed by `claude-code-provider-profile-resolution`.

## Decisions

### 1. Create a fresh corrective v2 change

The active `llm-config-standardization` directory reuses the name of an archived change, omits capability deltas, and marks work complete that runtime probes contradict. The v2 change is the only future execution owner.

### 2. Introduce an immutable resolved profile while retaining a narrow mapping projection

`tdt-core` defines typed, frozen values for primary/fallbacks, model behavior, non-secret provider routes, runtime settings, registered environment-key metadata, credential availability, per-field source provenance, and source fingerprints. `load_agent_config()` remains as a compatibility mapping API using the same secure inputs.

### 3. Resolve precedence once, before model construction

The resolver applies: explicit run-scoped override → consumer-specific registered process environment → shared registered model environment → agent overlay → global YAML → typed defaults. Invalid high-priority values fail closed.

### 4. Separate secure source loading, overlay policy, and effective resolution

Three layers: secure single-mapping reader, source-preserving agent-overlay reader with allowed-key policy, typed effective-profile resolver. Harness domain keys are accepted only by the harness overlay policy.

### 5. Keep effective resolution fresh and cache only safely keyed inputs

The effective profile is rebuilt on each call. File parsing is cached only when the key includes effective root, environment profile, explicit paths, allowed-key policy, and source fingerprints.

### 6. Converge provider/model configuration toward native CLI pattern

TDT Python consumers should configure providers and models the same way Codex, Grok, and Kimi do: YAML `providers.*` for endpoint/protocol/credential-reference, YAML `models.*` for named aliases, YAML `defaults.model` for selection. The packaged `environment-key-registry.json` is a temporary validation mechanism during migration and must not become a second source of provider definitions.

### 7. Make tdt-core the only Python dotenv authority

`tdt_core.env.load_tdt_env` is the single public dotenv authority. Development may apply governed repo-local override; production does not.

### 8. Use one profile through agent-core, docs-sync, and harness

Agent-core CLI, SDK, and base-agent paths consume the same resolved profile. Docs-sync stores the resolved profile in `DocsSyncConfig`. Harness composes the resolved profile with source-preserved domain sections.

### 9. Add a provider-neutral projection for CLI invokers

`ai-harness-skills` and `ai-review` are planned to consume a projection containing executable identity, model alias, effort, bounded limits, key-name metadata, and provenance. This is not yet implemented. The `project_cli_profile()` API exists in tdt-core but no consumer imports it. The CLI adapter spec should require a projection into each native CLI's format.

### 10. Preserve explicit runtime boundaries

`prime-agent` remains TypeScript. `claude-code-provider-adapter` remains provider infrastructure. `code-daily-scan` remains non-LLM. Claude Code's `~/.claude/settings.json` is a separate native runtime configuration surface.

### 11. Reconcile the main contracts before implementation

The v2 delta is explicit about main-spec conflicts. The resolved-profile contract is normative until the delta is synchronized by the sole OpenSpec store writer.

### 12. Acceptance and lifecycle evidence is part of the contract

Before sync or archive, the sole writer must capture exact integrated SHAs, credential-safe fingerprint, and no unowned collisions. The evidence manifest must cover live streaming and non-streaming paths, direct-provider versus adapter scope, and stale task/doc-count reconciliation.

## Risks / Trade-offs

- **[Risk] Registry-to-YAML migration introduces regressions** → Stage in phases: interim unblocker first, then auth_env support, then registry retirement. Each phase has its own tests.
- **[Risk] Removing the registry too early leaves no validation** → Keep the registry as a compatibility shim until YAML-driven validation is proven.
- **[Risk] Native CLI format differences prevent perfect convergence** → Standardize the conceptual contract, not the file format. Each adapter projects into its target format.
- **[Risk] Credential registry gap blocks downstream validation** → Register keys as separate focused change, then rerun suites.
- **[Risk] CLI adapter integration not started** → Stage after Python participants stabilize.
- **[Risk] Cache optimization reintroduces stale configuration** → Key by root, path, policy, fingerprint; test invalidation.
- **[Risk] Provenance leaks sensitive data** → Store source class, logical key, file identity only; redaction tests.
- **[Trade-off] Two global settings models remain** → They coexist for non-LLM domains; all LLM projections derive from one resolved profile.
- **[Trade-off] JSON registry persists during migration** → Temporary overhead; will be reduced or removed once YAML validation is proven.

## Migration Plan

1. Register three custom provider credentials in the environment-key registry with `secret: true`, one provider binding each, and focused tests. **Interim unblocker — separate tdt-core change.**
2. Convert every agent-core model-construction entry point to the resolved profile. **Done on main.**
3. Convert docs-sync and harness. **Done on main.**
4. Define provider/model/default YAML schema in `tdt-core` aligned with native CLI pattern. **Not started.**
5. Add `auth_env` support to provider configuration. **Not started.**
6. Validate provider/model alias referential integrity. **Not started.**
7. Decide registry retirement versus generic schema-only role. **Not started.**
8. Convert ai-harness-skills and ai-review to the provider-neutral projection. **Not started.**
9. Run full per-repository tests, Ruff, strict mypy, cross-repo contract tests, redacted/source audits, and prerequisite-aware live LLM acceptance.
10. Reconcile and validate OpenSpec main-spec deltas.
11. Integrate in dependency order and rerun the complete matrix.

Rollback is commit-based per repository. Live credentials and `$TDT_HOME` files are not migrated automatically.
