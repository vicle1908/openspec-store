# Proposal

## Why

The OmniRoute supervisor watchdog (`~/Developer/scripts/omniroute-watchdog.sh`) previously issued `docker compose up -d` whenever OmniRoute was unhealthy or unresponsive. However, when OmniRoute's internal Node.js event loop deadlocks while the container remains in `State.Status == "running"`, Docker Compose treats the running container as already up to date, leaving the wedged process running indefinitely without recovery. Furthermore, unmanaged background test containers can saturate the Docker Desktop LinuxKit VM CPU and I/O, precipitating kernel uninterruptible disk sleep on large SQLite database checks. We must harden the supervisor watchdog to explicitly restart deadlocked running containers and ensure idle test stacks are stopped to protect gateway availability.

## What Changes

- **Watchdog Self-Healing Deadlock Recovery**:
  - Update `~/Developer/scripts/omniroute-watchdog.sh` to branch on container status:
    - If `omni_status == "running"` and `/healthz` fails (outside the `starting` grace period), execute `docker compose restart omniroute-base`.
    - If `omni_status != "running"`, execute `docker compose up -d`.
- **Workstation Lifecycle & VM Starvation Remediation**:
  - Drain idle, unmanaged test stacks (`microservices-platform-e2e` in `platform/go-microservices/deploy`) that thrash LinuxKit VM resources.
  - Purge orphaned zombie container processes in the Docker engine VM.
- **Verification & Specification Alignment**:
  - Update `docker-lifecycle` spec to require active container restarts for deadlocked running containers.
  - Verify OmniRoute `/healthz` returns `HTTP 200 OK`, port 20129 is responsive, and watchdog runs cleanly with exit code 0.

## Capabilities

### Modified Capabilities
- `docker-lifecycle`: Update `Continuous supervisor watchdog monitoring` requirement so that unresponsive containers in `running` status trigger an explicit container restart (`docker compose restart omniroute-base`) rather than a passive `docker compose up -d`.

## Non-Goals

- Altering OmniRoute application-level token caching, combo logic, or database schema.
- Replacing Docker Desktop on macOS with alternate container runtimes.
- Modifying microservice application business logic.

## Affected Ownership Boundaries

- **Workstation Lifecycle Management**: `~/Developer/scripts/omniroute-watchdog.sh`.
- **Docker Stacks**: `~/Omniroute`, `~/Developer/platform/go-microservices/deploy`.
- **OpenSpec Store**: `platform/openspec-store/openspec/specs/docker-lifecycle/spec.md`.
