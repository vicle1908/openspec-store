## 1. Create tdt-observability dbos_scheduling.py

- [x] 1.1 Create `tdt-observability/src/tdt_observability/dbos_scheduling.py` with `register_all_schedules(engine, apply=False)` registering `observability-retention-daily`
- [x] 1.2 Verify ruff and mypy pass

## 2. Update YAML manifest

- [x] 2.1 Update `~/.tdt/schedules/tdt-observability.yaml` from `module:function` to `register_fn`

## 3. Update generator

- [x] 3.1 Update `tdt-scheduler/generators/tdt_observability.py` to emit `register_fn` instead of `module:function`

## 4. Fix stale references

- [x] 4.1 Update agent-core test for tdt-observability generator
- [x] 4.2 Update code-daily-scan deploy.sh reference
- [x] 4.3 Update jira-daily-reports dbos_scheduling.py reference
- [x] 4.4 Update tdt-observability retention.py reference
- [x] 4.5 Update tdt-scheduler generator comments

## 5. Verify

- [x] 5.1 Run all test suites
- [x] 5.2 Run ruff across all repos
- [x] 5.3 Verify zero module:function patterns in YAML manifests
- [x] 5.4 Verify zero stale references

## 6. Commit

- [x] 6.1 Commit tdt-observability changes
- [x] 6.2 Commit tdt-scheduler changes
- [x] 6.3 Commit agent-core changes
- [x] 6.4 Commit code-daily-scan changes
- [x] 6.5 Commit jira-daily-reports changes
- [x] 6.6 Commit openspec-store change
