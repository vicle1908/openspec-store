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
| `CLIProviderProfile` | `agent_profile.py:967` | CLI adapter profile model |
| `CredentialResolver` | `agent_profile.py:225` | Process-local credential resolver |
| `ProtectedCredential` | `agent_profile.py:194` | Redacted credential wrapper |
| `ConfigMapping` | `config_loader.py:352` | Fresh validated mapping + source identity |
| `tdt_root()` | `paths.py:74` | Canonical TDT root resolution |
| `tdt_config_path_for_agent()` | `paths.py:132` | Per-agent config path |

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

## Test Evidence (current baselines)

### tdt-core focused config/profile tests (PASS)

```
cd ~/Developer/tdt-core
uv run pytest tests/test_config_primitives.py tests/test_llm_profile_v2.py -q
→ 60 passed in 0.49s
```

### agent-core (BLOCKED)

```
cd ~/Developer/agent-core
uv run pytest -q --tb=short
→ 25 failed, 12 passed
```

**SHA:** `e5fb49d`

### agent-harness (BLOCKED)

```
cd ~/Developer/agent-harness
uv run pytest -q --tb=short
→ 8 failed, 14 passed
```

**SHA:** `0ad49d2`

### agent-docs-sync (BLOCKED)

```
cd ~/Developer/agent-docs-sync
uv run pytest -q --tb=short
→ 8 failed, 237 passed, 4 warnings
```

**SHA:** `e0ba600`

---

## Blocker: Custom Provider Credential Registry Gap

### Root Cause

Production `~/.tdt/config.yaml` configures three custom providers:

| Provider | `api_key_env` value | Registry status |
|---|---|---|
| `giaoduc` | `HERMES_CUSTOM_GIAODUC_API_KEY` | **NOT REGISTERED** |
| `shopapikey` | `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` | **NOT REGISTERED** |
| `cockpit` | `HERMES_CUSTOM_COCKPIT_API_KEY` | **NOT REGISTERED** |

The canonical `environment-key-registry.json` contains only three credential entries:

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

`credential_entry()` at `agent_profile.py:395-402` correctly rejects:
- Unknown credential keys (no match in registry)
- Wrong-provider assignments (key registered for different provider)

### Failure Signature

```
ProfileResolutionError: credential key is not registered: HERMES_CUSTOM_GIAODUC_API_KEY
```

### Impact (verified with explicit exit codes)

| Repo | SHA | Failed | Passed | Total | Root cause |
|---|---|---|---|---|---|
| `tdt-core` (focused) | `d90283f` | 0 | 60 | 60 | N/A |
| `agent-core` | `e5fb49d` | 27 | 719 | 746 | registry gap |
| `agent-harness` | `0ad49d2` | 8 | 335 | 343 | registry gap |
| `agent-docs-sync` | `e0ba600` | 8 | 237 | 245 | registry gap |

### Resolution Required (separate tdt-core change)

A separate `tdt-core` change must:

1. Add three credential entries to `environment-key-registry.json`.
2. Each entry must include:
   - `logical_key`: e.g. `credential.giaoduc.api_key`
   - `canonical_key`: e.g. `HERMES_CUSTOM_GIAODUC_API_KEY`
   - `owner`: `tdt-core`
   - `value_type`: `string`
   - `precedence`: `shared`
   - `secret`: `true`
   - `provider`: `giaoduc` (or `shopapikey` / `cockpit`)
   - `aliases`: `[]`
   - `alias_status`: `{}` (no legacy aliases)
   - `allow_clearing`: `false`
3. Add focused tests:
   - Custom key accepted for its provider
   - Wrong-provider assignment rejected
   - Unknown credential key rejected
   - No credential value appears in profile/provenance/diagnostics
4. Run GitNexus impact analysis before editing (blast radius: cross-repository)

### Isolated TDT_HOME Validation (deferred)

The earlier isolated-TDT_HOME test failures were `fs_kernel` secure-path setup
failures, not resolver failures. Proper isolated validation requires:
- A `TDT_HOME` with correct directory permissions
- A `.env` file (can be empty)
- A `config.yaml` with registered credential keys
- No ambient `~/.tdt` contamination

This validation is deferred to after the registry fix.

---

## Spec-to-Code Alignment (verified)

| Spec | Requirement | Symbol match |
|---|---|---|
| `agent-config-resolution` | Six-layer precedence | `resolve_agent_profile()` — explicit → consumer env → shared env → agent YAML → global YAML → defaults |
| `agent-config-resolution` | Single config function | `load_agent_config()` delegates to `resolve_agent_profile()` |
| `agent-config-resolution` | Config caching | `_agent_config_cache` with fingerprint-sensitive key |
| `agent-config-resolution` | Secure overlay API | `load_config_mapping()` + `load_agent_overlay()` with `allowed_overlay_keys` |
| `agent-core-model-resolution` | Config-driven fallback | `build_agent()` calls `load_agent_config()`, passes model to SDK |
| `agent-core-model-resolution` | Model layer is config-input only | No YAML/dotenv readers in `_ai/models.py` |
| `agent-harness-runner` | Two-plane config | `HarnessConfig.from_config()` uses `load_agent_config()` + domain overlay |
| `consumer-config-composition` | Composes Settings | `ProfileSettingsProjection` from `ResolvedAgentProfile.settings` |
| `consumer-pattern` | Harness composes profile | `HarnessConfig` owns resolved runtime-profile field |
| `ecosystem-config-loading` | Typed settings share snapshot | `load_agent_config()` and `resolve_agent_profile()` use same root/loader |
| `tdt-env-loader-tdt-home` | Canonical dotenv authority | `load_tdt_env()` is the single public dotenv API |
| `tdt-env-loader-tdt-home` | Idempotency | `_initialize_identity` guard prevents duplicate load |
| `tdt-env-loader-tdt-home` | Environment-key registry | `EnvironmentKeyRegistry.from_resource()` with sealed validation |
| `cli-provider-profile-resolution` | Provider-neutral CLI profile | `project_cli_profile()` projects non-secret profile for CLI adapters |
| `agent-docs-sync` | Canonical config | `load_agent_config("agent-docs-sync")` in `config.py:65` |

---

## What Is NOT Proven

1. Full downstream consumer suites pass — blocked by credential registry gap.
2. Isolated-environment validation — earlier attempts failed in secure dotenv path setup and do not constitute resolver evidence.
3. CLI provider profile end-to-end smoke — `project_cli_profile()` exists in `tdt-core` but no consumer repo imports it.
4. Provider binding enforcement by `credential_entry()` — the code exists at `agent_profile.py:395-402` but no test exercises the wrong-provider path.

---

## OpenSpec Validation

- `openspec validate standardize-agent-llm-environment-resolution-v2` — **valid**
- `openspec validate --all --store openspec-store` — **358 passed, 0 failed**
- `git diff --check` — **clean**

---

## Worktree State

| Item | Value |
|---|---|
| Branch | `openspec/standardize-agent-llm-environment-resolution-v2` |
| HEAD | `d18373c` (evidence-refresh baseline; this commit replaces it) |
| OpenSpec main | `6462aec` |
| Files changed | 15 (all under `openspec/changes/standardize-agent-llm-environment-resolution-v2/`) |
| Insertions | 1696 |
| External code modified | None |
