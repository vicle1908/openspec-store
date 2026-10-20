# Spec Delta

## ADDED Requirements

### Requirement: Post-cask-upgrade Docker Desktop helper and stack restoration

The workstation daily maintenance pipeline (both `shb-schedule` durable workflows and `workstation-daily-update.sh`) SHALL invoke `docker-service.sh start` and `docker-service.sh up` immediately after Homebrew cask upgrades, and track `docker-service.sh` in `config/script-provenance-manifest.tsv`.

#### Scenario: Daily maintenance restores Docker Desktop after Homebrew cask upgrade
- **WHEN** the Homebrew cask upgrade stage completes in `workstation-daily-update.sh` or `shb-schedule`'s `workstation-daily-update` workflow and `/Applications/Docker.app/Contents/MacOS/install` and `/Users/androidteam/Developer/scripts/docker-service.sh` are executable
- **THEN** the maintenance runner SHALL execute `docker-service.sh start` and `docker-service.sh up`
- **AND** Docker Desktop privileged helpers (`com.docker.vmnetd`, `com.docker.socket`), the Docker daemon, and all registered Compose stacks (`~/Omniroute` and `~/Developer/shb/shb-schedule`) SHALL be restored to running state without manual intervention.

#### Scenario: Docker service script provenance is tracked in manifest
- **WHEN** `detect_script_drift` in `workstation-daily-update.sh` evaluates `/Users/androidteam/Developer/platform/openspec-store/config/script-provenance-manifest.tsv`
- **THEN** `/Users/androidteam/Developer/scripts/docker-service.sh` SHALL be listed with recorded mirror `scripts/docker-service.sh` and authority `executed`
- **AND** the SHA-256 digest of `/Users/androidteam/Developer/scripts/docker-service.sh` SHALL match `/Users/androidteam/Developer/platform/openspec-store/scripts/docker-service.sh` with zero drift.
