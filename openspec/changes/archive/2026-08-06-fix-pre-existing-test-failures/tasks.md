# Tasks

## Phase 1: code-daily-scan ✅
- [x] Replace hardcoded path with env var in test_quick_scan.py
- [x] Add pytest.skip() when path not available

## Phase 2: tdt-core
- [x] Add skipif decorator to SIGSTOP tests on macOS
- [ ] Verify tests pass on macOS

## Phase 3: jira-skill
- [ ] Add skip decorator for Redis integration tests
- [ ] Verify tests skip gracefully

## Phase 4: jira-daily-reports
- [ ] Add skip decorators for integration tests
- [ ] Verify tests skip gracefully

## Phase 5: Validation
- [ ] Run full test suite across all repos
- [ ] Verify all previously-failing tests now skip
- [ ] Commit all changes
- [ ] Update OpenSpec change status
