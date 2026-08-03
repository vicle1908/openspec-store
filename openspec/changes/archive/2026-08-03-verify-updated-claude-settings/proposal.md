## Why

Claude Code's previous tool-enabled benchmark was unavailable because the login shell overrode the configured endpoint with a dead local URL. The updated `~/.claude/settings.json` now supplies a working remote endpoint and token, so the coding path must be rechecked directly and independently verified.

## What Changes

- Inspect the updated Claude settings with credential redaction.
- Distinguish settings-provided environment from stale login-shell overrides.
- Verify direct Claude connectivity using the updated settings.
- Repeat the previous deterministic coding task and independently verify its diff and tests.
- Update Claude orchestration guidance to prefer direct invocation when settings own the endpoint/token.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. This is a configuration verification and procedural documentation update with `skip_specs: true`.

## Impact

- Claude Code user settings and Hermes Claude Code procedural guidance.
- Disposable fixture under `/tmp/claude-settings-recheck-20260803`.
- No production repository or credential value is modified or recorded.

## Non-Goals

- Rewriting the historical benchmark archive.
- Changing the user's Claude endpoint, token, plugins, or permissions.
- Comparing model quality beyond the repeated fixture.
