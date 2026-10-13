# Proposal

## Why

The standalone Python FastAPI container (`claude-code-provider-adapter` on port 8788) was originally introduced to translate Claude Code's Anthropic Messages protocol into OpenAI Responses requests for Cockpit Tools (`http://host.docker.internal:51006/v1/responses`). Operating this adapter requires an extra supervised Docker container, a LaunchAgent (`com.workspace.claude-code-provider-adapter`), and duplicate network hops.

Research confirms that OmniRoute v3.8.51 natively supports registering OpenAI Responses custom provider nodes (`openai-compatible-responses-*`) pointing to `http://host.docker.internal:51006/v1`. OmniRoute translates inbound Anthropic Messages requests on port 20129 into OpenAI Responses requests upstream, matching the adapter's error responses verbatim (`auth_unavailable: No available account: candidates=3...`).

Configuring Cockpit as a native custom provider node in OmniRoute enables direct routing through OmniRoute (`model: cockpit/gpt-5.6-luna`), safely retiring `claude-code-provider-adapter` without breaking Claude Code's `cockpit()` launcher or model routing.

## What Changes

- **Register Cockpit Custom Provider in OmniRoute**:
  - Configure `provider_nodes` entry `openai-compatible-responses-cockpit` (`type: openai-compatible`, `api_type: responses`, `base_url: http://host.docker.internal:51006/v1`, `prefix: cockpit`).
  - Configure active `provider_connections` entry with encrypted `HERMES_CUSTOM_COCKPIT_API_KEY`.
  - Expose models `cockpit/gpt-5.6-luna`, `cockpit/gpt-6-astra`, `cockpit/gpt-6.1-sol`, `cockpit/gpt-5.6-sol`, and `cockpit/gpt-5.6-terra` in the live catalog on ports 20128 and 20129.
- **Decommission Provider Adapter Container & LaunchAgent**:
  - Drain and stop container `claude-code-provider-adapter-adapter-1` via `docker compose down`.
  - Bootout and unload LaunchAgent `com.workspace.claude-code-provider-adapter` (`gui/502`).
  - Move/disable `~/Library/LaunchAgents/com.workspace.claude-code-provider-adapter.plist`.
- **Streamline Workstation Lifecycle Management**:
  - Remove `platform/claude-code-provider-adapter` from `COMPOSE_STACKS` in `~/Developer/scripts/docker-service.sh`, leaving `~/Omniroute` as the sole primary gateway stack.
  - Remove port 8788 health probes from `~/Developer/scripts/omniroute-watchdog.sh`.
- **Update Claude Code Cockpit Launcher & Profile**:
  - Update `~/.claude/profiles/cockpit.json` to route to OmniRoute's native Messages port (`http://localhost:20129`), model `cockpit/gpt-5.6-luna`, with `apiKeyHelper` pointing to `~/.claude/helpers/omniroute-key.sh`.
  - Update `cockpit()` zsh launcher function in `~/.zshrc` to align with the direct OmniRoute port 20129 route.

## Capabilities

### Modified Capabilities
- `docker-lifecycle`: Remove `claude-code-provider-adapter` from registered compose stack requirements and streamline lifecycle drainage, bring-up, and watchdog health probing to focus on OmniRoute.
- `claude-code-omniroute-pm-routing`: Expand scope to cover unified Claude Code launcher routing (`omniroute`, `cockpit`, `shopapikey`) through OmniRoute's native Messages endpoint (`/v1/messages` on port 20129).

## Non-Goals

- Modifying Cockpit Tools desktop core daemon listening on port 51006.
- Modifying OmniRoute internal source code or transpiling new translators (uses native `openai-responses.ts`).
- Altering external credential storage in `~/.zshenv`.

## Affected Ownership Boundaries

- **Workstation Lifecycle Management**: `~/Developer/scripts/docker-service.sh`, `~/Developer/scripts/omniroute-watchdog.sh`.
- **OmniRoute Storage**: `~/Omniroute` named volume `omniroute-data` (`storage.sqlite`).
- **Platform Infrastructure**: `~/Developer/platform/claude-code-provider-adapter/`.
- **User Environment & Agent Configuration**: `~/.zshrc`, `~/.claude/profiles/cockpit.json`, `~/Library/LaunchAgents/`.
