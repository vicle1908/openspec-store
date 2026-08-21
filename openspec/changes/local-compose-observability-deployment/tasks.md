## 1. Runbook and Override Templates Specification

- [ ] 1.1 Create `tdt-scheduler` Compose verification runbook documenting unique project invocation (`-p tdt-scheduler-verification`), port mapping (`127.0.0.1:19100:9100`), and disposable configuration directory setup (`TDT_HOME=/tmp/tdt-scheduler-verification-home`). Verify by reviewing runbook markdown structure and checking CLI commands.
- [ ] 1.2 Create `agent-core` Compose observability integration runbook detailing shared bridge network attachment (`agent-core-local_default`), OTel Collector endpoints, and PostgreSQL database connections. Verify documentation references match actual service names in compose definitions.
- [ ] 1.3 Standardize reusable Docker Compose verification override template (`tdt-scheduler-verification.override.yaml`) with container name overrides and isolated volume bindings. Verify syntax using `docker compose -f compose.yaml -f tdt-scheduler-verification.override.yaml config`.

## 2. Health Probing, Bounded Monitoring, and Teardown Procedures

- [ ] 2.1 Document non-disturbing health inspection procedures using HTTP curl checks against `http://127.0.0.1:19100/scheduler/health`, parsing JSON attributes (`schedule_count`, `schedules_applied`, `dbos_connected`). Verify command executes synchronously and exits 0 on healthy service.
- [ ] 2.2 Document container state verification commands using formatted `docker inspect` (`.State.Status`, `.State.Health.Status`, `.State.Health.FailingStreak`) and bounded log extraction (`docker logs --tail 30`). Verify that commands complete without continuous streaming or blocking agent execution.
- [ ] 2.3 Document safe teardown and resource cleanup procedures (`docker compose -p tdt-scheduler-verification down -v` and removal of `/tmp/tdt-scheduler-verification-home`) guaranteeing ambient running developer containers remain untouched. Verify by confirming container lists before and after execution.

## 3. Warning Classification and Decision Gate Protocol

- [ ] 3.1 Publish the expected warnings triage matrix documenting Tailscale webhook self-test timeouts (network isolation artifact), sprint switch spreadsheet warnings (configurable integration notice), and unconfigured telemetry sink messages. Verify that triage entries provide clear diagnostic guidance for each expected log pattern.
- [ ] 3.2 Formalize the defect remediation decision gate in documentation: any source-code defect or startup bug discovered during verification must be isolated, reproduced with a minimal test script, and escalated to a separate implementation change. Verify the decision gate section is explicitly present in the runbook.

## 4. End-to-End Operational Verification and Validation

- [ ] 4.1 Execute end-to-end verification rehearsal using the documented runbook commands in a temporary test directory, verifying container start, healthy status on `127.0.0.1:19100`, manifest reload (~19 schedules), and clean teardown. Verify all commands succeed without error.
- [ ] 4.2 Validate OpenSpec change status and strict store validation (`openspec validate local-compose-observability-deployment --strict --store openspec-store`). Verify validation passes with exit code 0.
