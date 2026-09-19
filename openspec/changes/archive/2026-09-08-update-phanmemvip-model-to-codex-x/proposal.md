# Proposal: Update phanmemvip Model from gpt-5.6-sol to codex-x + Rotate API Key
<!-- skip_specs: true -->

## Summary

Update the default model for the **phanmemvip provider** from `gpt-5.6-sol` to `codex-x` across all agent CLIs. Also rotate the phanmemvip API key.

## Context

The phanmemvip provider (`https://api.phanmemvip.shop/v1`) currently defaults to `gpt-5.6-sol`. The new model `codex-x` has been verified working on the API (returns `model: codex`). This change switches all phanmemvip-specific `gpt-5.6-sol` references to `codex-x`.

**Scope:** Remove the legacy Giaoduc provider from active CLI configuration, keep exactly four supported provider families (shopapikey, phanmemvip, cockpit, OmniRoute), update phanmemvip references to `codex-x`, rotate the phanmemvip key, and optimize OmniRoute/OMP routing. Cockpit remains separate and is not modified. Shopapikey remains separate using `Claude-Fable`.

## Scope Rules

- `provider: phanmemvip` + `model: gpt-5.6-sol` → change to `model: codex-x`
- `provider: cockpit` + `model: gpt-5.6-sol` → **SKIP** (separate provider)
- `provider: shopapikey` + `model: Claude-Fable` → **SKIP** (separate provider, different key)
- Existing `omniroute/sh/` references may be updated from stale `sh/gpt-5.6-sol` to `sh/codex-x` when they represent the OmniRoute shopapikey route.
- `omniroute/sh/Claude-Fable` and `omniroute/sh/codex-x` SHALL remain available as separate OmniRoute routes.
- `phanmemvip` + `model: Claude-Fable` → **SKIP** (already correct model name)

## Changes

### Surface 1: `~/.hermes/config.yaml` — 10 edits (phanmemvip only)

**Provider default:**
- L307: `model: gpt-5.6-sol` → `model: codex-x`

**Fallback providers:**
- L328: `model: gpt-5.6-sol` → `model: codex-x` (phanmemvip fallback entry)

**Goose custom_phanmemvip block:**
- L416: `model: gpt-5.6-sol` → `model: codex-x`

**MoA presets — phanmemvip references/aggregators only:**
- L534: default preset, phanmemvip reference
- L564: deep preset, phanmemvip reference
- L569: deep preset, phanmemvip aggregator
- L607: global reference_models, phanmemvip
- L617: claude-code global default, phanmemvip

**NOT touched (cockpit):** L526, L538, L560, L581, L602, L621
**NOT touched (shopapikey):** L325, L542, L555, L585, L597, L625

### Surface 2: `~/.config/goose/` — 3 edits

- `config.yaml` L159: `model: gpt-5.6-sol` → `model: codex-x` (custom_phanmemvip)
- `config.yaml` L163: `model: gpt-5.6-sol` → `model: codex-x` (fallback)
- `custom_providers/custom_phanmemvip.json` L10: `"name": "gpt-5.6-sol"` → `"name": "codex-x"`

### Surface 3: `~/.grok/config.toml` — 1 edit

- L53: `model = "gpt-5.6-sol"` → `model = "codex-x"` (phanmemvip provider)

**NOT touched:** L58 (cockpit), L74 (omniroute-chat)

### Surface 4: `~/.omp/agent/config.yml` — 4 edits

- L8: `task: phanmemvip/gpt-5.6-sol:xhigh` → `task: phanmemvip/codex-x:xhigh`
- L64: `- phanmemvip/gpt-5.6-sol:xhigh` → `- phanmemvip/codex-x:xhigh`
- L69: `phanmemvip/gpt-5.6-sol:` → `phanmemvip/codex-x:`
- L92: `- phanmemvip/gpt-5.6-sol:xhigh` → `- phanmemvip/codex-x:xhigh`

### Surface 5: `~/.omp/agent/models.yml` — 2 edits

- L132: `id: gpt-5.6-sol` → `id: codex-x`
- L133: `name: gpt-5.6-sol (phanmemvip)` → `name: codex-x (phanmemvip)`

**NOT touched:** L70-71, L155-156, L195-196 (omniroute/cockpit)

### Surface 6: `~/.pi/agent/models.json` — 2 edits

- L9: `"id": "gpt-5.6-sol"` → `"id": "codex-x"`
- L10: `"name": "gpt-5.6-sol"` → `"name": "codex-x"`

**NOT touched:** L180-181, L325-326 (omniroute)

### Surface 7: `~/.pi/agent/settings.json` — 1 edit

- L39: `"phanmemvip/gpt-5.6-sol": "xhigh"` → `"phanmemvip/codex-x": "xhigh"`

**NOT touched:** L31 (cockpit)

### Surface 8: `~/.config/opencode/opencode.json` — 7 edits

**Model references (phanmemvip provider):**
- L8: `"model": "phanmemvip/gpt-5.6-sol"` → `"model": "phanmemvip/codex-x"`
- L9: `"small_model": "phanmemvip/gpt-5.6-sol"` → `"small_model": "phanmemvip/codex-x"`
- L14: explore agent `"model": "phanmemvip/gpt-5.6-sol"` → `"model": "phanmemvip/codex-x"`
- L24: oracle agent `"model": "phanmemvip/gpt-5.6-sol"` → `"model": "phanmemvip/codex-x"`
- L35: frontend agent `"model": "phanmemvip/gpt-5.6-sol"` → `"model": "phanmemvip/codex-x"`
- L41: docwriter agent `"model": "phanmemvip/gpt-5.6-sol"` → `"model": "phanmemvip/codex-x"`

**Provider model definition:**
- L189: `"gpt-5.6-sol": {` → `"codex-x": {` (phanmemvip provider models block)
- L190: `"name": "GPT 5.6 Sol"` → `"name": "Codex X"`

**NOT touched:** L117 (cockpit model def), L58/206 (omniroute)

### Surface 9: `~/.Claude-Fable.toml` (kimi-code) — 2 edits + API key

**Model definition:**
- L47: `model = "gpt-5.6-sol"` → `model = "codex-x"` (pm-sol model, phanmemvip provider)

**NOT touched:**
- L52: `model = "Claude-Fable"` (pm-claude-fable, already correct)
- L65: cockpit model
- L71: omniroute model

**API key (hardcoded):**
- L27: `api_key = "pmv_-I8OvaQ2JHeK7X5z-RHpSCCekkjoErEG"` → new key

### Surface 10: `~/.factory/settings.json` — 3 edits

**Custom model definition:**
- L26: `"model": "gpt-5.6-sol"` → `"model": "codex-x"`
- L27: `"id": "custom:phanmemvip-gpt-5.6-sol-0"` → `"id": "custom:phanmemvip-codex-x-0"`
- L31: `"displayName": "Phanmemvip · GPT 5.6 Sol"` → `"displayName": "Phanmemvip · Codex X"`

**Mission settings:**
- L71: `"validationWorkerModel": "custom:phanmemvip-gpt-5.6-sol-0"` → `"validationWorkerModel": "custom:phanmemvip-codex-x-0"`

**NOT touched:** L7 (ShopAPIKey entry), L15 (Cockpit entry)

### Surface 11: `~/Developer/tdt-core/scripts/verify_v2_codex_acceptance.py` — 4 edits

- L38, L60, L61, L128: `gpt-5.6-sol` → `codex-x`

### API Key Rotation

**`~/.zshenv` L16:**
`HERMES_CUSTOM_PHANMEMVPNPMVIP_API_KEY='pmv_...'` → `HERMES_CUSTOM_PHANMEMVPNPMVIP_API_KEY='pmv_OZht_ENR3m3tsTVWODbmaYbYhLSEYD7t'`

**`~/.Claude-Fable.toml` L27 (kimi-code hardcoded key):**
`api_key = "pmv_-I8OvaQ2JHeK7X5z-RHpSCCekkjoErEG"` → `api_key = "pmv_OZht_ENR3m3tsTVWODbmaYbYhLSEYD7t"`

## OMP Routing Optimization

The active OMP configuration is `~/.omp/agent/config.yml` (not `~/.omp/config.yml`).

- `omniroute/sh/codex-x:xhigh` SHALL remain the active `task` and `default` model.
- `omniroute/sh/Claude-Fable:xhigh` SHALL be included in the `default` retry fallback chain.
- `omniroute/sh/Claude-Fable:xhigh` SHALL be included in the `phanmemvip/codex-x` retry fallback chain.
- Direct `phanmemvip/codex-x` and `shopapikey/Claude-Fable` fallbacks SHALL remain available.
- Cockpit fallback entries SHALL remain separate and unchanged.

## Hermes MoA Cockpit Reference

Hermes MoA cockpit references SHALL use `cockpit/gpt-6-astra` rather than `cockpit/gpt-5.6-sol` for the goal judge and all active MoA reference-model collections. The cockpit provider remains separate from phanmemvip and shopapikey.

The cockpit model catalog SHALL expose `gpt-6-astra` before those MoA references are activated. Verification SHALL confirm the cockpit endpoint accepts the model.

## Legacy Provider Removal

The active configuration surface SHALL contain only these supported provider families:

- `shopapikey` → `Claude-Fable`
- `phanmemvip` → `codex-x`
- `cockpit` → cockpit-native models
- `omniroute` → `sh/codex-x`, `sh/Claude-Fable`, and `pm/Claude-Fable` routes as configured

The legacy `giaoduc` provider SHALL be removed from active Cline/provider configuration. Historical backups, logs, sessions, and archived artifacts are not active runtime configuration and are excluded from this cleanup.

Every active coding CLI configuration covered by this change SHALL expose all four supported provider families: `shopapikey`, `phanmemvip`, `cockpit`, and `omniroute`. Cline and Goose require explicit provider additions because their current active configurations do not expose all four families.

## Verification

1. Active CLI configuration contains no `giaoduc`, `GIAODUC`, or `api.giaoduc.online` references
2. Active provider families are limited to shopapikey, phanmemvip, cockpit, and OmniRoute
3. Cline exposes both `shopapikey/Claude-Fable` and `phanmemvip/codex-x`
4. Direct and OmniRoute model tests pass

## Verification


1. No phanmemvip `gpt-5.6-sol` remaining in active config files
2. Cockpit references still present and unchanged
3. Shopapikey `Claude-Fable` references remain separate and available
4. `sh/codex-x` and `sh/Claude-Fable` exist in CLI model registries
5. OMP defaults to `omniroute/sh/codex-x:xhigh`
6. OMP fallback chains include `omniroute/sh/Claude-Fable:xhigh`
7. YAML/JSON validation passes for all modified files
8. Direct API test: `codex-x` with new key returns pong
9. OmniRoute tests: `sh/codex-x` and `sh/Claude-Fable` both return responses
10. Real OMP CLI tests pass for both OmniRoute models
