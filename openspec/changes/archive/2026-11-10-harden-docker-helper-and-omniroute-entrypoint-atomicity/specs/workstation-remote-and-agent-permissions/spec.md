# workstation-remote-and-agent-permissions Delta Specification

## MODIFIED Requirements

### Requirement: Docker Desktop privileged helper lifecycle SHALL use socket-only provisioning without obsolete vmnetd probes

Workstation Docker management tools (`docker-service.sh`) SHALL provision `com.docker.socket` non-interactively via `install config --user <user>` and `install socket-symlink-on-startup --user <user>`, enforce `<string><user></string>` in `/Library/LaunchDaemons/com.docker.socket.plist` and synchronous `/var/run/docker.sock` symlinking, and omit obsolete `com.docker.vmnetd` probes so `com.docker.backend` never invokes `osascript` admin prompts.

#### Scenario: Docker Desktop helper verification without vmnetd
- **WHEN** `docker-service.sh` verifies or provisions privileged helper tools for Docker Desktop
- **THEN** it SHALL verify that `/Library/PrivilegedHelperTools/com.docker.socket` matches `/Applications/Docker.app/Contents/MacOS/com.docker.socket`
- **AND** it SHALL NOT fail or attempt to kickstart `system/com.docker.vmnetd` when `com.docker.vmnetd` is absent from `/Applications/Docker.app`
- **AND** it SHALL NOT trigger `SecurityAgent.ExecuteWithPrivileges` modal authentication dialogs during daemon startup

#### Scenario: Socket startup task plist user argument and synchronous symlink enforcement
- **WHEN** `ensure_helpers()` provisions `com.docker.socket` or `is_socket_helper_up()` checks helper readiness
- **THEN** `ensure_helpers()` SHALL pass `--user "$target_user"` to both `install config --user "$target_user"` and `install socket-symlink-on-startup --user "$target_user"` and execute `sudo -n ln -sfn "$socket_path" /var/run/docker.sock` after `launchctl kickstart -p system/com.docker.socket`
- **AND** `is_socket_helper_up()` SHALL require `/Library/LaunchDaemons/com.docker.socket.plist` to contain `<string>${target_user}</string>` and `/var/run/docker.sock` to resolve to `${socket_path}` so `com.docker.backend.cmdline` never detects an empty `""` plist user argument or missing `/var/run/docker.sock`

#### Scenario: Pre-emptive termination of vendor cask processes
- **WHEN** an application package or cask upgrade contains vendor preinstall scripts that execute `osascript` quit commands
- **THEN** the maintenance pipeline SHALL terminate the application's active processes using POSIX signals (`pkill -TERM`) prior to invoking the package installer
- **AND** the vendor preinstall script's running process check SHALL evaluate to false, preventing `kTCCServiceAppleEvents` permission prompts
