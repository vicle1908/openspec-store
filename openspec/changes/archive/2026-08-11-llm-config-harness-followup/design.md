# Design: llm-config-harness-followup

## Context

Phase 4 of `llm-config-standardization` was never properly designed or implemented.
The archived change was created prematurely. The committed `agent-harness` code still
reads `$TDT_HOME/harness/config.yaml` via `_load_yaml_section()`.

## Root Cause

`tdt_core.load_agent_config()` restricts agent overlays to `{"model", "runtime"}`.
This is the correct LLM-config contract. `HarnessConfig` needs seven domain sections
(`gate`, `validation`, `persistence`, `budget`, `retention`, `authority`) that must
NOT go through the LLM merge logic.

A merged mapping loses source provenance. The harness cannot distinguish whether
`gate` came from the agent overlay or the global config. Two loaders are needed:
one for merged LLM config, one for raw source-preserving overlay.

## Three-Plane Architecture

### 1. `load_config_mapping(path: Path) -> dict`

Low-level secure YAML loader:

- Parses one file only
- No merge, no cache
- Validates mapping shape and secrets via `_reject_secrets()`
- Empty/missing file → `{}`
- Malformed YAML → `ConfigError`
- Non-mapping → `ConfigError`
- Returns a fresh dict per call

### 2. `load_agent_overlay(agent_name, config_path=None, allowed_keys=None) -> dict`

Source-preserving agent overlay loader:

- Reads ONLY the agent YAML (never global config)
- Calls `load_config_mapping()` for parsing and secret validation
- Validates top-level keys against `allowed_keys`
- Returns raw overlay dict (source provenance preserved)
- Default `allowed_keys`: `{"model", "runtime"}` (strict)
- Harness opts in to domain keys: `{"model", "runtime", "gate", "validation",
  "persistence", "budget", "retention", "authority"}`
- Missing file → `{}`

### 3. `load_agent_config(agent_name, *, config_path=None, allowed_overlay_keys=None) -> dict`

Merged LLM config loader (existing API, extended):

- Reads global config + agent overlay
- Preserves existing merge: deep-merge `model`, shallow-override `runtime`
- `allowed_overlay_keys`: allows the agent overlay to contain keys beyond
  `{"model", "runtime"}` without `ConfigError`. Domain keys are accepted
  by the overlay but NOT merged into the global result. They appear in the
  returned dict because the merged dict includes the full agent overlay for
  keys within the allowed set.
- Cache key: `(agent_name, str(config_path), frozenset(allowed_overlay_keys))`
- Default `allowed_overlay_keys`: `None` → `{"model", "runtime"}`
- Secret validation on full merged result

## Why Both Merged and Source-Preserving Loaders Are Needed

`load_agent_config()` returns a cached merged dict. If harness reads domain
sections from it, it cannot prove they came from the agent overlay vs global
config. `load_agent_overlay()` provides that guarantee. The harness calls both:

```python
# Plane 1: merged LLM config (global + agent overlay)
agent_config = load_agent_config("agent-harness")

# Plane 2: raw agent overlay (source-preserved)
overlay = load_agent_overlay("agent-harness")
domain_sections = {k: overlay[k] for k in overlay if k in HARNESS_DOMAIN_KEYS}
```

The `allowed_overlay_keys` on `load_agent_config()` ensures the merged loader
does not reject the domain keys that exist in the agent overlay file. Without
this parameter, `load_agent_config()` would raise `ConfigError` on the domain
keys before the harness can process them.

## HarnessConfig.load() Composition

```python
HARNESS_DOMAIN_KEYS = frozenset({
    "gate", "validation", "persistence",
    "budget", "retention", "authority",
})

@classmethod
def load(cls, config_path: Path | None = None) -> HarnessConfig:
    load_tdt_env()

    # Plane 1: merged LLM config (allows domain keys to pass through overlay)
    agent_config = load_agent_config("agent-harness",
        allowed_overlay_keys={"model", "runtime"} | HARNESS_DOMAIN_KEYS)

    # Plane 2: raw overlay for domain sections only
    overlay = load_agent_overlay("agent-harness", config_path=config_path,
        allowed_keys={"model", "runtime"} | HARNESS_DOMAIN_KEYS)
    domain_sections = {k: overlay[k] for k in overlay if k in HARNESS_DOMAIN_KEYS}

    # Build runtime from merged config
    runtime_data = dict(agent_config.get("runtime", {}))
    model_data = agent_config.get("model", {})
    if isinstance(model_data, dict) and "primary" in model_data:
        runtime_data.setdefault("model", model_data["primary"])

    env_overrides = _load_env_overrides()
    for key in _RUNTIME_ENV_KEYS:
        if key in env_overrides:
            runtime_data[key] = env_overrides.pop(key)

    runtime = ConsumerRuntimeProfile(
        consumer_name="agent-harness",
        consumer_version="0.1.0",
        settings=load_settings(),
        **{k: runtime_data[k] for k in _RUNTIME_ENV_KEYS if k in runtime_data},
    )

    # Domain sections sourced ONLY from agent overlay
    return cls(runtime=runtime, **domain_sections)
```

## Precedence

**Model and runtime** (via `load_agent_config()` merged result):
1. Process env (`HARNESS_*`)
2. Agent YAML (`~/.tdt/agents/agent-harness.yaml`)
3. Global config (`~/.tdt/config.yaml`)
4. Field defaults

**Harness domain sections** (from `load_agent_overlay()` of agent file):
1. Agent YAML
2. `HarnessConfig` field defaults

Global config NEVER contributes domain sections.

## Explicit config_path Contract

- `config_path=None`: standard `~/.tdt/agents/agent-harness.yaml`
- `config_path=<path>`: explicit file as agent overlay AND domain source
- Legacy `$TDT_HOME/harness/config.yaml`: never auto-read
- Explicit config MUST use top-level sections. Legacy `harness:` wrapper rejected
  with `ConfigMigrationError`.

## Cache Isolation

- `load_agent_config()`: cached. Key includes `(agent_name, config_path, allowed_overlay_keys)`.
  Strict call cannot return permissive results.
- `load_agent_overlay()`: uncached. Fresh dict per call.
- `HarnessConfig.load()`: must never `.pop()` from cached dicts.

## Secret Validation

All three loaders enforce the same rules:
- Literal `secret`/`token`/`api_key`/`dsn`/`credential` values rejected
- `api_key_env` under `providers.<name>` with valid `[A-Z][A-Z0-9_]*` accepted
- No weakening for domain sections

Negative scenarios:
- Unknown top-level key outside allowed set → `ConfigError`
- Literal secret value → `ConfigError`
- `api_key_env` in `gate`/`runtime` → `ConfigError`
- Malformed YAML → `ConfigError`
