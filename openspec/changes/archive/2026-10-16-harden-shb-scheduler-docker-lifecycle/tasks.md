# Tasks

## 1. OpenSpec Specification Delta

- [x] 1.1 Draft delta spec for `shb-schedule-engine` modifying `Containerized Orchestration via Docker Compose` and adding requirements for graceful shutdown and log rotation
- [x] 1.2 Verify delta spec syntax and strict compliance via `openspec validate --all --strict --store openspec-store`

## 2. Docker Compose Configuration Hardening

- [x] 2.1 Update `~/Developer/shb/shb-schedule/compose.yaml` to declare `stop_grace_period: 60s` for the `scheduler` service
- [x] 2.2 Add standard JSON log rotation directives (`max-size: "10m"`, `max-file: "3"`) to `db` and `scheduler` services in `compose.yaml`
- [x] 2.3 Verify compose file syntax via `docker compose -f ~/Developer/shb/shb-schedule/compose.yaml config`

## 3. Workstation Service Script Integration

- [x] 3.1 Update `COMPOSE_STACKS` in `~/Developer/scripts/docker-service.sh` to include `"/Users/androidteam/Developer/shb/shb-schedule"`
- [x] 3.2 Verify `docker-service.sh status --json` or status output recognizes the registered stack without errors

## 4. Operational Verification

- [x] 4.1 Execute `docker compose up -d` in `~/Developer/shb/shb-schedule` and confirm live container health probe on `http://127.0.0.1:9110/scheduler/health`
- [x] 4.2 Test zero-downtime sentinel hot-reload via `touch ~/.shb/schedules/.reload` and inspect logs for successful reload signal
- [x] 4.3 Run `uv run pytest -v` in `~/Developer/shb/shb-schedule` to confirm zero regression across the test suite
