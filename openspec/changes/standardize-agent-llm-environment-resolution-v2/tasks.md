# Tasks: standardize-agent-llm-environment-resolution-v2

## Phase 0: Specification and audit (complete)

- [x] 0.1 Audit existing `load_agent_config()` and `load_settings()` across all consumer repos.
- [x] 0.2 Map all six-layer precedence sources (explicit → consumer env → shared env → agent YAML → global YAML → defaults) against actual code paths.
- [x] 0.3 Identify the canonical resolution boundary: `resolve_agent_profile()` in `tdt-core`.

## Phase 1: Core primitives in tdt-core (verified on main)

- [x] 1.1 `EnvironmentKeyRegistry` with sealed validation, consumer/shared separation, and credential entry lookup.
  - Evidence: 17 entries registered (3 credential, 7 shared model, 7 consumer), `from_resource()` sealed on construction. Focused tests: **60 passed** in `test_config_primitives.py` + `test_llm_profile_v2.py`.
- [x] 1.2 `resolve_agent_profile()` implementing six-layer precedence with `Provenance` metadata per logical field.
  - Evidence: Returns frozen `ResolvedAgentProfile` with model, fallbacks, model_settings, runtime, providers, credentials, provenance, source_fingerprints. Source: `agent_profile.py:613`.
- [x] 1.3 `load_config_mapping()` as the secure, non-merging YAML reader with path containment and secret policy.
  - Evidence: Returns `ConfigMapping` with data, path, fingerprint, source_class. Source: `config_loader.py:433`.
- [x] 1.4 `load_agent_overlay()` with source-preserving agent overlay under explicit key policy.
  - Evidence: Default allowed keys are `{"model", "runtime"}`; unknown keys rejected. Source: `config_loader.py:497`.
- [x] 1.5 `load_agent_config()` as the compatibility mapping projection over v2 primitives.
  - Evidence: Delegates to `resolve_agent_profile()` internally; returns merged dict. Source: `config_loader.py:541`.
- [x] 1.6 `load_tdt_env()` with descriptor-pinned dotenv loading, fingerprint tracking, and environment isolation.
  - Evidence: Public API at `env.py:391`. Supports `env_file` override, root pinning, idempotent initialization.
- [x] 1.7 Path helpers (`tdt_root`, `tdt_config_path`, `tdt_config_path_for_agent`) with safe component validation.
  - Evidence: Public API at `paths.py:74-132`.

## Phase 2: Consumer wiring on main (verified)

- [x] 2.1 `agent-core` `build_agent()` routes per-agent model config through `tdt_core.config_loader.load_agent_config()`.
  - Evidence: `agent-core/src/agent_core/sdk/agents.py:80` calls `load_agent_config(agent_name)`. Commit: `e5fb49d`.
- [x] 2.2 `agent-harness` implements two-plane config loading: `load_agent_config()` for LLM, domain overlay for harness-specific fields.
  - Evidence: `agent-harness/src/agent_harness/config.py:123` `HarnessConfig` composes resolved profile. Commit: `6a89de6`.
- [x] 2.3 `agent-docs-sync` config alignment: `load_agent_config("agent-docs-sync")` provides merged model/fallback/providers.
  - Evidence: `agent-docs-sync/src/agent_docs_sync/config.py:62-65`. Commit: `267c3aa`.

## Phase 3: Implementation on main (verified)

- [x] 3.1 All v2 primitives committed to `tdt-core/main` (commits `e395611`, `8496f8e`, `d90283f`).
- [x] 3.2 `agent-core/main` routes per-agent config through SDK (commit `e5fb49d`).
- [x] 3.3 `agent-harness/main` two-plane config committed (commit `6a89de6`).
- [x] 3.4 `agent-docs-sync/main` config alignment committed (commit `267c3aa`).

## Phase 4: Downstream verification (BLOCKED)

### BLOCKER: Custom provider credential registry gap

**Status: BLOCKED** — Three custom provider credential environment variable names are configured in the production `~/.tdt/config.yaml` but are **not registered** in the canonical `environment-key-registry.json` in tdt-core.

#### Affected keys

| Config path | `api_key_env` value | Registry status |
|---|---|---|
| `providers.giaoduc.api_key_env` | `HERMES_CUSTOM_GIAODUC_API_KEY` | NOT REGISTERED |
| `providers.shopapikey.api_key_env` | `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` | NOT REGISTERED |
| `providers.cockpit.api_key_env` | `HERMES_CUSTOM_COCKPIT_API_KEY` | NOT REGISTERED |

#### Registered credential keys (3 total)

| `logical_key` | `canonical_key` | `provider` |
|---|---|---|
| `credential.anthropic.api_key` | `ANTHROPIC_API_KEY` | `anthropic` |
| `credential.openai.api_key` | `OPENAI_API_KEY` | `openai-chat` |
| `credential.model.api_key` | `MODEL_API_KEY` | (none) |

#### Failure signature

```
tdt_core.agent_profile.ProfileResolutionError:
  credential key is not registered: HERMES_CUSTOM_GIAODUC_API_KEY
```

This is raised by `credential_entry()` at `agent_profile.py:395-402` when `resolve_agent_profile()` iterates the `providers` mapping from the global YAML and finds an `api_key_env` that does not match any registered secret entry.

#### Impact (authoritative JUnit XML counts, exit code 1)

Test counts were captured via `pytest --junitxml` to avoid pipe-masking; explicit exit code `1` confirmed for each downstream repo. The failing path in every case is `resolve_agent_profile()` → `credential_entry()` → `HERMES_CUSTOM_GIAODUC_API_KEY` not registered.

| Repo | SHA | Failed | Passed | Total | Root cause |
|---|---|---|---|---|---|
| `tdt-core` (focused config tests) | `d90283f` | 0 | 60 | 60 | N/A |
| `agent-core` | `e5fb49d` | 27 | 719 | 746 | registry gap |
| `agent-harness` | `0ad49d2` | 8 | 335 | 343 | registry gap |
| `agent-docs-sync` | `e0ba600` | 8 | 237 | 245 | registry gap |

**Caveat:** All observed downstream failures enter the unresolved custom-provider credential path; independent post-fix failures remain unverified. The registry fix may surface additional issues.

**Common root cause:** `HERMES_CUSTOM_GIAODUC_API_KEY` is not in the registry. All consumer tests that call `load_agent_config()` hit this failure when the ambient `~/.tdt/config.yaml` is loaded.

- [ ] 4.1 **PREREQUISITE: Register custom provider credentials in the tdt-core environment-key registry.**
  - Add entries for `HERMES_CUSTOM_GIAODUC_API_KEY`, `HERMES_CUSTOM_SHOPAPIKEY_API_KEY`, `HERMES_CUSTOM_COCKPIT_API_KEY`.
  - Associate each key with exactly one provider (`giaoduc`, `shopapikey`, `cockpit`).
  - Preserve `secret: true` and provider binding.
  - Add registry tests: accepted custom key, wrong provider rejected, unregistered key rejected.
  - Run GitNexus impact analysis first (cross-repository blast radius).
  - **This is a tdt-core source change. Must be a separate change/PR — do not modify tdt-core from this OpenSpec worktree.**
- [ ] 4.2 Re-run `agent-core` full test suite after registry fix.
- [ ] 4.3 Re-run `agent-harness` full test suite after registry fix.
- [ ] 4.4 Re-run `agent-docs-sync` full test suite after registry fix.
- [ ] 4.5 Verify `agent-core` model propagation tests pass (no additional compatibility issue after credential fix).

## Phase 5: Spec reconciliation (complete)

- [x] 5.1 `agent-config-resolution` spec describes canonical six-layer precedence — matches `resolve_agent_profile()` implementation.
- [x] 5.2 `agent-core-model-resolution` spec describes config-driven fallback chain — matches `build_agent()` path.
- [x] 5.3 `agent-harness-runner` spec describes two-plane config — matches `HarnessConfig` implementation.
- [x] 5.4 `consumer-config-composition` spec describes Settings projection — matches `ProfileSettingsProjection`.
- [x] 5.5 `consumer-pattern` spec describes harness composition — matches `HarnessConfig` model.
- [x] 5.6 `ecosystem-config-loading` spec describes typed settings + agent profile sharing — matches `load_agent_config()` compatibility.
- [x] 5.7 `tdt-env-loader-tdt-home` spec describes canonical dotenv authority — matches `load_tdt_env()`.
- [x] 5.8 `cli-provider-profile-resolution` spec describes CLI adapter profiles — matches `project_cli_profile()`.
- [x] 5.9 `agent-docs-sync` spec describes docs-sync config alignment — matches `agent-docs-sync` config.py.

## Phase 6: Validation

- [x] 6.1 tdt-core focused config/profile tests: **60 passed** (`d90283f`).
- [x] 6.2 OpenSpec store validation: **358 passed, 0 failed** (post-rebase, current).
- [x] 6.3 Change-specific validation: **valid** (post-rebase, current).
- [x] 6.4 `git diff --check`: **clean**.
- [ ] 6.5 Downstream full-suite validation (blocked by 4.1).

## Phase 7: Documentation and delivery

- [x] 7.1 Proposal, design, tasks, EVIDENCE_MANIFEST rewritten to match actual code state.
- [x] 7.2 All 9 delta specs repaired: omitted scenarios restored, registry scenarios added.
- [x] 7.3 Rebased onto current OpenSpec main (`6462aec`).
- [x] 7.4 Committed as documentation-only change.
- [ ] 7.5 CLI-provider integrations for `ai-harness-skills` and `ai-review` — `project_cli_profile()` exists in tdt-core but no consumer imports it. Pending separate change.
- [ ] 7.6 Isolated TDT_HOME fixture validation — deferred to after registry fix.
- [ ] 7.7 Archive — **NOT YET**. Blocked by 4.1, 7.5, 7.6.
