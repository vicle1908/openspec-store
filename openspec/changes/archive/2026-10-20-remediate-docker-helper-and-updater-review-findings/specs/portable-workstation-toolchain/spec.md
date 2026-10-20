# portable-workstation-toolchain Delta Specification

## MODIFIED Requirements

### Requirement: Post-cask-upgrade Docker Desktop helper and stack restoration

The workstation daily maintenance pipeline (`shb-schedule` durable workflows and `workstation-daily-update.sh`) SHALL restore Docker Desktop and its Compose stacks after Homebrew cask upgrades, gate `docker-service.sh up` behind successful `docker-service.sh start` execution, and track `docker-service.sh` in `config/script-provenance-manifest.tsv`.

#### Scenario: Daily maintenance restores Docker Desktop after Homebrew cask upgrade
- **WHEN** the Homebrew cask upgrade stage updates `docker-desktop` in `shb-schedule`'s `workstation-daily-update` workflow, or when `workstation-daily-update.sh` completes `brew upgrade --cask` and detects that `docker info` fails or `/var/run/com.docker.vmnetd.sock`, `/Library/PrivilegedHelperTools/com.docker.vmnetd`, or `/Library/PrivilegedHelperTools/com.docker.socket` is missing
- **THEN** the maintenance runner SHALL execute `docker-service.sh start` and, only if `docker-service.sh start` exits `0`, execute `docker-service.sh up`
- **AND** Docker Desktop privileged helpers (`com.docker.vmnetd`, `com.docker.socket`), the Docker daemon, and all registered Compose stacks (`~/Omniroute` and `~/Developer/shb/shb-schedule`) SHALL be restored to running state without redundant Compose restarts on no-op cask runs.

#### Scenario: Failed Docker Desktop start after cask upgrade skips stack bring-up and records error
- **WHEN** `step_homebrew_update()` in `shb-schedule` upgrades `docker-desktop` and `docker-service.sh start` returns a non-zero exit code
- **THEN** `step_homebrew_update()` SHALL record the `docker-service.sh start` failure in `errors`, report step status `DEGRADED`, and skip invoking `docker-service.sh up` against the unreachable daemon.

#### Scenario: Docker service script provenance is tracked in manifest
- **WHEN** `detect_script_drift` in `workstation-daily-update.sh` evaluates `/Users/androidteam/Developer/platform/openspec-store/config/script-provenance-manifest.tsv`
- **THEN** `/Users/androidteam/Developer/scripts/docker-service.sh` SHALL be listed with recorded mirror `scripts/docker-service.sh` and authority `executed`
- **AND** the SHA-256 digest of `/Users/androidteam/Developer/scripts/docker-service.sh` SHALL match `/Users/androidteam/Developer/platform/openspec-store/scripts/docker-service.sh` with zero drift.
