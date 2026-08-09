## Why

Buzz Desktop 0.5.8 ships Hermes Agent as a preset managed runtime. The documented delivery path is:

```text
Buzz mention -> buzz-acp -> hermes-acp -> Hermes model + terminal tool -> buzz messages send -> relay
```

In practice, the agent's reply never appears in the channel. Hermes' terminal environment sanitizer strips `BUZZ_PRIVATE_KEY`, `BUZZ_RELAY_URL`, and `BUZZ_AUTH_TAG` before any shell command executes, even though `buzz-acp` injects them into the ACP parent process.

The root cause is a classification error: these three variables are registered in `OPTIONAL_ENV_VARS` with category `messaging`, and `_build_provider_env_blocklist()` in `tools/environments/local.py` adds every `messaging`-category variable to `_HERMES_PROVIDER_ENV_BLOCKLIST`. The sanitizer then drops them from every terminal child. The existing `env_passthrough` escape hatch is sealed for these names by the GHSA-rhgp-j443-p4rf security hardening: `_is_hermes_provider_credential()` rejects any blocklisted name from passthrough registration.

This is a known upstream issue tracked in Hermes #76243 and #78026, and in Buzz #3385 and #4923.

The relay, managed identity, channel membership, and direct CLI reply permissions are all healthy. The failure occurs solely at the terminal credential boundary.

This change documents a temporary compatibility wrapper already applied and verified on this workstation for `harness-1`. It does not pretend implementation followed proposal-first sequencing. The `harness-deep` wrapper is documented in a successor change.

## What Changes

### Applied

- Installed `~/.buzz/bin/hermes-acp-buzz-wrapper` (mode 0700) for `harness-1`.
- The wrapper copies `BUZZ_*` to `_HERMES_FORCE_BUZZ_*` before `exec hermes-acp`.
- Persisted `agent_command_override` in both `harness-1` managed-agent records (definition + instance).
- Backed up pristine pre-change `managed-agents.json` to `~/Library/Application Support/xyz.block.buzz.app/agents/backups/`.

### Removed

- Inactive MCP sidecar prototype `~/.buzz/bin/buzz-hermes-reply-mcp.py` (Buzz Desktop 0.5.8 ignores `mcp_command` for the known Hermes runtime).

## Capabilities

### New Capabilities

None. The wrapper restores documented Buzz Desktop managed-runtime behavior, not a new capability.

### Modified Capabilities

`harness-1` can now publish messages and replies to Buzz channels via the terminal tool. No other agents are affected.

## Impact

- **`harness-1`**: reply path restored via wrapper.
- **All other agents**: unchanged (see successor change for `harness-deep`).
- **Security**: `BUZZ_*` credentials are available to Hermes foreground terminal children of `harness-1`, but not to `execute_code`, background spawns, or other agents. `harness-1` remains `respond_to: owner-only`.
- **Rollback**: remove `agent_command_override` from the two `harness-1` records and restart Buzz Desktop.
- **Official migration**: when an accepted upstream fix ships, remove the wrapper override and verify with a labelled canary.
