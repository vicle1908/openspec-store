## Why

Buzz Desktop 0.5.8 ships Hermes Agent as a preset managed runtime. The documented flow is: Buzz Desktop spawns `buzz-acp`, which launches `hermes-acp` over stdio, and the agent replies via `buzz messages send` through its terminal tool. In practice, the agent's reply never appears in the channel because Hermes' terminal environment sanitizer strips the three `BUZZ_*` credentials before any shell command executes.

The root cause is a classification error: `BUZZ_PRIVATE_KEY`, `BUZZ_RELAY_URL`, and `BUZZ_AUTH_TAG` are registered in `OPTIONAL_ENV_VARS` with category `messaging`, and `_build_provider_env_blocklist()` in `tools/environments/local.py` adds every `messaging`-category variable to `_HERMES_PROVIDER_ENV_BLOCKLIST`. The sanitizer then drops them from every terminal child. The existing `env_passthrough` escape hatch is sealed for these names by the GHSA-rhgp-j443-p4rf security hardening: `_is_hermes_provider_credential()` rejects any blocklisted name from passthrough registration, regardless of source (skill, config, or adapter).

This is a known upstream issue tracked in Hermes #76243 and #78026, and in Buzz #3385 and #4923.

The relay, managed identity, channel membership, and direct CLI reply permissions are all healthy. The failure occurs solely at the terminal credential boundary.

This change documents a temporary compatibility wrapper already applied and verified on this workstation. It does not pretend implementation followed proposal-first sequencing.

## What Changes

- Record the temporary `_HERMES_FORCE_BUZZ_*` wrapper mechanism applied to `harness-1`.
- Preserve a canonical copy of the wrapper in the OpenSpec change for audit and drift detection.
- Create an operator runbook with rollback, drift detection, canary test, and official-migration gates.
- Retain a pristine pre-change backup of `managed-agents.json` at `~/Library/Application Support/xyz.block.buzz.app/agents/backups/managed-agents.before-harness-1-reply-compat-20260809.json`.
- Remove the inactive MCP sidecar prototype (`buzz-hermes-reply-mcp.py`) which Buzz Desktop 0.5.8 ignores for the known Hermes runtime.

## Capabilities

### New Capabilities

None. The wrapper restores documented Buzz Desktop managed-runtime behavior, not a new capability.

### Modified Capabilities

None. `skip_specs: true` because no product specification changes.

## Impact

- **`harness-1`**: reply path restored via wrapper. All other agents unchanged.
- **Security**: `BUZZ_*` credentials are available to Hermes foreground terminal children of the `harness-1` worker, but not to `execute_code`, background spawns, or other agents. `harness-1` remains `respond_to: owner-only`.
- **Rollback**: remove `agent_command_override` from the two `harness-1` records in `managed-agents.json` and restart Buzz Desktop.
- **Official migration**: when an accepted upstream fix ships, remove the wrapper override and verify with a labelled canary.
