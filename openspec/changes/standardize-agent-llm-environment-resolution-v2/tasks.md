# Tasks: standardize-agent-llm-environment-resolution-v2

## Phase 1: Native CLI research and conceptual mapping (complete)

- [x] 1.1 Research Codex, Grok Build, Kimi, and Pi configuration patterns.
  - Codex: `config.toml` — `[model_providers.X]` + `model` + `auth.json`.
  - Grok: `config.toml` — `[model_providers.X]` + `[model.X]` + `[models].default` + `auth.json`.
  - Kimi: `config.toml` — `[providers.X]` + `[models.X]` + `default_model` (credentials inline).
  - Pi: `mcp.json` — transport delegation, no standalone provider config.
- [x] 1.2 Identify universal pattern: provider definition → model alias → default selection.
- [x] 1.3 Document native CLI versions and config structure as research evidence.

## Phase 2: Current resolver implementation baseline (complete)

- [x] 2.1 `resolve_agent_profile()` implementing six-layer precedence with `Provenance` metadata.
  - Source: `tdt-core` `agent_profile.py:613`. Commit: `d90283f`.
- [x] 2.2 `load_agent_config()` compatibility mapping projection.
  - Source: `config_loader.py:541`. Commit: `d90283f`.
- [x] 2.3 `load_config_mapping()` and `load_agent_overlay()` secure source readers.
  - Source: `config_loader.py:433` and `config_loader.py:497`.
- [x] 2.4 `load_tdt_env()` canonical dotenv authority.
  - Source: `env.py:391`.
- [x] 2.5 `EnvironmentKeyRegistry` with sealed validation and credential entry lookup.
  - Source: `agent_profile.py:299`. 17 entries (3 credential, 7 shared model, 7 consumer).
- [x] 2.6 `project_cli_profile()` CLI adapter projection.
  - Source: `agent_profile.py:912`. Exists but no consumer imports it.
- [x] 2.7 Consumer wiring: `agent-core` (`e5fb49d`), `agent-harness` (`0ad49d2`), `agent-docs-sync` (`e0ba600`).
- [x] 2.8 Focused tdt-core tests: **60 passed** (`d90283f`).

## Phase 3: Interim registry credential fix (BLOCKED — separate tdt-core change)

### BLOCKER: Custom provider credential registry gap

Three custom provider credential environment variable names are configured in the production `~/.tdt/config.yaml` but are NOT registered in the canonical `environment-key-registry.json` in tdt-core.

#### Affected keys

| Config path | `api_key_env` value | Registry status |
|---|---|---|
| `providers.giaoduc.api_key_env` | `HERMES_CUSTOM_GIAODUC_API_KEY` | NOT REGISTERED |
| `providers.shopapikey.api_key_env` | `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` | NOT REGISTERED |
| `providers.cockpit.api_key_env` | `HERMES_CUSTOM_COCKPIT_API_KEY` | NOT REGISTERED |

#### Downstream impact (authoritative JUnit XML counts)

| Repo | SHA | Failed | Passed | Total |
|---|---|---|---|---|
| `tdt-core` (focused) | `d90283f` | 0 | 60 | 60 |
| `agent-core` | `e5fb49d` | 27 | 719 | 746 |
| `agent-harness` | `0ad49d2` | 8 | 335 | 343 |
| `agent-docs-sync` | `e0ba600` | 8 | 237 | 245 |

**Caveat:** All observed downstream failures enter the unresolved custom-provider credential path; independent post-fix failures remain unverified.

- [ ] 3.1 Register three custom credentials in `environment-key-registry.json` with `secret: true`, one provider binding each, and focused tests.
- [ ] 3.2 Re-run all four consumer suites after registry fix.

## Phase 4: New YAML provider/model/default schema (NOT STARTED)

Define a native-CLI-aligned YAML schema in `tdt-core`:

```yaml
defaults:
  model: shopapikey-fable-5
  reasoning_effort: xhigh

providers:
  shopapikey:
    *** https://api.phanmemvip.shop/v1
    protocol: messages
    auth_env: HERMES_CUSTOM_SHOPAPIKEY_API_KEY

models:
  shopapikey-fable-5:
    provider: shopapikey
    model: fable-5
```

- [ ] 4.1 Define `ProviderConfig` and `ModelProfile` typed models in tdt-core.
- [ ] 4.2 Add YAML schema validation: provider exists, model references valid provider, default alias exists.
- [ ] 4.3 Add `auth_env` support: validates env-name grammar, checks availability, never stores values.
- [ ] 4.4 Add protocol enum: `messages`, `responses`, `openai_chat`, `openai_responses` (no silent inference).
- [ ] 4.5 Add alias semantics: distinguish user-facing alias from wire model ID in provenance.
- [ ] 4.6 Define migration compatibility: old `model.primary`/`model.fallback` and `api_key_env` remain supported temporarily; conflict behavior when old and new schemas coexist.
- [ ] 4.7 Add focused tests for schema validation, referential integrity, and migration compatibility.

## Phase 5: Registry retirement decision (NOT STARTED)

- [ ] 5.1 Decide whether registry becomes generic schema-only validation or is removed entirely.
- [ ] 5.2 If retained: reduce to type/grammar validation only, remove provider-binding authority.
- [ ] 5.3 If removed: ensure all validation is covered by YAML schema.

## Phase 6: CLI projections and consumer wiring (NOT STARTED)

- [ ] 6.1 Add `project_cli_profile()` requirement that each adapter projects into its native CLI format.
- [ ] 6.2 Add scenario that no consumer appears implemented until it actually imports the API.
- [ ] 6.3 Define `ai-harness-skills` and `ai-review` integration requirements.

## Phase 7: Isolated TDT_HOME tests (NOT STARTED)

- [ ] 7.1 Create isolated TDT_HOME fixture with registered credentials, valid config, and empty .env.
- [ ] 7.2 Prove six-layer precedence: explicit > consumer env > shared env > agent YAML > global YAML > defaults.
- [ ] 7.3 Prove credential availability recording without secret values.
- [ ] 7.4 Prove provenance for each resolved field.
- [ ] 7.5 Prove cache isolation for root, environment profile, explicit paths, policy changes.

## Phase 8: Spec reconciliation (complete for existing specs)

- [x] 8.1 `agent-config-resolution` — six-layer precedence, single config function, secure overlay API.
- [x] 8.2 `agent-core-model-resolution` — config-driven fallback, model layer is config-input only.
- [x] 8.3 `agent-harness-runner` — two-plane config, domain provenance, artifact containment.
- [x] 8.4 `consumer-config-composition` — Settings projection, env/YAML loading, shortcuts.
- [x] 8.5 `consumer-pattern` — harness composition, public SDK usage.
- [x] 8.6 `ecosystem-config-loading` — typed settings + agent profile sharing.
- [x] 8.7 `tdt-env-loader-tdt-home` — canonical dotenv authority, idempotency, path containment, registry.
- [x] 8.8 `cli-provider-profile-resolution` — CLI adapter profiles, authentication isolation.
- [x] 8.9 `agent-docs-sync` — docs-sync config alignment.
- [ ] 8.10 `provider-model-profile-resolution` — new spec for YAML schema migration (Phase 4).

## Phase 9: Full downstream validation (BLOCKED by Phase 3)

- [ ] 9.1 After registry fix: re-run all consumer suites in isolated TDT_HOME.
- [ ] 9.2 After schema migration: re-run all consumer suites with new YAML schema.
- [ ] 9.3 Live LLM acceptance with registered canonical `provider:model` identifiers.
- [ ] 9.4 Redacted diagnostics and provenance verification.

## Phase 10: Validation and delivery

- [x] 10.1 OpenSpec change validation: valid.
- [x] 10.2 Full store validation: 358/358.
- [x] 10.3 `git diff --check`: clean.
- [ ] 10.4 Archive — NOT YET. Blocked by Phase 3, 4, 5, 6, 7, 9.
