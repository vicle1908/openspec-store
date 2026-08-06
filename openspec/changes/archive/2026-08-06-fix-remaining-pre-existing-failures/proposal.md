# Proposal: Fix Remaining Pre-existing Failures

## Why
After the main pydantic-settings migration, three pre-existing test failures remain that block clean CI:
1. code-daily-scan/test_quick_scan.py hardcodes a path to a specific developer's machine
2. jira-skill Redis integration tests require Docker, no graceful skip
3. webhook-receiver/test_settings.py tests fail with dotenv path assumptions

## What Changes
- code-daily-scan: Replace hardcoded iOS repo path with `IOS_REPO_PATH` env var + skip
- jira-skill: Add Docker/Redis availability check with skip
- webhook-receiver: Update test_settings.py to use proper env var mocking
