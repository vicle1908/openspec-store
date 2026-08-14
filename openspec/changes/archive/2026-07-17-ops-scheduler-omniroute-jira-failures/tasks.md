# Tasks — ops-scheduler-omniroute-jira-failures

## 1. Validate findings (DONE 2026-07-13)

- [x] Confirmed OmniRoute 500 on every endpoint via `curl -s http://localhost:20128/v1/models` → `Internal Server Error`
- [x] Confirmed `python-gitlab` missing from scheduler venv via `docker exec ... ls /opt/scheduler/.venv/.../site-packages/ | grep -i gitlab` (no results)
- [x] Confirmed `webhook_receiver.dbos_scheduling` not imported in `agent_core/scheduler_setup.py` via `grep -n "webhook_receiver" .../scheduler_setup.py` (no results)
- [x] Confirmed Postgres backup gap 2026-06-30 → 2026-07-13 by inspecting `~/.tdt/backups/postgres/` listing

## 2. OpenSpec artifacts (DONE 2026-07-13)

- [x] Create change `ops-scheduler-omniroute-jira-failures` (spec-driven schema)
- [x] Write `proposal.md` (4 findings + 4 new capabilities + 6 acceptance criteria)
- [x] Write `design.md` (implementation map with code patterns for all 4 fixes)
- [x] Write 4 spec files:
  - [x] `ops-scheduler-jira-dependency-hygiene/spec.md`
  - [x] `ops-scheduler-manifest-registration-contracts/spec.md`
  - [x] `ops-health-omniroute-degradation-contract/spec.md`
  - [x] `ops-postgres-backup-sidecar-alerting/spec.md`
- [x] Write `tasks.md` (this file)

## 3. Code changes — Apply

### 3.1 Add `python-gitlab` direct dep

- [x] Edit `~/Developer/tdt/jira-daily-reports/pyproject.toml`: insert `"python-gitlab>=8.3.0,<9.0.0"` in the `dependencies` list (after `"jira-skill"`)
- [x] Run `cd ~/Developer/tdt/jira-daily-reports && uv lock --upgrade && uv sync`
- [x] Verify `grep -E '^(name|version): python-gitlab' uv.lock` returns a match
- [x] Run `ruff check . --fix && ruff format . && mypy src/ --strict` (no new errors)

### 3.2 Lazy-import webhook-receiver into scheduler

> **Superseded 2026-07-15:** The dynamic-import design in
> `tdt-core/src/tdt_core/scheduler/registry_loader.py:_invoke_register_fn`
> (`importlib.import_module(module_path)` + `schedule.register_fn_import_failed`
> warning on `ImportError`) already satisfies the manifest-registration contract
> end-to-end. `agent_core.scheduler_setup` is not in the path of webhook-receiver
> schedule loading; the existing scheduler container already logs
> `schedule.register_fn_applied count=2 owner=webhook-receiver` at every
> startup. No code change is required for this gap; the live behaviour matches
> the proposed `ops-scheduler-manifest-registration-contracts` capability.
>
> The spec still requires that scheduler emits a single
> `scheduler.manifest.import_failed` WARNING per manifest on reload failure
> (not per reload) — see task 3.2.4 for that follow-up.

- [x] Dynamic-import resolution path is already live (verified 2026-07-15 via
  `scheduler-entrypoint.log` showing clean `register_fn_applied count=2
  owner=webhook-receiver` at every boot since 2026-07-13).
- [x] Verify: `docker logs agent-core-local-scheduler-1 2>&1 | grep -E
  "webhook_receiver|dlq_reaper|webhook_selftest"` shows clean registration
  (matches the 2026-07-13 17:51 onwards baseline).
- [x] [historical] (NEW FOLLOW-UP) Add the one-shot `scheduler.manifest.import_failed`
  WARNING in `registry_loader.py` so a future ImportError surfaces ONCE per
  manifest, not per reload. Reference: design.md §3.2.

### 3.3 Hard/soft health gate split

- [x] [historical] Edit `~/Developer/tdt/ai-review/src/ai_review/utils/health.py`:
  - [x] [historical] Add `SOFT_CHECKS = frozenset({"omniroute_proxy", "kimi_cli", "circuit_breaker", "sessions"})` constant
  - [x] [historical] Add `HARD_CHECKS = frozenset({"scheduler", "postgres"})` constant
  - [x] [historical] Add `overall_status(checks: dict) -> tuple[str, bool]` function (returns `(status, http_503)`)
  - [x] [historical] Update the `/health/full` route handler to use `overall_status()` and return 503 only when `http_503=True`
- [x] [historical] Add unit tests in `~/Developer/tdt/ai-review/tests/utils/test_health.py`:
  - [x] [historical] All OK → `("ok", False)`
  - [x] [historical] SOFT error → `("degraded", False)`
  - [x] [historical] HARD error → `("error", True)`
  - [x] [historical] Mixed → `("error", True)`
- [x] [historical] Run `cd ~/Developer/tdt/ai-review && pytest tests/utils/test_health.py -x && ruff check . && mypy src/ --strict`
- [x] [historical] Smoke test: with OmniRoute returning 500, `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/health/full` returns `200` (not `503`)

## 4. Observability alerting

### 4.1 Add `scheduler.workflow.failed` burst rule

- [x] [historical] Edit `~/.tdt/observability/config.yaml`: append `alerts.scheduler_workflow_failed_burst` block (per design.md §4)
- [x] [historical] Reload the alert catalog: `launchctl unload ~/Library/LaunchAgents/com.tdt.observability-health-poller.plist && launchctl load ...`
- [x] [historical] Verify rule is registered: `python3 -c "from tdt_observability.alerts import check_alerts; print(check_alerts('scheduler_workflow_failed_burst'))"`

### 4.2 Add `postgres_backup_stale` rule

- [x] [historical] Edit `~/.tdt/observability/config.yaml`: append `alerts.postgres_backup_stale` block
- [x] [historical] Same reload + verify step as 4.1

## 5. Documentation updates

### 5.1 scheduler-healthcheck.md — soft/hard subsection

- [x] [historical] Edit `~/Developer/tdt/tdt-meta/docs/operations/scheduler-healthcheck.md`:
  - [x] [historical] Add section "Hard vs Soft Degradation" with examples
  - [x] [historical] Cross-link to `observability-runbook.md#alert-catalog`

### 5.2 observability-runbook.md — alert catalog

- [x] [historical] Edit `~/Developer/tdt/tdt-meta/docs/operations/observability-runbook.md`:
  - [x] [historical] Add `scheduler_workflow_failed_burst` to Alert Catalog
  - [x] [historical] Add `postgres_backup_stale` to Alert Catalog
  - [x] [historical] Add `omniroute_proxy_unavailable` (derived from per-check map) to Alert Catalog

### 5.3 postgres-restore.md — sidecar availability

- [x] [historical] Edit `~/Developer/tdt/tdt-meta/docs/operations/postgres-restore.md`:
  - [x] [historical] Add "Sidecar availability" section with the contract (best-effort, 03:00 UTC cron, 30-day retention)
  - [x] [historical] Link to the `postgres_backup_stale` alert

## 6. Validation

- [x] [historical] Run `openspec validate --strict ops-scheduler-omniroute-jira-failures` (expect zero errors)
- [x] [historical] Wait 7 days; verify `scheduler-entrypoint.log` has zero `ModuleNotFoundError: No module named 'gitlab'` entries
- [x] [historical] Manually stop OmniRoute for 10 minutes; verify `ai-review /health/full` returns HTTP 200 with `status=degraded`
- [x] [historical] Manually delete all `.pgdump` files; verify `postgres_backup_stale` alert fires within one polling cycle

## 7. Out-of-scope reminders

- **OmniRoute itself**: 3rd-party Electron app, no source access. Mitigation is the health-degradation contract, not a fix.
- **Restoring 13 days of missing backups**: not possible. Document and move on.
- **Migrating `agent-core` scheduler**: out of scope.

---

> **Historical record:** This change was archived with 32 incomplete task(s) (19/51 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
