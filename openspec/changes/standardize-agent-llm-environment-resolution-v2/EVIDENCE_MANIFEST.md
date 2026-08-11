# Evidence Manifest: standardize-agent-llm-environment-resolution-v2

## Scope

This change standardizes agent LLM environment resolution across the TDT Python
ecosystem into a single canonical resolution boundary, converging toward the
provider/model/default configuration pattern proven by Codex, Grok, fable-5, and
Pi. All current implementation is committed to `main` across the six affected
repositories. The YAML schema migration (providers/models/defaults) is proposed
but not implemented.

---

## Research Evidence: Native CLI Configuration Patterns

### Installed CLI versions

| CLI | Version | Config file | Credential store |
|---|---|---|---|
| Codex | 0.147.0 | `~/.codex/config.toml` | `auth.json` |
| Grok Build | 1.0.0 | `~/.grok/config.toml` | `auth.json` |
| Kimi | 0.34.0 | `~/.kimi/config.toml` | inline (⚠️) |
| Pi | 0.84.1 | `~/.pi/agent/mcp.json` | parent runtime |

### Codex config.toml structure

```toml
model_provider = "codex_local_access"   # provider selector
model = "gpt-5.6-sol"                   # model selection
model_reasoning_effort = "high"          # behavior knob

[model_providers.codex_local_access]
base_url = "http://localhost:51006/v1"
wire_api = "responses"
```

### Grok Build config.toml structure

```toml
[models]
default = "cockpit-terra"               # alias selection

[model_providers.cockpit]
base_url = "http://localhost:51006/v1"
api_backend = "responses"
context_window = 1000000

[model.cockpit-terra]
model = "gpt-5.6-terra"
model_provider = "cockpit"
```

### fable-5 config.toml structure

```toml
default_model = "fable-52-6"            # alias selection

[providers.omniroute]
type = "openai_responses"
base_url = "http://localhost:20128/v1"

[models.fable-5-k2-6]
provider = "omniroute"
model = "dlg/fable-52.6"
```

### Universal pattern

All four CLIs converge on: provider definition (endpoint + protocol + auth) → model alias (provider + wire model + behavior) → default selection.

---

## Current Implementation Provenance

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
| `ResolvedAgentProfile` | `agent_profile.py:116` | Frozen effective LLM snapshot |
| `Provenance` | `agent_profile.py:77` | Redacted source provenance |
| `project_cli_profile()` | `agent_profile.py:912` | CLI adapter profile projection |
| `CLIProviderProfile` | `agent_profile.py:967` | CLI adapter profile model |

### agent-core (consumer wiring)

| Commit | Description |
|---|---|
| `e5fb49d` | `fix: route per-agent model config through build_agent and CLI paths` |

### agent-harness (two-plane config)

| Commit | Description |
|---|---|
| `6a89de6` | `feat(agent-harness): implement two-plane config loading strategy` |

### agent-docs-sync (config alignment)

| Commit | Description |
|---|---|
| `267c3aa` | `fix: align docs-sync config with tdt-core agent config chain` |

### ai-harness-skills, ai-review

No LLM config implementation changes. Branches identical to `main`.

---

## Test Evidence

### tdt-core focused config/profile tests (PASS)

```
cd ~/Developer/tdt-core
uv run pytest tests/test_config_primitives.py tests/test_llm_profile_v2.py -q
→ 60 passed in 0.49s
```

### Downstream suites (BLOCKED by credential registry gap)

Captured via `pytest --junitxml`; explicit exit code `1` confirmed for each.

| Repo | SHA | Failed | Passed | Total | Root cause |
|---|---|---|---|---|---|
| `tdt-core` (focused) | `d90283f` | 0 | 60 | 60 | N/A |
| `agent-core` | `e5fb49d` | 27 | 719 | 746 | registry gap |
| `agent-harness` | `0ad49d2` | 8 | 335 | 343 | registry gap |
| `agent-docs-sync` | `e0ba600` | 8 | 237 | 245 | registry gap |

**Caveat:** All observed downstream failures enter the unresolved custom-provider credential path; independent post-fix failures are currently masked by the first common failure.

---

## What Is NOT Proven

1. The new YAML `providers/models/defaults` schema — not implemented.
2. `auth_env` support — not implemented.
3. Alias/protocol validation — not implemented.
4. Registry retirement decision — not made.
5. CLI consumer integrations for `ai-harness-skills` and `ai-review` — not implemented.
6. Isolated `TDT_HOME` fixture validation — not completed.
7. Full downstream consumer suites pass — blocked by credential registry gap.
8. Live LLM acceptance — not performed.

---

## Worktree State

| Item | Value |
|---|---|
| Branch | `openspec/standardize-agent-llm-environment-resolution-v2` |
| HEAD baseline before this commit | `859fca5` |
| OpenSpec main | `d111c3d` |
| Files changed | 16 (all under `openspec/changes/standardize-agent-llm-environment-resolution-v2/`) |
| External code modified | None |
| Archive status | **NOT ARCHIVED** — blocked by Phase 3, 4, 5, 6, 7, 9 |
