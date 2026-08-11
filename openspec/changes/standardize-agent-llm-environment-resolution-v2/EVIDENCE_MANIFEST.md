# Phase-1 Baseline Evidence Manifest

**Change:** `standardize-agent-llm-environment-resolution-v2`
**Captured:** 2026-08-11T06:15:00Z
**Writer:** kimi-advance (sole Phase-1 evidence/tasks-ledger writer)

## 1. Worktree Inventory (Tasks 1.1-1.2)

### OpenSpec Store

| Field | Value |
|-------|-------|
| Path | `/Users/androidteam/Developer/.worktrees/openspec-llm-env-v2` |
| HEAD | `2f2960554202c6dca85fd3b34d2f8e157219ee59` |
| Branch | `openspec/standardize-agent-llm-environment-resolution-v2` |
| Git identity | `vinhlk2 <vinhlk2@ghtk.co>` |
| Dirty | Untracked: `openspec/changes/standardize-agent-llm-environment-resolution-v2/` |
| Change artifacts | `README.md`, `design.md`, `proposal.md`, `specs/`, `tasks.md` |

### tdt-core (Phase 2 foundation writer: @goose-luna)

| Field | Value |
|-------|-------|
| Path | `/Users/androidteam/Developer/.worktrees/llm-env-v2/tdt-core` |
| HEAD | `135268d18628b9c774b2303c37aa877a21def29c` |
| Branch | `work/llm-env-v2-tdt-core` |
| Git identity | `vinhlk2 <vinhlk2@ghtk.co>` |
| Dirty | Untracked: `tests/test_llm_profile_v2.py` (v2 API test stubs) |
| Fingerprint | `ada09eb596f0d1e869879cf3f5e7e74e64e5b9301403202bffde1ca6a8f9e207` |
| Imported module | N/A (pydantic not installed in system Python; use `uv run`) |
| GitNexus/Graphify | Stale (indexed at different commit) |

### agent-core (Phase 3 writer: @codex-luna)

| Field | Value |
|-------|-------|
| Path | `/Users/androidteam/Developer/.worktrees/llm-env-v2/agent-core` |
| HEAD | `e5fb49d18a2c8b3462b41626d088e766c8563b67` |
| Branch | `work/llm-env-v2-agent-core` |
| Git identity | `vinhlk2 <vinhlk2@ghtk.co>` |
| Dirty | Clean (no porcelain paths) |
| Fingerprint | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| Imported module | `agent_core.__init__` → `/Users/androidteam/Developer/.worktrees/llm-env-v2/agent-core/src/agent_core/__init__.py` |
| GitNexus/Graphify | Stale |

### agent-docs-sync (Phase 4 writer: @goose-luna)

| Field | Value |
|-------|-------|
| Path | `/Users/androidteam/Developer/.worktrees/llm-env-v2/agent-docs-sync` |
| HEAD | `e0ba6000476c724de748c64fced1161a323cb5ed` |
| Branch | `work/llm-env-v2-agent-docs-sync` |
| Git identity | `vinhlk2 <vinhlk2@ghtk.co>` |
| Dirty | Clean |
| Fingerprint | `a203223e922bd5ca6fbabc056733d8e705f871e8fa57794dcaffa19ebb5a9949` |
| Imported module | `agent_docs_sync.__init__` → `/Users/androidteam/Developer/.worktrees/llm-env-v2/agent-docs-sync/src/agent_docs_sync/__init__.py` |
| GitNexus/Graphify | Stale |

### ai-harness-skills (Phase 6 writer: @grok-fable)

| Field | Value |
|-------|-------|
| Path | `/Users/androidteam/Developer/.worktrees/llm-env-v2/ai-harness-skills` |
| HEAD | `e7e1b2a94de2806175306d67d76ba8ce0908469a` |
| Branch | `work/llm-env-v2-ai-harness` |
| Git identity | `vinhlk2 <vinhlk2@ghtk.co>` |
| Dirty | Clean |
| Fingerprint | `e9b4bcafe9c716ca492a3d544c6ff8b9ff2c9fc5c89d929761a82b7fa842ceaa` |
| Imported module | N/A (code-daily-scan dependency missing from worktree) |
| GitNexus/Graphify | Stale |

### ai-review (Phase 6 writer: @grok-fable)

| Field | Value |
|-------|-------|
| Path | `/Users/androidteam/Developer/.worktrees/llm-env-v2/ai-review` |
| HEAD | `a5195409a124830607e92bc4bd8d16a4d068d9b5` |
| Branch | `work/llm-env-v2-ai-review` |
| Git identity | `vinhlk2 <vinhlk2@ghtk.co>` |
| Dirty | Clean |
| Fingerprint | `e067ecb339990a013c960b3c6f9cc0b1a3a2861a479801cf741a8f83b675c8b0` |
| Imported module | `ai_review.__init__` → `/Users/androidteam/Developer/.worktrees/llm-env-v2/ai-review/src/ai_review/__init__.py` |
| GitNexus/Graphify | Stale |

### agent-harness (Phase 5 writer: @opencode-gd-1)

| Field | Value |
|-------|-------|
| Path | `/Users/androidteam/Developer/.worktrees/llm-env-v2/agent-harness` |
| HEAD | `f0ce05643a17667353f3e9c6e8536a54392b9fe4` |
| Branch | `work/llm-env-v2-agent-harness` |
| Git identity | `vinhlk2 <vinhlk2@ghtk.co>` |
| Dirty | Clean |
| Fingerprint | (not computed — added post-audit) |
| Imported module | `agent_harness.__init__` → `/Users/androidteam/Developer/.worktrees/llm-env-v2/agent-harness/src/agent_harness/__init__.py` |
| GitNexus/Graphify | Stale |

## 2. Test Suite Baseline (Pre-Implementation)

| Repo | Result | Count | Notes |
|------|--------|-------|-------|
| tdt-core | FAIL | 5 failed in `test_llm_profile_v2.py` | Tests for v2 API not yet implemented — expected failures |
| agent-core | PASS | All passed, 10 skipped | Skips: missing source fixtures (jira-daily-reports, tdt-observability, code-daily-scan) |
| agent-docs-sync | PASS | 245 passed, 4 warnings | Warnings: FutureWarning on --actor flag |
| ai-harness-skills | FAIL | 9 failed, 571 passed, 4 skipped | Failed: `test_json_preflight_is_exactly_one_document`, `test_default_fail_fast_contract_in_separate_process`, `test_load_uses_current_alternate_tdt_home_after_import`, + 6 more |
| ai-review | BLOCKED | Cannot run | Dependency `code-daily-scan==0.1.0` not present in worktree |
| agent-harness | PASS | 336 passed, 0 failed | Clean pass |

## 3. Failing Probes (Task 1.3) — Retained

### Probe 1: tdt-core v2 API (expected failures — foundation not yet implemented)

Tests in `tests/test_llm_profile_v2.py` fail because the v2 public API does not exist yet:
- `ImportError: cannot import name 'CredentialResolver' from 'tdt_core'`
- `ImportError: cannot import name 'load_config_mapping' from 'tdt_core.config_loader'`
- `ImportError: cannot import name 'load_agent_overlay' from 'tdt_core.config_loader'`
- `ModuleNotFoundError: No module named 'tdt_core.agent_profile'`
- `TypeError: load_tdt_env() got an unexpected keyword argument 'env_file'`

**These are the RED baseline for Phase 2 implementation.** They must turn GREEN after @goose-luna implements tasks 2.1-2.13.

### Probe 2: agent-docs-sync projection disagreement

`DocsSyncConfig.settings` delegates to `ConsumerRuntimeProfile.settings`, which independently invokes `agent_core.load_settings()`. `DocsSyncConfig.model` delegates to `runtime.model`. `generation._resolve_model_with_fallback` independently calls `tdt_core.load_agent_config()`. The shortcut model and settings.model.primary can diverge (deterministic repro: shortcut=openai-chat:yaml-model, settings.primary=anthropic:Advance).

### Probe 3: agent-core environment precedence

Agent-core model layer reads YAML, dotenv, TDT config-path, and independent process-environment values separately from the resolved profile. The `load_settings(env_file=...)` parameter is silently ignored in some paths.

### Probe 4: harness production model propagation

Harness `HarnessServices.production_services()` constructs model instances from `runtime.model` field. The default artifact root is resolved from a literal environment placeholder (`$TDT_HOME/artifacts`) rather than the canonical root object.

### Probe 5: ai-harness-skills config loading

`ai-harness-skills` reads `$TDT_HOME/.env` directly via `dotenv` and has independent model/alias resolution. 9 test failures indicate existing contract drift.

### Probe 6: code-daily-scan dependency

`ai-harness-skills` and `ai-review` both depend on `code-daily-scan==0.1.0` as an editable dependency. This package is not present in the worktree, blocking test execution for `ai-review` and causing import errors for `ai-harness-skills`.

## 4. Redacted Key/Alias Inventory (Task 1.4)

### Environment Keys (across all repos)

| Key Pattern | Repos | Notes |
|-------------|-------|-------|
| `ANTHROPIC_API_KEY` | tdt-core, agent-core, agent-docs-sync, ai-harness-skills, ai-harness-skills, agent-harness | Primary provider credential |
| `OPENAI_API_KEY` | tdt-core, agent-core, agent-docs-sync, ai-harness-skills, ai-harness-skills, agent-harness | Secondary provider credential |
| `TDT_HOME` | All repos | Root config directory |
| `TDT_ENV_FILE` | tdt-core | Explicit env file selection |
| `DOCS_SYNC_MODEL` | agent-docs-sync | Consumer-specific model override |
| `ANTHROPIC_MODEL` | agent-core, ai-harness-skills | Provider-specific model override |
| `OPENAI_MODEL` | agent-core, ai-harness-skills | Provider-specific model override |

### Model Configuration Keys

| Key | Repos | Precedence |
|-----|-------|------------|
| `model.primary` | tdt-core, agent-core, agent-docs-sync, ai-harness-skills, agent-harness | YAML config → env → default |
| `model.fallback` | tdt-core, agent-core, agent-docs-sync, ai-harness-skills, agent-harness | YAML config → env → empty |
| `runtime.model` | agent-harness | Harness-specific model field |
| `model_alias` | ai-harness-skills, ai-review | CLI provider alias |

### Compatibility Aliases

| Alias | Target | Repos |
|-------|--------|-------|
| `claude` → `anthropic` | Provider alias | ai-harness-skills, ai-review |
| `codex` → `openai` | Provider alias | ai-harness-skills, ai-review |
| `sonnet` | Model alias | ai-harness-skills |
| `kimi` | Provider alias | ai-review |

### Explicit Boundary Cases

| Case | Status | Notes |
|------|--------|-------|
| `prime-agent` | Outside scope | Does not have direct LLM path |
| `claude-code-provider-adapter` | Outside scope | External adapter, not in worktree |
| `code-daily-scan` | Boundary dep | Present as editable dependency, blocks ai-review tests |

## 5. Writer Assignments (Task 1.2)

| Repo | Assigned Writer | Status |
|------|----------------|--------|
| tdt-core | @goose-luna (reassigned from @kimi-advance) | Sole writer |
| agent-core | @codex-luna | Preflight only until foundation |
| agent-docs-sync | @goose-luna | Paused at clean base |
| ai-harness-skills | @grok-fable | Preflight only until foundation |
| ai-review | @grok-fable | Preflight only until foundation |
| agent-harness | @opencode-gd-1 | Preflight only until foundation |
| OpenSpec store | @kimi-advance | Sole tasks.md writer |

## 6. Dependency Gate

- **Closed** for: agent-core, docs-sync, harness, ai-harness-skills, ai-review application edits
- **Open** for: tdt-core foundation implementation (@goose-luna), OpenSpec ledger (@kimi-advance)
- **Next milestone:** @goose-luna publishes tdt-core foundation commit SHA with public API signatures
