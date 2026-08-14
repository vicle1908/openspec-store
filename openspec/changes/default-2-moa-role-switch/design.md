# Design: `default-2` MoA Role-Switch Preset

## Current Topology

The live profile uses `moa:default` as the global primary route:

| Preset | References | Aggregator | Tuning |
|---|---|---|---|
| `default` | `giaoduc:Advance` high; `cockpit:gpt-5.6-sol` high | `shopapikey:fable-5` xhigh | output 8192; refs 1000; temps 0.6/0.4; `every_n:3` |
| `deep` | `shopapikey:fable-5` high; `cockpit:gpt-5.6-sol` high; `giaoduc:Advance` high | `giaoduc:Advance` max | output 8192; refs 800; temps 0.6/0.3; `per_iteration` |
| `fast` | `cockpit:gpt-5.6-sol` high | `shopapikey:fable-5` high | output 4096; refs 300; temps 0.6/0.4; `user_turn` |

The MoA root is normalized: only `default_preset`, `privacy_filter`, and `presets` exist at the YAML root. Provider/model context is owned by provider configuration at one million tokens.

## Target Topology

Add only this preset:

```yaml
default-2:
  reference_models:
    - provider: shopapikey
      model: fable-5
      reasoning_effort: high
      enabled: true
    - provider: cockpit
      model: gpt-5.6-sol
      reasoning_effort: high
      enabled: true
  aggregator:
    provider: giaoduc
    model: Advance
    reasoning_effort: xhigh
  max_tokens: 8192
  reference_max_tokens: 1000
  reference_temperature: 0.6
  aggregator_temperature: 0.4
  fanout: every_n:3
  degraded_reference_policy: loud
  enabled: true
```

## Role Assignment

`default-2` reverses only the shopapikey/giaoduc roles relative to `default`:

- Current `default`: `giaoduc:Advance` is an advisor; `shopapikey:fable-5` aggregates.
- New `default-2`: `shopapikey:fable-5` is an advisor; `giaoduc:Advance` aggregates.
- `cockpit:gpt-5.6-sol` remains an advisor in both routes.

The aggregator is the acting model: it receives private reference outputs, the normal Hermes tool schema, tool results, and emits the user-visible continuation. Direct provider health proves reachability and response shape only; it does not establish comparative quality for private endpoints.

## Preservation Matrix

| Surface | Required state |
|---|---|
| `model.provider` | `moa` unchanged |
| `model.default` | `default` unchanged |
| Existing `default` | byte-for-byte semantic value unchanged |
| Existing `deep` | unchanged |
| Existing `fast` | unchanged |
| `providers.cockpit.model` | `gpt-5.6-luna` unchanged |
| `moa.privacy_filter` | literal empty string unchanged |
| Provider contexts | provider/model-owned `1000000` unchanged |
| Fallback chain | shopapikey → giaoduc → cockpit Luna unchanged |
| Delegation/compression | unchanged |
| Legacy flat MoA keys | remain absent |

## Verification Design

1. Capture a timestamped backup and SHA-256.
2. Re-read the live baseline immediately before mutation.
3. Atomically add `default-2` in memory and replace the config file only after shape assertions pass.
4. Assert existing preset semantic hashes are unchanged.
5. Run `hermes config check`, `hermes config get moa`, and `hermes moa list`.
6. Start a fresh session explicitly with `--provider moa -m default-2` and require a harmless terminal call.
7. Query the session store to verify the assistant terminal call, tool result, and post-tool response.
8. Sweep maintained spec and runbook surfaces; classify archived historical references separately.

## Rollback Design

The preferred rollback is restoring the verified backup. A narrower rollback deletes only `moa.presets.default-2` while preserving all existing presets and global routing. Either path requires the same structural and runtime checks before recovery is declared.
