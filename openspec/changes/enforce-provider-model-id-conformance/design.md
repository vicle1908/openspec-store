# Design: Enforce provider model-id conformance

## Context

See `proposal.md` — Why. Current state and constraints relevant to the approach:

- Two capabilities disagree. `claude-code-provider-profile-resolution` and `claude-code-provider-routing` both assert the launcher set is *"exactly shopapikey and cockpit"* and the profile set is *"exactly shopapikey.json and cockpit.json"*, while `claude-code-omniroute-pm-routing` requires `omniroute()` and `omniroute-pm.json` to exist. The machine has three of each, so the two-capability specs are stale.
- The `[1m]` suffix means two different things. `claude-code-provider-routing` documents that Claude Code **strips** the suffix before transmitting, so `Claude-Fable[1m]` reaches the provider as `Claude-Fable`. The cockpit provider reaches Claude Code through a model picker that understands the suffix; the phanmemvip provider is a raw Anthropic-compatible endpoint whose catalog the client does not describe.
- Provider acceptance is confirmed by direct probe against `https://api.phanmemvip.shop/v1/messages`: `Claude-Fable`, `opus`, `Claude-Opus`, and `fable` all return HTTP 200 with real completions. The provider is therefore not the constraint.
- Client acceptance differs from provider acceptance. A non-interactive `claude -p` invocation emits `[claude-code:unrecognized_model]` for the suffixed phanmemvip alias and still exits 0, because a cached remote feature flag (`tengu_curious_tower_stateless_models`) resolves an SDK-path model id independently of local settings. Selector acceptance by the client must not be treated as evidence of provider capacity, and a client warning must not be read as a hard failure without its exit code.
- `cockpit.json` and the `cockpit()` launcher already match their capability exactly and use a different provider.

## Goals / Non-Goals

### Goals

- One shared phanmemvip model identifier across the global settings file and both phanmemvip-backed profiles and launchers.
- Keep the OPUS-named alias independently selectable rather than aliasing it onto the fable identifier.
- Make the specs describe the launcher and profile set that actually exists.

### Non-Goals

- Making the client stop emitting the `unrecognized_model` warning. It originates from a cached remote feature flag, not from any local file this change owns.
- Introducing a `modelOverrides` map for the phanmemvip provider. The omniroute profile already uses `modelOverrides` for its gateway alias; extending that to the direct provider is a separate concern.
- Aligning the `cockpit` provider, its picker-based `[1m]` selector, or its capability declaration.

## Decisions

### Decision: Yield the global-settings default to `add-phanmemvip-codex-x-provider`

The active `add-phanmemvip-codex-x-provider` change also modifies the global-settings requirement, setting the default to `codex-x` rather than `Claude-Fable`. Two changes cannot both own the same requirement, and that change's intent is the newer one and is not contradicted by evidence: `codex-x` is published in the gateway's catalog and returns HTTP 200. This change therefore drops the global-settings requirement from its delta and asserts only the profile and launcher surfaces, which the other change does not touch.

**Alternative considered:** keep both and let the later archive win. Rejected — the store would report a validation failure in the meantime, and a silent last-writer-wins merge is not an explicit decision.

**Alternative considered:** revert `~/.claude/settings.json` to its pre-change value. Rejected — the pre-change value carried a `[1m]` suffix the client cannot resolve, so reverting would restore a known-bad value. The file is left at a functional value that the other change will update on its own schedule.

### Decision: Drop the `[1m]` suffix on phanmemvip-backed identifiers

The suffixed alias is not described by the client catalog, which is why it warns and falls back. `claude-code-provider-routing` already establishes that the suffix is stripped before transmission, so the wire value is unchanged either way — the suffix only adds a client-side recognition step that cannot succeed for this provider.

**Alternative considered:** keep `Claude-Fable[1m]` and suppress the warning. Rejected — it preserves a value the client cannot resolve and relies on warning suppression rather than a correct identifier.

**Alternative considered:** keep the suffix and add a `modelOverrides` entry mapping it. Rejected for this change as broader in scope; noted as a non-goal.

### Decision: The OPUS-named slot carries `opus`

The requirement that the alias stay independently selectable cannot hold if every slot resolves to the same string. Assigning `opus` to `ANTHROPIC_DEFAULT_OPUS_MODEL` keeps that slot meaningful and matches a value the provider accepts.

**Alternative considered:** set every slot to `Claude-Fable`. Rejected — it collapses the opus selector onto the fable identifier, making the alias contract vacuous.

**Alternative considered:** set the top-level `model` to `opus`. Rejected — fable is the primary shared-tier channel, and the cockpit and omniroute surfaces already treat fable as the default.

### Decision: Extend rather than replace the launcher and profile sets

The specs are widened to include `omniroute()`, `omniroute-pm.json`, and the shopapikey launcher's `omniroute` sibling surfaces. The `giaoduc` prohibition is preserved because it reflects a real retirement, not drift.

**Alternative considered:** remove `omniroute()` and `omniroute-pm.json` to satisfy the narrower specs. Rejected — the operator chose to keep every launcher, and `claude-code-omniroute-pm-routing` documents the surface in full.

### Decision: Preserve the `pm/` channel prefix

The OmniRoute gateway routes to the phanmemvip channel through the `pm/` prefix. Dropping the suffix touches only the context-window marker; dropping the prefix would change which channel the gateway selects.

**Alternative considered:** normalize to bare `Claude-Fable` for consistency with the direct provider. Rejected — the prefix is gateway routing, not a model suffix.

## Risks / Trade-offs

- **[The client warning persists after the change]** → Expected. The warning originates from a cached remote flag, so it is unaffected by local model values. Mitigation: the verification step asserts exit code and provider-side acceptance rather than the absence of the warning.
- **[A consumer asserts the literal suffixed selector]** → Any spec text, script, or note pinning `Claude-Fable[1m]` or `fable[1m]` goes stale. Mitigation: the change enumerates and updates every affected location, and the deltas record the old values so the mapping is auditable.
- **[`opus` resolves differently than `Claude-Fable` at the provider]** → Both were probed and return HTTP 200. The provider's own `served` field reported `Claude-Opus` for `opus` and `Claude-Fable` for `Claude-Fable`, so they are genuinely distinct channels rather than aliases.
- **[Widening the launcher set lets an unverified launcher satisfy the spec]** → The `omniroute()` launcher currently fails because the gateway has no active provider credential. Mitigation: the requirement asserts the launcher's wiring and model argument, which are verifiable without a live credential; the credential gap is recorded as an operational item rather than a conformance failure.

## Migration Plan

1. Back up each file to be edited, preserving the mode bits.
2. Update `~/.claude/settings.json`: set the top-level model and the fable, sonnet, haiku, and subagent aliases to `Claude-Fable`, and the opus alias to `opus`.
3. Update `~/.claude/profiles/shopapikey.json` with the same mapping.
4. Update `~/.claude/profiles/omniroute-pm.json`: replace `pm/Claude-Fable[1m]` with `pm/Claude-Fable` in the top-level model and every alias.
5. Update the `shopapikey()` and `omniroute()` model arguments in `~/.zshrc`.
6. Verify provider acceptance for every distinct identifier and confirm the profile and settings files parse with the expected values.
7. Sync the three capability deltas to the main specs.

**Rollback:** each edited file has a timestamped backup beside it; restoring the backups reverts every model value. The spec deltas revert by re-syncing from the previous capability text, which the deltas record.

## Open Questions

- Should the cockpit provider also drop its `[1m]` selector once its picker path changes? Deferrable: the selector resolves correctly today, and changing it would alter a working provider's effort contract.
