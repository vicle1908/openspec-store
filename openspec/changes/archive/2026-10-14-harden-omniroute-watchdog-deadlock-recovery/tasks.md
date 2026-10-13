# Tasks

## 1. Supervisor Watchdog Implementation Hardening

- [x] 1.1 Inspect `~/Developer/scripts/omniroute-watchdog.sh` and identify recovery limitation where `docker compose up -d` skips running containers.
- [x] 1.2 Update `omniroute-watchdog.sh` to branch on container status, invoking `docker compose restart omniroute-base` when `omni_status == "running"` and health probe fails.
- [x] 1.3 Preserve `docker compose up -d` execution when container is not running or halted.

## 2. Docker LinuxKit VM & Contention Remediation

- [x] 2.1 Terminate hanging buildkit prune processes (`docker builder prune -f`) on the host.
- [x] 2.2 Drain unmanaged background test containers (`microservices-platform-e2e` in `platform/go-microservices/deploy`).
- [x] 2.3 Force-stop Docker Desktop to terminate LinuxKit kernel zombie processes and restart cleanly via `docker-service.sh start`.
- [x] 2.4 Verify SQLite storage hydration completes without entering kernel uninterruptible disk sleep.

## 3. Verification & OpenSpec Validation

- [x] 3.1 Verify OmniRoute container transitions to healthy status (`docker ps`).
- [x] 3.2 Verify HTTP reachability on `127.0.0.1:20128/healthz` returning `HTTP 200 OK`.
- [x] 3.3 Verify API port `127.0.0.1:20129` authentication gate responsiveness.
- [x] 3.4 Execute `omniroute-watchdog.sh` directly and verify clean zero exit code.
- [x] 3.5 Validate OpenSpec change strictly via `openspec validate harden-omniroute-watchdog-deadlock-recovery --strict --store openspec-store`.
