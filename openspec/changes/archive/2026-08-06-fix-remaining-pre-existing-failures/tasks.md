# Tasks

## Phase 1: code-daily-scan
- [ ] Read test_quick_scan.py
- [ ] Replace hardcoded path with `IOS_REPO_PATH` env var
- [ ] Add pytest.skip when path not available
- [ ] Verify test skips gracefully

## Phase 2: jira-skill
- [ ] Read test_redis_integration.py
- [ ] Check if Docker/Redis available before running
- [ ] Add proper skip decorator

## Phase 3: webhook-receiver
- [ ] Read test_settings.py
- [ ] Fix dotenv path assumptions
- [ ] Update tests to use temp dirs

## Phase 4: Validation
- [ ] Run all modified test files
- [ ] Commit changes
- [ ] Update OpenSpec status
