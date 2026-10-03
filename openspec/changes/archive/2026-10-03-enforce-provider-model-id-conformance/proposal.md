# Enforce provider model-id conformance

## Why

Three Claude Code provider capabilities disagree with each other and with the machine: two of them mandate a launcher/profile set that excludes the live `omniroute()` launcher, and they pin model identifiers (`Claude-Fable[1m]`, `fable[1m]`) that no longer match what the providers actually serve.

## What Changes

- Pin the shared phanmemvip provider model to `Claude-Fable` across the shopapikey and omniroute profiles and their launchers, removing the stale `[1m]` suffix from the value.
- Keep the OPUS-named alias in each phanmemvip-backed profile distinct as `opus`, so the provider's opus channel remains independently selectable instead of collapsing onto the same identifier.
- Preserve the OmniRoute `pm/` channel prefix, which the gateway requires to route to the phanmemvip channel.
- Relax the "launcher set is exactly shopapikey and cockpit" and "profile set is exactly shopapikey.json and cockpit.json" clauses so the live `omniroute()` launcher and `omniroute-pm.json` profile are covered rather than implicitly forbidden.
- Leave the cockpit provider untouched: its `gpt-5.6-luna[1m]` selector is a different provider and already matches its capability.
- **BREAKING**: any consumer asserting the literal `Claude-Fable[1m]` or `fable[1m]` selector in a profile or launcher must adopt `Claude-Fable`.

### Non-Goals

- Re-authenticating the Codex provider account (stale upstream OAuth token) or restoring the OmniRoute gateway's provider credential. Both are operator-only actions and neither changes a model identifier.
- Changing the cockpit provider, its `gpt-5.6-luna[1m]` selector, or its `effort,max_effort` capability declaration.
- Removing or renaming any launcher or profile, including the ones the current specs omit.
- Changing the `[1m]` context-window convention for the cockpit provider.
- Owning the global `~/.claude/settings.json` default. The active `add-phanmemvip-codex-x-provider` change owns that surface and sets it to `codex-x`; this change deliberately does not assert it, so the two do not collide.

## Capabilities

### New Capabilities

None. This change reconciles existing behavior across capabilities that already own these surfaces.

### Modified Capabilities

- `claude-code-provider-profile-resolution`: the shopapikey profile model requirement pins `Claude-Fable[1m]`, and the launcher/profile set requirements name only shopapikey and cockpit. These must pin `Claude-Fable`, cover the live launcher and profile set, and keep the OPUS-named alias distinct. The global settings requirement is left to `add-phanmemvip-codex-x-provider`.
- `claude-code-provider-routing`: the launcher requirement pins the shopapikey selector as `Claude-Fable[1m]` and declares the launcher set as exactly shopapikey and cockpit. These must pin `Claude-Fable` and cover the live launcher set.
- `claude-code-omniroute-pm-routing`: the launcher requirement pins the selected model as `pm/Claude-Fable[1m]`, which must become `pm/Claude-Fable`.

## Impact

- **Global settings**: `~/.claude/settings.json` is deliberately **not** owned by this change; its default model is asserted by `add-phanmemvip-codex-x-provider`. The model values this change does set remain functional until that change applies its own update.
- **Provider profiles**: `~/.claude/profiles/shopapikey.json` and `~/.claude/profiles/omniroute-pm.json` — top-level `model` and model environment aliases.
- **Launchers**: the `shopapikey()` and `omniroute()` functions in `~/.zshrc` — the model argument passed to `_claude_with_profile`.
- **Unchanged**: `~/.claude/profiles/cockpit.json`, the `cockpit()` launcher, all `apiKeyHelper` credential paths, and every `ANTHROPIC_*_SUPPORTED_CAPABILITIES` declaration.
- **Verification**: provider acceptance for each identifier is confirmed against the live messages endpoint, and client-side acceptance is confirmed through a non-interactive Claude Code invocation.
