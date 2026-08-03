## Why

Claude Code appeared unauthenticated when launched directly from the Hermes service, despite the user having configured token authentication. The mismatch came from process-environment scope: the login shell loads `ANTHROPIC_AUTH_TOKEN`, while direct service subprocesses do not.

## What Changes

- Verify Claude Code authentication from the user's login-shell context without exposing token values.
- Execute a bounded, no-tools Claude print request using the token-loaded context.
- Update the Claude Code Hermes skill with the safe service-context invocation pattern.
- Record version, auth method, result metadata, and limitations in OpenSpec.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. This is a procedural skill and verification update with `skip_specs: true`.

## Impact

- **Skill:** `~/.hermes/skills/autonomous-ai-agents/claude-code/SKILL.md`.
- **Runtime:** Claude subprocess invocation on this macOS host.
- **Credentials:** No token values are printed, copied, rotated, or persisted.
- **Applications:** No project repositories or product APIs change.

## Non-Goals

- Converting token authentication to subscription OAuth.
- Moving the token into launchd or the Hermes global environment.
- Changing Claude account, provider, model, or billing configuration.
