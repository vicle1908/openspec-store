# Design

## Context

See proposal.md - Why.

- The archived change `add-phanmemvip-codex-x-provider` synced a requirement into `openspec/specs/claude-code-provider-profile-resolution/spec.md` that mandates the Claude Code default model be bare `codex-x` with no `[1m]` suffix. That is the state this change corrects.
- There is no `openspec unarchive` verb, so the archived change cannot be re-opened; a follow-up change that emits a MODIFIED delta for the same capability is the supported path.
- Live probe (verification, not a guess): `POST https://api.phanmemvip.shop/v1/responses` returns HTTP 200 for `Claude-Fable[1m]` with `HERMES_CUSTOM_PHANMEMVIP_API_KEY`. The gateway's `/v1/models` lists the Claude aliases `opus`/`sonnet`/`haiku`; `Claude-Fable[1m]` is accepted on the wire.
- Precedent: `~/.claude/settings.json.bak-pre-codex-x.20261003T205434` (the last known-good Fable config) used `Claude-Fable` for the default and `xhigh` effort, with `ANTHROPIC_DEFAULT_OPUS_MODEL=opus`. The `bak-fix-claude-code-fable-model-id.20260829` variant used `Claude-Fable[1m]`.
- Live state observed: home `settings.json` was half-edited by another actor (`model: "opus"` with `env` still `codex-x`).

## Goals / Non-Goals

**Goals:**
- Make `Claude-Fable[1m]` the served, credential-free Claude Code global default.
- Keep the Codex surface (`codex-x`) untouched, so the two tools stay intentionally distinct.

**Non-Goals:**
- Re-designing the Claude Code launcher functions or the Codex profile.
- Changing the project-level `.claude/settings.json`.

## Decisions

### Decision 1: `Claude-Fable[1m]` as the Claude Code default

Use `Claude-Fable[1m]` for the top-level `model` and all `ANTHROPIC_*_MODEL` aliases in the home `settings.json`. Rationale: the operator selected the Claude model with the 1M selector; the gateway accepts it (HTTP 200) and it matches the established Fable-default era. The `[1m]` suffix is a Claude-Code selector that Claude Code strips before sending — per the `claude-code-provider-routing` contract, selector acceptance is not proof of provider-side 1M capacity.

### Decision 2: Codex stays on `codex-x` (no `[1m]`)

Leave `~/.Claude-Fable.config.toml` at `model = "codex-x"`. Rationale: `[1m]` is a Claude Code selector and does not apply to the Codex tool; the operator confirmed "keep" for the Codex side. This keeps `codex-cli-provider-routing` unchanged.

### Decision 3: Follow-up change instead of main-spec hand-edit

Emit a MODIFIED delta for the existing capability path rather than editing the main spec directly. Rationale: preserves the change→archive→sync flow and avoids the inconsistency that out-of-band main-spec edits create. Alternative considered: edit `openspec/specs/claude-code-provider-profile-resolution/spec.md` in place — rejected as non-compliant.

## Risks / Trade-offs

- [Provider rejects `Claude-Fable[1m]` in a real session despite the probe] → Fall back to `Claude-Fable` (also probed 200) or `opus`; record the outcome.
- [Half-edited live state (`model: opus` + `env: codex-x`) confuses a later session] → Normalize all model fields to `Claude-Fable[1m]` in one edit during implementation.
- [`[1m]` misread as a 1M capacity claim] → Documented in the requirement: it is selector-side only.

## Migration Plan

1. In the home `~/.claude/settings.json`, set the top-level `model` and every `ANTHROPIC_*_MODEL` alias to `Claude-Fable[1m]`; keep base URL, `xhigh` effort, and `apiKeyHelper` unchanged.
2. Verify the file is valid JSON, contains the `[1m]` suffix, and has no `ANTHROPIC_AUTH_TOKEN`/secret in `env`.
3. Verify the Codex profile still reads `model = "codex-x"` (unchanged).

Rollback: restore the previous `settings.json` value (`codex-x` or `opus`); no data migration involved.

## Open Questions

- None blocking. If the operator later confirms a different exact string (`Claude-Fable[1m]`), it is a one-line value change to the same requirement.
