# Spec Delta

## ADDED Requirements

### Requirement: OmniRoute deployment SHALL configure coding-agent runtime limits and stream resilience

The local OmniRoute Docker deployment override SHALL configure runtime memory sizing, tool definition limits, and stream resilience calibrated for local workstation coding agents (`OMNIROUTE_MEMORY_MB`, `OMNIROUTE_MAX_TOOLS_LIMIT`, `STREAM_READINESS_STALL_RETRY`, and `EMPTY_STREAM_SIBLING_RECOVERY_ENABLED`).

#### Scenario: Coding agent runtime memory and tool limits are configured
- **WHEN** the `omniroute-base` container is deployed with `docker-compose.override.yml`
- **THEN** its environment SHALL contain `OMNIROUTE_MEMORY_MB=4096`
- **AND** its environment SHALL contain `OMNIROUTE_MAX_TOOLS_LIMIT=256`
- **AND** its environment SHALL contain `STREAM_READINESS_STALL_RETRY=true` and `EMPTY_STREAM_SIBLING_RECOVERY_ENABLED=true`
- **AND** `STREAM_RECOVERY_ENABLED` SHALL NOT be forced to `true` globally to avoid imposing a mandatory 750 ms time-to-first-token holdback latency penalty on interactive streams
