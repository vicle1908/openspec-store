# workstation-remote-and-agent-permissions Delta Specification

## ADDED Requirements

### Requirement: Docker Desktop privileged helper lifecycle SHALL use socket-only provisioning without obsolete vmnetd probes

Workstation Docker management tools (`docker-service.sh`) SHALL provision Docker Desktop privileged helpers exclusively through modern non-interactive subcommands (`install config --user <user>` and `install socket-symlink-on-startup`) and SHALL NOT query or mandate the obsolete `com.docker.vmnetd` binary or launch daemon, preventing `com.docker.backend` from falling back to interactive `osascript with administrator privileges` prompts.

#### Scenario: Docker Desktop helper verification without vmnetd
- **WHEN** `docker-service.sh` verifies or provisions privileged helper tools for Docker Desktop
- **THEN** it SHALL verify that `/Library/PrivilegedHelperTools/com.docker.socket` matches `/Applications/Docker.app/Contents/MacOS/com.docker.socket`
- **AND** it SHALL NOT fail or attempt to kickstart `system/com.docker.vmnetd` when `com.docker.vmnetd` is absent from `/Applications/Docker.app`
- **AND** it SHALL NOT trigger `SecurityAgent.ExecuteWithPrivileges` modal authentication dialogs during daemon startup

#### Scenario: Pre-emptive termination of vendor cask processes
- **WHEN** an application package or cask upgrade contains vendor preinstall scripts that execute `osascript` quit commands
- **THEN** the maintenance pipeline SHALL terminate the application's active processes using POSIX signals (`pkill -TERM`) prior to invoking the package installer
- **AND** the vendor preinstall script's running process check SHALL evaluate to false, preventing `kTCCServiceAppleEvents` permission prompts
