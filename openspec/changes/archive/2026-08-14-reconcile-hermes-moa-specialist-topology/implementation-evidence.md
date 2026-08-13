# Implementation Evidence: Reconcile Hermes MoA Specialist Topology

Evidence captured on 2026-08-14. Credentials, authorization headers, and secret values are excluded.

## Config Cleanup

### Backup

- Backup path: `~/.hermes/backups/config-before-moa-legacy-cleanup-20260814-061300.yaml`
- SHA-256 at creation: `961e11b878cb11604697598b9df4b661e496885b71307787789898ccb4e14a91`
- SHA-256 at verification: `961e11b878cb11604697598b9df4b661e496885b71307787789898ccb4e14a91` — match confirmed.

### Legacy keys removed

Nine flat-level `moa.*` keys were unset via `hermes config unset`:

1. `moa.reference_models`
2. `moa.aggregator`
3. `moa.reference_temperature`
4. `moa.aggregator_temperature`
5. `moa.degraded_reference_policy`
6. `moa.max_tokens`
7. `moa.reference_max_tokens`
8. `moa.fanout`
9. `moa.enabled`

### Post-cleanup root keys

After removal, `moa` contains exactly: `default_preset`, `privacy_filter`, `presets`.

### Preset integrity

Preset SHA-256 before and after: `003c0c8ff49a14c9d7e6663a1781acc53f41f49b29ac5c9f7054b5f5b116fcf6` — unchanged.

### Semantic comparison

A full recursive comparison of the backup (with legacy keys removed in-memory) against the live config returned zero differences.

## Live Config Topology (parsed from config, verified via CLI)

```
model.provider: moa
model.default: default
moa.default_preset: default
moa.privacy_filter: '' (literal empty string)
moa.presets: [deep, default, fast]

default:
  refs: giaoduc:Advance(high), cockpit:gpt-5.6-sol(high)
  agg: shopapikey:fable-5(xhigh)
  tokens: 8192/1000, temps: 0.6/0.4, fanout: every_n:3
  degraded_reference_policy: loud, enabled: true

deep:
  refs: shopapikey:fable-5(high), cockpit:gpt-5.6-sol(high), giaoduc:Advance(high)
  agg: giaoduc:Advance(max)
  tokens: 8192/800, temps: 0.6/0.3, fanout: per_iteration
  degraded_reference_policy: loud, enabled: true

fast:
  refs: cockpit:gpt-5.6-sol(high)
  agg: shopapikey:fable-5(high)
  tokens: 4096/300, temps: 0.6/0.4, fanout: user_turn
  degraded_reference_policy: loud, enabled: true
```

## CLI Verification (performed during this task)

- `hermes config check`: PASSED (schema v34, no errors)
- `hermes config get moa`: Shows clean output with only `default_preset`, `presets`, `privacy_filter` at root
- `hermes moa list`: Shows three presets (default, deep, fast) with correct models and efforts

## Provider Context (parsed from config)

- `providers.cockpit.model`: `gpt-5.6-luna` (provider default, independent of MoA slots)
- `providers.cockpit.context_length`: `1000000`
- `providers.shopapikey.model`: `fable-5`
- `providers.shopapikey.context_length`: `1000000`
- `providers.giaoduc.model`: `Advance`
- `providers.giaoduc.context_length`: `1000000`
- No MoA slot contains `context_length`.

## Fallback Chain (parsed from config)

1. `shopapikey:fable-5` (`xhigh`)
2. `giaoduc:Advance` (`xhigh`)
3. `cockpit:gpt-5.6-luna` (`max`)

## Provider Health (historical, from archived changes)

Provider inference verification was performed during the archived `2026-08-10-align-moa-cockpit-luna-max-effort` change. No fresh direct inference was performed during this reconciliation task.

## OpenSpec Change

- Branch: `reconcile-hermes-moa-specialist-topology`
- Worktree: `/Users/androidteam/Developer/openspec-moa-specialist-reconcile`
- Change directory: `openspec/changes/reconcile-hermes-moa-specialist-topology/`
- Delta spec: `specs/hermes-moa-configuration/spec.md`

## Stale-Reference Classification

- Active `~/.hermes/config.yaml` contains `gpt-5.6-sol` in all MoA preset slots. This is the intentional specialist topology.
- `providers.cockpit.model` is `gpt-5.6-luna` for direct routes and fallback.
- Archived historical changes (`2026-08-09-hermes-moa-quality-optimization`, `2026-08-10-align-moa-cockpit-luna-max-effort`) are preserved unmodified and classify as historical evidence.
- Generic model-resolution specs (`agent-core-model-resolution`) that mention Sol/Luna as fixtures are unrelated to the Hermes MoA profile and are not rewritten.
