# Tasks

## 1. Privileged Helpers & Daemon Lifecycle Hardening

- [x] 1.1 Register Docker Desktop privileged helpers (`com.docker.socket`, `com.docker.vmnetd`) into system launchd via official install command.
- [x] 1.2 Fix unbound variable `${timeout_sec}` in `~/Developer/scripts/docker-service.sh` under `set -euo pipefail`.
- [x] 1.3 Add `cmd_up` to `docker-service.sh` and integrate into `cmd_restart` for automatic stack restoration.

## 2. OmniRoute & Dependency Restart Policy Alignment

- [x] 2.1 Update `~/Omniroute/docker-compose.override.yml` with `restart: always` for `omniroute-base` and `redis`.
- [x] 2.2 Pin `COMPOSE_PROFILES=base` in `~/Omniroute/.env` to ensure `omniroute-base` is included by default on `docker compose up -d`.
- [x] 2.3 Update `platform/claude-code-provider-adapter/docker-compose.yml` with `restart: always` and reconcile LaunchAgent repo paths.
- [x] 2.4 Apply updated restart policies to live containers and verify `HostConfig.RestartPolicy.Name` equals `always`.

## 3. Continuous Supervisor Watchdog Implementation

- [x] 3.1 Implement `~/Developer/scripts/omniroute-watchdog.sh` with Docker daemon check, endpoint probing, and startup grace handling.
- [x] 3.2 Create and load macOS LaunchAgent `~/Library/LaunchAgents/com.omniroute.watchdog.plist` running every 120 seconds.
- [x] 3.3 Validate watchdog fault-injection recovery by stopping `omniroute` and asserting automated self-healing.

## 4. End-to-End Connectivity & OpenSpec Validation

- [x] 4.1 Verify OmniRoute `/healthz`, `/api/monitoring/health`, and model catalog endpoints.
- [x] 4.2 Smoke test live LLM routing through OMP (`omniroute-anthropic` and `omniroute` OpenAI gateway).
- [x] 4.3 Validate change artifacts strictly via `openspec validate --strict --json --store openspec-store`.
