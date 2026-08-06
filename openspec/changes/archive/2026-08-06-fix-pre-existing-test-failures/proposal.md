# Proposal: Fix Pre-existing Test Failures

## Why

Multiple test failures exist across the ecosystem that prevent clean CI runs:

1. **Hardcoded paths** — `code-daily-scan/test_quick_scan.py` has `/Users/lekhanhvinh/...` hardcoded
2. **Platform-specific tests** — `tdt-core/test_migration_executor.py` SIGSTOP tests fail on macOS
3. **Infrastructure-dependent tests** — Redis integration tests fail without Docker/Redis
4. **Integration tests** — Jira/Sheets integration tests need credentials that aren't available in all environments

These failures make it impossible to distinguish real regressions from pre-existing issues.

## What Changes

| Repo | Change | Impact |
|------|--------|--------|
| code-daily-scan | Replace hardcoded path with env var + skip | Test skips gracefully |
| tdt-core | Skip SIGSTOP tests on macOS | Test skips on macOS |
| jira-skill | Add skip decorator for Redis tests | Tests skip without Docker |
| jira-daily-reports | Add skip decorators for integration tests | Tests skip without credentials |

## Compatibility

- No runtime behavior changes
- Tests now skip gracefully instead of failing
- Existing test logic preserved
