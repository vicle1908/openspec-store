# Spec Delta: docker-lifecycle

## MODIFIED Requirements

### Requirement: Automated compose stack restoration on restart

The workstation lifecycle utility (`docker-service.sh`) SHALL support automated restoration of all registered compose stacks following daemon restart or explicit stack bring-up commands, targeting strictly primary gateway and application stacks.

#### Scenario: Restart restores registered compose stacks
- **WHEN** `docker-service.sh restart` is executed
- **THEN** the utility SHALL first drain registered stacks cleanly, restart Docker Desktop via the official CLI plugin, verify socket reachability, and invoke `cmd_up` to restore registered compose stacks (`~/Omniroute`) to active running status.

#### Scenario: Explicit up command starts registered stacks
- **WHEN** `docker-service.sh up` is executed
- **THEN** each configured compose stack in `COMPOSE_STACKS` SHALL be started via `docker compose up -d` without requiring manual directory navigation.

#### Scenario: Restart restores only primary gateway stack
- **WHEN** `docker-service.sh restart` or `docker-service.sh up` is executed
- **THEN** the utility SHALL target only active registered stacks (`~/Omniroute`)
- **AND** the decommissioned `claude-code-provider-adapter` path SHALL NOT be invoked or drained.

### Requirement: Continuous supervisor watchdog monitoring

A periodic system supervisor (`com.omniroute.watchdog`) SHALL monitor the health of the Docker daemon and local gateway stacks and auto-recover unhealthy or missing services, omitting decommissioned sidecar endpoints from health evaluation.

#### Scenario: Unhealthy or halted container auto-recovery
- **WHEN** `omniroute` container is halted or fails HTTP health probes
- **THEN** `omniroute-watchdog.sh` SHALL execute `docker compose up -d` in the respective stack directory to restore service availability.

#### Scenario: Container startup grace period observed
- **WHEN** `omniroute` is in the `starting` health status during initial boot
- **THEN** the supervisor SHALL NOT trigger redundant restarts, allowing the container to complete internal model route initialization.

#### Scenario: Down daemon recovery attempt
- **WHEN** Docker daemon is unreachable during supervisor execution
- **THEN** the supervisor SHALL invoke `docker-service.sh start` before attempting container checks.

#### Scenario: Supervisor probes primary gateway without sidecars
- **WHEN** `omniroute-watchdog.sh` executes its periodic health probe cycle
- **THEN** it SHALL evaluate Docker daemon socket availability and OmniRoute `/healthz` on port 20128
- **AND** it SHALL NOT probe port 8788 or trigger restarts for `claude-code-provider-adapter`.
