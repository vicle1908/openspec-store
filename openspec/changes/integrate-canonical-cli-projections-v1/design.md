# Design: integrate-canonical-cli-projections-v1

## Problem

The current TDT provider-model YAML schema resolves one canonical model for
`model.primary`. When multiple native CLI providers (Claude, Codex, Kimi, Pi)
are enabled simultaneously, consumers need per-provider selection — which alias,
which effort, which limits — from that single canonical profile.

The canonical selection/project APIs eliminate these guesses by resolving each CLI identity from the typed profile and passing validated provider-neutral fields to consumers.

1. The old local settings mapping was only enriched when new-schema wins, and only for
   `thinking`/`temperature`/`max_tokens` — not alias or effort.
2. One default model cannot describe multiple simultaneously enabled providers.
3. A provider-neutral projection must prevent a Codex-selected canonical model from
   leaking into a Claude request when both share one TDT_HOME.

## Architecture

### Core principle: one canonical profile, per-provider projection

The canonical YAML profile is the single source of truth. Each enabled native
CLI provider gets an independent selection from that profile. The selection
process is:

1. Resolve canonical profile (existing `resolve_agent_profile()`)
2. For each enabled CLI provider, call the new public selector
3. The selector returns a `CanonicalCLISelection` — provider-neutral,
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
| `model_alias` | `canonical_alias` / `wire_model` from `CanonicalCLISelection` | consumer config only if canonical absent AND spec permits | reject conflicts |
| `wire_model` | `wire_model` from canonical profile | none | canonical source of truth |
| `protocol` | `providers[name].protocol` in YAML | none | reject unsupported protocol |
| `effort` | `reasoning_effort` from `CanonicalCLISelection` | consumer config only if permitted | reject unsupported effort |
| `limits` | capability registry and consumer bounded defaults | bounded local defaults | reject out-of-range |
| `credential_key_names` | `auth_env` from selection, materialized by `CLIProviderProfile` | none | values never projected |
| `provenance` | resolved profile provenance | none | canonical source of truth |
| `native_auth_status` | `credential_available` from selection | "na" | report unavailable |

## Provider selection algorithm

```
select_canonical_cli_provider(profile, *, cli_provider) -> CanonicalCLISelection | None

1. Filter resolved candidates by exact `cli_provider` identity.
2. Return `None` when no candidate maps to the requested CLI.
3. Apply explicit `defaults.cli_models[cli_provider]` alias when present.
4. Without an override, require exactly one candidate; raise on ambiguity.
5. Determine credential availability from the resolved credential snapshot.
6. Return a frozen `CanonicalCLISelection` with no credential values.
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

Consumer calls `select_canonical_cli_provider(profile, cli_provider="codex")` →
returns selection with `wire_model="gpt-5.6-sol"`, `canonical_alias="codex-default"`,
`protocol="responses"`.

Consumer calls `select_canonical_cli_provider(profile, cli_provider="claude")` →
returns an independent Claude selection when the YAML catalog maps one.

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

`CanonicalCLISelection` contains the credential environment-variable name via
`auth_env`; `CLIProviderProfile.credential_key_names` carries names only.
Environment-variable values are never projected.

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

1. Public canonical CLI selection/projection API in tdt-core (`75cd519`)
2. Bridge and runtime integration in ai-harness-skills (`02d0410`)
3. Reviewer launch integration in ai-review (`bd27767`)
4. Downstream verification and live dual-consumer acceptance
5. OpenSpec archive and canonical-spec synchronization

The registry is NOT retired — it keeps providing CLI capability metadata
(`cli_capability()`) and legacy environment-key lookup. New-schema `auth_env`
remains direct and does not require per-provider registry entries.
