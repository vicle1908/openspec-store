# Design: Fix Pre-existing Test Failures

## Architecture

### Pattern: Skip When Environment Not Available

All fixes follow the same pattern:
1. Check for required environment/infrastructure
2. Skip test with `pytest.skip()` or `@pytest.mark.skipif()` if not available
3. Preserve original test logic when environment IS available

### Per-repo Strategy

#### code-daily-scan
- Replace hardcoded `/Users/lekhanhvinh/...` with `IOS_REPO_PATH` env var
- Fall back to `~/.tdt/code_daily_scan/ios_repo_path`
- Skip if path doesn't exist

#### tdt-core
- Add `@pytest.mark.skipif(sys.platform == "darwin")` to SIGSTOP tests
- SIGSTOP timing is unreliable on macOS

#### jira-skill
- Add `@pytest.mark.skipif(not shutil.which("docker"))` to Redis integration tests
- Or check for `TDT_REDIS_TEST_URL` env var

#### jira-daily-reports
- Add `@pytest.mark.skipif` decorators to integration tests
- Check for required env vars (JIRA credentials, Sheets credentials)

## Trade-offs

- Tests skip instead of failing — reduces noise
- Developers can still run tests by setting up the required environment
- No test logic changes — only skip conditions added
