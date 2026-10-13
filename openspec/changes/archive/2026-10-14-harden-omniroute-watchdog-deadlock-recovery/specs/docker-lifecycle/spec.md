# Spec Delta: docker-lifecycle

## MODIFIED Requirements

### Requirement: Continuous supervisor watchdog monitoring

A periodic system supervisor (`com.omniroute.watchdog`) SHALL monitor the health of the Docker daemon and local gateway stacks and auto-recover unhealthy or missing services, omitting decommissioned sidecar endpoints from health evaluation.

#### Scenario: Unhealthy or halted container auto-recovery
- **WHEN** `omniroute` container is halted or fails HTTP health probes outside the startup grace period
- **THEN** `omniroute-watchdog.sh` SHALL evaluate container status: if the container is running but unhealthy, it SHALL execute `docker compose restart omniroute-base`
- **AND** if the container is halted or not running, it SHALL execute `docker compose up -d` in the respective stack directory to restore service availability.

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
