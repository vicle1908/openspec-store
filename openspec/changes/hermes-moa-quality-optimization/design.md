# Design: Hermes MoA Quality Optimization

## Architecture

### Current State

```yaml
moa:
  # Legacy flat-level (deprecated, confusing)
  aggregator: {model: Advance, provider: giaoduc}
  reference_models: [fable-5/shopapikey, Advance/giaoduc]
  degraded_reference_policy: loud
  enabled: true
  fanout: user_turn
  max_tokens: 4096
  presets:
    default:
      # Same models as flat-level — no diversity
      reference_models: [fable-5/shopapikey, Advance/giaoduc]
      aggregator: Advance/giaoduc
```

**Problems:**
- Legacy flat block duplicates preset config
- Advisor models (fable-5, Advance) are the same model set as the aggregator (Advance) — no diversity
- cockpit gpt-5.6-sol not used despite being available
- No reasoning effort per-slot tuning

### Target State

```yaml
moa:
  default_preset: default
  privacy_filter: display
  presets:
    default:
      reference_models:
        - {provider: shopapikey, model: fable-5, reasoning_effort: high, enabled: true}
        - {provider: cockpit, model: gpt-5.6-sol, reasoning_effort: high, enabled: true}
      aggregator:
        provider: giaoduc
        model: Advance
        reasoning_effort: xhigh
      reference_max_tokens: 600
      fanout: user_turn
      enabled: true
    deep:
      reference_models:
        - {provider: shopapikey, model: fable-5, reasoning_effort: xhigh, enabled: true}
        - {provider: cockpit, model: gpt-5.6-sol, reasoning_effort: xhigh, enabled: true}
        - {provider: giaoduc, model: Advance, reasoning_effort: high, enabled: true}
      aggregator:
        provider: shopapikey
        model: fable-5
        reasoning_effort: max
      fanout: every_n:3
      enabled: true
    fast:
      reference_models:
        - {provider: cockpit, model: gpt-5.6-sol, reasoning_effort: medium, enabled: true}
      aggregator:
        provider: shopapikey
        model: fable-5
        reasoning_effort: high
      reference_max_tokens: 300
      fanout: user_turn
      enabled: true
```

### Design Decisions

1. **3-model diversity in default** — fable-5 (reasoning-focused small model), gpt-5.6-sol (frontier reasoning), and Advance as aggregator. Each brings a different architecture/perspective.

2. **gpt-5.6-sol as advisor in default** — cockpit's strongest model provides frontier analysis. Using it as advisor (not aggregator) keeps cost controlled while leveraging its reasoning quality.

3. **Advance as aggregator for default** — uses the most cost-efficient path for the model that runs with full tool schemas. Advisor insights boost its quality without increasing aggregator cost.

4. **fable-5 as aggregator for deep** — when maximum quality is needed, the aggregator itself is a reasoning model. Three advisors feed it diverse perspectives at xhigh/max effort.

5. **reference_max_tokens: 600** — concise advisor output cuts per-turn latency. The aggregator only needs the gist of each advisor's judgment.

6. **fanout cadence** — `user_turn` for default/fast (cheapest), `every_n:3` for deep (refreshes every 3 tool iterations for long-running tasks).

7. **privacy_filter: display** — redacts emails/phones from advisor outputs in UI without affecting aggregator input quality.

### Cost Implications

| Preset | Advisor calls per turn | Est. cost multiplier vs single model |
|--------|----------------------|--------------------------------------|
| default | 2 (fable-5 + gpt-5.6-sol) + 1 aggregator | ~2.5x |
| deep | 3 (all models) + 1 aggregator | ~4x |
| fast | 1 (gpt-5.6-sol) + 1 aggregator | ~1.5x |

### Trade-offs

- **3 advisors in deep preset** increases per-turn latency by ~30-50% vs 2 advisors, but provides the most diverse perspectives
- **Advance as aggregator** is cost-efficient but lower quality than using a frontier model — compensated by advisor insights
- **reference_max_tokens: 600** may truncate verbose advisor output — acceptable since aggregator needs the gist, not essays
