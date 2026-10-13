# Design

## Context

See `proposal.md - Why` for motivation. Technical constraints and observed system state:
- **Adapter Topology**: `claude-code-provider-adapter` (Python 3.12, FastAPI, Uvicorn) was built to translate Claude Code's Anthropic Messages protocol into OpenAI Responses requests for Cockpit Tools (`http://host.docker.internal:51006/v1/responses`). It publishes `127.0.0.1:8788` to the host.
- **Gateway Capability**: OmniRoute v3.8.51 running in container `omniroute` directly supports both Anthropic Messages (`/v1/messages` on port 20129) and OpenAI Responses (`openai-responses.ts`), while Cockpit Tools runs directly on the macOS host (listening on port 51006).
- **Workspace Burden**: Running the adapter sidecar requires a separate Docker container, a user LaunchAgent (`com.workspace.claude-code-provider-adapter`), compose stack lifecycle hooks in `docker-service.sh`, and health monitoring in `omniroute-watchdog.sh`.

## Goals / Non-Goals

**Goals:**
- Eliminate the standalone adapter container and its LaunchAgent, reducing host RAM usage and container count.
- Update `docker-service.sh` and `omniroute-watchdog.sh` to supervise strictly `~/Omniroute`.
- Reconcile `~/.zshrc` Claude Code launcher functions and profiles to remove references to port 8788 without breaking developer workflows.

**Non-Goals:**
- Deleting the `platform/claude-code-provider-adapter` repository directory (the repository remains archived for historical provenance).
- Modifying Cockpit Tools' port 51006 daemon.

## Decisions

### D1: Drain Container and Unload LaunchAgent
*Alternative considered*: Leaving the container stopped but loaded in launchd.
*Decision*: Fully drain the container via `docker compose down`, unload the LaunchAgent via `launchctl bootout "gui/$(id -u)/com.workspace.claude-code-provider-adapter"`, and rename/disable the plist.
*Rationale*: Prevents launchd from attempting to restart a dead container or spamming log files.

### D2: Streamline `docker-service.sh` and `omniroute-watchdog.sh`
*Alternative considered*: Keeping empty check loops.
*Decision*: Prune `COMPOSE_STACKS` in `~/Developer/scripts/docker-service.sh` to solely `/Users/androidteam/Omniroute`. In `omniroute-watchdog.sh`, eliminate the port 8788 HTTP probe.
*Rationale*: Reduces watchdog probe latency and ensures `docker-service.sh drain`, `stop`, `restart`, and `up` operate on the single authoritative gateway stack.

### D3: Reconcile Claude Code Launcher Configuration
*Alternative considered*: Retaining `http://localhost:8788` with a proxy redirect.
*Decision*: Update `cockpit()` in `~/.zshrc` and `~/.claude/profiles/cockpit.json` to route directly or use OmniRoute's native translation dialect.
*Rationale*: Clean cutover without shims per workspace completeness rules.

## Risks / Trade-offs

- **Risk: Breaking `cockpit()` CLI launcher**: If an active session invokes `cockpit` while port 8788 is down before the launcher function is updated, Claude Code fails with `ECONNREFUSED`.
  - *Mitigation*: Update `~/.zshrc` and verify `omniroute`, `shopapikey`, and `cockpit` launchers before final cutover verification.
