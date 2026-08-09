# Design: Synchronize Hermes MoA Configuration, Specs, and Docs

## Context

Hermes Agent v0.20.0 runs `model.provider: moa` with `model.default: default`. The live configuration has three named presets and three real provider/model backends. The previous config changes were archived with `skip_specs: true`, so no canonical capability describes the current contract and no maintained runbook explains operation or verification.

Ground-truth inspection also found:

- `hermes moa list` reports `Active in config: (off)` because `moa.active_preset` is empty; source inspection shows this field is a separate optional config-level override and does not negate `model.provider: moa`.
- the MoA resolver returns the virtual runtime `moa://local` with a placeholder credential, so stale direct-provider `model.base_url` and `model.key_env` fields do not participate in MoA resolution;
- the first fallback entry duplicates primary `moa:default`; the backend-identity probe returns `should_skip_candidate(...) == True`, so it cannot provide recovery and only adds noise;
- provider/model context lengths are already declared as `1000000`; MoA slots correctly omit `context_length`.

## Ownership

| Surface | Owner | Change |
|---|---|---|
| `~/.hermes/config.yaml` | active Hermes default profile | remove stale direct-model metadata; deduplicate fallback chain |
| `openspec/specs/hermes-moa-configuration/spec.md` | shared OpenSpec store | new canonical runtime contract via delta sync |
| `docs/governance/hermes-moa-configuration.md` | shared OpenSpec store | maintained operational runbook |
| Hermes Agent skill references | active Hermes profile | add concise MoA routing and config guidance |
| Hermes Agent source | upstream installation | read-only evidence; no edits |

## Canonical Runtime Topology

### Default preset

- references: `shopapikey:fable-5` at `high`, `cockpit:gpt-5.6-sol` at `high`
- aggregator: `cockpit:gpt-5.6-sol` at `xhigh`
- reference cap 600, output cap 4096, temperatures 0.6/0.4, cadence `user_turn`

### Deep preset

- references: `shopapikey:fable-5` at `xhigh`, `cockpit:gpt-5.6-sol` at `xhigh`, `giaoduc:Advance` at `high`
- aggregator: `cockpit:gpt-5.6-sol` at `max`
- reference cap 800, output cap 8192, temperatures 0.6/0.3, cadence `every_n:3`

### Fast preset

- reference: `cockpit:gpt-5.6-sol` at `medium`
- aggregator: `shopapikey:fable-5` at `high`
- reference cap 300, output cap 4096, temperatures 0.6/0.4, cadence `user_turn`

## Configuration Cleanup

### Stale model metadata

`model.base_url` and `model.key_env` describe the prior Antigravity direct provider. They are removed because the MoA resolver constructs its own virtual runtime and each real slot resolves from `providers.<name>`. Retaining stale values is misleading and increases the chance that a later direct-provider switch inherits the wrong endpoint.

### Fallback chain

The effective chain becomes:

1. `shopapikey:fable-5` (`xhigh`)
2. `giaoduc:Advance` (`xhigh`)
3. `cockpit:gpt-5.6-luna` (`max`)

The removed `moa:default` entry is identical to the primary route. Hermes compares provider/model/backend identity and skips it, so removal does not reduce redundancy.

## Documentation Design

The runbook records:

- advisor/aggregator execution semantics and tool-call ownership;
- exact presets and intended use;
- default vs `active_preset` semantics;
- one-million-token context ownership at provider/model level;
- partial-reference degradation, privacy behavior, and prompt caching;
- selection, inspection, health-check, smoke-test, and rollback commands;
- sanitized evidence rules.

Skill references remain concise and link operators to official docs and the canonical runbook rather than duplicating every preset field.

## Validation Matrix

| Gate | Evidence |
|---|---|
| YAML/schema | `yaml.safe_load`, exact assertions, `hermes config check` |
| normalized config | `hermes config get model`, `hermes config get moa`, `hermes moa list` |
| provider context | exact `providers.*.context_length == 1000000`; no MoA-slot context fields |
| direct backends | inference against cockpit, shopapikey, and giaoduc without logging secrets |
| real MoA | fresh `moa:default` session requests a terminal tool, transcript shows aggregator tool call and post-tool continuation |
| docs/specs | stale-pattern scan with archived-history classification |
| OpenSpec | focused strict validation, `openspec show --json`, strict full-store validation, store doctor |

## Security and Evidence

No API keys, tokens, credential values, raw authorization headers, or complete config dumps are committed. Evidence records only provider/model names, status, structural assertions, timestamps, and session identifiers required to reproduce the check.

## Rollback

A local timestamped backup of `config.yaml` is created before mutation. Rollback restores only the removed keys/entry or the complete local backup, then reruns config and MoA validation. Specs and docs can be reverted by reverting the archive commit; no application or provider state is changed.
