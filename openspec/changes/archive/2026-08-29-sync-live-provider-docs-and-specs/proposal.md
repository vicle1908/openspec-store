## Why

The live provider and tooling state has advanced, but selected canonical docs and specs still describe stale Prime Agent and Claude Code values. This change synchronizes the documented and specified state without altering runtime configuration.

## What Changes

- Update `docs/cli-agent-tooling-contract.md`:
  - Prime Agent version from `0.7.1` to `0.8.1-beta.564.1.d60fab8`.
  - Prime Agent MCP Router status from `Not configured` to `Configured (stdio)`.
- Update `claude-code-provider-profile-resolution`:
  - Global `model` and `ANTHROPIC_MODEL` values from `fable[1m]` to `Claude-Fable[1m]`.
- Update `claude-code-provider-routing`:
  - Shopapikey launcher scenario model from `fable[1m]` to `Claude-Fable[1m]`.
- Update `coding-cli-provider-registry`:
  - Preserve the general OmniRoute model requirement for consumer CLIs.
  - Add the verified Prime Agent exception using the reviewed allowlist from `~/.prime/agent/models.json`.
- Update `omniroute-agent-cli-routing`:
  - Add the canonical Prime Agent OmniRoute provider registration and reviewed allowlist derived from `~/.prime/agent/models.json`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `claude-code-provider-profile-resolution`
- `claude-code-provider-routing`
- `coding-cli-provider-registry`
- `omniroute-agent-cli-routing`

## Non-Goals

- Do not modify runtime provider, model, CLI, or MCP configuration.
- Do not perform live provider inference.
- Do not change the unrelated NTU keynote change.
- Do not update historical archived evidence.
- Do not broaden the OmniRoute catalog beyond reviewed allowlists.

## Ownership Boundaries

- Documentation updates are owned by `docs/cli-agent-tooling-contract.md`.
- Claude Code specification updates are owned by the two named Claude Code capabilities.
- Consumer CLI provider registration updates are owned by `coding-cli-provider-registry`.
- OmniRoute routing updates are owned by `omniroute-agent-cli-routing`.
- No runtime configuration or provider implementation is modified.
