# Proposal: claude-code-provider-profile-resolution

## Why

The previous `claude-code-model-effort-alias-routing` change fixed provider model aliases and effort mapping in `~/.zshrc` launcher subshells using environment variables. However, when the launchers were tested in a new shell, the model was not resolved correctly. The root cause: `~/.claude/settings.json` contained a global `"model": "Advance[1m]"` override that persisted across all sessions, and the launcher subshell env vars did not take precedence over the hardcoded settings file.

Additionally, the launcher subshells only passed `--model` via CLI flag but never exported the environment variables (`ANTHROPIC_MODEL`, `ANTHROPIC_BASE_URL`, `ANTHROPIC_CUSTOM_MODEL_OPTION`, model alias overrides) that fable-5's resolution pipeline reads. Claude Code's model resolution depends on these env vars, not just the CLI flag.

## What Changes

1. Remove the global `"model"` override from `~/.claude/settings.json` to provide a shopapikey default for bare `claude` invocations.
2. Create provider-specific profile JSON files under `~/.claude/profiles/` containing model, base URL, effort, capability declarations, and model alias overrides.
3. Replace the `_claude_model_default` helper with `_claude_with_profile` which passes `--settings <profile>` to Claude Code.
4. Each launcher subshell now only exports `ANTHROPIC_AUTH_TOKEN` (credentials stay in shell env, never in JSON files).
5. Add a `_claude_require_token` guard that exits early with a clear error when a provider API key is not set.

## Architecture

| Layer | Contains | Persistence |
|---|---|---|
| Profile JSON (`~/.claude/profiles/*.json`) | Model, base URL, aliases, effort, capabilities | Persistent file on disk |
| Shell launcher (`~/.zshrc`) | `ANTHROPIC_AUTH_TOKEN` from `$HERMES_CUSTOM_*_API_KEY` | Runtime only, per subshell |
| Global settings (`~/.claude/settings.json`) | shopapikey defaults (model, base URL, aliases, effort) | Persistent file on disk |

## Auth Architecture

Claude Code uses `apiKeyHelper` in settings/profile JSON: a script path whose stdout is the bearer token. No raw keys appear in JSON files.

| Layer | Auth source | Persistence |
|---|---|---|
| Profile `apiKeyHelper` | `~/.claude/helpers/<provider>-key.sh` reads `$HERMES_CUSTOM_*_API_KEY` | Script on disk, no secrets |
| Global `apiKeyHelper` | `~/.claude/helpers/shopapikey-key.sh` | Script on disk, no secrets |
| Shell `ANTHROPIC_AUTH_TOKEN` | Subshell env from `$HERMES_CUSTOM_*_API_KEY` | Runtime belt-and-suspenders |

## Security and Rollback

- Auth tokens are never written to JSON files on disk.
- `apiKeyHelper` scripts read from env vars; for cross-app use, migrate to macOS Keychain.
- Profile JSON files are `chmod 600` (owner-only).
- Helper scripts are `chmod 700` (owner-only executable).
- Rollback is restoring `~/.claude/settings.json` from backup and removing `~/.claude/profiles/` and `~/.claude/helpers/`.
- The `.zshrc` launcher block can be restored from `~/.zshrc.pre-profiles-patch.*` backups.
