# docker-lifecycle

## Purpose

Ensure Docker Desktop is reliably operable by unattended automation on this macOS
workstation: it starts without interactive GUI clicks, stops cleanly with automated
stack drainage, provides machine-readable status via official CLI commands, and
recovers automatically on system reboot.

## Requirements

### Requirement: Daemon auto-start on login and reboot

Docker Desktop SHALL be configured so that the Docker daemon, LinuxKit VM, and privileged
helpers come up automatically after user login or reboot on this workstation.

#### Scenario: Workstation reboot or user login

- **WHEN** the workstation reboots and the `androidteam` user logs in
- **THEN** the Docker socket at `~/.docker/run/docker.sock` becomes responsive
  without the user manually opening the Docker Desktop GUI dashboard

#### Scenario: AutoStart disabled in settings-store

- **WHEN** `"AutoStart"` is `false` in
  `~/Library/Group Containers/group.com.docker/settings-store.json`
- **THEN** the lifecycle verification check flags the configuration as non-compliant
  and outputs the exact JSON key to update to `true`

#### Scenario: Login item missing or disabled

- **WHEN** the macOS `Docker Desktop` login item is missing from `System Events`
- **THEN** the lifecycle verification check reports the missing login item and
  provides the command to register it

### Requirement: Official CLI-backed lifecycle management

Workstation lifecycle management SHALL use the official Docker Desktop CLI commands
(`docker desktop start`, `docker desktop stop`, `docker desktop restart`, and
`docker desktop status`) as the underlying execution mechanism.

#### Scenario: Start when daemon is stopped

- **WHEN** `docker desktop status` reports `stopped` and `docker-service.sh start` is invoked
- **THEN** the service invokes `docker desktop start --timeout 90`, verifies socket
  reachability via `docker info`, and exits 0 within 90 seconds

#### Scenario: Start when daemon is already running

- **WHEN** `docker info` already succeeds and `docker-service.sh start` is invoked
- **THEN** the command detects the active daemon and exits 0 immediately without
  redundant relaunch calls

#### Scenario: Start timeout failure

- **WHEN** `docker desktop start --timeout 90` fails to initialize the engine within 90 seconds
- **THEN** the service captures diagnostic output, reports the failure status, and exits
  with a non-zero code

#### Scenario: Graceful stop with active compose stacks

- **WHEN** `docker-service.sh stop` is invoked while containers or compose stacks are active
- **THEN** running compose stacks are first drained via `docker compose down --timeout 30`,
  followed by `docker desktop stop --timeout 30`, ensuring no uncommitted WAL state or
  abrupt container terminations

#### Scenario: Force stop on ungraceful hang

- **WHEN** a graceful stop exceeds its timeout or hangs
- **THEN** the service executes `docker desktop stop --force` and confirms all backend
  VM processes have terminated

### Requirement: Machine-readable status and health verification

The lifecycle utility SHALL output structured, machine-parseable JSON status integrating
official `docker desktop status --format json` output with socket and helper diagnostics.

#### Scenario: Healthy running daemon

- **WHEN** `docker-service.sh status --json` is executed on an active system
- **THEN** it outputs valid JSON containing `{ "status": "running", "socket": "/Users/androidteam/.docker/run/docker.sock", "context": "desktop-linux", "helpers": { "vmnetd": true, "socket": true } }`
  and exits with code 0

#### Scenario: Stopped daemon inspection

- **WHEN** `docker-service.sh status --json` is executed while Docker is down
- **THEN** it outputs JSON indicating `{ "status": "stopped", "socket_responsive": false }`
  and exits with code 1

### Requirement: Actionable diagnostic reporting

When a lifecycle command encounters a missing component or helper failure, it SHALL
print the exact diagnostic findings and the remediation command.

#### Scenario: Privileged helper unloaded

- **WHEN** `com.docker.socket` or `com.docker.vmnetd` is missing from system launchd
- **THEN** the status check reports the missing helper and outputs the exact
  `/Applications/Docker.app/Contents/MacOS/install config` command required to restore it

### Requirement: Automated compose stack restoration on restart

The workstation lifecycle utility (`docker-service.sh`) SHALL support automated restoration of all registered compose stacks following daemon restart or explicit stack bring-up commands, targeting strictly primary gateway and application stacks.

#### Scenario: Restart restores registered compose stacks
- **WHEN** `docker-service.sh restart` is executed
- **THEN** the utility SHALL first drain registered stacks cleanly, restart Docker Desktop via the official CLI plugin, verify socket reachability, and invoke `cmd_up` to restore registered compose stacks (`~/Omniroute`) to active running status.

#### Scenario: Explicit up command starts registered stacks
- **WHEN** `docker-service.sh up` is executed
- **THEN** each configured compose stack in `COMPOSE_STACKS` SHALL be started via `docker compose up -d` without requiring manual directory navigation.

#### Scenario: Restart restores only primary gateway stack
- **WHEN** `docker-service.sh restart` or `docker-service.sh up` is executed
- **THEN** the utility SHALL target only active registered stacks (`~/Omniroute`)
- **AND** the decommissioned `claude-code-provider-adapter` path SHALL NOT be invoked or drained.

### Requirement: Container always restart policy alignment

Critical gateway and dependency containers SHALL configure and run with `HostConfig.RestartPolicy.Name` set to `always` in Docker Compose declarations and live container inspection, ensuring automatic restart across host reboots, engine restarts, and unhandled exits.

#### Scenario: Container inspect reflects always restart policy
- **WHEN** `docker inspect` is run against `omniroute`, `omniroute-redis`, or `claude-code-provider-adapter-adapter-1`
- **THEN** `HostConfig.RestartPolicy.Name` MUST equal `always`.

#### Scenario: Compose project default profile inclusion
- **WHEN** `docker compose up -d` is executed in `~/Omniroute` without explicit `--profile` flags
- **THEN** `COMPOSE_PROFILES=base` in `~/Omniroute/.env` MUST ensure `omniroute-base` and `redis` are both started.

### Requirement: Continuous supervisor watchdog monitoring

A periodic system supervisor (`com.omniroute.watchdog`) SHALL monitor the health of the Docker daemon and local gateway stacks and auto-recover unhealthy or missing services, omitting decommissioned sidecar endpoints from health evaluation.

#### Scenario: Unhealthy or halted container auto-recovery
- **WHEN** `omniroute` container is halted or fails HTTP health probes
- **THEN** `omniroute-watchdog.sh` SHALL execute `docker compose up -d` in the respective stack directory to restore service availability.

#### Scenario: Container startup grace period observed
- **WHEN** `omniroute` is in the `starting` health status during initial boot
- **THEN** the supervisor SHALL NOT trigger redundant restarts, allowing the container to complete internal model route initialization.

#### Scenario: Down daemon recovery attempt
- **WHEN** Docker daemon is unreachable during supervisor execution
- **THEN** the supervisor SHALL invoke `docker-service.sh start` before attempting container checks.

#### Scenario: Supervisor probes primary gateway without sidecars
- **WHEN** `omniroute-watchdog.sh` executes its periodic health probe cycle
- **THEN** it SHALL evaluate Docker daemon socket availability and OmniRoute `/healthz` on port 20128
- **AND** it SHALL NOT probe port 8788 or trigger restarts for `claude-code-provider-adapter`.
