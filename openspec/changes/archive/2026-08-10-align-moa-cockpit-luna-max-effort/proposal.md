## Why

The active Hermes MoA configuration and canonical contract have drifted: cockpit slots still use `gpt-5.6-sol` in `deep` and `fast`, the default preset contains an extra `giaoduc:Advance` reference and a non-cockpit aggregator, and cockpit effort is below the requested maximum in some slots. The requested clean-break target is cockpit `gpt-5.6-luna` at `max` effort everywhere cockpit participates, with live config, canonical spec, and maintained docs describing one identical topology.

## What Changes

- Change every cockpit-backed MoA reference or aggregator from `gpt-5.6-sol` to `gpt-5.6-luna`.
- Set every cockpit-backed MoA slot to `reasoning_effort: max`.
- Align `default` to exactly two references (`shopapikey:fable-5` high and cockpit Luna max) with cockpit Luna max as aggregator.
- Preserve `deep`'s three-reference design, replacing its cockpit reference and aggregator with Luna max.
- Preserve `fast`'s one-reference design, replacing its cockpit reference with Luna max.
- Restore `moa.privacy_filter: display` to match the canonical contract while preserving existing temperatures, token caps, cadence, enablement, and loud degraded-reference behavior.
- Synchronize the canonical `hermes-moa-configuration` spec, governance runbook, and implementation evidence.
- Validate Hermes' existing virtual-provider code path; no upstream Hermes source modification is required.

## Goals

- No active MoA config, canonical spec, or maintained docs contain `gpt-5.6-sol` as a cockpit MoA slot.
- Every cockpit MoA slot uses `gpt-5.6-luna` and `max` effort.
- The default route delivers Luna's aggregator tool-call path.
- Provider health, direct inference, real MoA tool continuation, and OpenSpec state are reproducibly verified.

## Non-Goals

- Do not modify Hermes Agent source code or provider implementation.
- Do not change `shopapikey:fable-5`, `giaoduc:Advance`, temperatures, token caps, fanout cadence, fallback order, delegation, compression, cron, MCP, credentials, or provider endpoints except where required by the stated MoA alignment.
- Do not modify unrelated untracked OpenSpec changes in the canonical store.
- Do not rewrite archived historical changes.

## Affected Boundaries

- Live profile: `/Users/androidteam/.hermes/config.yaml`.
- Canonical store: `openspec/specs/hermes-moa-configuration/spec.md`.
- Maintained runbook: `docs/governance/hermes-moa-configuration.md`.
- Archived change evidence: this change's `implementation-evidence.md`.
- Hermes source is read-only verification context.

## Compatibility and Rollback

The provider/model pairs are already configured and direct inference for all three providers passes. The MoA virtual provider contract is unchanged. Before mutation, create a timestamped local config backup outside Git and verify its SHA-256. Rollback restores that backup, then reruns YAML assertions, `hermes moa list`, provider health, and the MoA smoke test.
