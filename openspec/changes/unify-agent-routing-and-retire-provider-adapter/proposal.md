# Proposal

## Why

Maintaining a standalone Python FastAPI container (`claude-code-provider-adapter`) on port 8788 introduces unnecessary LinuxKit VM container overhead, duplicate network hops, and an extra supervised launchd process when OmniRoute v3.8.51 natively supports both Anthropic Messages and OpenAI Responses protocol translations on loopback ports 20128 and 20129. Retiring the adapter sidecar unifies all local AI agent routing under OmniRoute's native dialect engine and streamlines workstation lifecycle management.

## What Changes

- **Decommission Provider Adapter Container**: Drain and stop container `claude-code-provider-adapter-adapter-1`, bootout and unload LaunchAgent `com.workspace.claude-code-provider-adapter`, and remove `platform/claude-code-provider-adapter` from active orchestration.
- **Streamline Workstation Lifecycle Management**:
  - Remove `platform/claude-code-provider-adapter` from `COMPOSE_STACKS` in `~/Developer/scripts/docker-service.sh`, leaving `~/Omniroute` as the sole primary gateway stack.
  - Remove port 8788 health probes from `~/Developer/scripts/omniroute-watchdog.sh` to focus continuous supervision strictly on Docker daemon health and OmniRoute `/healthz` on port 20128.
- **Unify Claude Code Launchers & Profiles**:
  - Reconcile `cockpit()` in `~/.zshrc` and `~/.claude/profiles/cockpit.json` to route directly through native OmniRoute endpoints or direct Cockpit Tools loopback endpoints (`51006`), eliminating the intermediate adapter proxy hop.
  - Validate all three agent launchers (`omniroute`, `shopapikey`, `cockpit`) operate without container dependency on port 8788.

## Capabilities

### Modified Capabilities
- `docker-lifecycle`: Remove `claude-code-provider-adapter` from registered compose stack requirements and streamline lifecycle drainage, bring-up, and watchdog health probing to focus on OmniRoute.
- `claude-code-omniroute-pm-routing`: Clarify unified direct routing for coding agent profiles through OmniRoute's native Anthropic Messages endpoint (`/v1/messages`), retiring legacy sidecar translation hops.

## Non-Goals

- Modifying Cockpit Tools desktop core process listening on port 51006.
- Altering OmniRoute internal routing algorithms, token rate limiting, or database schema.
- Removing or re-keying external credentials in `~/.zshenv` or `~/.claude/helpers/`.

## Affected Ownership Boundaries

- **Workstation Lifecycle Management**: `~/Developer/scripts/docker-service.sh`, `~/Developer/scripts/omniroute-watchdog.sh`.
- **Platform Infrastructure**: `~/Developer/platform/claude-code-provider-adapter/`.
- **User Environment & Agent Configuration**: `~/.zshrc`, `~/.claude/profiles/cockpit.json`, `~/Library/LaunchAgents/com.workspace.claude-code-provider-adapter.plist`.
