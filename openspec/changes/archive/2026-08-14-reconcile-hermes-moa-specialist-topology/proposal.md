## Why

The canonical `hermes-moa-configuration` specification and governance runbook describe a cockpit `gpt-5.6-luna` aggregator topology that does not match the live configuration. The live MoA presets use cockpit `gpt-5.6-sol` as a reasoning reference across all three presets, with `shopapikey:fable-5` as the default aggregator and `giaoduc:Advance` as the deep aggregator. The current configuration intentionally separates cockpit's MoA slot model (`gpt-5.6-sol`) from its direct-provider default and fallback model (`gpt-5.6-luna`).

Additionally, nine legacy flat-level `moa.*` keys (`reference_models`, `aggregator`, `reference_temperature`, `aggregator_temperature`, `degraded_reference_policy`, `max_tokens`, `reference_max_tokens`, `fanout`, `enabled`) were present as redundant duplicates of preset configuration. These have been removed. The `moa` root now contains only `default_preset`, `privacy_filter`, and `presets`.

This change reconciles the canonical specification and governance runbook to match the verified live topology, removes the obsolete "Active cockpit Luna topology" requirement, adds root-normalization requirements, and archives the change so the delta updates the main spec.

## What Changes

- Remove the obsolete **Active cockpit Luna topology** requirement from the canonical spec.
- Replace it with a **Specialist MoA topology and independent cockpit routes** requirement that documents the deliberate Sol-in-MoA / Luna-in-direct-route design.
- Modify the default, deep, and fast preset requirements to match the verified live topology exactly.
- Modify the advisor privacy and failure isolation requirement to use neutral literal privacy wording.
- Add a **MoA root normalization** requirement asserting that only `default_preset`, `privacy_filter`, and `presets` exist directly under `moa`, with no legacy flat-level operational fields.
- Update `docs/governance/hermes-moa-configuration.md` to describe the actual three-preset table, specialist role assignment, root normalization, literal `privacy_filter: ''`, independent fallback chain, provider-level context ownership, validation commands, and rollback instructions.
- Archive the change so the delta merges into the canonical spec.

## Capabilities

### Modified Capabilities

- `hermes-moa-configuration`: Reconcile the canonical contract with the current specialist preset topology and normalized MoA root.

## Goals

- Canonical spec, governance runbook, and live config describe one identical MoA topology.
- No stale `gpt-5.6-luna` MoA slot references remain in maintained (non-archived) surfaces.
- No legacy flat-level `moa.*` operational keys remain in the live config.
- The distinction between MoA Sol slots and direct Luna routes is explicitly documented.
- All unrelated requirements, scenarios, and archived historical changes are preserved.

## Non-Goals

- No modification to Hermes Agent source code or provider implementation.
- No changes to provider endpoints, credentials, fallback chains, delegation, compression, MCP, cron, or unrelated configuration.
- No rewriting of archived historical changes.
- No change to `privacy_filter: ''` — it remains at its configured literal value.

## Affected Boundaries

- Live profile: `~/.hermes/config.yaml` (legacy keys already removed).
- Canonical store: `openspec/specs/hermes-moa-configuration/spec.md`.
- Maintained runbook: `docs/governance/hermes-moa-configuration.md`.
- Archived change evidence: this change's `implementation-evidence.md`.
- Hermes source is read-only verification context.

## Compatibility and Rollback

The config mutation is already complete and verified. This change only reconciles documentation and specifications. Rollback restores the timestamped backup at `~/.hermes/backups/config-before-moa-legacy-cleanup-20260814-061300.yaml` and reruns structural validation.
