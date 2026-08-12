# Proposal: repair-claude-code-provider-auth-and-selector-routing

## Why

Claude Code v2.1.228 introduced an explicit mutual-exclusivity warning:

```
Both ANTHROPIC_AUTH_TOKEN and apiKeyHelper set • auth may not work as expected
```

The current default shell launchers (designed for Claude Code 2.1.227) export `ANTHROPIC_AUTH_TOKEN` as belt-and-suspenders alongside `apiKeyHelper`, which the 2.1.228 client now warns against.

Additionally:

1. **Plaintext provider API keys are persisted in `~/.zshrc`** (lines 240-243). The design intent was "env-var references only" (see `claude-code-three-provider-routing` proposal), but the credential block was never removed.

2. **Cockpit profile lost the `[1m]` selector.** The archived `claude-code-model-effort-alias-routing` change verified `gpt-5.6-luna[1m]` as the local selector, but the live profile and launcher have regressed to bare `gpt-5.6-luna`.

3. **`claude_reset()` does not unset `CLAUDE_CODE_SUBAGENT_MODEL`**, which the canonical `claude-code-provider-profile-resolution` spec requires.

## What Changes

1. Remove plaintext credential exports from `~/.zshrc` (lines 240-243).
2. Replace `_claude_require_token` with `_claude_require_helper` that invokes the provider's helper script as a preflight check.
3. Remove `ANTHROPIC_AUTH_TOKEN` exports from all three profile-based launchers; each subshell defensively unsets it.
4. Restore cockpit `[1m]` selector in profile JSON and launcher fallback to `gpt-5.6-luna[1m]`.
5. Add `unset CLAUDE_CODE_SUBAGENT_MODEL` to `claude_reset()`.
6. Write MODIFIED requirements in the `claude-code-provider-profile-resolution` delta spec covering launcher auth isolation, credential-free shell config, and helper-preflight behavior.
7. Reconcile the provider-profile skill/reference and adapter README so they describe helper-only profile launchers and distinguish `~/.hermes/.env` from the adapter's ignored Docker `.env`.

## Security

- Provider API keys are removed from `~/.zshrc` entirely.
- Helper scripts remain the sole credential source.
- The preflight redirects stdout/stderr to `/dev/null` — credentials are never printed.
- `settings.json` and profile JSONs remain credential-free.
- Exposed plaintext keys should be rotated as a separate security action.

## Rollback

1. Restore `~/.zshrc` from backup.
2. Restore `~/.claude/profiles/cockpit.json` from backup.
3. Run `zsh -n ~/.zshrc` to verify syntax.
