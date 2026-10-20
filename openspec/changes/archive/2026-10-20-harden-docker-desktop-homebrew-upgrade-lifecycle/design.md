# Design

## Context

See `proposal.md` — Why for problem motivation.

Root-cause analysis of the macOS `SecurityAgent` popup (`"Allow administrator access for a script started by “Docker”?"`) and headless startup stall following `brew upgrade --cask docker-desktop` (`4.96.0,243774`):

1. **Homebrew Cask `uninstall` Stanza Removes Privileged Helpers Without `postflight` Reinstall**:
   - The `docker-desktop` cask defines an `uninstall` stanza that runs before the new `.app` bundle is moved into `/Applications/Docker.app`:
     - `quit: "com.docker.docker"`
     - `launchctl: ["com.docker.helper", "com.docker.socket", "com.docker.vmnetd"]`
     - `delete: ["/Library/PrivilegedHelperTools/com.docker.socket", "/Library/PrivilegedHelperTools/com.docker.vmnetd"]`
   - Because `docker-desktop` does not run `/Applications/Docker.app/Contents/MacOS/install` in a cask `postflight` block, `/Library/PrivilegedHelperTools/com.docker.vmnetd` and `/Library/LaunchDaemons/com.docker.vmnetd.plist` remain absent after `brew upgrade --cask` completes.
2. **`com.docker.backend` Spawns Modal `osascript` Prompt When `vmnetd` Is Missing**:
   - When `omniroute-watchdog.sh` or `docker-service.sh start` subsequently invokes `docker desktop start`, `com.docker.backend` runs `configureVmnetd`.
   - Finding `/Library/PrivilegedHelperTools/com.docker.vmnetd` absent or outdated, `com.docker.backend` creates `/tmp/docker-desktop-privileged.<random>/` and executes `/usr/bin/osascript` (`do shell script "/Applications/Docker.app/Contents/MacOS/install config --user androidteam set-vmnetd set-docker-socket" with administrator privileges`).
   - This raises a modal `SecurityAgent` window on the macOS desktop and blocks `docker desktop start` until interactive credentials are entered or the timeout expires.
3. **macOS Bash 3.2 `set -u` Empty Array Expansion in `docker-service.sh`**:
   - In `cmd_drain()` and `cmd_up()` of `/Users/androidteam/Developer/scripts/docker-service.sh`, `local profile_args=()` is populated with `(--profile base)` only for `/Users/androidteam/Omniroute` and remains empty for `/Users/androidteam/Developer/shb/shb-schedule`.
   - Under macOS `/bin/bash` 3.2 with `set -euo pipefail`, unguarded `"${profile_args[@]}"` throws `profile_args[@]: unbound variable` when `profile_args` is empty, aborting `cmd_drain` and `cmd_up` before reaching the second stack.

## Goals / Non-Goals

**Goals:**
- Provision `/Library/PrivilegedHelperTools/com.docker.vmnetd`, `/Library/PrivilegedHelperTools/com.docker.socket`, `/Library/LaunchDaemons/com.docker.vmnetd.plist`, `/Library/LaunchDaemons/com.docker.socket.plist`, and `/var/run/docker.sock` non-interactively via `sudo -n /Applications/Docker.app/Contents/MacOS/install` inside `ensure_helpers()` before `docker desktop start` or `docker desktop restart`.
- Dismiss any stale `/tmp/docker-desktop-privileged*` `osascript` dialog processes automatically inside `ensure_helpers()`.
- Guard empty array expansion in `cmd_drain` and `cmd_up` with `${profile_args[@]+"${profile_args[@]}"}` for Bash 3.2 `set -u` compatibility.
- Automatically invoke `docker-service.sh start` and `docker-service.sh up` after `brew upgrade --cask` in both `workstation-daily-update.sh` and `shb-schedule`'s `workstation_update.py` workflow.
- Track `/Users/androidteam/Developer/scripts/docker-service.sh` in `config/script-provenance-manifest.tsv` with a byte-identical mirror in `/Users/androidteam/Developer/platform/openspec-store/scripts/docker-service.sh`.

**Non-Goals:**
- Modifying upstream Homebrew cask files or Docker Desktop's internal binaries.
- Altering container runtime definitions in `~/Omniroute` or `~/Developer/shb/shb-schedule`.

## Decisions

### 1. Pre-Start Privileged Helper Provisioning (`ensure_helpers()` in `docker-service.sh`)
- `ensure_helpers()` checks five conditions when `/Applications/Docker.app/Contents/MacOS/install` is executable:
  1. `[[ ! -f "/Library/LaunchDaemons/com.docker.vmnetd.plist" ]]`
  2. `[[ ! -f "/Library/LaunchDaemons/com.docker.socket.plist" ]]`
  3. `[[ ! -L "/var/run/docker.sock" ]]`
  4. `! cmp -s "/Applications/Docker.app/Contents/Library/LaunchServices/com.docker.vmnetd" "/Library/PrivilegedHelperTools/com.docker.vmnetd"`
  5. `! pgrep -x com.docker.vmnetd >/dev/null 2>&1`
- If any check fails, `ensure_helpers()` logs provisioning and runs:
  - `sudo -n /Applications/Docker.app/Contents/MacOS/install config --user "${USER:-$(id -un)}" set-vmnetd set-docker-socket >/dev/null 2>&1 || true`
  - `sudo -n launchctl kickstart -p system/com.docker.vmnetd >/dev/null 2>&1 || true`
- Next, it iterates over `/tmp/docker-desktop-privileged*`; for each existing directory, it writes `0` to `exitcode.txt` and terminates any lingering `osascript` helper matching that directory (`pkill -f "$priv_dir"`), releasing any blocked `com.docker.backend` caller.

### 2. Bash 3.2 `set -u` Safe Array Expansion in `cmd_drain` and `cmd_up`
- Replace `"${profile_args[@]}"` with `${profile_args[@]+"${profile_args[@]}"}` in both `cmd_drain()` and `cmd_up()` so Bash 3.2 expands `--profile base` for `/Users/androidteam/Omniroute` and expands to zero arguments (without triggering `unbound variable`) for `/Users/androidteam/Developer/shb/shb-schedule`.

### 3. Post-Cask-Upgrade Hook in Daily Maintenance & Provenance Tracking
- In `workstation-daily-update.sh` (Stage 1 Homebrew Maintenance) and `shb-schedule` (`src/shb_schedule/workflows/workstation_update.py`), immediately after `brew upgrade --cask`, check `[[ -x "/Applications/Docker.app/Contents/MacOS/install" && -x "/Users/androidteam/Developer/scripts/docker-service.sh" ]]` and run `docker-service.sh start` followed by `docker-service.sh up`.
- Add `/Users/androidteam/Developer/scripts/docker-service.sh	scripts/docker-service.sh	executed` to `/Users/androidteam/Developer/platform/openspec-store/config/script-provenance-manifest.tsv` (bringing the tracked script count from 8 to 9) and mirror both `docker-service.sh` and `workstation-daily-update.sh` into `platform/openspec-store/scripts/`.
