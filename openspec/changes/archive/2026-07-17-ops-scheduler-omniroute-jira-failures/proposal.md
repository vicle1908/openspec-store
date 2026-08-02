# ops-scheduler-omniroute-jira-failures

## Why

A 2026-07-14 operations log audit surfaced four high-impact reliability gaps that recur daily and silently degrade observability / scheduling:

| # | Gap | Recurrence | Surface | Why it matters |
|---|---|---|---|---|
| 1 | `python-gitlab` missing from scheduler venv | Every `jira-daily-reports dev-performance` (25×), `sprint-sheet` (15×), `remind`/`wip-age`/`wip`/`catalog-refresh` (5×) | `scheduler-entrypoint.log` `scheduler.workflow.failed` since 2026-07-05 | `jira-daily-reports/pyproject.toml` declares `tdt-core[jira,scheduler]` only — `gitlab` is installed transitively in the host venv but never reaches the scheduler container's `/opt/scheduler/.venv` because that venv is built from a closed dep set (pydantic-ai, langgraph, tdt-core[scheduler,jira]). The `from gitlab.exceptions import …` line at `jira-daily-reports/src/jira_daily_reports/dev_performance/source.py:28` is therefore an undeclared direct dependency. |
| 2 | `webhook-selftest` + `dlq-reaper` schedule manifests reference modules not imported in scheduler | Every scheduler start since the manifests landed | `scheduler-entrypoint.log`: `partially initialized module 'agent_core.scheduler_setup' has no attribute 'dlq_reaper'` / `webhook_selftest_workflow() got an unexpected keyword argument 'secret'` | `~/.tdt/schedules/webhook-receiver.yaml` points at `register_fn: webhook_receiver.dbos_scheduling:register_all_schedules`, but `agent_core.scheduler_setup` does not import `webhook_receiver.dbos_scheduling` and the scheduler container's venv does not include `webhook-receiver`. DBOS discovers the manifests, fails the lazy import, and the schedule registration aborts — but the manifests stay on disk and keep being attempted on every reload. |
| 3 | OmniRoute LLM proxy returns 500 on every endpoint (`/`, `/v1/models`, `/health`) | Continuous since at least 2026-07-13 22:46 UTC | `webhook-receiver.stdout.log` (15,290× 503) and `ai-review /health/full → omniroute_proxy: status=error detail=HTTP 500` | `OmniRoute.app` is up (PID 61559, listening on 20128) but every endpoint responds with body `Internal Server Error`. The 503 storm in `webhook-receiver` is *caused by ai-review's degraded health gate* (`degraded → status=503`), not by webhook-receiver itself. The root cause sits outside the TDT ecosystem (3rd-party Electron app), but the contract breach needs documentation: `OMNIROUTE_URL=http://localhost:20128/v1` is treated as a hard health dependency but has no documented degradation mode. |
| 4 | Postgres backup gap 2026-06-30 → 2026-07-13 (13 days missing) | One-time, silent | `~/.tdt/backups/postgres/` | The `postgres-backup` sidecar was down during that window — its PID-1 loop only runs while the compose stack is up. Today: container is back up (since 2026-07-13 14:18 UTC), 2026-07-13.pgdump was written. The recovery is fine, but the silent 13-day gap has no operator-visible warning. |

The fixes below are scoped: one direct dependency declaration, one module-import wiring fix, one health-degradation contract change, and one new alerting rule. No behaviour changes to the workflows themselves.

## What Changes

- **Add direct dependency `python-gitlab>=8.3.0,<9.0.0` to `jira-daily-reports/pyproject.toml`** so the scheduler container's `uv sync` installs it alongside the existing `tdt-core[scheduler,jira]` extras. No new transitive risk (the package is already in the host venv).
- **Add an explicit `webhook_receiver.dbos_scheduling:register_all_schedules` import in `agent_core/scheduler_setup.py`** so the YAML manifests can find their `register_fn`. The import must be lazy (under `if TYPE_CHECKING:` or guarded by `try/except`) to preserve the circular-import tolerance already documented in `dbos_scheduling.py:99–100`.
- **Make `ai-review`'s `check_omniroute_proxy` degrade-gracefully** in the overall `/health/full` aggregate: keep `omniroute_proxy: status=error` in the per-check map, but do **not** flip the top-level `status` to `degraded` solely on OmniRoute 5xx. Document the new contract in the spec.
- **Add a `tdt_observability` alert rule for `>= 3 scheduler.workflow.failed events / 24h`** in `~/.tdt/observability/config.yaml`. The scheduler already emits structured `error` records via `dbos_scheduling.subprocess_nontransient`; we add a derived alert.
- **Document the Postgres backup gap contract** in `tdt-meta/docs/operations/postgres-restore.md`: the sidecar is best-effort, not durable, and a backup missing for > 24 h is an alertable condition.

## Capabilities

### New Capabilities

#### `ops-scheduler-jira-dependency-hygiene`
The scheduler container must run every registered workflow end-to-end without `ModuleNotFoundError` from missing transitive dependencies. The dependency declarations in each Python sub-repo's `pyproject.toml` are the **single source of truth** for what `uv sync` installs in the scheduler's venv.

#### `ops-scheduler-manifest-registration-contracts`
YAML manifests in `~/.tdt/schedules/<owner>.yaml` MUST point at a `register_fn` that is actually importable from the scheduler's venv. The scheduler MUST lazy-import the wrapper module and log a `WARNING scheduler.manifest.import_failed manifest=<path> module=<module>` on failure (one warning per manifest, not per reload).

#### `ops-health-omniroute-degradation-contract`
`ai-review /health/full` distinguishes between **degraded-soft** (omniroute_proxy 5xx, kimi_cli missing, circuit-breaker open) and **degraded-hard** (postgres unreachable, scheduler initialisation failure). Soft-degraded responses stay HTTP 200 with `status=degraded`; only hard-degraded responses return HTTP 503.

#### `ops-postgres-backup-sidecar-alerting`
The `postgres-backup` sidecar's output directory is monitored by `tdt_observability`. A `.pgdump` file older than 26 hours (cron runs at 03:00 UTC, so 24 h + 2 h slack) raises a `backup_stale` alert.

### Modified Capabilities

- `ops-scheduler-warning-hygiene` (existing, in-flight via `ops-fix-three-scheduler-warnings`) gains one new scenario: `manifest_import_failed`.
- `tdt-observability-health-poller` (existing, `~/.tdt/observability/config.yaml`) gains two new alert rules: `scheduler.workflow.failed >= 3 in 24h` and `postgres_backup_stale > 26h`.
- `webhook-receiver-health-contract` (existing) — clarify that `/health` always returns 200 (liveness) while `/health/full` is the readiness probe and may return 503 only on hard-degraded states.

## Out of Scope

- Fixing OmniRoute itself (3rd-party Electron app, no source access).
- Migrating `agent-core` to a different scheduler engine.
- Restoring the missing 2026-06-30 → 2026-07-13 backups (data loss; document and move on).

## Acceptance Criteria

- [ ] `cd ~/Developer/tdt/jira-daily-reports && uv sync` adds `python-gitlab` to the lock file.
- [ ] After restarting the scheduler container, no `ModuleNotFoundError: No module named 'gitlab'` in `scheduler-entrypoint.log` for 7 consecutive days.
- [ ] `webhook_receiver.dbos_scheduling:register_all_schedules` is callable from inside the scheduler container's Python REPL.
- [ ] With OmniRoute returning 500, `ai-review /health/full` returns HTTP 200 with `status=degraded` (not 503).
- [ ] With OmniRoute down for > 5 minutes, `tdt_observability` raises an `omniroute_proxy_unavailable` alert (and stays HTTP 200 on ai-review).
- [ ] `tdt_observability` raises a `scheduler_workflow_failed_burst` alert when `>= 3 scheduler.workflow.failed events fire within 24h`.
- [ ] `tdt_observability` raises a `postgres_backup_stale` alert if the latest `.pgdump` is older than 26 hours.