# Evidence Manifest: standardize-agent-llm-environment-resolution-v2

## Scope

This change standardizes agent LLM environment resolution across the TDT Python
ecosystem into a single canonical resolution boundary. All implementation is
already committed to `main` across the six affected repositories. This worktree
contains only OpenSpec documentation artifacts.

---

## Implementation Provenance

### tdt-core (foundation)

| Commit | Description |
|---|---|
| `e395611` | `feat(tdt-core): add per-agent config resolution` |
| `135268d` | `fix: make agent config cache path-sensitive` |
| `8496f8e` | `feat(tdt-core): add v2 config primitives for LLM config standardization` |
| `d90283f` | `docs(tdt-core): add v2 config primitives to README` |

**Source symbols on `main` (`d90283f`):**

| Symbol | File:Line | Purpose |
|---|---|---|
| `resolve_agent_profile()` | `agent_profile.py:613` | Canonical six-layer resolution boundary |
| `load_agent_config()` | `config_loader.py:541` | Compatibility mapping projection |
| `load_config_mapping()` | `config_loader.py:433` | Secure, non-merging YAML reader |
| `load_agent_overlay()` | `config_loader.py:497` | Source-preserving agent overlay reader |
| `load_tdt_env()` | `env.py:391` | Canonical dotenv authority |
| `EnvironmentKeyRegistry` | `agent_profile.py:299` | Registered env-key validation |
| `EnvironmentKey` | `agent_profile.py:281` | Per-key metadata (type, precedence, secret, provider) |
| `ResolvedAgentProfile` | `agent_profile.py:116` | Frozen effective LLM snapshot |
| `Provenance` | `agent_profile.py:77` | Redacted source provenance |
| `project_cli_profile()` | `agent_profile.py:912` | CLI adapter profile projection |
| `ConfigMapping` | `config_loader.py:352` | Fresh validated mapping + source identity |
| `tdt_root()` | `paths.py:74` | Canonical TDT root resolution |

### agent-core (consumer wiring)

| Commit | Description |
|---|---|
| `e5fb49d` | `fix: route per-agent model config through build_agent and CLI paths` |

**Symbol:** `build_agent()` at `sdk/agents.py:80` calls `tdt_core.config_loader.load_agent_config(agent_name)`.

### agent-harness (two-plane config)

| Commit | Description |
|---|---|
| `6a89de6` | `feat(agent-harness): implement two-plane config loading strategy` |

**Symbol:** `HarnessConfig` at `config.py:123` composes resolved profile via `load_agent_config("agent-harness")`.

### agent-docs-sync (config alignment)

| Commit | Description |
|---|---|
| `267c3aa` | `fix: align docs-sync config with tdt-core agent config chain` |

**Symbol:** `config.py:65` calls `load_agent_config("agent-docs-sync")`.

### ai-harness-skills, ai-review

No LLM config implementation changes. Branches (`work/llm-env-v2-ai-harness`, `work/llm-env-v2-ai-review`) are identical to `main`.

---

## Test Evidence

### tdt-core focused config/profile tests (PASS)

```
uv run pytest tests/test_config_primitives.py tests/test_llm_profile_v2.py -v -q
→ 60 passed in 0.59s
```

### agent-core (PARTIAL FAILURE)

```
uv run pytest --tb=line -q
→ 17 failed, 12 passed
```

**Failure pattern:** Every `build_agent` test fails with:

```
ProfileResolutionError: credential key is not registered: HERMES_CUSTOM_GIAODUC_API_KEY
```

### agent-harness (PARTIAL FAILURE)

```
uv run pytest --tb=line -q
→ 8 failed, 14 passed
```

**Same failure pattern.**

### agent-docs-sync (PARTIAL FAILURE)

```
uv run pytest --tb=line -q
→ 8 failed, 237 passed, 4 warnings
```

**Same failure pattern in guardrails/parity/subagents/write-containment tests.**

---

## Blocker: Custom Provider Credential Registry Gap

### Root Cause

Production `~/.tdt/config.yaml` configures three custom providers:

| Provider | `api_key_env` value | Registry status |
|---|---|---|
| `giaoduc` | `HERMES_CUSTOM_GIAODUC_API_KEY` | **NOT REGISTERED** |
| `shopapikey` | `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` | **NOT REGISTERED** |
| `cockpit` | `HERMES_CUSTOM_COCKPIT_API_KEY` | **NOT REGISTERED** |

The canonical `environment-key-registry.json` only contains three credential entries:

| `logical_key` | `canonical_key` | `provider` |
|---|---|---|
| `credential.anthropic.api_key` | `ANTHROPIC_API_KEY` | `anthropic` |
| `credential.openai.api_key` | `OPENAI_API_KEY` | `openai-chat` |
| `credential.model.api_key` | `MODEL_API_KEY` | (none) |

### Failure Mechanism

`resolve_agent_profile()` at `agent_profile.py:862-865` iterates the `providers`
mapping from global YAML, and for each entry with an `api_key_env` string, calls
`registry.credential_entry(key_name, provider_id)`. When the key is not registered,
`credential_entry()` raises `ProfileResolutionError`.

### Resolution Required (separate change)

A separate `tdt-core` change must:

1. Add three credential entries to `environment-key-registry.json`.
2. Associate each with exactly one provider (`giaoduc`, `shopapikey`, `cockpit`).
3. Preserve `secret: true` classification.
4. Add focused tests: accepted custom key, wrong-provider rejection, unknown-key rejection.

This is a cross-repo implementation prerequisite, not a spec/documentation issue.

---

## Spec-to-Code Alignment (verified)

| Spec | Requirement | Symbol match |
|---|---|---|
| `agent-config-resolution` | Six-layer precedence | `resolve_agent_profile()` — explicit → consumer env → shared env → agent YAML → global YAML → defaults |
| `agent-config-resolution` | Single config function | `load_agent_config()` delegates to `resolve_agent_profile()` |
| `agent-config-resolution` | Config caching | `_agent_config_cache` with fingerprint-sensitive key |
| `agent-core-model-resolution` | Config-driven fallback | `build_agent()` calls `load_agent_config()`, passes model to SDK |
| `agent-core-model-resolution` | Model layer is config-input only | No YAML/dotenv readers in `_ai/models.py` |
| `agent-harness-runner` | Two-plane config | `HarnessConfig.from_config()` uses `load_agent_config()` + domain overlay |
| `consumer-config-composition` | Composes Settings | `ProfileSettingsProjection` from `ResolvedAgentProfile.settings` |
| `consumer-pattern` | Harness composes profile | `HarnessConfig` owns resolved runtime-profile field |
| `ecosystem-config-loading` | Typed settings share snapshot | `load_agent_config()` and `resolve_agent_profile()` use same root/loader |
| `tdt-env-loader-tdt-home` | Canonical dotenv authority | `load_tdt_env()` is the single public dotenv API |
| `tdt-env-loader-tdt-home` | Idempotency | `_initialize_identity` guard prevents duplicate load |
| `cli-provider-profile-resolution` | Provider-neutral CLI profile | `project_cli_profile()` projects non-secret profile for CLI adapters |
| `agent-docs-sync` | Canonical config | `load_agent_config("agent-docs-sync")` in `config.py:65` |

---

## What Is NOT Proven

1. Full downstream consumer suites pass — blocked by credential registry gap.
2. Isolated-environment validation — earlier attempts failed in secure dotenv path setup and do not constitute resolver evidence.
3. CLI provider profile end-to-end smoke — `project_cli_profile()` exists but no live invocation evidence captured.

---

## OpenSpec Validation

- `openspec validate --all --store openspec-store` — **358 passed, 0 failed** (pre-rebase baseline; will re-run after commit).
