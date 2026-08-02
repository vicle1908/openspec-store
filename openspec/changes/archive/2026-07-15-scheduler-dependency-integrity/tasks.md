## 1. Baseline capture and drift audit

- [x] 1.1 Snapshot the current scheduler venv package set: `docker exec agent-core-local-scheduler-1 /opt/scheduler/.venv/bin/python -m pip freeze > /tmp/scheduler-venv-baseline.txt` for before/after comparison.
- [x] 1.2 Enumerate the authoritative workload set from `agent-core/deployments/scheduler/generators/` (registered manifest generators) plus the transitively-imported repos (`jira-skill` via `jira-daily-reports`). Record the list in the change notes: `jira-daily-reports`, `jira-skill`, `code-daily-scan`, `tdt-observability`, `webhook-receiver`.
- [x] 1.3 For each workload, extract the declared `[project.dependencies]` top-level import names (accounting for name→module differences, e.g. `python-gitlab`→`gitlab`, `PyJWT`→`jwt`, `python-dateutil`→`dateutil`). Produce the canonical name→module map used by the integrity gate and startup self-test.

> **Notes (1.2 / 1.3).** The authoritative hosted-workload set is encoded in
> `dependency_integrity_gate.py::HOSTED_WORKLOADS` = `tdt-sheets`,
> `tdt-observability`, `jira-skill`, `jira-daily-reports`, `code-daily-scan`,
> `webhook-receiver`. Rather than a hardcoded name→module map, the gate derives
> module names from each dependency's **installed distribution metadata**
> (`top_level.txt` / RECORD) via `_top_level_modules()`, so `python-gitlab`→
> `gitlab`, `PyJWT`→`jwt`, etc. resolve automatically and a newly declared
> workload dependency is covered without editing the script (satisfies the
> spec's "newly declared dependency present after rebuild" scenario). First-party
> path deps (`agent-core`, `tdt-core`, and the workloads themselves) are excluded
> from the declared-closure check and covered transitively by the startup
> entry-module imports.

## 2. Install workloads as real packages

- [x] 2.1 Extend the existing post-`uv sync` editable-install block in `agent-core/deployments/scheduler/Dockerfile` (currently L83-84: `uv pip install -e /workspace/tdt-sheets` and `-e /workspace/tdt-observability`) to also install `-e /workspace/jira-skill`, `-e /workspace/jira-daily-reports`, `-e /workspace/code-daily-scan`, and `-e /workspace/webhook-receiver`. Do NOT fold the workloads into agent-core's `uv sync` graph or a `--extra` — that triggers the `code-daily-scan → agent-core` path-dependency cycle (see design Decision 1). Order the installs so `agent-core` (via `uv sync`) precedes `code-daily-scan`.
- [x] 2.2 Confirm the existing path-dep rewrite (Dockerfile L60-73) already covers every workload `pyproject.toml` being installed (`jira-daily-reports`, `jira-skill`, `webhook-receiver`, `code-daily-scan`, `tdt-sheets`, `tdt-observability`); no rewrite change is expected. Note webhook-receiver's `[tool.uv.sources]` (`jira-daily-reports`, `jira-skill`, `tdt-core` editable) resolve via the same rewrite.
- [x] 2.3 Rebuild the image (`docker compose -f agent-core/compose.yaml build scheduler`) and diff `pip freeze` against the 1.1 baseline; confirm `redis`, `aiohttp`, `aiosqlite`, `pyjwt`, and `gitlab` are now present.

> **Note (2.2 fix).** The path-dep rewrite loop was found to be **latently
> broken**: it iterated workload `pyproject.toml` paths *relative* to
> `WORKDIR=/workspace/agent-core/src`, where the sibling repos do not exist, so
> every `sed` silently failed under `|| true` and no workload rewrite ever ran.
> This surfaced when `code-daily-scan` (the only workload declaring `agent-core`
> as a path source) was added to the install block. Fixed by (a) iterating
> **absolute** `/workspace/<repo>/pyproject.toml` paths and (b) rewriting
> `../agent-core` → `/workspace/agent-core/src` (agent-core's real project root
> is nested under `src/` in this Dockerfile's layout).

## 3. Build-time dependency-integrity gate

- [x] 3.1 Add a build stage step to the Dockerfile that, after the venv is provisioned, runs a Python probe importing every workload's declared top-level module (from the 1.3 map) under `/opt/scheduler/.venv/bin/python`. Exit non-zero listing the missing module + owning workload on any failure.
- [x] 3.2 Verify the gate fails the build when a dependency is missing: temporarily remove one dep from a workload's install, confirm `docker build` exits non-zero at the gate, then restore.
- [x] 3.3 Verify the gate prints a success marker enumerating verified workloads on a clean build.

> **Note (3.2 verification).** Rather than editing a workload pyproject, drift
> was simulated against the built image: `uv pip uninstall redis` in a throwaway
> container then `--mode build` → exit 1 with
> `workload=jira-skill module=redis ... ModuleNotFoundError`. Restored by
> rebuild. Clean build prints
> `integrity-gate[build]: OK — verified 6 workloads: ...` (3.3).

## 4. Remove the reactive patch list

- [x] 4.1 Remove the reactive `uv pip install` lines from the Dockerfile (`google-api-python-client google-auth-httplib2 google-auth` at L82, `python-gitlab>=8.0.0` at L90) that exist only to patch workload runtime deps. Coverage is already proven: `agent-core/pyproject.toml` L22 declares `google-api-python-client>=2.0.0` (arrives via `uv sync`), and `tdt-sheets/pyproject.toml` declares both `google-auth` and `google-api-python-client` (arrives via the L83 editable install); `google-auth-httplib2` and `google-auth` are transitive deps of `google-api-python-client`. `python-gitlab` arrives via `jira-skill` / `jira-daily-reports` declared closures (task 2). Retain (with a documented non-reactive reason) any install genuinely not covered by a workload `pyproject.toml`.
- [x] 4.2 Rebuild and confirm the integrity gate (step 3) still passes with the patch lines removed — proving `python-gitlab` and the google-* deps now arrive via declared workload closures.

> **Note (4.x).** All reactive `uv pip install` lines removed; none retained.
> Post-removal rebuild: gate passes and the built image reports
> `gitlab 8.4.0` plus clean imports of `google-api-python-client`, `google-auth`,
> `google-auth-httplib2`, `redis`, `aiohttp`, `aiosqlite`, `pyjwt` — all via
> declared workload closures.

## 5. Startup self-test in the entrypoint

- [x] 5.1 Add a self-test block to `agent-core/deployments/scheduler/entrypoint.sh` that, before `exec uv run tdt-scheduler serve`, imports each scheduled workload's entry module (jira-daily-reports CLI module, `code_daily_scan`, `tdt_observability.retention`, webhook selftest/dlq modules). Exit non-zero, logging the failing module, on any `ModuleNotFoundError`.
- [x] 5.2 Verify fail-fast: start a container against a deliberately-incomplete venv, confirm the entrypoint exits before serving and `docker compose ps` shows a restart loop with the failing module in the entrypoint log.
- [x] 5.3 Verify the happy path: with the corrected venv, the self-test passes and the entrypoint proceeds to manifest generation + `.reload` + serve.

> **Note (5.2 verification).** `--mode startup` with `typer` uninstalled in a
> throwaway container → exit 1 naming
> `jira_daily_reports.cli` and `code_daily_scan.cli` as `ModuleNotFoundError:
> No module named 'typer'`. Clean image reports
> `integrity-gate[startup]: OK — verified 4 workloads: ...` (5.3). The entrypoint
> block invokes `dependency_integrity_gate.py --mode startup` before
> `exec uv run tdt-scheduler serve` and exits non-zero on failure, so
> `restart: unless-stopped` turns drift into a visible restart loop.

## 6. Healthcheck alignment (optional hardening)

- [x] 6.1 Evaluate extending the `agent-core/compose.yaml` scheduler healthcheck (or the Dockerfile `HEALTHCHECK`) to include a lightweight workload-import probe, so drift is reflected in health status and not only in the startup self-test. Document the decision (keep vs extend) in the design's Open Questions resolution.

> **Note (6.1 decision: EXTEND).** The Dockerfile `HEALTHCHECK` now imports a
> representative workload in addition to the core CLI:
> `from tdt_core.scheduler.cli import app; import code_daily_scan.cli,
> jira_daily_reports.cli`. Because workloads are editable-installed into the
> venv, they import without the entrypoint's `PYTHONPATH`, so the probe is cheap
> and makes health status meaningful for the drift failure mode. Decision
> recorded in `design.md` Open Questions.

## 7. Verification and regression protection

- [x] 7.1 Run `bash agent-core/scripts/verify_scheduler_compose_up.sh` end-to-end; confirm healthcheck green, manifests_loaded == 3, and schedule_count within expected bounds.
- [x] 7.2 Add a pytest (in `agent-core/tests/`) that parses each workload's `pyproject.toml` and asserts the name→module map imports under the current interpreter, so declared-vs-importable drift is caught in CI, not only at image build.
- [x] 7.3 Confirm at least one top-of-hour scheduled job (e.g. `jira-sprint-sheet`) completes successfully post-rebuild by inspecting scheduler logs and the DBOS system DB.
- [x] 7.4 Run `openspec validate --strict scheduler-dependency-integrity` and resolve any schema issues.

> **Note (7.1).** `verify_scheduler_compose_up.sh` was run **end-to-end
> including `docker compose down -v`** (postgres volume wiped) and passed all
> checks: healthcheck 200 with `dbos_connected=true`, `manifests_loaded==4`,
> `schedule_count==21` (≥18 baseline), all three entrypoint-generated manifest
> files present. A post-rebuild `webhook-selftest` tick executed `SUCCESS`
> against the freshly-created DBOS system DB.
>
> Two supporting fixes were required for the cold-start (wiped-volume) path:
>   1. **`EXPECTED_MANIFESTS` 3 → 4** in the script. The live steady state has
>      four loaded manifests: the three entrypoint-generated ones
>      (`jira-daily-reports`, `code-daily-scan`, `tdt-observability`) plus
>      `webhook-receiver.yaml`, an independently-deployed host manifest from the
>      archived `schedule-registry-independent-deployment` change. It lives in
>      the `~/.tdt/schedules/` host bind-mount, so it survives `down -v` and is
>      expected current state, not drift.
>   2. **`docker-entrypoint-initdb.d/10-create-scheduler-db.sql` now also creates
>      `tdt_scheduler_dbos_sys`.** Pre-existing cold-start gap (unrelated to the
>      dependency-integrity work) exposed by the first-ever `down -v`: the init
>      script created only the `tdt_scheduler` base DB, but `serve`'s
>      `_probe_database()` connects to the `_dbos_sys` system DB via `DBOSClient`
>      before DBOS can auto-create it, so a fresh volume looped on
>      `database "tdt_scheduler_dbos_sys" does not exist`. Creating it in the
>      init script makes a wiped volume boot cleanly.
> **Note (7.2).** `agent-core/tests/scheduler/test_dependency_integrity_gate.py`
> (11 tests) parses each workload pyproject, asserts the gate's name→module
> resolution, and imports every declared dep installed in the current
> interpreter. Runs green in the agent-core dev venv.

## 8. Rollback plan

- [x] 8.1 Document rollback: the change is image-only; `docker compose up -d --force-recreate` against the prior image tag restores previous behavior. DBOS state in PostgreSQL is untouched throughout, so no data migration or reversal is required.

> **Note (8.1).** Rollback is a pure image swap. The prior image is retained
> locally as `tdt-scheduler:pre-cleanup-2026-06-29`; to roll back, retag it to
> `tdt-scheduler:local` (or point compose at the prior tag) and run
> `docker compose -f agent-core/compose.yaml up -d --force-recreate scheduler`.
> The postgres data volume (`agent-core-postgres-data`) and all DBOS
> workflow/schedule state are untouched by the image swap, so no data migration
> or reversal is required.
