# Design: integrate-canonical-cli-projections-v1

## Problem

The current TDT provider-model YAML schema resolves one canonical model for
`model.primary`. When multiple native CLI providers (Claude, Codex, Kimi, Pi)
are enabled simultaneously, consumers need per-provider selection — which alias,
which effort, which limits — from that single canonical profile.

The existing bridge in `ai-harness-skills` guesses field sources
(`model_settings.get("alias")`, `model_settings["defaults"]["effort"]`) that
are not established public contracts. These guesses fail because:

1. `model_settings` is only enriched when new-schema wins, and only for
   `thinking`/`temperature`/`max_tokens` — not alias or effort.
2. One default model cannot describe multiple simultaneously enabled providers.
3. The bridge projects a Codex-selected canonical model into a Claude request
   when both share one TDT_HOME.

## Architecture

### Core principle: one canonical profile, per-provider projection

The canonical YAML profile is the single source of truth. Each enabled native
CLI provider gets an independent selection from that profile. The selection
process is:

1. Resolve canonical profile (existing `resolve_agent_profile()`)
2. For each enabled CLI provider, call the new public selector
3. The selector returns a `CanonicalProviderSelection` — provider-neutral,
   immutable, secret-free
4. Each consumer projects the selection into its native format

### Why not let each consumer resolve independently?

- Consumers lack the six-layer precedence engine
- Consumers should not duplicate resolution logic
- Canonical values must override stale native config uniformly

## Field-source matrix (normative)

| Projected field | Canonical source | Fallback | Failure behavior |
|---|---|---|---|
| `executable` | CLI capability registry (`cli_capability()`) | none | reject unsupported executable |
| `model_alias` | `selected_alias` from `CanonicalProviderSelection` | consumer config only if canonical absent AND spec permits | reject conflicts |
| `wire_model` | `direct_model_id` from canonical profile | none | canonical source of truth |
| `protocol` | `providers[name].protocol` in YAML | none | reject unsupported protocol |
| `effort` | `effort` from `CanonicalProviderSelection` | consumer config only if permitted | reject unsupported effort |
| `limits` | `limits` from `CanonicalProviderSelection` | bounded local defaults | reject out-of-range |
| `credential_key_names` | `credentials` tuple key names | none | values never projected |
| `provenance` | `provenance` from canonical profile | none | canonical source of truth |
| `native_auth_status` | caller detects via `credential_available()` | "na" | report unavailable |

## Provider selection algorithm

```
select_canonical_provider(profile, *, provider) -> CanonicalProviderSelection | None

1. If provider not in profile.providers: raise ValueError
2. If provider not registered in cli_capability(): raise ValueError
3. Find the model alias where models[alias].provider == provider
4. If no alias matches: raise ProfileResolutionError
5. Return CanonicalProviderSelection with all canonical fields
```

### Multi-provider scenario

```yaml
# config.yaml — single canonical profile
defaults:
  model: codex-default
providers:
  tdt-codex:
    base_url: http://localhost:51006/v1
    protocol: responses
    auth_env: OPENAI_API_KEY
  tdt-claude:
    base_url: http://localhost:51006/v1
    protocol: messages
    auth_env: ANTHROPIC_API_KEY
  tdt-kimi:
    base_url: http://localhost:51006/v1
    protocol: responses
    auth_env: KIMI_API_KEY
models:
  codex-default:
    provider: tdt-codex
    model: gpt-5.6-sol
  claude-review:
    provider: tdt-claude
    model: claude-sonnet-4-20250514
  kimi-review:
    provider: tdt-kimi
    model: kimi-local
```

Consumer calls `select_canonical_provider(profile, provider="codex")` →
returns selection with `wire_model="gpt-5.6-sol"`, `model_alias` from
the model definition or registry alias, `protocol="responses"`.

Consumer calls `select_canonical_provider(profile, provider="claude")` →
returns selection with `wire_model="claude-sonnet-4-20250514"`.

Each selection is independent. No cross-contamination.

## Canonical vs local precedence

When a consumer has local config (adapter config, legacy YAML), the canonical
value always wins if present. Local values are fallback only when:

1. Canonical profile has no entry for the requested provider, OR
2. Canonical profile exists but the specific field is absent

If canonical config is present but malformed → reject before launch (fail closed).
If canonical config is absent → consumer may use local config (graceful fallback).

## Unsupported alias/effort/limit behavior

The public selector validates against the CLI capability registry:

- Unknown alias → `ProfileResolutionError`
- Unsupported effort → `ProfileResolutionError` (unless caller passes
  `effort=None` to omit)
- Limit outside bounds → `ProfileResolutionError`

The consumer does NOT validate — the selector does.

## Credential-name projection and secret isolation

`CanonicalProviderSelection` contains `credential_key_names: tuple[str, ...]`
— environment variable names only, never values. The consumer uses these for
diagnostic reporting and credential-boundary checking.

Secret values stay in the environment. The projection object is frozen.

## Legacy compatibility

- `ai-harness-skills` has a standalone `SafeProcessRunner` that manages its
  own environment allowlist. The new projection replaces the adapter's local
  config, not the runner's allowlist.
- `ai-review` launches reviewers as subprocesses. The projection provides
  command-line arguments. The subprocess still authenticates through its
  native boundary.
- Legacy environment-key overrides (e.g., `TDT_AGENT_MODEL_PRIMARY`) continue
  to work through the six-layer precedence in `resolve_agent_profile()`.

## Migration path

1. Public selector API in tdt-core (Phase 3)
2. Bridge correction in ai-harness-skills (Phase 4)
3. Integration in ai-review (Phase 5)
4. Downstream verification (Phase 6)
5. Phase 5 registry decision (Phase 7)

The registry is NOT retired — it keeps providing CLI capability metadata
(`cli_capability()`) and legacy environment-key lookup. New-schema `auth_env`
remains direct and does not require per-provider registry entries.
