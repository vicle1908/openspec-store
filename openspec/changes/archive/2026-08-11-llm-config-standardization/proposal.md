# Proposal: llm-config-standardization

## Why

Three separate OpenSpec changes address overlapping LLM config concerns:

1. `standardize-agent-llm-config-loading` — per-agent config in tdt-core, model factory refactor
2. `agent-core-model-resolution-hardening` — streaming + fallback chain tests
3. `agent-docs-sync-config-and-report-hardening` — config precedence + report semantics tests

These have significant overlap:
- Fallback chain tests belong with the model factory refactor
- Config precedence tests belong with the config resolution work
- All three converge on the same architectural goal: centralized, per-agent config resolution

Consolidating into a single change eliminates redundant planning, ensures consistent implementation order, and provides a single verification gate.

## What Changes

### Phase 1: tdt-core — Agent Config Resolution
Add `load_agent_config(agent_name)` to tdt-core. This is the foundation: reads `~/.tdt/config.yaml` as global base, deep-merges `model.*` from `~/.tdt/agents/{agent_name}.yaml`, shallow-overrides `runtime.*` fields.

### Phase 2: agent-core — Model Factory Refactor + Tests
Refactor model factory to accept config params (providers, model_config, fallback_ids) instead of reading YAML directly. Add streaming model tests and fallback chain tests.

### Phase 3: agent-docs-sync — Config Alignment + Tests
Remove hardcoded defaults, use `load_agent_config()` for model resolution, add config precedence tests and report semantics tests.

### Phase 4: agent-harness — Remove Old Config Path
Migrate harness config from `$TDT_HOME/harness/config.yaml` to `~/.tdt/agents/agent-harness.yaml`.

### Phase 5: Documentation and Validation
Update docs across all three repos, validate specs, run full test suites.

## Capabilities Affected

- `tdt-core/config-resolution` — new capability
- `agent-core/model-factory` — refactored
- `agent-docs-sync/config-loading` — refactored
- `agent-harness/config-loading` — refactored

## Impact

- **Breaking**: agent-docs-sync repo-local `runtime.model` field will be rejected (migration to `~/.tdt/agents/`)
- **Breaking**: agent-harness old config path `$TDT_HOME/harness/config.yaml` will be ignored
- **Non-breaking**: all consumers get per-agent config override capability
- **Non-breaking**: model factory backward-compatible (optional params default to current behavior)

## Verification

- Unit tests across all three repos
- Live LLM test on agent-core with `docs-sync sync --full`
- OpenSpec validation
