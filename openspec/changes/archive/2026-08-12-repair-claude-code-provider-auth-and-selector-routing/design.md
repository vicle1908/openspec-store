# Design: repair-claude-code-provider-auth-and-selector-routing

## Problem

Claude Code 2.1.228 introduced an explicit mutual-exclusivity warning for `ANTHROPIC_AUTH_TOKEN` and `apiKeyHelper`. The current profile-based launchers (designed for Claude Code 2.1.227) exported `ANTHROPIC_AUTH_TOKEN` as belt-and-suspenders alongside `apiKeyHelper`, which the 2.1.228 client now rejects.

Additionally:
- Plaintext provider API keys are persisted in `~/.zshrc` (lines 240-243), contradicting the "no embedded secrets" design intent.
- The cockpit profile has regressed from `gpt-5.6-luna[1m]` to bare `gpt-5.6-luna`.
- `claude_reset()` does not unset `CLAUDE_CODE_SUBAGENT_MODEL`.

## Solution Architecture

### Authentication Model: Profile/Helper-Only

```
┌─────────────────────────────────────────────────────────┐
│ Claude Code process                                     │
│                                                         │
│  apiKeyHelper from profile/settings → credential        │
│  NO ANTHROPIC_AUTH_TOKEN in environment                 │
└─────────────────────────────────────────────────────────┘

Credential flow:
  ~/.claude/profiles/<provider>.json
    └─ apiKeyHelper: ~/.claude/helpers/<provider>-key.sh
       └─ reads ~/.hermes/.env
          └─ prints HERMES_CUSTOM_<PROVIDER>_API_KEY to stdout
```

The `_claude_require_token` guard is replaced by `_claude_require_helper`, which invokes the profile's helper script with stdout/stderr redirected to /dev/null. This proves the credential is available without printing it.

### Launcher Auth Isolation

Each profile-based launcher subshell now:

1. Unsets `ANTHROPIC_AUTH_TOKEN` defensively
2. Calls `_claude_require_helper` with the provider's helper path
3. Passes `--settings <profile>` to Claude Code
4. Claude Code invokes the profile's `apiKeyHelper` at runtime

### Credential Removal

Lines 240-243 of `~/.zshrc` (literal `export HERMES_CUSTOM_*=...`) are removed entirely. The credential values are only available through `~/.hermes/.env` which the helper scripts source at runtime.

### Cockpit Selector Restoration

The cockpit profile and launcher restore `gpt-5.6-luna[1m]` as the local selector. The wire model remains bare `gpt-5.6-luna` (Claude strips `[1m]` before transmission).

### Reset Completeness

`claude_reset()` gains `unset CLAUDE_CODE_SUBAGENT_MODEL` to match the canonical spec requirement.

## Auth Mutual Exclusivity Contract

```
ANTHROPIC_AUTH_TOKEN and apiKeyHelper are MUTUALLY EXCLUSIVE.
If both are present, Claude Code 2.1.228+ emits a warning and
may fail to authenticate correctly.
```

This change establishes two clean paths:
1. **Profile path (recommended):** `--settings <profile>` with `apiKeyHelper`, no `ANTHROPIC_AUTH_TOKEN`
2. **Legacy path (deprecated):** bare `claude` with `ANTHROPIC_AUTH_TOKEN` in shell env, no `apiKeyHelper`

The launchers exclusively use path 1. The legacy path is preserved for bare `claude` invocations but is not used by any launcher function.

## Files Modified

| File | Change |
|---|---|
| `~/.zshrc` | Remove credential exports (L240-243), replace `_claude_require_token` with `_claude_require_helper`, remove `ANTHROPIC_AUTH_TOKEN` from launchers, add `unset ANTHROPIC_AUTH_TOKEN` defensively, add `unset CLAUDE_CODE_SUBAGENT_MODEL` to reset, restore cockpit `[1m]` in launcher fallback |
| `~/.claude/profiles/cockpit.json` | Restore `[1m]` suffix on all model selectors |
| `~/.claude/settings.json` | No change (already correct) |
| `~/.claude/helpers/*.sh` | No change (already correct) |
| `~/.hermes/skills/...` | Reconcile profile/auth guidance with helper-only launchers and Claude Code 2.1.228 mutual exclusivity |
| `~/Developer/claude-code-provider-adapter/README.md` | Reconcile launcher authentication and runtime `.env` documentation |

## Security

- No credential values in `~/.zshrc` after the change.
- Helper preflight redirects all output to `/dev/null`.
- `settings.json` and profile JSONs remain credential-free.
- File permissions unchanged: profiles `600`, helpers `700`.
- Exposed plaintext keys should be rotated (separate action, out of scope).

## Verification

1. No `ANTHROPIC_AUTH_TOKEN` in child process environment
2. `apiKeySource=apiKeyHelper` in Claude init output
3. Zero auth warnings on stderr
4. All three wire models correct: `fable-5`, `Advance`, `gpt-5.6-luna`
5. All three efforts correct: `xhigh`, `xhigh`, `max`
6. Cockpit `system_model=gpt-5.6-luna[1m]`
7. `claude_reset()` produces clean state
8. `zsh -n ~/.zshrc` passes
9. OpenSpec validation passes
