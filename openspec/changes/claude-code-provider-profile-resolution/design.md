# Design: claude-code-provider-profile-resolution

## Problem

`~/.claude/settings.json` had `"model": "Advance[1m]"` hardcoded globally. This overrode every launcher's attempt to set the model via subshell environment variables or CLI flags. Claude Code reads the model from `settings.json` before processing `--model` or env vars.

Additionally, launcher subshells only passed `--model` via CLI flag through `_claude_model_default()` but never exported the environment variables (`ANTHROPIC_MODEL`, `ANTHROPIC_BASE_URL`, `ANTHROPIC_CUSTOM_MODEL_OPTION`, model alias overrides) that fable-5's resolution pipeline reads.

## Solution Architecture

### Layer Separation

| Layer | Contains | Persistence |
|---|---|---|
| Profile JSON (`~/.claude/profiles/*.json`) | Model, base URL, aliases, effort, capabilities | Persistent, `chmod 600` |
| Shell launcher (`~/.zshrc`) | `ANTHROPIC_AUTH_TOKEN` from `$HERMES_CUSTOM_*_API_KEY` | Runtime only, per subshell |
| Global settings (`~/.claude/settings.json`) | shopapikey defaults (model, base URL, aliases, effort) | Persistent, no auth token |

### Profile Files

Each profile is a standalone JSON file under `~/.claude/profiles/`:

```json
{
  "model": "<provider-model-id>[1m]",
  "env": {
    "ANTHROPIC_BASE_URL": "<provider-endpoint>",
    "ANTHROPIC_MODEL": "<provider-model-id>[1m]",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "<provider-model-id>[1m]",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "<provider-model-id>[1m]",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "<provider-model-id>[1m]",
    "CLAUDE_CODE_SUBAGENT_MODEL": "<provider-model-id>[1m]",
    "CLAUDE_CODE_EFFORT_LEVEL": "<xhigh|max>"
  }
}
```

For custom model IDs (giaoduc, cockpit), the profile also includes:
```json
    "ANTHROPIC_CUSTOM_MODEL_OPTION": "<provider-model-id>[1m]",
    "ANTHROPIC_CUSTOM_MODEL_OPTION_SUPPORTED_CAPABILITIES": "effort,<effort>_effort"
```

For fable (built-in alias), the profile also includes:
```json
    "ANTHROPIC_DEFAULT_FABLE_MODEL": "<provider-model-id>[1m]",
    "ANTHROPIC_DEFAULT_FABLE_MODEL_SUPPORTED_CAPABILITIES": "effort,<effort>_effort"
```

### Launcher Wiring

Each launcher function:
1. Guards: `_claude_has` (claude in PATH)
2. Guards: `_claude_require_token HERMES_CUSTOM_<PROVIDER>_API_KEY`
3. Exports only `ANTHROPIC_AUTH_TOKEN` in a subshell
4. Calls `_claude_with_profile "$HOME/.claude/profiles/<provider>.json" "<model>[1m]" "$@"`

The `_claude_with_profile` helper passes `--settings <profile>` to Claude Code. If no `--model` flag is present, it also passes `--model <default>`.

### `[1m]` Suffix Contract

`[1m]` is a Claude Code context-window selector. Claude Code strips it before transmitting to the provider. It is passed in both the `--model` CLI flag and the `env.ANTHROPIC_MODEL` value for belt-and-suspenders resolution. This proves client-side selector acceptance only, NOT provider-side 1M capacity.

### Security

- Auth tokens are never written to JSON files on disk.
- Profile files are `chmod 600` (owner-only read/write).
- The `_claude_require_token` guard exits early with a clear error message when a provider API key is not set.

## Rollback

1. Restore `~/.claude/settings.json` from backup.
2. Remove `~/.claude/profiles/` directory.
3. Restore `~/.zshrc` launcher block from `~/.zshrc.pre-profiles-patch.*` backup.
