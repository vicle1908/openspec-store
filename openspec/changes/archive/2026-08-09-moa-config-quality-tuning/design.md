# Design: MoA Config Quality Tuning

## Architecture

### Current → Target

| Preset | Current Aggregator | Target Aggregator | Current max_tokens | Target max_tokens |
|--------|-------------------|-------------------|-------------------|-------------------|
| default | Advance (giaoduc) | fable-5.6-sol (cockpit) | none | 4096 |
| deep | fable-5 (shopapikey) | fable-5.6-sol (cockpit) | none | 8192 |
| fast | fable-5 (shopapikey) | fable-5 (shopapikey) | none | 4096 |

### Temperature Settings

| Preset | ref_temp | agg_temp | Rationale |
|--------|----------|----------|-----------|
| default | 0.6 | 0.4 | Balanced — official recommendation |
| deep | 0.6 | 0.3 | Lower aggregator temp for precision on hard tasks |
| fast | 0.6 | 0.4 | Same as default |

### Field Changes

| Field | Action | Rationale |
|-------|--------|-----------|
| `context_length` (all slots) | **Remove** | Not in official docs, provider-level only |
| `max_tokens` (all presets) | **Add** | Official example uses 4096 |
| `reference_temperature` (all presets) | **Add** | Original MoA used 0.6 |
| `aggregator_temperature` (all presets) | **Add** | Original MoA used 0.4 |
| `reference_max_tokens` (deep) | **Add** | Cap advisor output for speed |

### Design Decisions

1. **fable-5.6-sol as aggregator for default/deep** — cockpit's strongest model. Uses `api_mode: codex_responses` which supports extended reasoning. This is the single biggest quality upgrade.

2. **fable-5 stays as fast aggregator** — lightweight, fast, good enough for quick tasks. No need to burn cockpit tokens on simple queries.

3. **deep gets `max_tokens: 8192`** — complex tasks (code review, architecture analysis) need longer outputs. 4096 may truncate.

4. **deep aggregator_temperature: 0.3** — lower temperature = more deterministic output. Critical for hard tasks where precision matters.

5. **reference_max_tokens: 800 on deep** — deeper than default's 600 but still capped for speed.

### Cost Implications

| Preset | Before | After | Change |
|--------|--------|-------|--------|
| default | 2 refs + 1 agg (Advance) | 2 refs + 1 agg (fable-5.6-sol) | +cost (stronger aggregator) |
| deep | 3 refs + 1 agg (fable-5) | 3 refs + 1 agg (fable-5.6-sol) | +cost (stronger aggregator) |
| fast | 1 ref + 1 agg (fable-5) | 1 ref + 1 agg (fable-5) | no change |

### Trade-offs

- **Stronger aggregator = higher per-turn cost** — fable-5.6-sol is more expensive than Advance/fable-5. But quality gain is significant (official benchmark: +6 points).
- **Temperature 0.6/0.4 reduces diversity** — may miss creative solutions. Acceptable for code/technical tasks.
- **Removing context_length** — no impact since provider-level settings already handle 1M context.
