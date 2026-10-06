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
