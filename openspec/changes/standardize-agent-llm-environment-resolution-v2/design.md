## Context

See `proposal.md` for motivation and scope. The implementation starts from these verified constraints:

- `tdt-core` owns dynamic TDT-root helpers, dotenv profile loading, global typed settings, and a cached global-plus-agent mapping loader. The canonical `resolve_agent_profile()` and `load_agent_config()` are committed to `main`.
- `agent-core` routes per-agent model config through `build_agent()` → `load_agent_config()`. Model construction consumes already-resolved values.
- `agent-docs-sync` uses `load_agent_config("agent-docs-sync")` for merged model/fallback/providers. Settings and generation derive from the same profile.
- `agent-harness` implements two-plane config: `load_agent_config("agent-harness")` for LLM, domain overlay for harness-specific fields. `HarnessConfig` composes the resolved profile.
- `ai-harness-skills` and `ai-review` invoke provider CLIs rather than Pydantic-AI. They need shared non-secret selection metadata without sharing provider credential stores. **Not yet wired** — `project_cli_profile()` exists in tdt-core but no consumer repo imports it.
- The main specs contain contradictory requirements for fallback lookup, repository model overrides, settings composition, and config inheritance.

## Runtime Transaction Boundary

One profile-resolution call captures all selected file identities, registered environment inputs, explicit overrides, and source provenance into an immutable snapshot. Agent or CLI construction consumes that snapshot without reopening configuration sources. Provider invocation and credential access occur after this transaction and remain provider-specific.

## Goals / Non-Goals

**Goals:**

- Produce one internally consistent, redacted effective LLM profile for every participating consumer.
- Make precedence, provenance, failure behavior, and cache invalidation directly testable.
- Reuse tdt-core's existing root, environment, secret classification, and containment patterns.
- Preserve consumer domain ownership and provider CLI authentication isolation.
- Stage migration so the four direct Python participants stabilize before CLI-provider consumers.

**Non-Goals:**

- Replace every field in `agent_core.foundation.Settings` with `TDTSettings`.
- Normalize all provider model names to one ecosystem-wide model version.
- Change provider credentials, copy them, or expose them in a resolved profile.
- Refresh dirty Graphify or GitNexus indexes.
- Remove or archive concurrent untracked OpenSpec drafts.

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

### 6. Publish an environment-key registry

tdt-core packages a machine-readable registry describing each logical field's canonical key, owner, type, precedence class, secret status, supported consumers, and compatibility aliases. **The three custom provider credentials (`HERMES_CUSTOM_GIAODUC_API_KEY`, `HERMES_CUSTOM_SHOPAPIKEY_API_KEY`, `HERMES_CUSTOM_COCKPIT_API_KEY`) are not yet registered. This is the primary implementation prerequisite.**

### 7. Make tdt-core the only Python dotenv authority

`tdt_core.env.load_tdt_env` is the single public dotenv authority. Development may apply governed repo-local override; production does not.

### 8. Use one profile through agent-core, docs-sync, and harness

Agent-core CLI, SDK, and base-agent paths consume the same resolved profile. Docs-sync stores the resolved profile in `DocsSyncConfig`. Harness composes the resolved profile with source-preserved domain sections.

### 9. Add a provider-neutral projection for CLI invokers

`ai-harness-skills` and `ai-review` are planned to consume a projection containing executable identity, model alias, effort, bounded limits, key-name metadata, and provenance. **This is not yet implemented.** The `project_cli_profile()` API exists in tdt-core but no consumer repo imports it.

### 10. Preserve explicit runtime boundaries

`prime-agent` remains TypeScript. `claude-code-provider-adapter` remains provider infrastructure. `code-daily-scan` remains non-LLM.

### 11. Reconcile the main contracts before implementation

The v2 delta is explicit about main-spec conflicts. The resolved-profile contract is normative until the delta is synchronized by the sole OpenSpec store writer.

### 12. Acceptance and lifecycle evidence is part of the contract

Before sync or archive, the sole writer must capture exact integrated SHAs, credential-safe fingerprint, and no unowned collisions. The evidence manifest must cover live streaming and non-streaming paths, direct-provider versus adapter scope, and stale task/doc-count reconciliation.

## Risks / Trade-offs

- **[Risk] Broad six-repository rollout becomes difficult to integrate** → Land in dependency order with one writer per repository.
- **[Risk] Breaking removal of repo-local models changes operator behavior** → Provide migration command/example.
- **[Risk] Credential registry gap blocks downstream validation** → Register keys as separate focused change, then rerun suites.
- **[Risk] CLI adapter integration not started** → Stage after Python participants stabilize.
- **[Risk] Cache optimization reintroduces stale configuration** → Key by root, path, policy, fingerprint; test invalidation.
- **[Risk] Provenance leaks sensitive data** → Store source class, logical key, file identity only; redaction tests.
- **[Trade-off] Two global settings models remain** → They coexist for non-LLM domains; all LLM projections derive from one resolved profile.

## Migration Plan

1. Register three custom provider credentials in the environment-key registry with `secret: true`, one provider binding each, and focused tests.
2. Convert every agent-core model-construction entry point to the resolved profile. **Done on main.**
3. Convert docs-sync and harness. **Done on main.**
4. Convert ai-harness-skills and ai-review to the provider-neutral projection. **Not started.**
5. Run full per-repository tests, Ruff, strict mypy, cross-repo contract tests, redacted/source audits, and prerequisite-aware live LLM acceptance.
6. Reconcile and validate OpenSpec main-spec deltas.
7. Integrate in dependency order and rerun the complete matrix.

Rollback is commit-based per repository. Live credentials and `$TDT_HOME` files are not migrated automatically.
