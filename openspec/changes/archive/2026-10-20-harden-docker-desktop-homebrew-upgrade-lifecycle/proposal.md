# Proposal

## Why

When Homebrew upgrades the `docker-desktop` cask (`brew upgrade --cask docker-desktop`, e.g., to `4.96.0,243774`), Homebrew executes the previous cask version's `uninstall` stanza (`quit: com.docker.docker`, `launchctl: [com.docker.helper, com.docker.socket, com.docker.vmnetd]`, `delete: [/Library/PrivilegedHelperTools/com.docker.socket, /Library/PrivilegedHelperTools/com.docker.vmnetd]`), which stops Docker Desktop and removes its privileged helpers without reinstalling `com.docker.vmnetd` or `com.docker.socket` in `postflight`.

On subsequent startup of `com.docker.backend` (triggered by `omniroute-watchdog.sh` or `docker-service.sh start`), `configureVmnetd` detects `vmnetd is not installed on this system` and spawns `/usr/bin/osascript` (`with administrator privileges`) to run `/Applications/Docker.app/Contents/MacOS/install config --user androidteam set-vmnetd set-docker-socket`. This blocks headless startup behind a modal `SecurityAgent` password dialog (`"Allow administrator access for a script started by “Docker”?"`). Additionally, `cmd_drain` and `cmd_up` in `/Users/androidteam/Developer/scripts/docker-service.sh` expanded `${profile_args[@]}` unguarded under macOS `/bin/bash` 3.2 `set -euo pipefail`, failing with `profile_args[@]: unbound variable` on stacks with an empty `profile_args=()` array (`/Users/androidteam/Developer/shb/shb-schedule`).

## What Changes

- **Non-Interactive Privileged Helper Provisioning & Dialog Recovery (`~/Developer/scripts/docker-service.sh`)**:
  - Add `ensure_helpers()` invoked at the start of `cmd_start` and `cmd_restart` before `docker desktop start`/`restart`.
  - When `/Library/LaunchDaemons/com.docker.vmnetd.plist`, `/Library/LaunchDaemons/com.docker.socket.plist`, or `/var/run/docker.sock` is missing, or `/Library/PrivilegedHelperTools/com.docker.vmnetd` does not match `/Applications/Docker.app/Contents/Library/LaunchServices/com.docker.vmnetd` (`cmp -s`), or `com.docker.vmnetd` is not running (`pgrep -x com.docker.vmnetd`), execute `sudo -n /Applications/Docker.app/Contents/MacOS/install config --user "${USER:-$(id -un)}" set-vmnetd set-docker-socket` and `sudo -n launchctl kickstart -p system/com.docker.vmnetd`.
  - Clear any pending `/tmp/docker-desktop-privileged*` `osascript` dialog directories (`echo 0 > "$priv_dir/exitcode.txt"` + `pkill -f "$priv_dir"`) so headless startup never stalls behind a modal `SecurityAgent` prompt.
  - Fix macOS Bash 3.2 `set -u` empty array expansion in `cmd_drain` and `cmd_up` using `${profile_args[@]+"${profile_args[@]}"}` so registered stacks without Compose profiles (`/Users/androidteam/Developer/shb/shb-schedule`) drain and start cleanly alongside `/Users/androidteam/Omniroute` (`--profile base`).
- **Post-Cask-Upgrade Restoration & Provenance Mirroring (`workstation-daily-update.sh`, `shb-schedule`, `config/script-provenance-manifest.tsv`)**:
  - Update `/Users/androidteam/Developer/scripts/workstation-daily-update.sh` (and its provenance mirror in `/Users/androidteam/Developer/platform/openspec-store/scripts/workstation-daily-update.sh`) and the durable `shb-schedule` `workstation-daily-update` workflow (`/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py`) so that immediately after `brew upgrade --cask`, if `/Applications/Docker.app/Contents/MacOS/install` and `/Users/androidteam/Developer/scripts/docker-service.sh` are executable, the pipeline runs `docker-service.sh start` and `docker-service.sh up`.
  - Register `/Users/androidteam/Developer/scripts/docker-service.sh` -> `scripts/docker-service.sh` (`executed`) in `/Users/androidteam/Developer/platform/openspec-store/config/script-provenance-manifest.tsv` and mirror `docker-service.sh` byte-for-byte into `/Users/androidteam/Developer/platform/openspec-store/scripts/docker-service.sh`.

## Non-Goals

- Modifying upstream Homebrew cask definitions in `homebrew/cask` (`docker-desktop.rb`).
- Disabling macOS `SecurityAgent` or system-wide TCC authorization outside Docker Desktop's official `/Applications/Docker.app/Contents/MacOS/install` binary.
- Changing container configurations in `/Users/androidteam/Omniroute` or `/Users/androidteam/Developer/shb/shb-schedule`.

## Affected Ownership Boundaries

- **Workstation Lifecycle Scripts**: `/Users/androidteam/Developer/scripts/docker-service.sh` and `/Users/androidteam/Developer/scripts/workstation-daily-update.sh`.
- **Durable Scheduler Workflow**: `/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py`.
- **OpenSpec Governance Store**: `/Users/androidteam/Developer/platform/openspec-store` (`config/script-provenance-manifest.tsv`, `scripts/docker-service.sh`, `scripts/workstation-daily-update.sh`, `openspec/specs/docker-lifecycle/spec.md`, `openspec/specs/portable-workstation-toolchain/spec.md`).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `docker-lifecycle`: Add requirement for non-interactive privileged helper (`com.docker.vmnetd`, `com.docker.socket`) provisioning, stale `osascript` privilege dialog cleanup, and Bash 3.2 `set -u`-safe Compose profile array expansion in `docker-service.sh`.
- `portable-workstation-toolchain`: Add requirement for post-cask-upgrade Docker Desktop helper/stack restoration (`docker-service.sh start` + `docker-service.sh up`) in daily maintenance workflows and SHA-256 provenance tracking of `docker-service.sh` in `config/script-provenance-manifest.tsv`.

## Impact

- **Zero Modal SecurityAgent Prompts**: `brew upgrade --cask docker-desktop` no longer leaves `com.docker.vmnetd` uninstalled or stalls `omniroute-watchdog.sh` / `docker-service.sh` behind a GUI password dialog.
- **Automatic Stack Recovery**: Registered Compose stacks (`/Users/androidteam/Omniroute` and `/Users/androidteam/Developer/shb/shb-schedule`) automatically resume immediately after cask upgrades.
- **Provenance Integrity**: `docker-service.sh` is versioned and SHA-256 drift-checked alongside the other 8 workstation maintenance scripts.
