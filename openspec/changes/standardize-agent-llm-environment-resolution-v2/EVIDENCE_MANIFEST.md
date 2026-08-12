# Evidence Manifest: standardize-agent-llm-environment-resolution-v2

## Scope

This change standardizes agent LLM environment resolution across the TDT Python
ecosystem into a single canonical resolution boundary, converging toward the
provider/model/default configuration pattern proven by Codex, Grok, Kimi, and
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
| `d63aa08` | `fix(config): register custom provider credentials` — **interim registry fix integrated** |

**Source symbols on `main` (`d63aa08`):**

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
→ 60 passed
```

### Full tdt-core suite (integrated main, no PYTHONPATH)

```
cd ~/Developer/tdt-core
uv run pytest -q --junitxml=/tmp/tdt-core-main.xml
→ tests=618 passed=612 failures=0 errors=0 skipped=6
```

### Downstream suites (integrated main, no PYTHONPATH)

All downstream suites ran against integrated tdt-core main (`d63aa08`) through the normal `pyproject.toml` editable dependency (`tdt-core = { path = "../tdt-core", editable = true }`). No `PYTHONPATH` override.

| Repo | SHA | Tests | Passed | Failed | Errors | Skipped |
|---|---|---|---|---|---|---|
| `tdt-core` | `d63aa08` | 618 | 612 | 0 | 0 | 6 |
| `agent-core` | `e5fb49d` | 746 | 746 | 0 | 0 | 0 |
| `agent-harness` | `0ad49d2` | 343 | 343 | 0 | 0 | 0 |
| `agent-docs-sync` | `e0ba600` | 245 | 245 | 0 | 0 | 0 |
| **Total** | | **1952** | **1946** | **0** | **0** | **6** |

### Consumer import verification

```
agent-core:       /Users/androidteam/Developer/tdt-core/src/tdt_core/__init__.py
agent-harness:    /Users/androidteam/Developer/tdt-core/src/tdt_core/__init__.py
agent-docs-sync:  /Users/androidteam/Developer/tdt-core/src/tdt_core/__init__.py
```

---

## What Is NOT Proven

1. The new YAML `providers/models/defaults` schema — not implemented.
2. `auth_env` support — not implemented.
3. Alias/protocol validation — not implemented.
4. Registry retirement decision — not made.
5. CLI consumer integrations for `ai-harness-skills` and `ai-review` — not implemented.
6. Isolated `TDT_HOME` fixture validation — not completed.
7. Live LLM acceptance — not performed.

---

## Worktree State

| Item | Value |
|---|---|
| Branch | `openspec/standardize-agent-llm-environment-resolution-v2` |
| OpenSpec baseline at original reconciliation | `6f2763a` |
| OpenSpec current verification | `c88f9b5` |
| tdt-core main | `d63aa08` (registry fix integrated) |
| External code modified | None (documentation only) |
| Archive status | **NOT ARCHIVED** — YAML migration and CLI projections remain unimplemented |
