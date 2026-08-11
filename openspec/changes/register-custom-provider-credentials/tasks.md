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

## Phase 4: Downstream validation (complete — integrated, no PYTHONPATH)

- [x] 4.1 `agent-core`: `uv run pytest -q` → **746 passed, 0 failures**.
- [x] 4.2 `agent-harness`: `uv run pytest -q` → **343 passed, 0 failures**.
- [x] 4.3 `agent-docs-sync`: `uv run pytest -q` → **245 passed, 0 failures**.
- [x] 4.4 All downstream suites ran against integrated tdt-core main (`d63aa08`) through normal `pyproject.toml` editable dependency — no `PYTHONPATH` override.

## Phase 5: Evidence and commit (complete)

- [x] 5.1 Update `evidence.md` with integrated SHA (`d63aa08`), non-PYTHONPATH counts, consumer import paths.
- [x] 5.2 Commit tdt-core change: `d63aa08 fix(config): register custom provider credentials`.
- [x] 5.3 Integrate tdt-core branch into main: cherry-pick `2897df7` → `d63aa08`.

## Phase 6: Documentation reconciliation (not started)

- [ ] 6.1 Update v2 `EVIDENCE_MANIFEST.md` to mark registry blocker resolved, record integrated SHA `d63aa08`, replace old blocked downstream counts.
- [ ] 6.2 Update v2 `tasks.md` to mark Phase 3 (registry fix) complete and Phase 4 downstream as verified against integrated main.
- [ ] 6.3 Update v2 `proposal.md` and `design.md` where they state the registry fix is pending.
- [ ] 6.4 Validate both changes, stage only change directories, commit.

## Phase 7: Cleanup (not started)

- [ ] 7.1 Pop graphify-out stash on tdt-core main.
- [ ] 7.2 Remove isolated integration worktree (`~/Developer/tdt-core-credentials-integration`).
- [ ] 7.3 Remove v2 worktree branch if no longer needed.
- [ ] 7.4 Decide whether to archive `register-custom-provider-credentials` — **NOT YET** until v2 change is reconciled.

## Phase 8: Archive decision (deferred)

- [ ] 8.1 Archive `register-custom-provider-credentials` only after v2 change is reconciled and no cross-repo issues remain.
- [ ] 8.2 **Do not archive the v2 change** — provider/model/default YAML migration and CLI projections remain unimplemented.
