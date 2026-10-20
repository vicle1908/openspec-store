# docker-lifecycle Delta Specification

## MODIFIED Requirements

### Requirement: Non-interactive privileged helper provisioning on start and restart

The Docker Desktop lifecycle script (`docker-service.sh`) SHALL non-interactively verify and provision macOS privileged helpers (`com.docker.vmnetd` and `com.docker.socket`) before starting or restarting the daemon, clean up any pending `osascript` privilege dialogs, fall through to socket polling when `com.docker.backend` is mid-boot, and safely expand empty Compose profile arrays under Bash 3.2 `set -u`.

#### Scenario: Missing or mismatched vmnetd helper is provisioned before daemon start
- **WHEN** `docker-service.sh start` or `docker-service.sh restart` executes and `/Library/LaunchDaemons/com.docker.vmnetd.plist`, `/Library/LaunchDaemons/com.docker.socket.plist`, `/Library/PrivilegedHelperTools/com.docker.vmnetd`, or `/Library/PrivilegedHelperTools/com.docker.socket` is missing, or `/var/run/docker.sock` does not resolve to `${HOME}/.docker/run/docker.sock`, or `/var/run/com.docker.vmnetd.sock` is absent while `com.docker.vmnetd` is not running, or the installed helper binaries differ from `/Applications/Docker.app`
- **THEN** `ensure_helpers()` SHALL invoke `sudo -n /Applications/Docker.app/Contents/MacOS/install config --user "${USER:-$(id -un)}" set-vmnetd set-docker-socket` and `sudo -n launchctl kickstart -p system/com.docker.vmnetd` before calling `docker desktop start` or `docker desktop restart`
- **AND** `com.docker.backend` SHALL start without spawning an interactive `SecurityAgent` password dialog.

#### Scenario: Pending osascript privileged prompt is cleared automatically
- **WHEN** `ensure_helpers()` finds any `/tmp/docker-desktop-privileged*` directory left by a current or prior `com.docker.backend` `osascript` invocation
- **THEN** if a matching `osascript` process is running, it SHALL write `0` to `exitcode.txt`, terminate the `osascript` process via `pkill -f`, and wait 1 second for `com.docker.backend` to read `exitcode.txt`, and in all cases it SHALL remove `exitcode.txt`, `cmd`, and the temporary directory so stale directories do not accumulate.

#### Scenario: Mid-boot com.docker.backend falls through to socket readiness polling
- **WHEN** `docker-service.sh start` invokes `docker desktop start --timeout <sec>` and that CLI call returns non-zero while `com.docker.backend` is actively running and completing VM initialization
- **THEN** `cmd_start()` SHALL NOT exit `1` immediately, and SHALL instead proceed into the bounded `while ((waited < timeout_sec))` socket reachability loop until `docker info` succeeds or the timeout expires.

#### Scenario: Socket helper status requires installed binary and LaunchDaemon plist
- **WHEN** `docker-service.sh status` or `docker-service.sh status --json` evaluates `com.docker.socket` health
- **THEN** it SHALL report `com.docker.socket` as active/true only when `/Library/LaunchDaemons/com.docker.socket.plist` and executable `/Library/PrivilegedHelperTools/com.docker.socket` exist alongside the `/var/run/docker.sock` symlink (or a running `com.docker.socket` process).

#### Scenario: Bash 3.2 empty profile_args expansion succeeds across all registered stacks
- **WHEN** `docker-service.sh drain` or `docker-service.sh up` iterates over `COMPOSE_STACKS` under macOS `/bin/bash` 3.2 with `set -euo pipefail`
- **THEN** it SHALL expand `${profile_args[@]+"${profile_args[@]}"}` without raising an `unbound variable` error on stacks with an empty `profile_args` array (`/Users/androidteam/Developer/shb/shb-schedule`) while passing `--profile base` for `/Users/androidteam/Omniroute`.
