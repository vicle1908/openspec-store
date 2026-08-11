# Tasks: register-custom-provider-credentials

## Phase 1: Registry entries (complete)

- [x] 1.1 Add three credential entries to `tdt-core/src/tdt_core/data/environment-key-registry.json`.
  - `credential.giaoduc.api_key` → `HERMES_CUSTOM_GIAODUC_API_KEY` (provider: `giaoduc`)
  - `credential.shopapikey.api_key` → `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` (provider: `shopapikey`)
  - `credential.cockpit.api_key` → `HERMES_CUSTOM_COCKPIT_API_KEY` (provider: `cockpit`)
  - Evidence: 17 → 20 entries, minified JSON format preserved, semantic diff verified.
- [x] 1.2 Verify existing entries unchanged.
  - Evidence: `ANTHROPIC_API_KEY` (anthropic), `OPENAI_API_KEY` (openai-chat), `MODEL_API_KEY` (none) — all identical to main.

## Phase 2: Tests (complete)

- [x] 2.1 Add focused tests to `tdt-core/tests/test_custom_provider_credentials.py`.
  - 12 tests: accepted (3), wrong-provider rejected (3), unknown rejected (1), availability metadata (2), serialization safety (1), existing entries unchanged (3).
  - Evidence: `uv run pytest tests/test_custom_provider_credentials.py -v` → 12 passed.
- [x] 2.2 Existing config tests unchanged.
  - Evidence: `uv run pytest tests/test_config_primitives.py tests/test_llm_profile_v2.py -q` → 60 passed.

## Phase 3: Focused regression (complete)

- [x] 3.1 `uv run pytest tests/test_config_primitives.py tests/test_llm_profile_v2.py -q` — **60 passed**.
- [x] 3.2 `uv run pytest -q --junitxml=<path>` — full tdt-core suite: **612 passed, 6 skipped, 0 failures, 0 errors**.

## Phase 4: Downstream validation (complete via PYTHONPATH override)

- [x] 4.1 `agent-core`: `PYTHONPATH=.../tdt-core-register-credentials/src uv run pytest -q` → **746 passed, 0 failures**.
- [x] 4.2 `agent-harness`: `PYTHONPATH=.../tdt-core-register-credentials/src uv run pytest -q` → **343 passed, 0 failures**.
- [x] 4.3 `agent-docs-sync`: `PYTHONPATH=.../tdt-core-register-credentials/src uv run pytest -q` → **245 passed, 0 failures**.
- [ ] 4.4 **Re-run downstream suites without PYTHONPATH override** after tdt-core main integration.

## Phase 5: Evidence and commit (complete)

- [x] 5.1 Update `evidence.md` with exact SHA (`2897df7`), test commands, counts, downstream results, PYTHONPATH caveat.
- [x] 5.2 Commit tdt-core change: `2897df7 fix(config): register custom provider credentials`.
- [ ] 5.3 Integrate tdt-core branch into main (not yet done).
- [ ] 5.4 Re-run downstream suites against integrated main.
- [ ] 5.5 Archive — **NOT YET**. Blocked by 5.3 and 5.4.

## Phase 6: Integration into tdt-core main (NOT STARTED)

- [ ] 6.1 Create clean integration branch from current tdt-core main.
- [ ] 6.2 Cherry-pick or merge `2897df7` into integration branch.
- [ ] 6.3 Run full tdt-core suite against integration branch (no PYTHONPATH override).
- [ ] 6.4 Verify downstream consumers resolve the integrated tdt-core (not the isolated worktree).
- [ ] 6.5 Run agent-core, agent-harness, agent-docs-sync suites against integrated tdt-core (no PYTHONPATH override).
- [ ] 6.6 Push integration branch or merge to main.
- [ ] 6.7 Clean up isolated worktree (`~/Developer/tdt-core-register-credentials`).
- [ ] 6.8 Update evidence.md with integrated SHA and remove PYTHONPATH caveat.
