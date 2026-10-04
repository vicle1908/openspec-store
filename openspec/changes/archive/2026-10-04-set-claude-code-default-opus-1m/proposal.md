# Proposal

## Why

The archived change `add-phanmemvip-codex-x-provider` set the Claude Code global default (home `~/.claude/settings.json`) to the bare model `codex-x` and explicitly forbade the `[1m]` suffix. That decision is superseded: the Claude Code global default should be the Claude model `Claude-Fable[1m]`. The governing spec `claude-code-provider-profile-resolution` currently mandates the now-wrong `codex-x` value, so it must be corrected to keep the store consistent with the decision.

## What Changes

- Reverse the Claude Code home-default decision from the archived change: the home `~/.claude/settings.json` global default model SHALL be `Claude-Fable[1m]` (Claude model with the 1M context-window selector), replacing the bare `codex-x` value.
- The `[1m]` suffix is now **required** on the Claude Code default selector, not forbidden. The base URL (`https://api.phanmemvip.shop`), effort (`xhigh`), resolution aliases, and credential-free `apiKeyHelper` pattern are unchanged.
- No change to the Codex surface: `~/.Claude-Fable.config.toml` keeps `model = "codex-x"` under `[model_providers.phanmemvip]` (the `codex-cli-provider-routing` capability is unchanged).

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `claude-code-provider-profile-resolution`: the "Global settings SHALL provide ... defaults" requirement changes its selected model from bare `codex-x` (no `[1m]`) to `Claude-Fable[1m]` on the same phanmemvip base URL, with the `[1m]` suffix required. The credential-free requirement and all other requirements are unchanged.

## Impact

- Files: `~/.claude/settings.json` (home, model value change only — no secret, no base URL, no effort change).
- Supersedes the Claude Code portion of archived change `add-phanmemvip-codex-x-provider`; the Codex portion of that change remains in force.
- Live-state note: the home `settings.json` was observed in a half-edited state (`model: "opus"` with `env` still `codex-x`); this change normalizes it to `Claude-Fable[1m]` throughout.

## Non-Goals

- No change to the Codex CLI provider/model (`codex-x` stays).
- No change to the project-level `.claude/settings.json`.
- No change to the Claude Code zsh launcher set (`claude-code-provider-routing`).
