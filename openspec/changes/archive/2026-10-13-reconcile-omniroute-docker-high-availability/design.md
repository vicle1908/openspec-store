# Design

## Context

See `proposal.md - Why` for motivation. Technical constraints and facts observed on this macOS workstation (Darwin 27.0.0, Apple Silicon):
- **Docker Desktop Architecture**: Runs via Apple Virtualization Framework with LinuxKit VM on `desktop-linux` context, communicating via socket `~/.docker/run/docker.sock` and privileged helper tools (`/Library/PrivilegedHelperTools/com.docker.socket`, `com.docker.vmnetd`).
- **Compose Conventions**: SQLite databases use Docker named volumes (`omniroute-data:/app/data`) to eliminate VirtioFS WAL corruption per `docker-resource-access`. Port bindings are strictly loopback (`127.0.0.1:20128`, `127.0.0.1:20129`, `127.0.0.1:8788`).
- **Supervision Gaps**: While macOS login items launch Docker Desktop on GUI user login, stopped containers remained stopped under `unless-stopped` if manually terminated or aborted during transient daemon errors.
- **Service Stack Roster**: `~/Developer/scripts/docker-service.sh` registers `~/Omniroute` and `~/Developer/platform/claude-code-provider-adapter`.

## Goals / Non-Goals

**Goals:**
- Provide four-tier resilience: (1) Host login/helper autostart, (2) Engine `always` restart policies, (3) CLI lifecycle stack restoration on restart, (4) Continuous launchd periodic supervisor watchdog.
- Guarantee OmniRoute base service is never omitted by `docker compose up -d` by default profile binding.
- Ensure zero false restarts while the container is in its 6–8s internal route initialization phase (`health: starting`).

**Non-Goals:**
- Modifying container base images or recompiling upstream code.
- Intercepting network traffic or replacing host reverse proxies.

## Decisions

### D1: Upgrade Container Restart Policies to `always`
*Alternative considered*: Keeping `unless-stopped`.
*Decision*: Configure `restart: always` in `docker-compose.override.yml` for `omniroute-base` and `redis`, and in `claude-code-provider-adapter/docker-compose.yml`.
*Rationale*: `unless-stopped` records an explicit stop flag when containers are stopped by manual intervention or transient crashes during daemon restarts. `always` instructs Docker engine to always restart the container upon daemon startup regardless of prior exit status.

### D2: Default Profile Setting in `~/Omniroute/.env`
*Alternative considered*: Requiring every script and caller to pass `--profile base`.
*Decision*: Set `COMPOSE_PROFILES=base` directly in `~/Omniroute/.env`.
*Rationale*: Upstream `docker-compose.yml` places `omniroute-base` under `profiles: [base]`. Without `COMPOSE_PROFILES=base`, standard `docker compose up -d` invocations start only Redis, leaving OmniRoute unstarted. Setting this in `.env` guarantees all compose invocations activate the gateway.

### D3: Workstation Lifecycle Wrapper Enhancement (`docker-service.sh`)
*Decision*:
1. Fix `${timeout_sec}` variable binding under `set -euo pipefail` in `cmd_start()`.
2. Add `cmd_up()` subcommand iterating `COMPOSE_STACKS`.
3. In `cmd_restart()`, invoke `cmd_up()` after verifying the Docker daemon socket is reachable.
*Rationale*: Ensures operators and automated maintenance runners using `docker-service.sh restart` do not leave stacks in a drained state.

### D4: LaunchAgent Periodic Supervisor Watchdog (`com.omniroute.watchdog`)
*Decision*: Implement `~/Developer/scripts/omniroute-watchdog.sh` scheduled via launchd every 120 seconds.
*Rationale*: Native Docker engine handles container restarts while the daemon runs, but cannot recover if the daemon itself stalls or if containers enter a degraded state without exiting. The watchdog probes:
1. `docker info`: If down, executes `docker-service.sh start`.
2. `omniroute`: Checks container status and `/healthz` on `127.0.0.1:20128`. If `health == "starting"`, grants startup grace period to avoid flapping.
3. `claude-code-provider-adapter`: Checks `/health` on `127.0.0.1:8788`.

## Risks / Trade-offs

- **Risk: Flapping during container boot**: OmniRoute initialization takes ~6 seconds to mount SQLite and register routes, reporting `starting` health status.
  - *Mitigation*: Watchdog inspects `.State.Health.Status` and skips restart if status is `starting`.
- **Risk: Resource contention on reboot**: Multiple stacks starting simultaneously on system login.
  - *Mitigation*: Watchdog runs with 120-second interval, and `docker-service.sh` uses ordered sequential compose startup.
