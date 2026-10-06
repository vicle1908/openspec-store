# Tasks

## 1. Container Image and Ignore Rules

- [ ] 1.1 Create `shb-schedule/Dockerfile` as a multi-stage build (python:3.14-slim base, uv install, `COPY` sibling `shb-core`, `shb-tools`, and `shb-schedule` sources, `uv sync --frozen`, non-root user, entrypoint `shb-schedule serve --port 9110`); verify `docker build` completes successfully with build context set to the `~/Developer/shb` parent.
- [ ] 1.2 Create `shb-schedule/.dockerignore` excluding `.gitnexus/`, `graphify-out/`, `__pycache__/`, `.venv/`, and test caches; verify the built image does not contain those paths (`docker run --rm <image> ls -a`).

## 2. Docker Compose Stack

- [ ] 2.1 Create `shb-schedule/compose.yaml` defining a `db` service (`postgres:18-alpine`, `pg_isready` healthcheck, named volume `shb-scheduler-pgdata`) and a `scheduler` service with `depends_on: db: condition: service_healthy`, env `SHB_SCHEDULER_BACKEND=postgres`, `SHB_SCHEDULER_DATABASE_URL=postgresql://...@db:5432/shb_scheduler`, `SHB_SCHEDULER_POSTGRES_SCHEMA=shb_scheduler`, `SHB_SCHEDULER_SCHEDULES_DIR=/etc/shb/schedules`, and a read-only mount of `${HOME}/.shb/schedules` to `/etc/shb/schedules`; verify `docker compose config` renders without error.
- [ ] 2.2 Create `shb-schedule/compose.override.yaml` adding local bindings: publish `127.0.0.1:9110:9110` and an optional commented read-only workspace mount; verify `docker compose config` shows merged config and base profile remains manifest-only.
- [ ] 2.3 Verify the full stack boots from clean state: run `docker compose down -v && docker compose up -d`, confirm `docker compose ps` reports `db` healthy and `scheduler` up, and confirm `shb_scheduler` schema with 13 DBOS tables exists via `docker compose exec db psql -U shb_scheduler -c "SELECT tablename FROM pg_tables WHERE schemaname='shb_scheduler';"`.

## 3. Runtime Verification of Containerized Scheduler

- [ ] 3.1 Verify manifests load in-container: run `docker compose exec scheduler shb-schedule validate /etc/shb/schedules` and confirm all three manifests (`daily-shb-docs-sync`, `eod-settlement-recon`, `nightly-compliance-scan`) validate.
- [ ] 3.2 Verify durable execution across the network: run `docker compose exec scheduler shb-schedule run-now eod-settlement-recon` and confirm status `BALANCED` / `ACTION_REQUIRED`; verify the `workflow_status` row is persisted in the `shb_scheduler` schema.
- [ ] 3.3 Verify the HTTP health surface: `curl -fsS http://127.0.0.1:9110/scheduler/health` returns ownership/persistence/schedule status without credentials.

## 4. Remove Host Service Installers

- [ ] 4.1 Delete `src/shb_schedule/service/launchd.py` (and the `service` package if it becomes empty), remove the `service` Typer sub-app and `service install` command from `src/shb_schedule/cli.py`, and verify `shb-schedule --help` no longer lists `service` and the test suite still passes (`uv run pytest tests/ -q`).
- [ ] 4.2 Add or update a unit test asserting the `service` subcommand is absent from the CLI, and verify it passes with `uv run pytest tests/ -q`.

## 5. Documentation

- [ ] 5.1 Update `shb-schedule/README.md` to document containerized operation (`docker compose up -d`, `docker compose exec scheduler ...`, health probe, Postgres 18.6 pin, clean-start semantics); verify documented commands run as written.
- [ ] 5.2 Update `shb-agent-skills/skills/scheduler-skill/SKILL.md` to reference Docker Compose operation and remove LaunchAgent/systemd install guidance; verify the skill renders and contains no `launchctl`/`systemctl` install instructions.

## 6. Integration Verification

- [ ] 6.1 End-to-end: from a clean volume, `docker compose up -d`, wait for health, run all three `run-now` triggers, tail logs to confirm zero errors, then `docker compose down`; record the evidence.
- [ ] 6.2 Cross-check portability: confirm `compose.yaml` contains no host-absolute paths beyond `${HOME}`-based manifest mounts and no host binary invocations.
