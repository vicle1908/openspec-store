# Design: Hermes MoA Provider Reconfiguration

## Context

### Provider Inventory (Verified 2026-08-06)

**shopapikey** — phanmemvip.shop proxy
- Endpoint: `https://api.phanmemvip.shop/v1`
- Auth: `HERMES_CUSTOM_SHOPAPIKEY_API_KEY` (SET)
- Models endpoint: returns `['fable-5']` only
- Inference tests:
  - `fable-5` → ✅ WORKS (reasoning model, returns reasoning_content)
  - `sh/claude-opus-4.8` → ✅ works (alias, routes to fable-5 internally)
  - `claude-sonnet-4.6` → ✅ works (alias, routes to fable-5 internally)
  - `fable-5-4.8` → ❌ BLOCKED ("API KEY chỉ dùng được fable-5")
  - Config lists: fable-5, fable-5-4.8, claude-sonnet-4.6, sh/claude-opus-4.8, default
- **Effective capacity:** 1 real model (fable-5), aliases route through it

**cockpit** — localhost:51006
- Endpoint: `http://localhost:51006/v1`
- Auth: `HERMES_CUSTOM_COCKPIT_API_KEY` (SET)
- Models endpoint: returns 10 models
- Inference tests:
  - ALL 10 models → ❌ FAILED
  - 5 models: "模型不在当前 API Key 的可用模型范围内" (model not in API key's range)
  - 5 models: "authentication token has been invalidated"
- **Effective capacity:** 0 models (needs credential renewal)

**giaoduc** — api.giaoduc.online
- Endpoint: `https://api.giaoduc.online/v1`
- Auth: `HERMES_CUSTOM_GIAODUC_API_KEY` (SET)
- Models endpoint: returns HTML (broken /v1/models)
- Inference test:
  - `Advance` → ✅ WORKS (reasoning model, returns reasoning_content)
- **Effective capacity:** 1 model (Advance)

**copilot** — GitHub Copilot
- Auth: gh auth token (1 credential)
- Missing: `COPILOT_GITHUB_TOKEN` env var
- **Effective capacity:** Unknown, not tested for MoA

### Existing MoA Config (Current State)

```yaml
moa:
  presets:
    default:
      reference_models:
        - provider: openai-codex        # NOT CONFIGURED
          model: gpt-5.5               # NOT REACHABLE
        - provider: openrouter          # NOT CONFIGURED
          model: fable-5/fable-54-pro  # NOT REACHABLE
      aggregator:
        provider: openrouter            # NOT CONFIGURED
        model: anthropic/claude-opus-4.8  # NOT REACHABLE
      degraded_reference_policy: loud
      fanout: user_turn
  # Legacy flat-level block (deprecated format):
  reference_models:
    - provider: shopapikey
      model: fable-5                    # works, but format is wrong
      enabled: true
    - provider: giaoduc
      model: Advance                    # works, but format is wrong
      enabled: true
    - provider: shopapikey
      model: fable-5                    # DUPLICATE
      enabled: true
  aggregator:
    provider: giaoduc
    model: Advance
  degraded_reference_policy: loud
  max_tokens: 4096
  fanout: user_turn
  enabled: true
```

**Issues:**
1. Preset `default` uses 2 providers that don't exist (openai-codex, openrouter)
2. Legacy flat-level block is deprecated format and has a duplicate reference
3. No preset is configured with only working providers
4. `cockpit` is listed as a provider in the config but all models are inaccessible

---

## Proposed MoA Configuration

### Design Rationale

With only 2 working providers (shopapikey, giaoduc) and 2 working models (fable-5, Advance), MoA presets must be designed within these constraints:

**Key insight:** fable-5 (shopapikey) and Advance (giaoduc) are both reasoning models from different providers/architectures. This is ideal for MoA — different model perspectives yield better aggregation than same-model duplicates.

### Preset 1: `default` — Balanced Quality

**Role:** General-purpose MoA with best available multi-model reasoning.

```yaml
default:
  reference_models:
    - provider: giaoduc
      model: Advance
    - provider: shopapikey
      model: fable-5
  aggregator:
    provider: shopapikey
    model: fable-5
  reference_max_tokens: 600
  fanout: user_turn
  enabled: true
```

| Slot | Provider | Model | Why |
|------|----------|-------|-----|
| Ref 1 | giaoduc | Advance | Different architecture → diverse perspective |
| Ref 2 | shopapikey | fable-5 | Reasoning model → strong analysis |
| Aggregator | shopapikey | fable-5 | Best available aggregator with tool support |

**Trade-offs:**
- `reference_max_tokens: 600` — concise advice, measurably faster turns (advisor output is capped, aggregator output is not)
- `fanout: user_turn` — cheapest cadence; advisors run once per user message, not per tool iteration
- Using fable-5 as both reference and aggregator is suboptimal but the only option with 2 models

### Preset 2: `fast` — Quick & Cheap

**Role:** One-shot quick tasks where speed matters more than depth.

```yaml
fast:
  reference_models:
    - provider: giaoduc
      model: Advance
  aggregator:
    provider: shopapikey
    model: fable-5
  reference_max_tokens: 300
  fanout: user_turn
  enabled: true
```

| Slot | Provider | Model | Why |
|------|----------|-------|-----|
| Ref 1 | giaoduc | Advance | Single advisor → fast fan-out |
| Aggregator | shopapikey | fable-5 | Normal quality aggregation |

**Trade-offs:**
- Single reference model → fastest possible MoA turn
- `reference_max_tokens: 300` → very concise advice
- ~50% fewer model calls than `default` preset

### Preset 3: `deep` — Maximum Reasoning

**Role:** Hard tasks requiring maximum analytical depth (architecture reviews, complex debugging).

```yaml
deep:
  reference_models:
    - provider: giaoduc
      model: Advance
      reasoning_effort: high
    - provider: shopapikey
      model: fable-5
      reasoning_effort: high
  aggregator:
    provider: shopapikey
    model: fable-5
    reasoning_effort: xhigh
  fanout: per_iteration
  enabled: true
```

| Slot | Provider | Model | Why |
|------|----------|-------|-----|
| Ref 1 | giaoduc | Advance | High reasoning effort for deep analysis |
| Ref 2 | shopapikey | fable-5 | High reasoning effort |
| Aggregator | shopapikey | fable-5 | xhigh reasoning for thorough tool calling |

**Trade-offs:**
- `per_iteration` cadence — advisors refresh on every tool call (expensive but freshest advice)
- `reasoning_effort: high/xhigh` — more thinking, higher quality, higher cost
- No `reference_max_tokens` — uncapped advisor output for maximum depth
- Most expensive preset; use for genuinely hard tasks only

### Global Settings

Remove all legacy flat-level moa settings. The preset system handles everything.

```yaml
moa:
  default_preset: default
  privacy_filter: display
  presets:
    # ... presets above ...
```

| Setting | Value | Why |
|---------|-------|-----|
| `default_preset` | `default` | `/moa` slash command uses this |
| `privacy_filter` | `display` | Redacts emails/phones from advisor outputs in UI; raw text still reaches aggregator for quality |

### Cockpit Recovery (Future)

When cockpit credentials are renewed, enhance presets:
- Add `cockpit/gpt-5.6-sol` as reference (strong non-reasoning model for diversity)
- Add `cockpit/gpt-5.6-terra` as reference in `deep` preset
- Create a `review` preset using `cockpit/gpt-5.3-codex` (code specialist)

---

## Verification

After applying changes:

1. `hermes moa list` — confirm 3 presets listed, default active
2. `hermes moa configure` — interactive wizard should show working models
3. Test each preset with a real prompt:
   - `/model default --provider moa` then send a message
   - `/model fast --provider moa` then send a message
   - `/model deep --provider moa` then send a message
4. `hermes config get moa` — confirm clean YAML structure, no legacy block
