# Delta Spec: test-skip-conditions (ADDED)

## Purpose

Define skip conditions for tests that require specific environments, infrastructure, or credentials.

## ADDED Requirements

### Requirement: Tests SHALL skip when environment unavailable

Tests that require specific infrastructure (Redis, Docker), credentials (Jira, Sheets), or platform-specific behavior (SIGSTOP on macOS) SHALL use `pytest.skip()` or `@pytest.mark.skipif()` to skip gracefully when the required environment is not available.

#### Scenario: iOS repo path not available

- **GIVEN** `IOS_REPO_PATH` env var is not set and `~/.tdt/code_daily_scan/ios_repo_path` does not exist
- **WHEN** `test_validate_ios_rules` runs
- **THEN** it SHALL skip with a descriptive message

#### Scenario: macOS platform

- **GIVEN** `sys.platform == "darwin"`
- **WHEN** `test_subprocess_sigterm_recovers_from_every_durable_boundary` runs
- **THEN** it SHALL skip with reason "SIGSTOP timing unreliable on macOS"

#### Scenario: Redis not available

- **GIVEN** Docker is not running and `TDT_REDIS_TEST_URL` is not set
- **WHEN** Redis integration tests run
- **THEN** they SHALL skip gracefully

#### Scenario: Integration credentials missing

- **GIVEN** Jira/Sheets credentials are not configured
- **WHEN** integration tests run
- **THEN** they SHALL skip with a descriptive message
