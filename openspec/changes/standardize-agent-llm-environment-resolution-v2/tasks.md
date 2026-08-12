# Tasks: standardize-agent-llm-environment-resolution-v2

## Phase 1: Native CLI research and conceptual mapping (complete)

- [x] 1.1 Research Codex, Grok Build, Kimi, and Pi configuration patterns.
- [x] 1.2 Identify universal pattern: provider definition → model alias → default selection.
- [x] 1.3 Document native CLI versions and config structure as research evidence.

## Phase 2: Current resolver implementation baseline (complete)

- [x] 2.1 `resolve_agent_profile()` implementing six-layer precedence with `Provenance` metadata.
- [x] 2.2 `load_agent_config()` compatibility mapping projection.
- [x] 2.3 `load_config_mapping()` and `load_agent_overlay()` secure source readers.
- [x] 2.4 `load_tdt_env()` canonical dotenv authority.
- [x] 2.5 `EnvironmentKeyRegistry` with sealed validation and credential entry lookup.
- [x] 2.6 `project_cli_profile()` CLI adapter projection.
- [x] 2.7 Consumer wiring: `agent-core` (`e5fb49d`), `agent-harness` (`6a89de6`), `agent-docs-sync` (`267c3aa`).
- [x] 2.8 Focused tdt-core tests: **60 passed** (`d90283f`).

## Phase 3: Interim registry credential fix (RESOLVED — `d63aa08`)

### RESOLVED: Custom provider credential registry gap

Three custom provider credential environment variable names were registered in `tdt-core`'s `environment-key-registry.json` via the `register-custom-provider-credentials` change.

#### Integrated entries

| Config path | `api_key_env` value | `logical_key` | `provider` |
|---|---|---|---|
| `providers.giaoduc.api_key_env` | `HERMES_CUSTOM_GIAODUC_API_KEY` | `credential.giaoduc.api_key` | `giaoduc` |
| `providers.shopapikey.api_key_env` | `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` | `credential.shopapikey.api_key` | `shopapikey` |
| `providers.cockpit.api_key_env` | `HERMES_CUSTOM_COCKPIT_API_KEY` | `credential.cockpit.api_key` | `cockpit` |

#### Downstream validation (integrated main, no PYTHONPATH)

| Repo | SHA | Tests | Passed | Failed | Errors | Skipped |
|---|---|---|---|---|---|---|
| `tdt-core` | `d63aa08` | 618 | 612 | 0 | 0 | 6 |
| `agent-core` | `e5fb49d` | 746 | 746 | 0 | 0 | 0 |
| `agent-harness` | `0ad49d2` | 343 | 343 | 0 | 0 | 0 |
| `agent-docs-sync` | `e0ba600` | 245 | 245 | 0 | 0 | 0 |
| **Total** | | **1952** | **1946** | **0** | **0** | **6** |

- [x] 3.1 Register three custom credentials in `environment-key-registry.json` with `secret: true`, one provider binding each, and focused tests.
  - Commit: `d63aa08`. 12 focused tests added. Registry: 17 → 20 entries.
- [x] 3.2 Run all four consumer suites after registry fix.
  - Evidence: 1946 passed, 0 failures across all repos (integrated main, no PYTHONPATH override).

## Phase 4: New YAML provider/model/default schema (COMPLETE — `21dcd5b`)

- [x] 4.1 Define `ProviderConfig` and `ModelProfile` typed models in tdt-core.
  - Commit: `21dcd5b`. ProviderModelConfig, ModelProfile, ModelDefaults, ProviderProtocol enum.
- [x] 4.2 Add YAML schema validation.
  - Commit: `21dcd5b`. Aggregated referential integrity, base_url validation, field validators.
- [x] 4.3 Add `auth_env` support.
  - Commit: `21dcd5b`. auth_env field in ProviderModelConfig, runtime resolution through CredentialResolver.
- [x] 4.4 Add protocol enum.
  - Commit: `21dcd5b`. ProviderProtocol enum: messages, responses, openai_chat.
- [x] 4.5 Add alias semantics.
  - Commit: `21dcd5b`. Alias resolution in resolve_cli_projection(), model_settings enrichment.
- [x] 4.6 Define migration compatibility.
  - Commit: `21dcd5b`. Mixed-schema rejection, legacy-only fallback, _project_new_schema() integration.
- [x] 4.7 Add focused tests.
  - Commit: `21dcd5b`. 46 parser tests + 39 resolver tests = 85 new tests. Total suite: 687/681/0/6.

## Phase 5: Registry retirement decision (DEFERRED to successor change)

- [ ] 5.1 Decide whether registry becomes generic schema-only validation or is removed entirely.
  - Deferred to `integrate-canonical-cli-projections-v1`. Registry retirement affects all consumers.

## Phase 6: CLI projections and consumer wiring (DEFERRED to successor change)

- [ ] 6.1 Add `project_cli_profile()` requirement for each adapter to project into its native format.
  - Bridge foundation committed at `b160709` in `ai-harness-skills-phase6` (9/9 GREEN).
  - NOT wired into `build_runtime()`. NOT evidence of integration.
- [ ] 6.2 Add scenario that no consumer appears implemented until it imports the API.
- [ ] 6.3 Define `ai-harness-skills` and `ai-review` integration requirements.
  - Deferred to `integrate-canonical-cli-projections-v1`.

## Phase 7: Isolated TDT_HOME tests (COMPLETE — `21dcd5b`)

- [x] 7.1 Create isolated TDT_HOME fixture.
  - Used across 19 precedence tests and 39 resolver tests.
- [x] 7.2 Prove six-layer precedence.
  - 19 TestSixLayerPrecedence tests covering explicit, consumer, shared, agent, new-schema, global, defaults.
- [x] 7.3 Prove credential availability recording without secret values.
  - Credential tests verify available/unavailable recording, no secret leakage.
- [x] 7.4 Prove provenance for each resolved field.
  - Provenance tests verify source_class, source_key, shadowed_sources.
- [x] 7.5 Prove cache isolation.
  - reset_profile_state() tested across multiple resolution paths.

## Phase 8: Spec reconciliation (complete for existing specs)

- [x] 8.1 `agent-config-resolution`
- [x] 8.2 `agent-core-model-resolution`
- [x] 8.3 `agent-harness-runner`
- [x] 8.4 `consumer-config-composition`
- [x] 8.5 `consumer-pattern`
- [x] 8.6 `ecosystem-config-loading`
- [x] 8.7 `tdt-env-loader-tdt-home`
- [x] 8.8 `cli-provider-profile-resolution`
- [x] 8.9 `agent-docs-sync`
- [x] 8.10 `provider-model-profile-resolution` — implemented and integrated at `21dcd5b`.

## Phase 9: Full downstream validation (PARTIAL — `21dcd5b`)

- [x] 9.1 After registry fix: all consumer suites pass in integrated main (no PYTHONPATH override).
  - Evidence: 687/681/0/6 (tdt-core), 746/746 (agent-core), 343/343 (agent-harness), 245/245 (agent-docs-sync).
- [ ] 9.2 After schema migration: re-run all consumer suites with new YAML schema.
  - Deferred to `integrate-canonical-cli-projections-v1`.
- [x] 9.3 Live LLM acceptance with registered canonical `provider:model` identifiers.
  - Commit: `4c277c4`. Native Codex invocation, exit 0, nonce `TDT_8ef49e53`, 7.25s.
  - Command: `codex exec --ephemeral --skip-git-repo-check --sandbox read-only -m gpt-5.6-sol ...`
  - Evidence file: `scripts/verify_v2_codex_acceptance.py`.
- [ ] 9.4 Redacted diagnostics and provenance verification.
  - Deferred to `integrate-canonical-cli-projections-v1`.

## Phase 10: Validation and delivery

- [x] 10.1 OpenSpec change validation: valid.
- [x] 10.2 Full store validation: 360/360.
- [x] 10.3 `git diff --check`: clean.
- [ ] 10.4 Archive — **NOT YET**. Phase 5 and Phase 6 deferred to successor change `integrate-canonical-cli-projections-v1`.

---

## Successor Change: integrate-canonical-cli-projections-v1

Phase 6 crosses two independent repositories (`ai-harness-skills`, `ai-review`) and introduces runtime dependency/package changes. It is isolated into a dedicated successor change.

### Scope

- Public canonical projection contract (if needed)
- `ai-harness-skills` dependency and runtime integration
- `ai-review` provider-neutral launch projection
- Claude/Codex/Kimi/Pi capability handling
- Fallback/error semantics
- Clean-install dependency verification
- Downstream matrix
- Real CLI acceptance for each applicable provider

### Foundation (pre-existing)

- `ai-harness-skills-phase6` branch with bridge foundation at `b160709`
  - `tdt_projection.py`: bridge module (9/9 focused GREEN)
  - `tdt-core` editable dependency added
  - NOT wired into `build_runtime()`
  - Bridge field contract needs correction before wiring
