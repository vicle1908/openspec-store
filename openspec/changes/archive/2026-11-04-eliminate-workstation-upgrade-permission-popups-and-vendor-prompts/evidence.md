# Evidence: Eliminate Workstation Upgrade Permission Popups and Vendor Prompts

## 1. Live Forensic Analysis & Root Cause Identification

### 1.1 `SecurityAgent.ExecuteWithPrivileges` Investigation
- **Unified Log Query**:
  ```bash
  log show --predicate 'process == "SecurityAgent" OR subsystem == "com.apple.Authorization"' --start "2026-11-04 22:24:20" --end "2026-11-04 22:25:00"
  ```
- **Discovery**:
  At 22:24:47, `authd` recorded:
  ```
  authd: Succeeded authorizing right 'system.privilege.admin' by client '/usr/bin/osascript' [94893] for authorization created by '/usr/bin/osascript' [94893]
  SecurityAgent: Donating to LocalAuthentication.UI.Dialogs: <dialogID: com.apple.SecurityAgent.ExecuteWithPrivileges>
  ```
  Tracing PID 94893 revealed it was launched via Docker's internal fallback runner `/tmp/docker-desktop-privileged2813254440/`.

### 1.2 Root Cause in `docker-service.sh`
- `docker-service.sh` contained obsolete verification logic for `com.docker.vmnetd`:
  - In Docker Desktop 4.39+ through 4.98.0, `vmnetd` was permanently deleted from `/Applications/Docker.app/Contents/Library/LaunchServices/com.docker.vmnetd`.
  - Because `com.docker.vmnetd` was missing, `docker-service.sh` failed its comparison check, passed obsolete `set-vmnetd` arguments to `/Applications/Docker.app/Contents/MacOS/install`, and attempted to kickstart an uninstalled `com.docker.vmnetd` LaunchDaemon.
  - When `com.docker.backend` started, it detected that the requested helper configuration was incomplete and triggered its internal fallback: executing `/usr/bin/osascript ... with administrator privileges`, creating a modal OS password prompt.

### 1.3 Vendor Cask Preinstall AppleScript (`tailscale-app`)
- Extracted and inspected `Tailscale-1.104.5-macos.pkg` (`Distribution.pkg/Scripts/preinstall`):
  - Line 4 contained: `osascript -e 'if app id "io.tailscale.ipn.macsys" is running then' -e 'quit app id "io.tailscale.ipn.macsys"' -e 'end if'`
  - When Tailscale was running, this vendor preinstall script invoked AppleEvents without entitlements, prompting for `kTCCServiceAppleEvents`.
  - By enforcing pre-emptive POSIX termination (`pkill -TERM -x Tailscale`) prior to `brew upgrade --cask`, `io.tailscale.ipn.macsys` is already stopped, causing the vendor `if app id ... is running` condition to evaluate to false and completely avoiding the vendor's `osascript` quit prompt.

## 2. Technical Remediation & Verification

### 2.1 Modernization of `docker-service.sh`
- Completely removed `is_vmnetd_up()`, `app_vmnetd`, and `set-vmnetd` calls.
- Configured modern socket helper provisioning via:
  ```bash
  sudo -n /Applications/Docker.app/Contents/MacOS/install remove-vmnetd
  sudo -n /Applications/Docker.app/Contents/MacOS/install config --user "${USER:-$(id -un)}"
  sudo -n /Applications/Docker.app/Contents/MacOS/install socket-symlink-on-startup
  sudo -n launchctl kickstart -p system/com.docker.socket
  ```
- Tested helper status non-interactively:
  ```bash
  /Users/androidteam/Developer/scripts/docker-service.sh status
  ```
  Result:
  ```
  Docker Desktop Status:
    Status: running
    Socket: /Users/androidteam/.docker/run/docker.sock (exists=true)
    Helpers:
      com.docker.socket: active (symlink verified)
    Registered Stacks:
      /Users/androidteam/Omniroute: 3 running
      /Users/androidteam/Developer/shb/shb-schedule: 2 running
  ```

### 2.2 Test Suite Assertions
- `openspec-store`: `pytest` passed (234 passed, 2 skipped in 104.16s).
- `shb-schedule`: `env -u PYTHONPATH uv run pytest -q` passed (122 passed in 144.10s).
- TCC Provenance: `tcc_provenance.py --bundles` returned `CLEAN` across all 8 canonical bundles (`client_type = 0`).
