# ops-scheduler-omniroute-jira-failures — Design

## Implementation Map

| # | Change | Repo | File | Strategy |
|---|---|---|---|---|
| 1 | Add `python-gitlab` direct dep | `jira-daily-reports/` | `pyproject.toml` (deps block) | Add `"python-gitlab>=8.3.0,<9.0.0"` between `jira-skill` and the `[project.scripts]` block. `uv lock --upgrade` regenerates `uv.lock`. |
| 2 | Lazy-import `webhook_receiver.dbos_scheduling` | `agent-core/` | `src/agent_core/scheduler_setup.py` | Append `from webhook_receiver.dbos_scheduling import register_all_schedules as _wr_register` wrapped in `try/except ImportError` at module top-level. Call `_wr_register(engine=_ENGINE)` inside `_apply_yaml_manifests()` after the existing manifests are applied. |
| 3 | Hard/soft health gate split | `ai-review/` | `src/ai_review/utils/health.py` (HealthChecker class) | Introduce `SOFT_CHECKS = {"omniroute_proxy", "kimi_cli", "circuit_breaker", "sessions"}` and `HARD_CHECKS = {"scheduler"}` constant sets. Refactor `_aggregate_status()` to return `degraded` if any soft check errors but raise HTTP 503 only when a hard check errors. |
| 4 | Add `scheduler.workflow.failed` burst alert | `tdt-observability/` | `~/.tdt/observability/config.yaml` | Append new rule under `alerts:`: `scheduler_workflow_failed_burst: window=24h threshold=3 metric=scheduler.workflow.failed level=error`. |
| 5 | Postgres backup stale alert | `tdt-observability/` | `~/.tdt/observability/config.yaml` | Append `postgres_backup_stale: file_glob=~/.tdt/backups/postgres/*.pgdump max_age_hours=26 level=warning`. |
| 6 | Document soft/hard contract | `tdt-meta/` | `docs/operations/scheduler-healthcheck.md` (new section) + `docs/operations/observability-runbook.md` (alert catalog) | Add "Hard vs Soft Degradation" subsection with examples. Cross-link from healthcheck.md to runbook. |
| 7 | Document backup gap contract | `tdt-meta/` | `docs/operations/postgres-restore.md` | Add a "Sidecar availability" subsection explaining when backups stop, and link to the new alert. |

## Code Patterns

### 1. `jira-daily-reports/pyproject.toml` — diff

```toml
dependencies = [
    "tdt-core[jira,scheduler]",
    "tdt-sheets>=0.1.0",
    "typer>=0.15.0",
    "rich>=13.9.0",
    "python-dotenv>=1.0.0",
    "pyyaml>=6.0.0",
    "jira-skill",
    "python-gitlab>=8.3.0,<9.0.0",   # NEW: direct dep for dev_performance/source.py:28
]
```

### 2. `agent_core/scheduler_setup.py` — append at module top-level (after line 289)

```python
# --- Optional: webhook-receiver schedules ----------------------------------
# webhook-receiver defines its own DBOS workflows (webhook-selftest,
# dlq-reaper) and registers them via webhook_receiver.dbos_scheduling. The
# module may not be present in the scheduler container's venv (it is a
# Go/FastAPI service with a separate deploy unit). Lazy-import and skip
# gracefully so the scheduler can still come up without webhook-receiver.
try:
    from webhook_receiver.dbos_scheduling import register_all_schedules as _wr_register
except ImportError as _exc:  # pragma: no cover - exercised only when venv differs
    logger.warning(
        "scheduler_setup.webhook_receiver_import_skipped module=webhook_receiver error=%s",
        _exc,
    )
    _wr_register = None
```

Then inside `_apply_yaml_manifests()` (after the existing manifest loop):

```python
    if _wr_register is not None:
        try:
            _wr_register(engine=_ENGINE, apply=False)
        except Exception as _exc:  # noqa: BLE001
            logger.warning(
                "scheduler_setup.webhook_receiver_register_failed error=%s",
                _exc,
            )
```

### 3. `ai_review/utils/health.py` — split SOFT vs HARD

```python
SOFT_CHECKS = frozenset({"omniroute_proxy", "kimi_cli", "circuit_breaker", "sessions"})
HARD_CHECKS = frozenset({"scheduler", "postgres"})

def overall_status(checks: dict[str, HealthResult]) -> tuple[str, bool]:
    """Return (status, http_503).

    status: 'ok' | 'degraded' | 'error'
    http_503: True iff the HTTP layer should return 503.
    """
    has_soft_error = any(c.status == "error" for name, c in checks.items() if name in SOFT_CHECKS)
    has_hard_error = any(c.status == "error" for name, c in checks.items() if name in HARD_CHECKS)
    if has_hard_error:
        return "error", True
    if has_soft_error:
        return "degraded", False
    return "ok", False
```

The `/health/full` route handler then does:

```python
status, http_503 = overall_status(checks)
return JSONResponse({"status": status, "checks": checks}, status_code=503 if http_503 else 200)
```

### 4. `~/.tdt/observability/config.yaml` — append

```yaml
alerts:
  # ... existing alert rules ...

  # NEW: scheduler workflows failing repeatedly
  scheduler_workflow_failed_burst:
    description: >
      scheduler.workflow.failed events accumulated in the last 24 hours.
      Indicates that a registered CLI workflow is failing on every tick —
      usually a missing Python dependency or a broken register_fn.
    query: |
      SELECT COUNT(*) AS failed_count
      FROM events
      WHERE event_type = 'scheduler.workflow.failed'
        AND timestamp > now() - INTERVAL '24 hours'
    threshold: 3
    severity: error
    runbook: docs/operations/observability-runbook.md#scheduler-workflow-failed-burst

  # NEW: postgres backup sidecar stale
  postgres_backup_stale:
    description: >
      Most recent postgres .pgdump in ~/.tdt/backups/postgres/ is older than 26h.
      The sidecar only runs while the compose stack is up — a stale backup
      almost always means the stack has been down.
    query: |
      SELECT
        MAX(filename) AS latest,
        EXTRACT(EPOCH FROM (now() - MAX(modified_at))) / 3600 AS age_hours
      FROM (
        SELECT
          filename,
          MAX(timestamp) AS modified_at
        FROM events
        WHERE filename GLOB '~/.tdt/backups/postgres/*.pgdump'
        GROUP BY filename
      )
    threshold_hours: 26
    severity: warning
    runbook: docs/operations/postgres-restore.md#sidecar-availability
```

## Verification Plan

```bash
# 1. python-gitlab dep
cd ~/Developer/tdt/jira-daily-reports
uv lock --upgrade
uv sync
grep -E '^(name|version): python-gitlab' uv.lock  # expect match

# 2. webhook-receiver import
cd ~/Developer/tdt/agent-core
docker exec agent-core-local-scheduler-1 python -c \
  "import webhook_receiver.dbos_scheduling as m; print(m.register_all_schedules)"

# 3. health soft/hard split
curl -s http://localhost:8080/health/full | python -m json.tool
# With OmniRoute 500: expect status=degraded, HTTP 200

# 4. Alerts
python3 -c "
from tdt_observability.alerts import check_alerts
print(check_alerts('scheduler_workflow_failed_burst'))
print(check_alerts('postgres_backup_stale'))
"

# 5. Long-running validation
# Watch scheduler-entrypoint.log for 7 days: zero ModuleNotFoundError: gitlab
```

## Risk & Rollback

- **Risk**: Adding `python-gitlab` to `jira-daily-reports` deps increases the host venv size by ~5 MB and one transitive dep tree. Low risk — same package is already in `tdt-core[all]` extras.
- **Risk**: The soft/hard health split changes ai-review's HTTP status code from 503 → 200 in the OmniRoute-down case. **Consumer impact**: `tdt_observability.health_poller` currently treats 503 as "service down" and emits an alert. After the fix, the poller will treat it as "service degraded" and emit a different alert (`omniroute_proxy_unavailable` derived from per-check map). Verify the consumer-side alert mapping in `~/.tdt/observability/config.yaml`.
- **Rollback**: Each change is isolated. The `python-gitlab` dep can be removed with `uv remove python-gitlab`. The lazy-import is a `try/except`. The soft/hard split is gated on a new code path that defaults to the old behaviour if `overall_status` raises (we keep the old `if any error: 503` as a fallback for one release).
- **No DB migrations. No new env vars. No new secrets.**

## Out-of-Scope Reminders

- OmniRoute itself: out of scope (3rd-party). Mitigation is the health-degradation contract, not a code fix.
- Restoring 13 days of missing backups: not possible. Document and move on.
- Migrating `agent-core` to a new scheduler engine: out of scope.