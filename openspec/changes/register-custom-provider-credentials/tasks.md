# Tasks: register-custom-provider-credentials

## Phase 1: Registry entries (not started)

- [ ] 1.1 Add three credential entries to `tdt-core/src/tdt_core/data/environment-key-registry.json` matching the existing entry shape: `logical_key`, `canonical_key`, `owner`, `value_type`, `precedence`, `secret`, `provider`, `allow_clearing`.
  - `credential.giaoduc.api_key` → `HERMES_CUSTOM_GIAODUC_API_KEY` (provider: `giaoduc`)
  - `credential.shopapikey.api_key` → `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` (provider: `shopapikey`)
  - `credential.cockpit.api_key` → `HERMES_CUSTOM_COCKPIT_API_KEY` (provider: `cockpit`)
- [ ] 1.2 Verify existing entries (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `MODEL_API_KEY`) unchanged.

## Phase 2: Tests (not started)

- [ ] 2.1 Add focused tests to `tdt-core/tests/test_llm_profile_v2.py`:
  - Custom key accepted for its matching provider.
  - Wrong-provider assignment raises `ProfileResolutionError`.
  - Unknown key raises `ProfileResolutionError`.
  - `resolve_agent_profile()` records availability as a boolean.
  - Serialized profile/diagnostic contains key name and provider, never the credential value.
  - Existing Anthropic/OpenAI/model entries unchanged.

## Phase 3: Focused regression (not started)

- [ ] 3.1 `uv run pytest tests/test_config_primitives.py tests/test_llm_profile_v2.py -q` — must stay green.
- [ ] 3.2 `uv run pytest` — full tdt-core suite.

## Phase 4: Downstream validation (not started)

- [ ] 4.1 `agent-core`: `uv run pytest -q` — report honest count.
- [ ] 4.2 `agent-harness`: `uv run pytest -q` — report honest count.
- [ ] 4.3 `agent-docs-sync`: `uv run pytest -q` — report honest count.

## Phase 5: Evidence and commit (not started)

- [ ] 5.1 Update `evidence.md` with exact SHA, test commands, counts.
- [ ] 5.2 Commit `tdt-core` change.
- [ ] 5.3 Commit `openspec-store` change.
- [ ] 5.4 **Do not archive** — downstream verification may reveal additional issues.
