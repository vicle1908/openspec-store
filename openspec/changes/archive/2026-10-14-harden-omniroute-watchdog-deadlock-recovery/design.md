# Design

## Context

See `proposal.md - Why` for motivation. Technical constraints and facts observed on this macOS workstation (Darwin 27.0.0, Apple Silicon):
- **Docker Compose Idempotency Contract**: `docker compose up -d` inspects existing containers. If a container is in `State.Status == "running"`, `docker compose up -d` skips recreating or restarting it even if `State.Health.Status == "unhealthy"`.
- **Node.js Main-Thread Deadlock Characteristics**: When high-concurrency requests or upstream proxy failures wedge the main event loop, the container process never exits, preventing Docker engine `restart: always` from triggering.
- **Resource Contention on LinuxKit VM**: Docker Desktop runs a LinuxKit VM with 8 CPUs and 5.78 GiB RAM. Leaving heavy multi-container development stacks (e.g. 31 microservice containers) active starves the VM CPU and leads to Linux page-cache wait hangs (`folio_wait_bit_common` in `D` state) during large SQLite database health checks (3.58 GB `storage.sqlite`).

## Goals / Non-Goals

**Goals:**
- Guarantee that `~/Developer/scripts/omniroute-watchdog.sh` terminates and recreates running-but-unresponsive OmniRoute containers via `docker compose restart omniroute-base`.
- Retain the non-disruptive `docker compose up -d` path for halted or unstarted stacks.
- Maintain the startup grace period (`health == "starting"`) to avoid false-positive flapping during SQLite hydration.

**Non-Goals:**
- Modifying OmniRoute container internals, Node.js code, or better-sqlite3 configuration.
- Changing Docker Compose override files or port bindings.

## Decisions

### D1: Branch on Container Status for Watchdog Self-Healing
*Alternative considered*: Calling `docker compose up -d --force-recreate` unconditionally.
*Decision*: Inspect `.State.Status`. If `running`, invoke `docker compose restart omniroute-base`. If not running, invoke `docker compose up -d`.
*Rationale*: `docker compose restart` immediately sends signals to the wedged container and re-spawns it, whereas `docker compose up -d` is a no-op on already running containers.

### D2: Drain Idle Test Stacks Post-Verification
*Alternative considered*: Allowing all development containers to run indefinitely.
*Decision*: Stop unmanaged background test containers (`microservices-platform-e2e`) when verification completes.
*Rationale*: LinuxKit VM CPU and I/O resources must be preserved for primary gateway services. Containers configured with `unless-stopped` will not automatically restart once stopped.

## Risks / Trade-offs

- **Risk: Service interruption during restart**: A restart briefly disconnects active connections.
  - *Mitigation*: The restart only fires when `/healthz` has already failed or timed out outside the 120s `starting` period.
