# Proposal

## Why

Docker Desktop privileged helper registration and container restart policies previously allowed the OmniRoute AI gateway and its sidecar stacks to remain down after machine boot, helper corruption, or manual container halts, blocking local agent-CLI LLM connectivity. We need an unattended self-healing architecture combining engine-level `always` restart policies, an enhanced lifecycle wrapper (`docker-service.sh up/restart`), and a continuous launchd supervisor watchdog (`com.omniroute.watchdog`).

## What Changes

- **Engine Restart Policy Hardening**: Upgrade container restart policies from `unless-stopped` to `always` in `~/Omniroute/docker-compose.override.yml` (`omniroute-base`, `redis`) and `platform/claude-code-provider-adapter/docker-compose.yml`.
- **Default Profile Enforcement**: Pin `COMPOSE_PROFILES=base` in `~/Omniroute/.env` so unattended `docker compose up -d` invocations never silently omit `omniroute-base`.
- **Workstation Lifecycle Wrapper Enhancement**:
  - Fix unbound variable `${timeout_sec}` under `set -euo pipefail` in `~/Developer/scripts/docker-service.sh`.
  - Add `cmd_up` (`docker-service.sh up`) to bring up all registered compose stacks.
  - Connect `cmd_restart` to automatically bring up registered stacks after Docker daemon verification.
- **Continuous Supervisor Watchdog**:
  - Deploy `~/Developer/scripts/omniroute-watchdog.sh` to probe Docker daemon reachability, OmniRoute `/healthz` on port 20128, and adapter `/health` on port 8788.
  - Implement startup grace period handling so initializing containers are not restarted prematurely.
  - Supervise watchdog execution via macOS LaunchAgent `~/Library/LaunchAgents/com.omniroute.watchdog.plist` scheduled every 120 seconds.
- **Sidecar LaunchAgent Path Reconciliation**: Reconcile LaunchAgent path resolution in `platform/claude-code-provider-adapter/start-adapter.sh` and `config/com.workspace.claude-code-provider-adapter.plist`.

## Capabilities

### Modified Capabilities
- `docker-lifecycle`: Add requirements for automated compose stack restoration on daemon restart, container `always` restart policy alignment, and continuous supervisor watchdog health monitoring.

## Non-Goals

- Modifying OmniRoute application internal routing logic, token counters, or database schema.
- Replacing Docker Desktop on macOS with alternate container runtimes (such as OrbStack or Colima).
- Exposing OmniRoute ports publicly or outside loopback interface (`127.0.0.1`).

## Affected Ownership Boundaries

- **Workstation Lifecycle Management**: `~/Developer/scripts/docker-service.sh`, `~/Developer/scripts/omniroute-watchdog.sh`.
- **OmniRoute Deployment**: `~/Omniroute/docker-compose.override.yml`, `~/Omniroute/.env`.
- **Platform Adapter**: `~/Developer/platform/claude-code-provider-adapter/`.
- **macOS User LaunchAgents**: `~/Library/LaunchAgents/com.omniroute.watchdog.plist`, `~/Library/LaunchAgents/com.workspace.claude-code-provider-adapter.plist`.
