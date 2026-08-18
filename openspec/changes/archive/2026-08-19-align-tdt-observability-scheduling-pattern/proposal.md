## Why

After the `decouple-scheduler-workflows-from-agent-core` and `move-scheduler-to-dedicated-directory` changes, 4 of 5 scheduling repos use the `register_fn` pattern. `tdt-observability` still uses the legacy `module:function` pattern (`tdt_observability.retention:daily_observability_retention`). This creates inconsistency in the scheduling ecosystem.

## What Changes

- **Create `tdt-observability/src/tdt_observability/dbos_scheduling.py`** — register `observability-retention-daily` via `register_all_schedules(engine, apply=False)` following the same pattern as jira-daily-reports, code-daily-scan, jira-epic-report, and webhook-receiver
- **Update `~/.tdt/schedules/tdt-observability.yaml`** — change from `module:function` to `register_fn: tdt_observability.dbos_scheduling:register_all_schedules`
- **Update `tdt-scheduler/generators/tdt_observability.py`** — emit `register_fn` instead of `module:function`
- **Update stale references** across agent-core, code-daily-scan, jira-daily-reports, tdt-observability, and tdt-scheduler

## Capabilities

### Modified Capabilities

- `scheduler-docker-deployment`: All repos now use register_fn pattern consistently

## Impact

- **Code repos touched**: tdt-observability (new file), tdt-scheduler (generator update), agent-core (test update), code-daily-scan (doc update), jira-daily-reports (doc update)
- **Risk**: LOW — same pattern as 4 other repos, proven approach
