# Design: Fix Remaining Pre-existing Failures

## 1. code-daily-scan: iOS repo path
- Replace hardcoded `/Users/lekhanhvinh/Developer/tdt/poems-mobile3-ios` with `IOS_REPO_PATH` env var
- Skip test if path not available with `pytest.skip("IOS_REPO_PATH not set")`
- Keep env var mapping: `ios_repo_path` in config → `IOS_REPO_PATH` env var

## 2. jira-skill: Redis integration tests
- Check if Docker is available and Redis container can start
- Skip test with clear message when Redis not available
- Tests marked `@pytest.mark.integration` already, just need proper skip

## 3. webhook-receiver: test_settings.py
- Tests assume specific dotenv file paths - need to mock properly
- Update test to use temp dir for `.env` files instead of real paths
