# workstation-toolchain-inventory Delta Specification

## ADDED Requirements

### Requirement: Automated workstation cask maintenance SHALL execute active graceful lifecycle rather than passive deferral

Workstation automated maintenance pipelines (`workstation_update.py` and `workstation-daily-update.sh`) SHALL actively terminate, upgrade, and relaunch running GUI applications and background daemons rather than skipping them indefinitely under passive deferral.

#### Scenario: Running application termination via POSIX signals prior to cask upgrade
- **WHEN** an outdated Homebrew cask has active processes detected in its process name mapping
- **THEN** the pipeline SHALL issue `pkill -TERM -x <proc>` to gracefully request process exit
- **AND** it SHALL poll for process termination within a bounded timeout (up to 6 seconds)
- **AND** if still running after the timeout, it SHALL issue `pkill -KILL -x <proc>` fallback
- **AND** it SHALL NOT execute AppleEvents (`osascript -e 'quit app ...'`) to prevent `kTCCServiceAppleEvents` privacy prompts

#### Scenario: Background daemon relaunch post-upgrade
- **WHEN** an outdated cask belonging to `CASK_RELAUNCH_APPS` (such as `tailscale-app`, `cloudflare-warp`, `google-drive`, `onedrive`, `orca`, or `chatgpt`) is successfully upgraded
- **AND** its process was actively running prior to the upgrade
- **THEN** the pipeline SHALL automatically relaunch the application in the background (`open -a "<App>" --background`)
- **AND** the pipeline telemetry SHALL record the cask in `casks_restarted`

#### Scenario: Coordinated container drainage and restoration for Docker Desktop
- **WHEN** `docker-desktop` is outdated and scheduled for upgrade
- **THEN** the pipeline SHALL invoke `docker-service.sh stop` to drain registered compose stacks and shut down the daemon
- **AND** it SHALL execute the cask upgrade non-interactively with standard input closed (`< /dev/null`)
- **AND** it SHALL invoke `docker-service.sh start` and `docker-service.sh up` to restore daemon health and container workloads
