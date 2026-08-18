## Context

The `decouple-scheduler-workflows-from-agent-core` change moved workflow functions from `agent-core/scheduler_setup.py` to individual repos. The `move-scheduler-to-dedicated-directory` change moved the Docker deployment to `tdt-scheduler/`. Both changes established the `register_fn` pattern with `register_all_schedules()`.

However, `tdt-observability` was not part of those changes and still uses the legacy `module:function` pattern. This creates an inconsistency in the scheduling ecosystem.

## Goals / Non-Goals

**Goals:**
- Align tdt-observability with the `register_fn` pattern
- Clean up all stale `agent-core/deployments/scheduler` references across the ecosystem
- Ensure all 5 YAML manifests use the same pattern

**Non-Goals:**
- Changing the scheduler framework or engine
- Modifying the tdt-observability retention logic
- Changing the Docker deployment

## Decisions

### D1: Follow the existing register_fn pattern exactly

**Decision:** Create `tdt_observability.dbos_scheduling.py` with `register_all_schedules(engine, apply=False)` following the exact same pattern as the other 4 repos.

**Rationale:** Consistency reduces cognitive load and maintenance burden. The pattern is proven across 4 repos with 21 schedules.

## Risks / Trade-offs

- **[Low risk]** → The pattern is identical to 4 other working repos. No new behavior introduced.

## Migration Plan

1. Create `tdt-observability/src/tdt_observability/dbos_scheduling.py`
2. Update `~/.tdt/schedules/tdt-observability.yaml` to use `register_fn`
3. Update `tdt-scheduler/generators/tdt_observability.py` to emit `register_fn`
4. Fix stale references across 5 repos
5. Verify all tests pass
