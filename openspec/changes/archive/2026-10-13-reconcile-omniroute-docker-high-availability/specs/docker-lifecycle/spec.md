# Spec Delta: docker-lifecycle

## ADDED Requirements

### Requirement: Automated compose stack restoration on restart

The workstation lifecycle utility (`docker-service.sh`) SHALL support automated restoration of all registered compose stacks following daemon restart or explicit stack bring-up commands.

#### Scenario: Restart restores registered compose stacks
- **WHEN** `docker-service.sh restart` is executed
- **THEN** the utility SHALL first drain registered stacks cleanly, restart Docker Desktop via the official CLI plugin, verify socket reachability, and invoke `cmd_up` to restore registered compose stacks (`~/Omniroute`, `platform/claude-code-provider-adapter`) to active running status.

#### Scenario: Explicit up command starts registered stacks
- **WHEN** `docker-service.sh up` is executed
- **THEN** each configured compose stack in `COMPOSE_STACKS` SHALL be started via `docker compose up -d` without requiring manual directory navigation.

### Requirement: Container always restart policy alignment

Critical gateway and dependency containers SHALL configure and run with `HostConfig.RestartPolicy.Name` set to `always` in Docker Compose declarations and live container inspection, ensuring automatic restart across host reboots, engine restarts, and unhandled exits.

#### Scenario: Container inspect reflects always restart policy
- **WHEN** `docker inspect` is run against `omniroute`, `omniroute-redis`, or `claude-code-provider-adapter-adapter-1`
- **THEN** `HostConfig.RestartPolicy.Name` MUST equal `always`.

#### Scenario: Compose project default profile inclusion
- **WHEN** `docker compose up -d` is executed in `~/Omniroute` without explicit `--profile` flags
- **THEN** `COMPOSE_PROFILES=base` in `~/Omniroute/.env` MUST ensure `omniroute-base` and `redis` are both started.

### Requirement: Continuous supervisor watchdog monitoring

A periodic system supervisor (`com.omniroute.watchdog`) SHALL monitor the health of the Docker daemon and local gateway stacks and auto-recover unhealthy or missing services.

#### Scenario: Unhealthy or halted container auto-recovery
- **WHEN** `omniroute` or adapter container is halted or fails HTTP health probes
- **THEN** `omniroute-watchdog.sh` SHALL execute `docker compose up -d` in the respective stack directory to restore service availability.

#### Scenario: Container startup grace period observed
- **WHEN** `omniroute` is in the `starting` health status during initial boot
- **THEN** the supervisor SHALL NOT trigger redundant restarts, allowing the container to complete internal model route initialization.

#### Scenario: Down daemon recovery attempt
- **WHEN** Docker daemon is unreachable during supervisor execution
- **THEN** the supervisor SHALL invoke `docker-service.sh start` before attempting container checks.
