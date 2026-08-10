# Design: Cockpit Luna Max-Effort MoA Alignment

## Ground Truth Before Change

Hermes Agent v0.20.0 is installed. The primary route is `moa:default`. Direct inference checks for `cockpit:gpt-5.6-luna`, `shopapikey:fable-5`, and `giaoduc:Advance` all returned HTTP 200 in the pre-change verification.

Current drift:

| Preset | Current cockpit slots | Other drift |
|---|---|---|
| default | reference `gpt-5.6-luna` high | third `Advance` reference; `fable-5` aggregator |
| deep | reference + aggregator `gpt-5.6-sol` | cockpit reference is xhigh rather than max |
| fast | reference `gpt-5.6-sol` medium | — |

The canonical spec currently describes an older `gpt-5.6-sol` topology. The maintained runbook also contains that stale model and effort language.

## Target Topology

| Preset | References | Aggregator | Existing tuning retained |
|---|---|---|---|
| default | `shopapikey:fable-5` high; `cockpit:gpt-5.6-luna` max | `cockpit:gpt-5.6-luna` max | ref cap 600; output 4096; temperatures 0.6/0.4; `user_turn` |
| deep | `shopapikey:fable-5` xhigh; `cockpit:gpt-5.6-luna` max; `giaoduc:Advance` high | `cockpit:gpt-5.6-luna` max | ref cap 800; output 8192; temperatures 0.6/0.3; `every_n:3` |
| fast | `cockpit:gpt-5.6-luna` max | `shopapikey:fable-5` high | ref cap 300; output 4096; temperatures 0.6/0.4; `user_turn` |

`moa.privacy_filter` becomes `display`. Existing per-preset `degraded_reference_policy: loud`, `enabled: true`, and provider-level one-million-token context declarations remain unchanged.

## Why This Shape

- Luna replaces Sol in every cockpit slot as explicitly requested.
- `max` is applied only to cockpit slots; `fable-5` and `Advance` retain their existing role-specific efforts.
- Default now matches the intended canonical two-advisor topology and makes cockpit Luna the acting tool-capable aggregator.
- Deep retains provider diversity while using Luna consistently for the strongest reference and aggregation path.
- Fast remains structurally fast by retaining one advisor and a `fable-5` aggregator; the Luna advisor is max-effort as requested, so it is quality-focused rather than the lowest-cost option.

## Code Alignment

No Hermes source patch is needed. Existing installed code was inspected before authoring:

- `runtime_provider.py` resolves provider `moa` to `moa://local`.
- `agent_init.py` builds the MoA facade for `provider == "moa"`.
- `agent/chat_completion_helpers.py` routes calls through the in-process MoA client.
- Auxiliary tasks unwrap the preset to its real aggregator.

The implementation change is profile configuration plus contract/docs synchronization; the code path already supports the target.

## Validation Gates

1. Backup and SHA-256 verification.
2. Atomic YAML update with assertions for exact topology and no stale `gpt-5.6-sol` cockpit slots.
3. `hermes config check`, `hermes config get`, `hermes moa list`, and fallback inspection.
4. Direct inference for all providers, including cockpit Luna.
5. Fresh `moa:default` session requiring a harmless terminal call; verify aggregator call, tool result, and post-tool final response through the session store.
6. Stale-pattern sweep across active config, current spec, runbook, and change artifacts; archived history is classified, not rewritten.
7. Focused strict OpenSpec validation, archive, strict main-spec validation, and store health.

## Rollback

Restore the timestamped local backup if runtime or smoke verification fails. The backup is not committed. After rollback, verify the original model/provider selections, then report the failed gate rather than claiming completion.
