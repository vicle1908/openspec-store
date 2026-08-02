## Context

agent-core uses DBOS for cron scheduling but doesn't leverage durable execution for agent runs. Pydantic AI provides `DBOSDurability`, `TemporalDurability`, and `PrefectDurability` capabilities that wrap agent I/O in durable steps.

## Goals / Non-Goals

**Goals:**
- Wire durable execution via `harness_config`
- Default to DBOS (already installed)
- Support Temporal/Prefect as optional extras
- Maintain backward compatibility

**Non-Goals:**
- Rewriting agent run loops
- Changing scheduling infrastructure
- Adding new external dependencies (DBOS already installed)

## Decisions

### Decision 1: DBOS as default

DBOS is already installed and used for scheduling. Zero new dependencies.

### Decision 2: Config-driven backend selection

```python
harness_config = {
    "durable_execution": {
        "backend": "dbos",  # "dbos" | "temporal" | "prefect"
    }
}
```

### Decision 3: Capability pattern

Follow the same pattern as other harness capabilities:
- Config key → capability instantiation
- Optional imports for temporal/prefect
- Graceful fallback if dependency missing

## Risks / Trade-offs

- **Risk**: DBOSDurability requires `@DBOS.workflow` context → **Mitigation**: Document requirement
- **Trade-off**: DBOS only vs. multiple backends → **Mitigation**: Keep optional via config
