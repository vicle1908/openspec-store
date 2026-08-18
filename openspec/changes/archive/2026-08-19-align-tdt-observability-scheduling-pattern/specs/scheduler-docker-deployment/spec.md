## MODIFIED Requirements

### Requirement: Movable workloads are consolidated in the Docker scheduler

The jira-daily-reports cron (13 reports), the review-coverage scan, code-daily-scan, jira-epic-report, webhook-receiver, and tdt-observability SHALL all run as DBOS `@scheduled_workflow`s inside the single Docker `scheduler` container, not as host-native jobs. All repos SHALL use the `register_fn` pattern with `register_all_schedules()` in their `dbos_scheduling.py` module.

#### Scenario: All repos use register_fn pattern

- **WHEN** `grep -l "register_fn" ~/.tdt/schedules/*.yaml` runs
- **THEN** all 5 YAML manifests SHALL use `register_fn` (no `module:function` patterns)
- **AND** each manifest SHALL point to `<repo>.dbos_scheduling:register_all_schedules`

#### Scenario: Coverage scan runs in the Docker scheduler

- **WHEN** the migration is complete
- **THEN** the coverage scan SHALL execute on its cron inside the `scheduler` container, and the `com.tdt.review-coverage` launchd job SHALL no longer exist

### Requirement: Deployment topology exclusions are honored

The Docker scheduler stack SHALL NOT host workloads that are contract-bound or host-coupled. The `webhook-receiver` (:8080) debouncers SHALL remain in-process and launchd-managed per the binding `ai-review-deployment-state` spec; the `ai-review` (:8090) service SHALL remain launchd-managed; the CLV2 observer SHALL remain native and launchd-supervised due to host-filesystem coupling.

#### Scenario: Contract-bound services are not containerized

- **WHEN** the scheduler stack is deployed
- **THEN** `webhook-receiver` and `ai-review` SHALL continue to run under launchd on :8080 and :8090 respectively, with only their DSN pointed at the Docker PostgreSQL

#### Scenario: Host-coupled observer stays native

- **WHEN** the CLV2 observer is migrated
- **THEN** it SHALL run as a DBOS scheduled workflow from a native, launchd-supervised host — NOT inside the Docker `scheduler` container
