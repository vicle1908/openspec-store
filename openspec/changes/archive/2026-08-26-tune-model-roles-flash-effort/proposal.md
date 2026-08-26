# tune-model-roles-flash-effort

## Why

High-frequency OMP background roles are over-provisioned or unrouted: `smol` and `commit` sit at `shopapikey/fable-5:xhigh`, while `tiny` and `vision` are unset and inherit `defaultThinkingLevel: xhigh` (falling through to the flagship `default` model). The user has added the `google-antigravity/gemini-3.7-flash` family — the only fast catalog entry with confirmed `image` input — and directed "use high effort" for it. Meanwhile `retry.fallbackChains.default` still terminates in `omniroute/dlg/kimi-k2.6` despite the user directive that omniroute is unused for now, and no model-keyed chains exist to survive role reassignment. The earlier `omp-model-role-fallback-tuning` change was archived as superseded (its giaoduc-restore premise was invalidated by `replace-giaoduc-with-phanmemvip`, which migrated `task` to `phanmemvip/gpt-5.6-sol:xhigh`); this change re-expresses the tuning intent against the current live state.

## What Changes

- Rebind high-frequency roles onto `google-antigravity/gemini-3.7-flash:high`: `smol` (was `shopapikey/fable-5:xhigh`), `tiny` (new role), and `vision` (new role — flash is the only fast catalog model with confirmed image input). Per the user's "use high effort" direction, every flash selector carries an explicit `:high` thinking suffix so background roles never inherit `defaultThinkingLevel: xhigh`.
- Reduce `commit` effort from `:xhigh` to `:low` on the shopapikey gateway model. The shopapikey model id was canonicalized `fable-5` → `Claude-Fable` by the concurrent `canonicalize-claude-fable-and-responses` change mid-apply (its gateway now reports `Claude-Fable` upstream); this change adopts the canonical id, binding `commit: shopapikey/Claude-Fable:low`.
- Keep ALL other roles byte-unchanged: `default: openrouter/stealth/ox-alpha:max`, `slow: cockpit/gpt-5.6-luna:max`, `plan: cockpit/gpt-5.6-sol:max`, `task: phanmemvip/gpt-5.6-sol:xhigh`, `advisor: cockpit/gpt-5.6-sol:xhigh`. (Post-apply note 2026-08-26: an external concurrent actor subsequently rebound `default` to `phanmemvip/gpt-5.6-sol:max`; that rebinding is outside this change's scope and ownership.)
- Restructure `retry.fallbackChains`: remove `omniroute/dlg/kimi-k2.6` from the `default` chain and append `google-antigravity/gemini-3.7-flash:high` as the terminal hop, giving `[phanmemvip/gpt-5.6-sol, shopapikey/Claude-Fable, cockpit/gpt-5.6-sol, google-antigravity/gemini-3.7-flash:high]`.
- Add model-selector-keyed chains per OMP `docs/settings.md` semantics (keys containing `/` bind a chain to the model across role reassignment): `phanmemvip/gpt-5.6-sol → [cockpit/gpt-5.6-sol, shopapikey/Claude-Fable]`, `cockpit/gpt-5.6-luna → [cockpit/gpt-5.6-sol, shopapikey/Claude-Fable]`, `cockpit/gpt-5.6-sol → [cockpit/gpt-5.6-luna, shopapikey/Claude-Fable]`, and the documented wildcard `google-antigravity/* → [google/*, google-vertex/*, shopapikey/Claude-Fable]` where `provider/*` entries swap provider keeping the model id with skipped-if-absent semantics.
- No `giaoduc` anywhere. `omniroute` stays defined in the `models.yml` catalog but is absent from every `modelRoles` entry and every fallback chain.
- Extend the isolated-profile smoke gate to all seven distinct final role selectors — `openrouter/stealth/ox-alpha:max`, `cockpit/gpt-5.6-luna:max`, `cockpit/gpt-5.6-sol:max`, `cockpit/gpt-5.6-sol:xhigh`, `phanmemvip/gpt-5.6-sol:xhigh`, `google-antigravity/gemini-3.7-flash:high`, `shopapikey/Claude-Fable:low` — every one must pong on itself (exit 0, judged on the requested selector; a 401→fallback masquerade FAILS the gate) before any live mutation.

Non-goals:

- `models.yml` is untouched by THIS change; no provider definition, catalog entry, or credential edit belongs to it. (The `fable-5` → `Claude-Fable` id rename in `models.yml` was applied by the separate concurrent `canonicalize-claude-fable-and-responses` change, which owns that edit; this change only consumes the canonical id in `config.yml`.)
- No changes to `advisor.enabled`, `tier`, compaction, or tool settings.
- The `omniroute` catalog entry remains defined and pickable; it is simply unrouted. No re-enablement of omniroute routing.

## Capabilities

### New Capabilities
- None. Fallback-chain composition is added as a requirement under the existing `omp-provider-routing` capability.

### Modified Capabilities
- `omp-provider-routing`: This capability already owns OMP provider blocks, credential references, `modelRoles` role allocation, and isolated-profile validation. This change modifies its role-allocation requirement (new bindings for `smol`/`tiny`/`vision`/`commit`), extends the omniroute-preservation requirement with a fallback-chains prohibition, extends isolated-profile validation to the seven-selector gate with native-provider credential resolution, and adds a fallback-chain composition/coverage requirement.

## Capabilities Affected (ownership)

- Owner: workstation OMP config (`/Users/androidteam/.omp/agent/config.yml`), planned via the `omp-provider-routing` capability in openspec-store. Implementation edits outside the store require the apply workflow.
