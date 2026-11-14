# Spec Delta

## MODIFIED Requirements

### Requirement: Automated compose stack restoration on restart

The workstation lifecycle utility (`docker-service.sh`) SHALL support automated restoration of all registered compose stacks following daemon restart or explicit stack bring-up commands, targeting strictly primary gateway and application stacks.

#### Scenario: Restart restores registered compose stacks
- **WHEN** `docker-service.sh restart` is executed
- **THEN** the utility SHALL first drain registered stacks cleanly, restart Docker Desktop via the official CLI plugin, verify socket reachability, and invoke `cmd_up` to restore registered compose stacks (`/Users/androidteam/Omniroute`, `/Users/androidteam/Developer/shb/shb-schedule`, and `/Users/androidteam/Developer/docker/ts-media-relay`) to active running status

#### Scenario: Explicit up command starts registered stacks
- **WHEN** `docker-service.sh up` is executed
- **THEN** each configured compose stack in `COMPOSE_STACKS` (`/Users/androidteam/Omniroute`, `/Users/androidteam/Developer/shb/shb-schedule`, and `/Users/androidteam/Developer/docker/ts-media-relay`) SHALL be started via `docker compose up -d` (with `--profile base` applied only to `/Users/androidteam/Omniroute`) without requiring manual directory navigation

#### Scenario: Restart restores only primary gateway stack
- **WHEN** `docker-service.sh restart` or `docker-service.sh up` is executed
- **THEN** the utility SHALL target only active registered stacks (`/Users/androidteam/Omniroute`, `/Users/androidteam/Developer/shb/shb-schedule`, and `/Users/androidteam/Developer/docker/ts-media-relay`)
- **AND** the decommissioned `claude-code-provider-adapter` path SHALL NOT be invoked or drained

#### Scenario: Provenance mirror parity and JSON stack status reporting
- **WHEN** `COMPOSE_STACKS` in `/Users/androidteam/Developer/scripts/docker-service.sh` is updated to include `/Users/androidteam/Developer/docker/ts-media-relay`
- **THEN** `/Users/androidteam/Developer/platform/openspec-store/scripts/docker-service.sh` SHALL remain byte-identical to `/Users/androidteam/Developer/scripts/docker-service.sh` per `config/script-provenance-manifest.tsv`, and `/Users/androidteam/Developer/scripts/docker-standardize-check.sh --strict` SHALL scan `/Users/androidteam/Developer/docker/ts-media-relay/docker-compose.yml` read-only with zero modifications to `docker-standardize-check.sh`
- **AND** `docker-service.sh status` and `docker-service.sh status --json` SHALL count only active containers via `docker compose --project-directory "$stack_dir" ps -q --status running` (reporting `"path":"/Users/androidteam/Developer/docker/ts-media-relay"` with `"running_containers":2` when healthy and excluding `restarting` or non-running containers)

#### Scenario: Named volume state persists across docker-service drain and up cycles
- **WHEN** `docker-service.sh drain` tears down `/Users/androidteam/Developer/docker/ts-media-relay` and `docker-service.sh up` brings it back up
- **THEN** named volumes `ts-media-relay_ts-media-relay-state` and `ts-media-relay_singbox-media-cache` SHALL retain the enrolled Tailscale node identity (`tailscaled.state`) and persisted FakeIP mappings (`cache.db`) without re-consuming `TS_AUTHKEY`
