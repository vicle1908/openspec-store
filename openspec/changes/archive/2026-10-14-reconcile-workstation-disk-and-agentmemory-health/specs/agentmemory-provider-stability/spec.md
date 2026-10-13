# Spec Delta: agentmemory-provider-stability

## ADDED Requirements

### Requirement: Healthcheck watchdog SHALL authenticate when server secret exists

The agentmemory launchd watchdog healthcheck script (`~/.hermes/scripts/agentmemory-healthcheck.sh`) SHALL authenticate against `/agentmemory/health` using the local bearer token from `~/.agentmemory/secret` when present, preventing spurious 401 restarts during normal operations.

#### Scenario: Watchdog authenticates with local bearer secret
- **WHEN** the agentmemory server runs with secret-based authentication enabled and `~/.agentmemory/secret` exists
- **THEN** `agentmemory-healthcheck.sh` SHALL supply `Authorization: Bearer <token>` on all `/agentmemory/health` calls
- **AND** the probe SHALL evaluate to HTTP 200 with status `healthy` rather than triggering unneeded `launchctl kickstart` restarts.

#### Scenario: Watchdog succeeds when secret file is absent
- **WHEN** `~/.agentmemory/secret` does not exist or server authentication is disabled
- **THEN** `agentmemory-healthcheck.sh` SHALL send an unauthenticated probe without error.
