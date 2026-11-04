# Design: Eliminate Workstation Upgrade Permission Popups and Vendor Prompts

## 1. Context & Architectural Root Cause

Through forensic inspection of macOS Unified System Logs (`authd`, `SecurityAgent`, `tccd`, `nesessionmanager`), two independent mechanisms were identified as responsible for modal authorization pop-ups during workstation upgrades:

### Mechanism 1: Docker Desktop Helper Probe (`vmnetd` Retirement)
In `/Users/androidteam/Developer/scripts/docker-service.sh`:
- The legacy probe checked for `/Applications/Docker.app/Contents/Library/LaunchServices/com.docker.vmnetd` and compared it via `cmp -s` against `/Library/PrivilegedHelperTools/com.docker.vmnetd`.
- In Docker Desktop 4.39+ through 4.98.0, Docker retired `vmnetd` in favor of `com.docker.socket`. The binary `/Applications/Docker.app/Contents/Library/LaunchServices/com.docker.vmnetd` no longer exists.
- Because the file was missing, `cmp -s` continuously failed, causing `ensure_helpers()` to issue:
  ```bash
  sudo -n /Applications/Docker.app/Contents/MacOS/install config --user androidteam set-vmnetd set-docker-socket
  sudo -n launchctl kickstart -p system/com.docker.vmnetd
  ```
- Kickstart failed because `com.docker.vmnetd.plist` was absent.
- On subsequent startup of `com.docker.backend`, Docker detected the missing helper and created a temporary directory `/tmp/docker-desktop-privileged.<pid>/` executing an internal fallback:
  ```applescript
  do shell script "/Applications/Docker.app/Contents/MacOS/install config --user androidteam set-vmnetd set-docker-socket" with administrator privileges
  ```
- This spawned `/usr/bin/osascript` [PID 94893], which invoked `SecurityAgent.ExecuteWithPrivileges` and prompted the user for admin credentials via GUI dialog.

### Mechanism 2: Vendor Cask Package Preinstall AppleScript (`tailscale-app`)
In `Tailscale-1.104.5-macos.pkg` (`Distribution.pkg/Scripts/preinstall`):
- The installer package executes:
  ```bash
  osascript -e 'if app id "io.tailscale.ipn.macsys" is running then' -e 'quit app id "io.tailscale.ipn.macsys"' -e 'end if'
  ```
- When `tailscale-app` is upgraded while `Tailscale` or `IPNExtension` is running, this script triggers `kTCCServiceAppleEvents` permission prompts in macOS TCC.

## 2. Technical Remediation

### 2.1 Modernizing `docker-service.sh`
1. **Remove `vmnetd` Probes**:
   Eliminate `is_vmnetd_up()`, `app_vmnetd`, `set-vmnetd`, and `launchctl kickstart -p system/com.docker.vmnetd`.
2. **Clean Up Legacy Artifacts**:
   Run `/Applications/Docker.app/Contents/MacOS/install remove-vmnetd` during helper configuration.
3. **Provision Sole Helper (`com.docker.socket`)**:
   Modern Docker Desktop requires only `com.docker.socket`. Helper provisioning executes non-interactively via:
   ```bash
   sudo -n /Applications/Docker.app/Contents/MacOS/install config --user "${USER:-$(id -un)}"
   sudo -n /Applications/Docker.app/Contents/MacOS/install socket-symlink-on-startup
   sudo -n launchctl kickstart -p system/com.docker.socket
   ```
4. **Helper Validation**:
   `ensure_helpers()` succeeds whenever `/Library/PrivilegedHelperTools/com.docker.socket` matches `/Applications/Docker.app/Contents/MacOS/com.docker.socket` and the socket service is active.

### 2.2 Pre-emptive POSIX Teardown
1. Workstation upgrade routines (`workstation_update.py` and `workstation-daily-update.sh`) execute `terminate_cask_processes()` using POSIX `pkill -TERM -x <proc>` before invoking Homebrew.
2. Because `Tailscale` and `IPNExtension` are already stopped before `installer -pkg` runs, the vendor preinstall script's `if app id ... is running` condition evaluates to false, completely bypassing the vendor's `osascript` quit command.

## 3. Invariants & Verification
- Zero `SecurityAgent.ExecuteWithPrivileges` dialogs.
- Zero `kTCCServiceAppleEvents` prompts.
- Permanent bundle attribution preserved under `client_type = 0` in `TCC.db`.
