# Spec Delta

## ADDED Requirements

### Requirement: Non-interactive privileged helper provisioning on start and restart

The Docker Desktop lifecycle script (`docker-service.sh`) SHALL non-interactively verify and provision macOS privileged helpers (`com.docker.vmnetd` and `com.docker.socket`) before starting or restarting the daemon, clear any pending `osascript` privilege dialogs, and safely expand empty Compose profile arrays under macOS Bash 3.2 `set -u`.

#### Scenario: Missing or mismatched vmnetd helper is provisioned before daemon start
- **WHEN** `docker-service.sh start` or `docker-service.sh restart` executes and `/Library/LaunchDaemons/com.docker.vmnetd.plist`, `/Library/LaunchDaemons/com.docker.socket.plist`, or `/var/run/docker.sock` is missing, or `/Library/PrivilegedHelperTools/com.docker.vmnetd` differs byte-for-byte from `/Applications/Docker.app/Contents/Library/LaunchServices/com.docker.vmnetd`, or `com.docker.vmnetd` is not running
- **THEN** `ensure_helpers()` SHALL invoke `sudo -n /Applications/Docker.app/Contents/MacOS/install config --user "${USER:-$(id -un)}" set-vmnetd set-docker-socket` and `sudo -n launchctl kickstart -p system/com.docker.vmnetd` before calling `docker desktop start` or `docker desktop restart`
- **AND** `com.docker.backend` SHALL start without spawning an interactive `SecurityAgent` password dialog.

#### Scenario: Pending osascript privileged prompt is cleared automatically
- **WHEN** `ensure_helpers()` finds any `/tmp/docker-desktop-privileged*` directory left by a prior `com.docker.backend` `osascript` invocation
- **THEN** it SHALL write `0` to `exitcode.txt` inside that directory and terminate the matching `osascript` process via `pkill -f` so headless startup is not blocked.

#### Scenario: Bash 3.2 empty profile_args expansion succeeds across all registered stacks
- **WHEN** `docker-service.sh drain` or `docker-service.sh up` iterates over `COMPOSE_STACKS` under macOS `/bin/bash` 3.2 with `set -euo pipefail`
- **THEN** it SHALL expand `${profile_args[@]+"${profile_args[@]}"}` without raising an `unbound variable` error on stacks with an empty `profile_args` array (`/Users/androidteam/Developer/shb/shb-schedule`) while passing `--profile base` for `/Users/androidteam/Omniroute`.
