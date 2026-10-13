# Design

## Context

See `proposal.md - Why` for motivation. Technical constraints and observed system state:
- **Adapter Topology**: `claude-code-provider-adapter` (Python 3.12, FastAPI, Uvicorn) was built to translate Claude Code's Anthropic Messages protocol into OpenAI Responses requests for Cockpit Tools (`http://host.docker.internal:51006/v1/responses`). It publishes `127.0.0.1:8788` to the host.
- **Gateway Capability**: OmniRoute v3.8.51 running in container `omniroute` natively supports custom provider nodes with `api_type: "responses"` (`openai-compatible-responses-*`) pointing to OpenAI Responses endpoints, including `http://host.docker.internal:51006/v1`.
- **Dialect Parity Verified**: Probing OmniRoute on `POST http://127.0.0.1:20129/v1/messages` with model `cockpit/gpt-5.6-luna` forwards the request directly to Cockpit Tools upstream (`host.docker.internal:51006`), returning the exact upstream response payload. This proves that OmniRoute completely supersedes the Python adapter.

## Goals / Non-Goals

**Goals:**
- Formally register Cockpit Tools as a first-class custom provider node in OmniRoute's SQLite database (`storage.sqlite`).
- Reconcile `cockpit()` in `~/.zshrc` and `~/.claude/profiles/cockpit.json` to route to `http://localhost:20129` with model `cockpit/gpt-5.6-luna`.
- Safely decommission `claude-code-provider-adapter`, unregister its LaunchAgent, and prune its references from `docker-service.sh` and `omniroute-watchdog.sh`.

**Non-Goals:**
- Modifying Cockpit Tools' port 51006 daemon.
- Deleting the `platform/claude-code-provider-adapter` repository directory (retained as an archive).

## Decisions

### D1: Register Cockpit as an `openai-compatible-responses` Node in OmniRoute
*Decision*: Configure `provider_nodes` (`openai-compatible-responses-cockpit`) and `provider_connections` (`c0ckp1t0-0000-4000-a000-000000000001`), referencing encrypted `HERMES_CUSTOM_COCKPIT_API_KEY`.
*Rationale*: Leverages OmniRoute's battle-tested `openai-responses.ts` request translator and streaming response translator, unifying all local agent proxying under a single gateway.

### D2: Update Claude Code Cockpit Launcher & Profile
*Decision*:
- Update `~/.claude/profiles/cockpit.json` to set `ANTHROPIC_BASE_URL: "http://localhost:20129"`, model `cockpit/gpt-5.6-luna`, and `apiKeyHelper: "~/.claude/helpers/omniroute-key.sh"`.
- Update `cockpit()` in `~/.zshrc` to point to port 20129.
*Rationale*: All Claude Code launchers (`omniroute`, `shopapikey`, `cockpit`) now share the standardized OmniRoute loopback port and authentication helper.

### D3: Drain Container and Unload LaunchAgent
*Decision*: Execute `docker compose down` in `platform/claude-code-provider-adapter`, unload `com.workspace.claude-code-provider-adapter` via launchctl, and remove port 8788 probes from `docker-service.sh` and `omniroute-watchdog.sh`.
*Rationale*: Eliminates a redundant container and background launchd daemon, saving host memory and CPU cycles.

## Risks / Trade-offs

- **Risk: Upstream Cockpit Account Availability**: Cockpit Tools upstream may return `auth_unavailable: No available account` when the user's upstream pool is exhausted.
  - *Mitigation*: Both the legacy adapter on port 8788 and OmniRoute on port 20129 receive and return the exact same upstream error message from Cockpit Tools. OmniRoute does not alter or swallow upstream account errors.
