## Why

The active Hermes MoA profile has a balanced `default` route whose aggregator is `shopapikey:fable-5`, while `giaoduc:Advance` is a reference advisor. The operator wants a second selectable default route that reverses those two roles without changing the established `default`, `deep`, or `fast` presets.

The new `default-2` route provides an alternate acting-model choice for comparison and operational use. It keeps the existing cockpit Sol advisor, token budgets, temperatures, cadence, degraded-reference policy, and enablement unchanged. The role switch is limited to the new preset so the current default behavior remains available and rollback is a preset selection rather than a global-route rewrite.

## What Changes

- Add a new enabled `moa.presets.default-2` preset.
- Configure `giaoduc:Advance` as the `default-2` aggregator at `xhigh`.
- Configure `shopapikey:fable-5` as a `default-2` reference advisor at `high`.
- Preserve the cockpit `gpt-5.6-sol` reference advisor at `high`.
- Preserve the current `default` preset unchanged.
- Preserve `deep`, `fast`, the global `model.provider`, `model.default`, fallback chain, delegation, auxiliary compression, privacy value, and provider endpoints.
- Update the canonical `hermes-moa-configuration` spec and the maintained governance runbook.
- Validate direct provider availability and a fresh `default-2` MoA tool-call continuation before archival.

## Capabilities

### Modified Capabilities

- `hermes-moa-configuration`: Add the externally selectable `default-2` preset and its role-switch contract while preserving existing preset behavior.

## Goals

- Provide a working `default-2` preset with shopapikey and giaoduc roles switched relative to the current `default` preset.
- Keep the existing `default` route as the unchanged primary route.
- Make the alternate topology explicit and selectable through `/model default-2 --provider moa`.
- Prove the new aggregator owns the tool-call continuation through a fresh runtime smoke test.
- Keep specifications, runbook, live configuration, and evidence aligned.

## Non-Goals

- Do not change the global primary route from `moa:default`.
- Do not modify the existing `default`, `deep`, or `fast` presets.
- Do not change provider endpoints, credentials, provider defaults, fallback order, delegation, auxiliary compression, privacy, or context ownership.
- Do not edit archived historical changes.
- Do not claim comparative quality superiority for private provider endpoints; live inference proves availability only.

## Affected Boundaries

- Live profile: `/Users/androidteam/.hermes/config.yaml`, only `moa.presets.default-2` is added.
- Canonical store: `openspec/specs/hermes-moa-configuration/spec.md`.
- Maintained runbook: `docs/governance/hermes-moa-configuration.md`.
- Archived evidence: this change's `implementation-evidence.md` after archive.
- No Hermes source code or provider implementation changes.

## Compatibility

The new preset is additive. Existing sessions using `default`, `deep`, or `fast` retain their current topology. The global model remains `moa:default`. Users opt into the alternate route with `/model default-2 --provider moa` or an explicit CLI provider/model selection.

## Rollout

1. Verify current config and provider health.
2. Back up and atomically add only `moa.presets.default-2`.
3. Validate YAML shape and unchanged existing presets.
4. Run Hermes structural checks and a fresh default-2 tool-call smoke test.
5. Update and validate the canonical spec and runbook.
6. Archive and commit only owned store paths.

## Rollback

Remove only `moa.presets.default-2` from the live configuration, restore the verified backup if needed, and rerun YAML assertions, `hermes config check`, `hermes moa list`, and the existing-default smoke path. Existing presets are not modified by this change.
