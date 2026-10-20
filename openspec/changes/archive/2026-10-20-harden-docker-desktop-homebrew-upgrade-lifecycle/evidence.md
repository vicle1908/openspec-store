# Evidence: `harden-docker-desktop-homebrew-upgrade-lifecycle`

**Date**: 2026-10-20  
**Store**: `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`)  
**Implementation Roots**:
- `/Users/androidteam/Developer/scripts/docker-service.sh` (mirrored to `/Users/androidteam/Developer/platform/openspec-store/scripts/docker-service.sh`)
- `/Users/androidteam/Developer/scripts/workstation-daily-update.sh` (mirrored to `/Users/androidteam/Developer/platform/openspec-store/scripts/workstation-daily-update.sh`)
- `/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py`
- `/Users/androidteam/Developer/platform/openspec-store/config/script-provenance-manifest.tsv`

---

## 1. Root Cause & Live Docker Desktop Runtime Status

- **Installed Versions**:
  - Docker Desktop Cask: `4.96.0,243774`
  - Docker Engine: `29.9.1`
  - Docker Compose: `v5.6.0`
- **Live `docker-service.sh status` Output**:
  - `Status`: `running`
  - `Session ID`: `d390edc7-6b10-4259-8d02-b4eaba5157b2`
  - `Socket`: `/Users/androidteam/.docker/run/docker.sock (exists=true)`
  - `Context`: `desktop-linux`
  - `Helpers`: `com.docker.vmnetd: up`, `com.docker.socket: active (symlink verified)`
  - `Registered Stacks`:
    - `/Users/androidteam/Omniroute`: `2 running` (`http://127.0.0.1:20128/healthz` -> `ok`)
    - `/Users/androidteam/Developer/shb/shb-schedule`: `2 running` (`shb-schedule-scheduler-1` and `shb-schedule-db-1` healthy)

---

## 2. Computer Use AX & Simulated Cask `uninstall` Verification

- **Computer Use AX Inspection**:
  - Verified `SecurityAgent windows: []` (pending macOS `osascript` administrator dialog dismissed and cleared).
  - Verified Docker Desktop GUI window `window "Containers - Docker Desktop" [ref=e40]` reporting `"Engine running"` and `"You are up to date"`.
- **Simulated Homebrew Cask `uninstall` Test**:
  - Simulated the exact `docker-desktop` cask `uninstall` helper removal:
    ```bash
    sudo -n launchctl bootout system/com.docker.vmnetd
    sudo -n rm -f /Library/PrivilegedHelperTools/com.docker.vmnetd /Library/LaunchDaemons/com.docker.vmnetd.plist
    ```
  - Executed `/Users/androidteam/Developer/scripts/docker-service.sh start`:
    - `ensure_helpers()` detected the missing helper/plist and ran `sudo -n /Applications/Docker.app/Contents/MacOS/install config --user androidteam set-vmnetd set-docker-socket` + `sudo -n launchctl kickstart -p system/com.docker.vmnetd`.
    - Restored `/Library/PrivilegedHelperTools/com.docker.vmnetd`, `/Library/LaunchDaemons/com.docker.vmnetd.plist`, and `/var/run/docker.sock` with **zero** `SecurityAgent` dialogs (`SecurityAgent windows: []`).
- **Bash 3.2 `set -u` Empty Array Expansion Fix (`cmd_drain` & `cmd_up`)**:
  - Updated `${profile_args[@]}` to `${profile_args[@]+"${profile_args[@]}"}` in `/Users/androidteam/Developer/scripts/docker-service.sh`.
  - Executed `/Users/androidteam/Developer/scripts/docker-service.sh up` and verified both `/Users/androidteam/Omniroute` (`2 running`, `127.0.0.1:20128/healthz` -> `ok`) and `/Users/androidteam/Developer/shb/shb-schedule` (`2 running`, `shb-schedule-scheduler-1` & `shb-schedule-db-1` healthy) came up cleanly without `unbound variable` errors.

---

## 3. Daily Maintenance Integration & Script Provenance Verification

- **Daily Maintenance Post-Cask Hook**:
  - Updated `/Users/androidteam/Developer/scripts/workstation-daily-update.sh` (Stage 1 Homebrew Maintenance) and `/Users/androidteam/Developer/shb/shb-schedule/src/shb_schedule/workflows/workstation_update.py` to execute `docker-service.sh start` and `docker-service.sh up` immediately after `brew upgrade --cask` when `/Applications/Docker.app/Contents/MacOS/install` is present.
- **Script Provenance Manifest (`config/script-provenance-manifest.tsv`)**:
  - Registered `/Users/androidteam/Developer/scripts/docker-service.sh	scripts/docker-service.sh	executed` in `/Users/androidteam/Developer/platform/openspec-store/config/script-provenance-manifest.tsv` and mirrored both `docker-service.sh` and `workstation-daily-update.sh` into `/Users/androidteam/Developer/platform/openspec-store/scripts/` with zero SHA-256 drift.
