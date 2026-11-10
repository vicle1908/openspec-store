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

A periodic system supervisor (`com.omniroute.watchdog`) SHALL monitor Docker daemon and local gateway health, serialize its cycle via `/usr/bin/lockf` on `~/.omniroute/update.lock` at Step 0, coordinate with `workstation_update.py` during `docker-desktop` cask upgrades, force-recreate containers stuck in `restarting` state, omit decommissioned sidecar endpoints, and run a 6-hour read-only SQLite `PRAGMA integrity_check` without restarting a healthy gateway.

#### Scenario: Unhealthy or halted container auto-recovery
- **WHEN** `omniroute` container is halted or fails HTTP health probes outside the startup grace period
- **THEN** `omniroute-watchdog.sh` SHALL evaluate container status: if the container is running but unhealthy, it SHALL execute `docker compose restart omniroute-base`
- **AND** if the container is halted or not running, it SHALL execute `docker compose --profile base up -d` in the respective stack directory (adding `--no-build --pull never --force-recreate` when `omni_status` equals `restarting` so a damaged container writable layer is replaced cleanly) to restore service availability.

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

#### Scenario: Active update or maintenance lock suppresses watchdog restarts
- **WHEN** `omniroute-watchdog.sh` starts at Step 0 (before Docker daemon or container checks), opens persistent `~/.omniroute/update.lock` (`umask 077`) on file descriptor `9` (`exec 9>>"$LOCK_FILE"`), and invokes `/usr/bin/lockf -s -t 0 9`
- **THEN** if `/usr/bin/lockf` returns exit code `75` (`EX_TEMPFAIL` because `update.sh`, `workstation_update.py` during a `docker-desktop` cask upgrade, manual `/usr/bin/lockf -k -t 0 ~/.omniroute/update.lock` maintenance, or another watchdog instance holds the kernel lock), `omniroute-watchdog.sh` SHALL log that the maintenance lock is active and exit `0` without starting the daemon, restarting `omniroute`, or running `docker compose up -d`
- **AND** if `/usr/bin/lockf` fails with any other non-zero exit code, `omniroute-watchdog.sh` SHALL log an error and fail closed with a non-zero exit code
- **AND** when the kernel lock is acquired (`rc = 0`), `omniroute-watchdog.sh` SHALL retain open FD `9` across its entire cycle until process exit (closing `9>&-` on child invocations), SHALL ignore file contents/mtime without parsing PID/epoch metadata or expiring live locks by age, SHALL NEVER unlink `~/.omniroute/update.lock`, and SHALL remain byte-identical to `/Users/androidteam/Developer/platform/openspec-store/scripts/omniroute-watchdog.sh` per `config/script-provenance-manifest.tsv`.

#### Scenario: Periodic read-only SQLite integrity check runs every 6 hours without restarting a healthy gateway
- **WHEN** `omniroute` is `running`, `State.Health.Status != starting`, and `http://127.0.0.1:20128/healthz` returns HTTP 200 under the Step 0 FD `9` kernel lock, and `~/.omniroute/integrity-last-ok` is missing or its mtime is `>= 21600` seconds (6 hours) old
- **THEN** `omniroute-watchdog.sh` SHALL execute a read-only full `PRAGMA integrity_check` (`better-sqlite3` `{readonly:true, fileMustExist:true, timeout:15000}`, no `autoRepair`) bounded by an in-container child timeout of `110s` (`SIGKILL`) and outer `gtimeout --signal=TERM --kill-after=5s 120s`
- **AND** it SHALL update `~/.omniroute/integrity-last-ok` only when all returned rows equal `'ok'`, and on any integrity failure or timeout it SHALL log `ERROR` and exit non-zero without restarting the otherwise healthy `omniroute` container.

### Requirement: Non-interactive privileged helper provisioning on start and restart

The Docker Desktop lifecycle script (`docker-service.sh`) SHALL non-interactively verify and provision `com.docker.socket` before starting or restarting the daemon, pass `--user "$target_user"` to both `install config` and `install socket-symlink-on-startup`, synchronously enforce `/var/run/docker.sock`, clean up pending `osascript` dialogs, fall through to socket polling when `com.docker.backend` is mid-boot, and safely expand empty Compose profile arrays under Bash 3.2 `set -u`.

#### Scenario: Missing or mismatched vmnetd helper is provisioned before daemon start
- **WHEN** `docker-service.sh start` or `docker-service.sh restart` executes and `/Library/LaunchDaemons/com.docker.socket.plist` or `/Library/PrivilegedHelperTools/com.docker.socket` is missing, `/Library/LaunchDaemons/com.docker.socket.plist` does not contain `<string>${target_user}</string>`, `/var/run/docker.sock` does not resolve to `${HOME}/.docker/run/docker.sock`, or `/Library/PrivilegedHelperTools/com.docker.socket` differs from `/Applications/Docker.app/Contents/MacOS/com.docker.socket`
- **THEN** `ensure_helpers()` SHALL invoke `sudo -n /Applications/Docker.app/Contents/MacOS/install remove-vmnetd`, `sudo -n /Applications/Docker.app/Contents/MacOS/install config --user "$target_user"`, `sudo -n /Applications/Docker.app/Contents/MacOS/install socket-symlink-on-startup --user "$target_user"`, `sudo -n launchctl kickstart -p system/com.docker.socket`, and `sudo -n ln -sfn "$socket_path" /var/run/docker.sock` before calling `docker desktop start` or `docker desktop restart`
- **AND** `com.docker.backend` SHALL start without spawning an interactive `SecurityAgent` password dialog.

#### Scenario: Pending osascript privileged prompt is cleared automatically
- **WHEN** `ensure_helpers()` finds any `/tmp/docker-desktop-privileged*` directory left by a current or prior `com.docker.backend` `osascript` invocation
- **THEN** if a matching `osascript` process is running, it SHALL write `0` to `exitcode.txt`, terminate the `osascript` process via `pkill -f`, and wait 1 second for `com.docker.backend` to read `exitcode.txt`, and in all cases it SHALL remove `exitcode.txt`, `cmd`, and the temporary directory so stale directories do not accumulate.

#### Scenario: Mid-boot com.docker.backend falls through to socket readiness polling
- **WHEN** `docker-service.sh start` invokes `docker desktop start --timeout <sec>` and that CLI call returns non-zero while `com.docker.backend` is actively running and completing VM initialization
- **THEN** `cmd_start()` SHALL NOT exit `1` immediately, and SHALL instead proceed into the bounded `while ((waited < timeout_sec))` socket reachability loop until `docker info` succeeds or the timeout expires.

#### Scenario: Socket helper status requires installed binary and LaunchDaemon plist
- **WHEN** `docker-service.sh status` or `docker-service.sh status --json` evaluates `com.docker.socket` health
- **THEN** it SHALL report `com.docker.socket` as active/true only when `/Library/LaunchDaemons/com.docker.socket.plist` (containing `<string>${target_user}</string>`) and executable `/Library/PrivilegedHelperTools/com.docker.socket` exist alongside the `/var/run/docker.sock` symlink pointing to `${socket_path}`.

#### Scenario: Bash 3.2 empty profile_args expansion succeeds across all registered stacks
- **WHEN** `docker-service.sh drain` or `docker-service.sh up` iterates over `COMPOSE_STACKS` under macOS `/bin/bash` 3.2 with `set -euo pipefail`
- **THEN** it SHALL expand `${profile_args[@]+"${profile_args[@]}"}` without raising an `unbound variable` error on stacks with an empty `profile_args` array (`/Users/androidteam/Developer/shb/shb-schedule`) while passing `--profile base` for `/Users/androidteam/Omniroute`.
