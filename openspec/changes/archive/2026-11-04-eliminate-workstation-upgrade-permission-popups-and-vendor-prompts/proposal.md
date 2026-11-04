# Proposal: Eliminate Workstation Upgrade Permission Popups and Vendor Prompts

## Why
macOS Unified System Logs (`SecurityAgent` and `authd`) revealed that upgrade operations still triggered authorization dialogs:
1. At 22:24:47, `authd` authorized `system.privilege.admin` for `/usr/bin/osascript` [PID 94893], generating a `SecurityAgent.ExecuteWithPrivileges` modal prompt.
2. Root cause investigation isolated this to `docker-service.sh`: the helper probe checked for `/Applications/Docker.app/Contents/Library/LaunchServices/com.docker.vmnetd`. In modern Docker Desktop (4.39+ through 4.98.0), `vmnetd` was retired and deleted by Docker in favor of `com.docker.socket`.
3. Because `vmnetd` was permanently missing, `docker-service.sh` passed obsolete `set-vmnetd` arguments to `/Applications/Docker.app/Contents/MacOS/install` and failed to start `com.docker.vmnetd`. On startup, `com.docker.backend` detected the missing helper, created a temporary `/tmp/docker-desktop-privileged*` staging folder, and executed `/usr/bin/osascript (do shell script ".../install config ... set-vmnetd set-docker-socket" with administrator privileges)`, popping an OS password dialog.
4. Additionally, vendor installer packages (`Tailscale-1.104.5-macos.pkg`) contain preinstall scripts that invoke `osascript -e 'quit app ...'` if `io.tailscale.ipn.macsys` is running, prompting for `kTCCServiceAppleEvents`.

## What Changes
1. **Modernize `docker-service.sh`**:
   - Eliminate all references to the obsolete `vmnetd` binary, plist, and `set-vmnetd` arguments.
   - Run `/Applications/Docker.app/Contents/MacOS/install remove-vmnetd` during helper configuration.
   - Restrict helper provisioning strictly to `com.docker.socket` via `sudo -n /Applications/Docker.app/Contents/MacOS/install config --user "${USER:-$(id -un)}"` and `socket-symlink-on-startup`.
   - Ensure `is_socket_helper_up()` is the sole requirement, eliminating the condition that triggers Docker's `com.docker.backend` fallback to `osascript with administrator privileges`.
2. **Pre-emptive Cask Process Termination**:
   - Guarantee that all vendor package processes (e.g. `Tailscale`, `IPNExtension`, `warp-svc`) are terminated via POSIX `pkill -TERM` prior to invoking `brew upgrade --cask`, completely bypassing vendor preinstall AppleScript quit stanzas.
3. **Spec Delta**:
   - Update `workstation-remote-and-agent-permissions` specification to forbid obsolete privileged helper probes and require non-interactive socket provisioning.
