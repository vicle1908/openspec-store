## 1. jira-epic-report — ScheduleConfig and TOML parsing

- [x] 1.1 Add `ScheduleConfig` dataclass to `jira-epic-report/epic_report/config.py` with fields: `enabled: bool = False`, `epics: list[str] = []`, `cron: str = "0 7 * * *"`, `timezone: str | None = None`, `format: str = "spreadsheet"`, `spreadsheet_url: str | None = None`
- [x] 1.2 Extend `AppConfig.from_env` (`epic_report/config.py:198-212`) to read the `[schedule]` table; populate `AppConfig.schedule`; tolerate missing section (returns `ScheduleConfig(enabled=False)`)
- [x] 1.3 Resolve `[schedule].spreadsheet_url`: explicit value wins, otherwise fall back to `output.spreadsheet_url`; store as `AppConfig.schedule.spreadsheet_url`
- [x] 1.4 Resolve `[schedule].timezone`: explicit value wins, otherwise call the new inline workspace-timezone resolver (returns the canonical workspace timezone — see step 1.7)
- [x] 1.5 Extend `AppConfig.validate()` (config.py:249-258) to require `epics` non-empty when `schedule.enabled is True`; append `"schedule.epics required when enabled"` to the error list
- [x] 1.6 Update `AppConfig.to_display_dict()` (config.py:260-273) to surface `[schedule]` fields when present
- [x] 1.7 Add a small private helper `_resolve_workspace_timezone()` at module scope that implements the env-var chain `PERSON_CAPACITY_TIMEZONE` → `TDT_TIMEZONE` → `TZ` → `tzlocal.get_localzone_name()` → `"UTC"`, with a docstring citing `jira_daily_reports.config.workspace_timezone_name()` as the canonical reference
- [x] 1.8 Add a regression test in `jira-epic-report/tests/test_config.py` that mocks `PERSON_CAPACITY_TIMEZONE=Asia/Ho_Chi_Minh` and asserts the inline resolver returns `"Asia/Ho_Chi_Minh"` (and a parallel test that asserts `None` for all env vars → `"UTC"`)
- [x] 1.9 Add unit tests in `jira-epic-report/tests/test_config.py`: missing-section (defaults to disabled), enabled-with-epics, enabled-without-epics (validation error), `[schedule].spreadsheet_url` defaulting to `[output].spreadsheet_url`, `[schedule].timezone` defaulting to the resolver output

## 2. jira-epic-report — `scheduled-run` CLI subcommand

- [x] 2.1 Add `scheduled-run` Typer command in `jira-epic-report/epic_report/cli.py` that calls `AppConfig.from_env()`
- [x] 2.2 When `enabled=False`, log `scheduled_run.disabled` and exit 0 (no Jira calls, no spreadsheet writes)
- [x] 2.3 When `enabled=True`, validate non-empty `epics` (CLI-layer pre-flight per spec scenario "CLI subcommand — missing required fields exit non-zero"); exit non-zero with a clear error if empty
- [x] 2.4 Resolve `EPIC_REPORT_SPREADSHEET_URL` from `schedule.spreadsheet_url` (which is already `[schedule].spreadsheet_url` → fallback `[output].spreadsheet_url` per task 1.3)
- [x] 2.5 Invoke `generate()` via `subprocess.run([sys.executable, "-m", "epic_report", "generate", *schedule.epics, "--format", schedule.format], env={"EPIC_REPORT_SPREADSHEET_URL": url, **os.environ}, check=False, capture_output=True, text=True)`; raise `subprocess.CalledProcessError` on non-zero exit so the workflow surfaces failures per spec req "DBOS workflow wiring — Subprocess failure surfaces"
- [x] 2.6 Add unit tests in `jira-epic-report/tests/test_cli.py`: disabled-no-op, enabled-success (mocked subprocess), enabled-validation-error, env-var propagation when `[schedule].spreadsheet_url` is absent (falls back to `[output].spreadsheet_url`), subprocess non-zero exit propagated
- [x] 2.7 Update `jira-epic-report/README.md` (and any config docs) with a `[schedule]` example block including a `timezone` line and a one-line "set enabled=true to run daily" usage note

## 3. agent-core — manifest generator

- [x] 3.1 Create `agent-core/deployments/scheduler/generators/jira_epic_report.py` mirroring `code_daily_scan.py`'s structure (a `jira_epic_report_manifest()` factory + self-call to `register("jira-epic-report", ...)` at module load)
- [x] 3.2 Implement `jira_epic_report_manifest()`: resolve the container-localized `epic_report.config` import (same pattern as `code_daily_scan.py:24-31`), call `AppConfig.from_env()`, build the `ScheduleSpec`-shaped dict: `{name: "daily-epic-report", cron, timezone, automatic_backfill: False, workflow: {module: "agent_core.scheduler_setup", function: "daily_epic_report"}}`
- [x] 3.3 Handle the disabled path: if `schedule.enabled` is `False` (or section absent), return `{"apiVersion": "tdt-schedule/v1", "owner": "jira-epic-report", "version": "1.0.0", "schedules": []}` so the dispatcher skips the write
- [x] 3.4 Handle the enabled-invalid path: if `schedule.enabled` is `True` but `epics` is empty or `cron` fails `re.match(r"^[\d\*\-\/,\s]+$", schedule.cron)`, **raise RuntimeError** BEFORE returning — so the dispatcher's outer `except Exception` exits non-zero and `entrypoint.sh` aborts the container
- [x] 3.5 Add tests in `agent-core/tests/test_scheduler_setup.py` (extend the existing test file rather than create a new one) covering: disabled → empty-schedules manifest (no write), enabled → one-schedule manifest with `automatic_backfill: False` and `daily-epic-report` as the name, enabled-with-empty-epics → raises, enabled-with-invalid-cron → raises, missing-config → disabled path

## 4. agent-core — generator registration + entrypoint

- [x] 4.1 Edit `agent-core/deployments/scheduler/generators/__init__.py:_import_submodules()` to append `"jira_epic_report"` to the tuple on line 53
- [x] 4.2 Edit `agent-core/deployments/scheduler/entrypoint.sh` to append `jira-epic-report` to the `for repo in ...` loop on line 66 (the loop already passes `repo` to `dispatch_manifest_generation.py`, which looks up the factory in `GENERATORS`)

## 5. agent-core — DBOS workflow + env-var forwarding

- [x] 5.1 Add `_run_epic_report()` private helper in `agent_core/scheduler_setup.py` (mirror `_run_platform_scan`'s env-var forwarding at lines 223-274). Build the command `[sys.executable, "-m", "epic_report", "scheduled-run"]`, copy `os.environ`, and forward `GOOGLE_APPLICATION_CREDENTIALS` plus the resolved spreadsheet URL via `EPIC_REPORT_SPREADSHEET_URL`. The host-provided `JIRA_*` env vars are inherited automatically via `os.environ.copy()` — the `JiraClientFactory.from_env()` call inside `epic-report` reads them.
- [x] 5.2 Add `@_dbos.DBOS.workflow() async def daily_epic_report(*args, **kwargs)` that calls `await asyncio.to_thread(_run_epic_report)`
- [x] 5.3 Add unit tests in `agent-core/tests/test_scheduler_setup.py` for `_run_epic_report`: env-var forwarding (`JIRA_*` inherits from `os.environ`, `GOOGLE_APPLICATION_CREDENTIALS` is passed, `EPIC_REPORT_SPREADSHEET_URL` is set), subprocess failure → `subprocess.CalledProcessError`

## 6. agent-core — Dockerfile, compose, gate wiring

- [x] 6.1 Edit `agent-core/deployments/scheduler/Dockerfile` to add (after line 52, mirroring the `code-daily-scan` block 49-52):
  - `COPY --chown=agent:agent jira-epic-report/pyproject.toml jira-epic-report/README.md /workspace/jira-epic-report/`
  - `COPY --chown=agent:agent jira-epic-report/src /workspace/jira-epic-report/src`
- [x] 6.2 Add `jira-epic-report` to the `sed` rewrite loop in `Dockerfile` lines 61-81: include `/workspace/jira-epic-report/pyproject.toml` in the file list, and add `path = "/workspace/jira-epic-report"` to the rewrites
- [x] 6.3 Add `uv pip install --python /opt/scheduler/.venv/bin/python3 -e /workspace/jira-epic-report` to the editable-install chain at `Dockerfile:110-115`. Place it **after** `webhook-receiver` (line 115), since `jira-epic-report` depends transitively on `jira-skill` (already installed at line 112). Specifically the chain order is: `tdt-sheets` → `tdt-observability` → `jira-skill` → `jira-daily-reports` → `code-daily-scan` → `webhook-receiver` → **`jira-epic-report`** (new last).
- [x] 6.4 Edit `agent-core/compose.yaml` `scheduler.volumes` to add `- ../jira-epic-report/src:/workspace/jira-epic-report/src:ro` (mirroring the `code-daily-scan/src` line 141)
- [x] 6.5 Edit `agent-core/deployments/scheduler/dependency_integrity_gate.py:HOSTED_WORKLOADS` to append `"jira-epic-report"`
- [x] 6.6 Edit `agent-core/deployments/scheduler/dependency_integrity_gate.py:ENTRY_MODULES` to add `"jira-epic-report": ("epic_report.cli",)` (so the startup-mode import exercises `epic_report.cli`)
- [x] 6.7 Edit `agent-core/deployments/scheduler/Dockerfile:HEALTHCHECK` (line 137) so the `python -c` invocation ALSO imports `epic_report.cli`. The current string is `from tdt_core.scheduler.cli import app; import code_daily_scan.cli, jira_daily_reports.cli; print('ok')` — change to `from tdt_core.scheduler.cli import app; import code_daily_scan.cli, jira_daily_reports.cli, epic_report.cli; print('ok')` (single string, comma-separated imports in one statement)

## 7. End-to-end verification

- [x] 7.1 `ruff check . --fix && ruff format .` in both repos
- [x] 7.2 `mypy jira-epic-report/ --strict` and `mypy agent-core/ --strict`
- [x] 7.3 `pytest -x` in both repos; all new tests green; coverage stays above `pyproject.toml:66`'s `cov-fail-under=80`
- [x] 7.4 `openspec validate --strict scheduled-epic-report` exits 0
- [x] 7.5 Manual smoke: `cd agent-core && docker compose up --build -d scheduler` and verify `~/.tdt/schedules/jira-epic-report.yaml` contains one `daily-epic-report` entry with `automatic_backfill: false` and the resolved `cron_timezone` — VERIFIED: container rebuilt, manifest written with `name=daily-epic-report` / `cron=0 7 * * *` / `timezone=Asia/Ho_Chi_Minh` / `automatic_backfill=false`
- [x] 7.6 Manual smoke: invoke `epic-report scheduled-run` inside the container once to confirm end-to-end behavior before relying on the cron tick; verify the dedicated spreadsheet is updated — VERIFIED: `uv run python -m epic_report scheduled-run --verbose` exit 0 with `cmd=...epic_report generate RMD-4160 --format spreadsheet` and `url=<set>`
- [x] 7.7 Verify scheduler health: `curl http://127.0.0.1:9100/scheduler/health` and confirm `daily-epic-report` is registered — VERIFIED: `schedule_count=22`, `manifests_loaded=5`, log shows `schedule.workflow_registered ... schedule=daily-epic-report`
- [x] 7.8 Verify integrity gate: `docker compose exec scheduler /dependency_integrity_gate.py --mode startup` exits 0 — VERIFIED: `integrity-gate[startup]: OK — verified 5 workloads: jira-daily-reports, code-daily-scan, tdt-observability, webhook-receiver, jira-epic-report`
- [x] 7.9 Verify `tdt-scheduler schedules list` (per `scheduler-cli` spec requirement "List all schedules") shows `daily-epic-report` alongside `daily-android-scan` / `daily-ios-scan` — VERIFIED: `daily-epic-report | daily_epic_report | 0 7 * * * | ACTIVE`