# Tasks

## 1. Container Image and Ignore Rules

- [x] 1.1 Create `shb-schedule/Dockerfile` as a multi-stage build based on `python:3.14-slim` (3.14.8): copy the pinned uv binary from `ghcr.io/astral-sh/uv:0.12.23` (`COPY --from=ghcr.io/astral-sh/uv:0.12.23 /uv /uvx /bin/`), `COPY` only sibling sources `shb-core`, `shb-tools`, `shb-schedule` into `/app`, run `uv sync --frozen --no-dev --no-editable` (with a `--mount=type=cache,target=/root/.cache/uv` cache mount and `ENV UV_COMPILE_BYTECODE=1`), then in the runner stage copy only `/app/shb-schedule/.venv` and run as a non-root user. Entrypoint: `["shb-schedule"]`, default command `["serve", "--host", "0.0.0.0", "--port", "9110"]` (the explicit `--host 0.0.0.0` is REQUIRED because `cli.py` hardcodes the `serve` default to `127.0.0.1`). Verify `docker build` succeeds.
- [x] 1.2 Create `shb-schedule/Dockerfile.dockerignore` (NOT `shb-schedule/.dockerignore`, which BuildKit ignores when context is `..`) with recursive globs `**/.venv/`, `**/.gitnexus/`, `**/graphify-out/`, `**/__pycache__/`, `**/.git/`, and `**/*.pyc`; verify `docker build` context transfer excludes those paths (the build context is the entire `~/Developer/shb` parent, ~2.4 GB across 13 repos).

## 2. Docker Compose Stack

- [x] 2.1 Create `shb-schedule/compose.yaml` defining a `db` service (`postgres:18.6-alpine`, with environment `PGDATA=/var/lib/postgresql/data/pgdata`, explicit `healthcheck:` block using `pg_isready -U shb_scheduler -d shb_scheduler`, `interval: 5s`, `timeout: 5s`, `retries: 5`, `start_period: 10s`, and a named volume `shb-scheduler-pgdata` declared at top-level `volumes:` and mounted at `/var/lib/postgresql/data`) and a `scheduler` service with `depends_on: { db: { condition: service_healthy } }`, env `SHB_SCHEDULER_BACKEND=postgres`, `SHB_SCHEDULER_DATABASE_URL=postgresql://shb_scheduler:${SHB_SCHEDULER_DB_PASSWORD:-shb_dev_secret}@db:5432/shb_scheduler`, `SHB_SCHEDULER_POSTGRES_SCHEMA=shb_scheduler`, `SHB_SCHEDULER_SCHEDULES_DIR=/etc/shb/schedules`, and a read-only mount of `${HOME}/.shb/schedules` to `/etc/shb/schedules`. Verify `docker compose config` parses without errors.
- [x] 2.2 Create `shb-schedule/compose.override.yaml` adding local bindings: publish `127.0.0.1:9110:9110` and an optional commented read-only workspace mount; verify `docker compose config` shows merged config and base profile remains manifest-only.
- [x] 2.3 Verify the full stack boots and persists state: run `docker compose up -d`, confirm `docker compose ps` reports `db` healthy and `scheduler` up, and confirm `shb_scheduler` schema with 13 DBOS tables exists via `docker compose exec db psql -U shb_scheduler -c "SELECT tablename FROM pg_tables WHERE schemaname='shb_scheduler';"`; restart via `docker compose down && docker compose up -d` (without `-v`) to assert named volume persistence.

## 3. Runtime Verification of Containerized Scheduler

- [x] 3.1 Verify manifests load in-container: run `docker compose exec scheduler shb-schedule validate /etc/shb/schedules` and confirm all three manifests (`daily-shb-docs-sync`, `eod-settlement-recon`, `nightly-compliance-scan`) validate.
- [x] 3.2 Verify durable execution across the network: run `docker compose exec scheduler shb-schedule run-now eod-settlement-recon` and confirm fail-closed status `ACTION_REQUIRED` on absent input; with fixture ledgers supplied, verify `BALANCED`; verify the `workflow_status` row is persisted in the `shb_scheduler` schema (PostgreSQL MVCC row locks enable concurrent `run-now` triggers alongside the daemon without lock contention).
- [x] 3.3 Verify the HTTP health surface: `curl -fsS http://127.0.0.1:9110/scheduler/health` returns ownership/persistence/schedule status without credentials (and confirm the container binds `0.0.0.0:9110`, not loopback only, by checking the entrypoint passes `--host 0.0.0.0`; verify single-owner leadership is governed by PostgreSQL session advisory lock across containers, with competing daemons exiting cleanly with status 0 or serving read-only standby returning HTTP 503).
- [x] 3.4 Verify fail-closed behavior for documentation and compliance workflows: in manifest-only container, run `docker compose exec scheduler shb-schedule run-now daily-shb-docs-sync` and `nightly-compliance-scan` and confirm both report `PARTIAL` (not `SUCCESS`) when all target repositories are unmounted; verify with mounted fixture workspace both scan real repositories.

## 4. Remove Host Service Installers

- [x] 4.1 Delete `src/shb_schedule/service/launchd.py` (and the `service` package if it becomes empty), remove the `service` Typer sub-app and the `service install` command from `src/shb_schedule/cli.py`, and verify `shb-schedule --help` no longer lists `service` and the test suite still passes (`uv run pytest tests/ -q`).
- [x] 4.2 Add or update a unit test asserting the `service` subcommand is absent from the CLI, and verify it passes with `uv run pytest tests/ -q`.

## 5. Documentation

- [x] 5.1 Update `shb-schedule/README.md` to document containerized operation (`docker compose up -d`, `docker compose exec scheduler ...`, health probe, pinned `postgres:18.6-alpine`, clean-start semantics); verify documented commands run as written.
- [x] 5.2 Update `shb-agent-skills/skills/scheduler-skill/SKILL.md` to reference Docker Compose operation and remove LaunchAgent/systemd install guidance; verify the skill renders and contains no `launchctl`/`systemctl` install instructions.

## 6. Integration Verification

- [x] 6.1 End-to-end: from a clean volume, `docker compose up -d`, wait for health, run all three `run-now` triggers, tail logs to confirm zero errors, then `docker compose down`; record the evidence.
- [x] 6.2 Cross-check portability: confirm `compose.yaml` contains no host-absolute paths beyond `${HOME}`-based manifest mounts and no host binary invocations.

## 7. Hardening and Multi-Container Ownership Verification

- [x] 7.1 Multi-container PostgreSQL advisory lock ownership: implement `PostgresLeaderLock` with session advisory locking; verify secondary container exits cleanly (code 0) without port collision while primary is active, and verify `--standby` mode serves read-only health/reload/trigger returning HTTP 503.
- [x] 7.2 Bounded ownership liveness and fail-closed demotion: verify termination of leader database backend session (`pg_locks` advisory PID) causes existing primary to demote to standby within bounded check (HTTP 503), halting sentinel watcher, tearing down signal handlers, and destroying DBOS runtime dispatchers, enabling a fresh contender to acquire leadership cleanly.
- [x] 7.3 Fail-closed workflow and ledger input hardening: verify partial repository availability (1 succeeded, 11 missing) reports `PARTIAL` rather than false `SUCCESS`; verify non-finite, nan, inf, bool, overflow, and one-sided transaction inputs report `ACTION_REQUIRED`; verify direct `psycopg[binary]` dependency and dev-only `httpx2` eliminate all test suite warnings (47 passed, 0 warnings).
- [x] 7.4 Hermetic disabled mode passthrough: implement plain unrecorded workflow orchestration helpers for all 3 built-in workflows (`eod-settlement-recon`, `daily-shb-docs-sync`, `nightly-compliance-scan`); verify `resolve_callable` dispatches to plain functions when `SHB_SCHEDULER_ENABLED=false` without requiring an active scheduler database or initialized DBOS runtime; verify fresh subprocess execution runs all 3 workflows without creating SQLite database files.
