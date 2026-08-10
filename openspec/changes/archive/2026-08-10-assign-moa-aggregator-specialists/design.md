# Design: Specialist MoA Aggregator Assignment

## Current and Target

| Preset | Current aggregator | Target aggregator | Effort | Other settings |
|---|---|---|---|---|
| `default` | `cockpit:gpt-5.6-luna` | `shopapikey:fable-5` | `max` | temperature 0.4; output 4096; `user_turn` |
| `deep` | `cockpit:gpt-5.6-luna` | `giaoduc:Advance` | `max` | temperature 0.3; output 8192; `every_n:3` |
| `fast` | `shopapikey:fable-5` | unchanged | `high` | unchanged |

References remain unchanged:

- `default`: `shopapikey:fable-5` high and `cockpit:gpt-5.6-luna` max.
- `deep`: `shopapikey:fable-5` xhigh, `cockpit:gpt-5.6-luna` max, and `giaoduc:Advance` high.
- `fast`: cockpit Luna max.

## Research Basis

1. **Official Hermes MoA guide**: references run first without tools; the aggregator receives their private outputs, owns the normal Hermes tool schema, emits the actual response, and continues after tool results. This makes the requested model assignment a change to the acting/tool-capable role, not to advisor fan-out.
   Source: <https://hermes-agent.nousresearch.com/docs/user-guide/features/mixture-of-agents>
2. **Hermes official benchmark section**: the documented benchmark example uses a dedicated aggregator over a reference model and reports a higher MoA score than either listed standalone component. This supports separating roles but does not rank the private providers used here.
3. **Wang et al., “Mixture-of-Agents Enhances Large Language Model Capabilities”**: the paper reports that model selection should consider performance and output diversity; its tables evaluate different models as aggregators and proposers separately. Source: <https://arxiv.org/html/2406.04692v1>
4. **Live provider evidence**: fresh direct inference for cockpit Luna, shopapikey fable-5, and giaoduc Advance all returned HTTP 200 with usable choices. This proves availability, not comparative answer quality.

## Implementation Boundary

Hermes source already resolves `provider: moa` to the in-process MoA facade. The aggregator field is configuration data consumed by that existing path. No code patch is required.

## Safety and Verification

- Backup `~/.hermes/config.yaml` and verify SHA-256.
- Change only `presets.default.aggregator` and `presets.deep.aggregator` through the safe complex-MoA configuration path; detect and reject string-shaped `moa` data.
- Assert all non-aggregator settings remain unchanged.
- Run `hermes moa list`, direct inference for all models, and a fresh `moa:default` smoke session requiring a terminal call.
- Update docs/specs only after the live target is verified.
- Archive and integrate only owned OpenSpec/docs paths.

## Rollback

Restore the backup atomically if YAML shape, provider health, or smoke evidence fails. Alternatively, set both changed aggregator pairs back to cockpit Luna at max and rerun all validation gates.
