# Evidence Manifest: standardize-agent-llm-environment-resolution-v2

## Scope

Corrective v2 of the agent LLM environment resolution standardization. Aligns the TDT Python agent ecosystem with the provider/model/default configuration pattern proven by Codex, Grok, Kimi, and Pi.

**Core implementation complete. Phase 6 (CLI consumer wiring) deferred to successor change `integrate-canonical-cli-projections-v1`.**

---

## Current Implementation Provenance

### tdt-core (foundation + schema + resolver integration)

| Commit | Description |
|---|---|
| `e395611` | `feat(tdt-core): add per-agent config resolution` |
| `135268d` | `fix: make agent config cache path-sensitive` |
| `8496f8e` | `feat(tdt-core): add v2 config primitives for LLM config standardization` |
| `d90283f` | `docs(tdt-core): add v2 config primitives to README` |
| `d63aa08` | `fix(config): register custom provider credentials` — interim registry fix |
| `21dcd5b` | `test: strict Codex acceptance proof via new-schema YAML pipeline` — **schema + resolver integration + acceptance** |

**Source symbols on `main` (`21dcd5b`):**

| Symbol | Purpose |
|---|---|
| `resolve_agent_profile()` | Canonical six-layer resolution boundary |
| `_NewSchemaProjection` | New-schema YAML → `_choose()` pipeline |
| `_project_new_schema()` | Schema parser → projection dataclass |
| `ProviderModelConfig` | Typed YAML schema: providers, models, defaults |
| `project_cli_profile()` | CLI adapter profile projection |
| `CLIProviderProfile` | CLI adapter profile model |

### agent-core (consumer wiring)

| Commit | Description |
|---|---|
| `e5fb49d` | `fix: route per-agent model config through build_agent and CLI paths` |

### agent-harness (two-plane config)

| Commit | Description |
|---|---|
| `0ad49d2` | `feat(agent-harness): implement two-plane config loading strategy` |

### agent-docs-sync (config alignment)

| Commit | Description |
|---|---|
| `e0ba600` | `fix: align docs-sync config with tdt-core agent config chain` |

### ai-harness-skills (Phase 6 foundation — NOT wired)

| Commit | Description |
|---|---|
| `b160709` | `feat(projection): add TDT provider-neutral projection bridge` — bridge module + 9 focused tests, NOT wired into `build_runtime()` |

### ai-review (Phase 6 — NOT started)

No implementation. Branch `phase6/tdt-core-projection` exists at `a519540` (same as main).

---

## Test Evidence

### tdt-core focused config/profile tests

```
cd ~/Developer/tdt-core
uv run pytest tests/test_config_primitives.py tests/test_llm_profile_v2.py tests/test_provider_model_profile.py tests/test_resolver_precedence.py -q
→ 129 passed
```

### Full tdt-core suite (integrated main, no PYTHONPATH)

```
cd ~/Developer/tdt-core
uv run pytest -q --junitxml=/tmp/tdt-provider-model-main.xml
→ tests=687 passed=681 failures=0 errors=0 skipped=6
```

### Downstream suites (integrated main, no PYTHONPATH)

| Repo | SHA | Tests | Passed | Failed | Errors | Skipped |
|---|---|---|---|---|---|---|
| `tdt-core` | `21dcd5b` | 687 | 681 | 0 | 0 | 6 |
| `agent-core` | `e5fb49d` | 746 | 746 | 0 | 0 | 0 |
| `agent-harness` | `0ad49d2` | 343 | 343 | 0 | 0 | 0 |
| `agent-docs-sync` | `e0ba600` | 245 | 245 | 0 | 0 | 0 |
| **Total** | | **2021** | **2015** | **0** | **0** | **6** |

### ai-harness-skills bridge tests (Phase 6 foundation)

```
cd ~/Developer/ai-harness-skills-phase6
uv run pytest tests/unit/test_tdt_projection.py -v --no-cov
→ 9 passed
```

---

## Strict Codex Acceptance Evidence

| Item | Value |
|---|---|
| Commit | `4c277c4` |
| Script | `scripts/verify_v2_codex_acceptance.py` |
| Command | `codex exec --ephemeral --skip-git-repo-check --sandbox read-only -m gpt-5.6-sol ...` |
| Exit code | 0 |
| Nonce | `TDT_8ef49e53` |
| Duration | 7.25s |
| Provider | Native Codex (`gpt-5.6-sol` via `codex_local_access`) |

---

## Missing-Credential Proof

| Path | Result |
|---|---|
| New-schema `auth_env` path | Profile resolves, `CredentialResolver.resolve()` raises at use-time ✅ |
| Legacy `api_key_env` path | Profile resolves, `CredentialResolver.resolve()` raises at use-time ✅ |

---

## What Is NOT Done

| Item | Status | Blocked by |
|---|---|---|
| Phase 5: Registry retirement decision | Deferred | Successor change |
| Phase 6: CLI projections for ai-harness-skills | Foundation only, NOT wired | Field-source matrix correction |
| Phase 6: CLI projections for ai-review | NOT started | Phase 6 design |
| Phase 9.2: Re-run consumers with new YAML schema | NOT done | Phase 6 completion |
| Phase 9.4: Redacted diagnostics verification | NOT done | Phase 6 completion |

---

## Worktree State

| Item | Value |
|---|---|
| tdt-core main | `21dcd5b` |
| OpenSpec baseline | `6f2763a` |
| OpenSpec current | `c88f9b5` |
| ai-harness-skills-phase6 | `b160709` (NOT wired) |
| ai-review-phase6 | `a519540` (NOT started) |
| Archive status | **NOT ARCHIVED** — Phase 5 and 6 deferred to successor change |
