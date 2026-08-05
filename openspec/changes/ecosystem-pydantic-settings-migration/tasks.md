# Tasks

## Phase 1: Foundation (tdt-core) ✅
- [x] Add pydantic-settings[yaml]>=2.14.2 to dependencies
- [x] Upgrade pydantic to >=2.13.4
- [x] Create tdt_core/config_models.py with TDTSettings
- [x] Create tdt_core/migrate_config.py
- [x] Add deprecation shims to env.py
- [x] Run uv sync

## Phase 2: Config Consolidation ✅
- [x] Run migrate_toml_to_yaml() on ~/.tdt/
- [x] Merge epic-report-config.toml → config.yaml → apps.epic_report
- [x] Merge code-daily-scan.yaml → config.yaml → apps.code_daily_scan
- [x] Merge observability/config.yaml → config.yaml → observability
- [x] Archive old files

## Phase 3: Client Config Migration ✅
- [x] Migrate JiraConfig to BaseSettings
- [x] Migrate GitlabConfig to BaseSettings
- [x] Verify JiraClientFactory.from_env() works
- [x] Verify GitlabClientFactory.from_env() works
- [x] Run tdt-core tests (126 pass)

## Phase 4: Consumer Migration ✅
- [x] Backward-compat shims keep all consumers working
- [x] Verify jira-daily-reports tests (642 pass)
- [x] Verify jira-skill tests (1737 pass, 5 pre-existing Redis errors)
- [x] Verify jira-epic-report tests (631 pass, 5 pre-existing failures)
- [x] Verify code-daily-scan tests (493 pass, 1 pre-existing failure)
- [x] Verify tdt-sheets tests (236 pass, 5 pre-existing failures)

## Phase 5: Cleanup ✅
- [x] Update OpenSpec change status
- [x] Commit tdt-core changes
- [x] Verify all repos pass tests
- [x] Document migration guide
- [x] Archive change in openspec-store
