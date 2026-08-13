# Design: Reconcile Hermes MoA Specialist Topology

## Architecture

### Current State (verified from live config)

```yaml
moa:
  default_preset: default
  privacy_filter: ''
  presets:
    default:
      reference_models:
        - {provider: giaoduc, model: Advance, reasoning_effort: high, enabled: true}
        - {provider: cockpit, model: gpt-5.6-sol, reasoning_effort: high, enabled: true}
      aggregator: {provider: shopapikey, model: fable-5, reasoning_effort: xhigh}
      max_tokens: 8192
      reference_max_tokens: 1000
      reference_temperature: 0.6
      aggregator_temperature: 0.4
      fanout: every_n:3
      degraded_reference_policy: loud
      enabled: true
    deep:
      reference_models:
        - {provider: shopapikey, model: fable-5, reasoning_effort: high, enabled: true}
        - {provider: cockpit, model: gpt-5.6-sol, reasoning_effort: high, enabled: true}
        - {provider: giaoduc, model: Advance, reasoning_effort: high, enabled: true}
      aggregator: {provider: giaoduc, model: Advance, reasoning_effort: max}
      max_tokens: 8192
      reference_max_tokens: 800
      reference_temperature: 0.6
      aggregator_temperature: 0.3
      fanout: per_iteration
      degraded_reference_policy: loud
      enabled: true
    fast:
      reference_models:
        - {provider: cockpit, model: gpt-5.6-sol, reasoning_effort: high, enabled: true}
      aggregator: {provider: shopapikey, model: fable-5, reasoning_effort: high}
      max_tokens: 4096
      reference_max_tokens: 300
      reference_temperature: 0.6
      aggregator_temperature: 0.4
      fanout: user_turn
      degraded_reference_policy: loud
      enabled: true
```

### Previously Stale Canonical State

The canonical spec described:
- `cockpit:gpt-5.6-luna` as aggregator and reference across all presets
- `shopapikey:fable-5` as default aggregator at `max` effort
- `reference_max_tokens: 600` on default (actual: 1000)
- `max_tokens: 4096` on default (actual: 8192)
- `fanout: user_turn` on default (actual: `every_n:3`)
- A separate "Active cockpit Luna topology" requirement that no cockpit MoA slot should use Sol

### Design Decisions

1. **Specialist role separation** — MoA presets use `gpt-5.6-sol` for cockpit-backed references, while the direct cockpit provider default and fallback route use `gpt-5.6-luna`. These are independent configuration surfaces, not drift. The archived `2026-08-10-assign-moa-aggregator-specialists` change documents the aggregator assignment as an explicit operator decision.

2. **Default aggregator is `shopapikey:fable-5`** — Uses the most cost-efficient path for the model that runs with full tool schemas. Advisor insights from Advance and Sol boost quality without increasing aggregator cost.

3. **Deep aggregator is `giaoduc:Advance`** — When maximum quality is needed, the aggregator itself is the strongest available model. Three advisors feed it diverse perspectives at high effort.

4. **`fanout: every_n:3` on default** — Refreshes advisor context every third tool iteration rather than once per turn, providing more current reasoning context for longer interactions.

5. **`privacy_filter: ''`** — The literal empty value is preserved as configured. Runtime interpretation follows Hermes defaults.

6. **No per-slot `context_length`** — Context window ownership belongs to provider and model configuration. All three providers declare `context_length: 1000000` at the provider level.

### Cost Implications

| Preset | Advisor calls per turn | Est. cost multiplier vs single model |
|--------|----------------------|--------------------------------------|
| default | 2 (Advance + Sol) + 1 aggregator | ~2.5x |
| deep | 3 (all models) + 1 aggregator | ~4x |
| fast | 1 (Sol) + 1 aggregator | ~1.5x |
