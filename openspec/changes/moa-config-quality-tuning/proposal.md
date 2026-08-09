# Proposal: MoA Config Quality Tuning

## Why

Research against official Hermes docs and HermesBench benchmarks reveals 6 gaps in our current MoA config:

1. **Aggregator too weak** — official benchmark proves aggregator strength is the #1 quality driver. Opus-4.8 aggregator beats both models alone by ~6 points. Our `Advance` aggregator is mid-tier.
2. **Missing `max_tokens`** — official example sets `4096`. Without it, aggregator output may be truncated by provider defaults.
3. **No temperature control** — original MoA used `reference_temperature: 0.6`, `aggregator_temperature: 0.4`. Omitting these means random provider defaults.
4. **Unsupported `context_length` on preset slots** — not in official docs. It's a provider-level setting (already set to 1M for all providers). May be silently ignored.
5. **`reference_max_tokens: uncapped` on deep preset** — advisors write unbounded output, slowing every turn.
6. **No `max_tokens` on deep preset** — complex tasks need more output room.

### Provider Health (verified this session)

| Provider | Model | Status |
|----------|-------|--------|
| cockpit | fable-5.6-sol | ✅ Live |
| shopapikey | fable-5 | ✅ Live |
| giaoduc | Advance | ✅ Live |

## What Changes

### 1. Upgrade default/deep aggregator to fable-5.6-sol
- Biggest quality gain — cockpit's strongest reasoning model as aggregator
- Keep Advance as reference in deep preset (diversity)
- Keep fable-5 as aggregator in fast (speed-optimized)

### 2. Add `max_tokens` to all presets
- default: 4096 (official recommendation)
- deep: 8192 (complex tasks need more room)
- fast: 4096

### 3. Add temperature control
- reference_temperature: 0.6 (reduces advisor randomness)
- aggregator_temperature: 0.4 (focused aggregation)
- deep aggregator: 0.3 (maximum precision for hard tasks)

### 4. Remove unsupported `context_length` from preset slots
- Provider-level `context_length: 1000000` already set for all 3 providers
- Preset-level `context_length` is not in official docs — remove

### 5. Add `reference_max_tokens` to deep preset
- Cap at 800 (concise advice, faster turns)

## Goals
- Aggregator quality matches official benchmark pattern
- All presets have explicit output limits and temperature
- Config matches official docs format exactly
- Remove unsupported fields

## Non-Goals
- Adding new providers
- Changing delegation or compression config
- Modifying cron job settings

## Affected Boundaries
- `~/.hermes/config.yaml` — moa section only

## Compatibility
- All presets use standard MoA config format
- `hermes moa configure` and `hermes moa list` continue to work
- No behavioral change for delegation (already uses moa:default)

## Rollback
- Individual presets disabled with `enabled: false`
- Full rollback: restore config.yaml from backup
