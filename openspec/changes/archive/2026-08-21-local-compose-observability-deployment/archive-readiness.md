# Archive Readiness

The documentation/verification change is complete and source-free. Its final
gate was the separately owned `reconcile-stale-dbos-schedule-state` change.

Accepted evidence:

- `tdt-scheduler` runbook/template commits: `73f9e52` and `3c7d1bd`.
- `agent-core` integration-runbook commits: `144e401` and `183ff40`.
- `tdt-core` reconciliation source: `a4baee611fa2388f5e11dabfc76bb2f4d6601fc3`.
- Accepted `tdt-core/main`: `fa72c9c341c3db339e6671513248283efc73b2c1`.
- Reversible disposable PostgreSQL migration/rollback: passed.
- Real shared stale-database control: healthy, zero retired schedules, zero new unregistered-workflow errors.
- Real fresh-database control: healthy, canonical 19/19 current schedule baseline.
- 170-second monitor: zero restarts, OOM kills, health failures, or unregistered-workflow errors.
- Strict selected-change validation and store doctor are required immediately before archive.

The ownership statements in this change describe the historical scope that was
implemented. The newer active `consolidate-observability-docker-deployment`
change governs any later transfer or consolidation of Docker ownership and is
not part of this archive.
