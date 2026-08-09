# Proposal: Hermes MoA Provider Reconfiguration

## Why

The current Mixture of Agents (MoA) configuration is **completely non-functional**. The existing `default` preset references three providers that do not exist in the active provider configuration:

| Preset Model | Provider | Status |
|---|---|---|
| `openai-codex/gpt-5.5` | openai-codex | NOT CONFIGURED — no OAuth credentials |
| `openrouter/deepseek-v4-pro` | openrouter | NOT CONFIGURED — `OPENROUTER_API_KEY` missing |
| `openrouter/anthropic/fable-5-4.8` | openrouter | NOT CONFIGURED — `OPENROUTER_API_KEY` missing |

`hermes moa list` confirms: "Active in config: (off)". MoA has never been usable with the current provider setup.

Additionally, a legacy flat-level `moa.reference_models` / `moa.aggregator` block exists in config.yaml that is a deprecated format and also references models from shopapikey that don't match the actual working models (e.g., `fable-5` works, but `claude-opus-4.8` and `claude-sonnet-4.6` are aliases that all route to `fable-5`).

## What Changes

### 1. Remove all broken provider references
- Delete the existing `default` preset (uses openai-codex + openrouter — neither available)
- Delete the legacy flat-level `moa.reference_models` / `moa.aggregator` / `moa.degraded_reference_policy` / `moa.max_tokens` / `moa.fanout` / `moa.enabled` block

### 2. Create new MoA presets using verified working providers
Replace with presets built exclusively from providers confirmed working via API inference tests:

| Provider | Endpoint | Verified Models | Notes |
|---|---|---|---|
| `shopapikey` | `api.phanmemvip.shop/v1` | `fable-5` (reasoning model) | API key restricted to fable-5 only |
| `giaoduc` | `api.giaoduc.online/v1` | `Advance` (reasoning model) | /models endpoint broken, /chat/completions works |
| `cockpit` | `localhost:51006/v1` | NONE currently | Token invalidated, all models fail — needs re-auth |

### 3. Add purpose-specific presets
- **default** — Best available quality using shopapikey + giaoduc
- **fast** — Quick turns with low token usage
- **deep** — Maximum reasoning for hard tasks

## Goals
- MoA becomes usable with current provider credentials
- Each preset uses only verified-working provider/model combinations
- Legacy broken config cleaned up
- Cost/latency tuning via `reference_max_tokens` and `fanout` settings

## Non-Goals
- Fixing cockpit provider (requires credential renewal — out of scope)
- Adding new providers (openrouter, openai-codex, etc.)
- MoA preset for code review (cockpit models needed but unavailable)

## Affected Boundaries
- `~/.hermes/config.yaml` — moa section only
- No service code, no spec changes, no multi-repo impact

## Compatibility
- All presets use standard MoA config format
- `hermes moa configure` and `hermes moa list` continue to work
- Presets selectable via `/model`, Desktop settings, Dashboard

## Rollback
- Individual presets can be disabled with `enabled: false`
- Full rollback: restore config.yaml from git or backup
