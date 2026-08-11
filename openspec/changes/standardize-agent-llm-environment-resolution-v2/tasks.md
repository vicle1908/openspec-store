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

## Phase 4: New YAML provider/model/default schema (NOT STARTED)

- [ ] 4.1 Define `ProviderConfig` and `ModelProfile` typed models in tdt-core.
- [ ] 4.2 Add YAML schema validation.
- [ ] 4.3 Add `auth_env` support.
- [ ] 4.4 Add protocol enum.
- [ ] 4.5 Add alias semantics.
- [ ] 4.6 Define migration compatibility.
- [ ] 4.7 Add focused tests.

## Phase 5: Registry retirement decision (NOT STARTED)

- [ ] 5.1 Decide whether registry becomes generic schema-only validation or is removed entirely.

## Phase 6: CLI projections and consumer wiring (NOT STARTED)

- [ ] 6.1 Add `project_cli_profile()` requirement for each adapter to project into its native format.
- [ ] 6.2 Add scenario that no consumer appears implemented until it imports the API.
- [ ] 6.3 Define `ai-harness-skills` and `ai-review` integration requirements.

## Phase 7: Isolated TDT_HOME tests (NOT STARTED)

- [ ] 7.1 Create isolated TDT_HOME fixture.
- [ ] 7.2 Prove six-layer precedence.
- [ ] 7.3 Prove credential availability recording without secret values.
- [ ] 7.4 Prove provenance for each resolved field.
- [ ] 7.5 Prove cache isolation.

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
- [ ] 8.10 `provider-model-profile-resolution` — new spec added but not implemented.

## Phase 9: Full downstream validation (COMPLETE)

- [x] 9.1 After registry fix: all consumer suites pass in integrated main (no PYTHONPATH override).
- [ ] 9.2 After schema migration: re-run all consumer suites with new YAML schema.
- [ ] 9.3 Live LLM acceptance with registered canonical `provider:model` identifiers.
- [ ] 9.4 Redacted diagnostics and provenance verification.

## Phase 10: Validation and delivery

- [x] 10.1 OpenSpec change validation: valid.
- [x] 10.2 Full store validation: 360/360.
- [x] 10.3 `git diff --check`: clean.
- [ ] 10.4 Archive — **NOT YET**. Blocked by Phase 4, 5, 6, 7, 9.2-9.4.
