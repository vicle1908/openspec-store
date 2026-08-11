# Proposal: llm-config-harness-followup

## Why

Phase 4 of `llm-config-standardization` (agent-harness config migration) was never properly implemented or designed. The archived change was created prematurely with stale task tracking.

The root cause is an architectural mismatch:

- `tdt_core.load_agent_config()` intentionally limits agent overlays to `model` and `runtime` sections — correct for LLM config
- `HarnessConfig` needs seven domain sections: `runtime`, `gate`, `validation`, `persistence`, `budget`, `retention`, `authority`
- The current committed `agent-harness` code still uses the legacy `$TDT_HOME/harness/config.yaml` path via `_load_yaml_section()`
- The on-disk `~/.tdt/agents/agent-harness.yaml` only contains `runtime`, which is insufficient

This corrective change resolves the mismatch by introducing a harness-specific composition layer while preserving the `load_agent_config()` contract.

## What Changes

### Shared Secure YAML Primitive (tdt-core)

Add `load_config_mapping(path: Path) -> dict[str, Any]` — a reusable YAML loader that provides:
- Empty YAML → `{}`
- Malformed YAML → `ConfigError`
- Non-mapping YAML → `ConfigError`
- Secret-shaped value rejection (using existing `classify_secret_key()`)
- `api_key_env` path-aware metadata handling

`load_agent_config()` refactors to use this primitive internally.

### Harness-Specific Composition Layer (agent-harness)

`HarnessConfig.load()` reads two sources:
1. `load_agent_config("agent-harness")` for `model` + `runtime` (standard LLM chain)
2. `load_config_mapping(~/.tdt/agents/agent-harness.yaml)` for harness domain sections (`gate`, `persistence`, `authority`, etc.)

Harness domain sections live in `~/.tdt/agents/agent-harness.yaml` alongside `model`/`runtime`. The harness loader reads the full file and extracts only the owned keys, without going through `load_agent_config()` merge semantics.

### Config-Path Compatibility

- `config_path=None`: use standardized agent location (default)
- Explicit `config_path`: read explicit file as migration/test override
- Legacy default `$TDT_HOME/harness/config.yaml`: never read automatically

### No Live Mutation During Planning

No credential rotation, no service restart, no `~/.tdt/agents/` file modification during planning phase.

## Capabilities Affected

- `tdt-core/config-resolution` — new `load_config_mapping()` primitive
- `agent-harness/config-loading` — refactored `HarnessConfig.load()`

## Impact

- **Breaking**: `_load_yaml_section()` removed from agent-harness
- **Breaking**: `$TDT_HOME/harness/config.yaml` legacy path no longer read automatically
- **Non-breaking**: explicit `config_path` parameter preserved
- **Non-breaking**: all harness domain defaults unchanged

## Verification

- Unit tests for `load_config_mapping()` YAML/security edge cases
- Harness config tests with isolated `TDT_HOME`
- Real LLM smoke test after structural tests pass
- OpenSpec validation
