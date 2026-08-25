# omp-model-role-fallback-tuning

## Why

The OMP advisor and maintenance roles are routed to stale or broken model bindings: `omniroute/dlg/deepseek-v4-pro` appears in runtime UI despite no persistent binding, `giaoduc/Advance` returned `401 invalid_api_key` on 2026-08-25, and cheap background roles (`smol`, `tiny`, `commit`) inherit `xhigh` thinking or fall through to the flagship `default` model. The user has also added the `google-antigravity/gemini-3.7-flash` family and directed that omniroute be dropped from active routing for now.

## What Changes

- Rebind cheap/high-frequency roles onto `google-antigravity/gemini-3.7-flash:high`: `smol`, `tiny`, and `vision` (the only fast catalog model with confirmed `image` input). Per the user's "use high effort" direction, every assigned and fallback `gemini-3.7-flash` selector carries an explicit `:high` thinking suffix.
- Restore `task: giaoduc/Advance:xhigh` per user direction, with a model-keyed fallback chain covering its current credential failure (`401 invalid_api_key`) by failing over to proven providers.
- Reduce `commit` from `shopapikey/fable-5:xhigh` to `shopapikey/fable-5:low`.
- Restructure `retry.fallbackChains`: role-inherited `default` chain reordered to currently-successful providers first (cockpit luna — live; shopapikey fable-5 — same-day success), then giaoduc, then antigravity flash.
- Remove all `omniroute/*` entries from fallback chains (user directive: omniroute unused for now; provider stays defined in `models.yml`).
- Add model-selector-keyed chains per OMP docs semantics: `cockpit/gpt-5.6-luna` ↔ `cockpit/gpt-5.6-sol` cross-fallback then provider jump; `google-antigravity/*` wildcard following the documented `google-antigravity/* → google/* → google-vertex/*` pattern.
- Extend the isolated-profile smoke test to all nine final role selectors — every one, including `giaoduc/Advance:xhigh` and `google-antigravity/gemini-3.7-flash:high`, must pass before live application; the giaoduc 401 is a blocking prerequisite, not an accepted failure.

Non-goals:

- No changes to provider definitions, credentials, or `models.yml` (including the known cosmetic `gpt-5.6-terra` name bug — out of scope).
- No changes to `advisor.enabled`, `tier`, compaction, or tool settings.
- No re-enablement of omniroute routing; revisit when OmniRoute deployment/key state is resolved.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `omp-provider-routing`: This capability already owns OMP provider blocks, credential references, and `modelRoles` role allocation. This change modifies its role-allocation requirements (new bindings for `smol`/`tiny`/`vision`/`commit`/`task`, omniroute exclusion extended to fallback chains) and adds fallback-chain ordering/coverage requirements plus an antigravity flash smoke-test requirement.

## Capabilities Affected (ownership)

- Owner: workstation OMP config (`~/.omp/agent/config.yml`), planned via the `omp-provider-routing` capability in openspec-store. Implementation edits outside the store require the apply workflow.
