# Proposal: Hermes MoA Quality Optimization

## Why

The current MoA config has quality issues:

1. **Single-preset design** — only a `default` preset exists with no quality tiering
2. **Duplicate model in references** — both advisors are `fable-5` + `Advance`, same as the aggregator. No diversity in perspectives
3. **Missing cockpit models** — `gpt-5.6-sol` (cockpit) is a powerful reasoning model but not used in MoA at all, despite cockpit being fully operational
4. **Legacy flat-level config** — deprecated `moa.reference_models` / `moa.aggregator` block coexists with presets, causing confusion
5. **No reasoning effort tuning** — all slots use default reasoning effort, missing the per-slot optimization MOA supports
6. **No privacy filter** — advisor outputs may echo sensitive conversation data into UI

### Provider Health (verified 2026-08-09)

| Provider | Model | Endpoint | Status |
|----------|-------|----------|--------|
| cockpit | gpt-5.6-sol | localhost:51006 | ✅ Inference verified |
| shopapikey | fable-5 | api.phanmemvip.shop | ✅ Inference verified |
| giaoduc | Advance | api.giaoduc.online | ✅ Inference verified |

## What Changes

### 1. Remove legacy flat-level MoA config
Delete deprecated top-level `moa.reference_models`, `moa.aggregator`, `moa.degraded_reference_policy`, `moa.max_tokens`, `moa.fanout`, `moa.enabled` — these coexist with the preset system and cause confusion.

### 2. Create quality-tiered presets

| Preset | Advisors | Aggregator | Use Case |
|--------|----------|------------|----------|
| **default** | fable-5 (shopapikey, effort: high) + gpt-5.6-sol (cockpit, effort: high) | Advance (giaoduc, effort: xhigh) | Balanced quality — 3 diverse model perspectives |
| **deep** | fable-5 (shopapikey, effort: xhigh) + gpt-5.6-sol (cockpit, effort: xhigh) + Advance (giaoduc, effort: high) | fable-5 (shopapikey, effort: max) | Maximum reasoning for hard tasks |
| **fast** | gpt-5.6-sol (cockpit, effort: medium) | fable-5 (shopapikey, effort: high) | Quick turns — single advisor, lower latency |

### 3. Add quality tuning
- `reference_max_tokens: 600` on default/fast for faster advisor turns
- Per-slot `reasoning_effort` for each model
- `fanout: user_turn` on default/fast, `fanout: every_n:3` on deep
- `privacy_filter: display` for advisor output redaction

### 4. Set global defaults
- `moa.default_preset: default`
- `moa.privacy_filter: display`

## Goals
- 3 diverse models provide multi-perspective reasoning
- gpt-5.6-sol (cockpit) integrated as advisor for high-quality analysis
- Quality-tiered presets for different task complexity
- Clean config with no legacy flat-level blocks
- Per-slot reasoning effort tuning

## Non-Goals
- Adding new providers beyond the 3 verified
- MoA for delegation (delegation has its own provider chain)
- Changing the delegation or fallback provider chains

## Affected Boundaries
- `~/.hermes/config.yaml` — moa section only
- No code changes, no spec changes, no multi-repo impact

## Compatibility
- All presets use standard MoA config format
- `hermes moa configure` and `hermes moa list` continue to work
- Presets selectable via `/model`, Desktop settings, Dashboard
- `/moa` shortcut uses the default preset

## Rollback
- Individual presets disabled with `enabled: false`
- Full rollback: restore config.yaml from backup
