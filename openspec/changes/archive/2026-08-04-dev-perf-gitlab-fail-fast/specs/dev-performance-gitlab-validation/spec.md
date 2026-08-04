# Capability: dev-performance-gitlab-validation

## Purpose

The `dev_performance` CLI must surface GitLab authentication failures
explicitly instead of silently producing Jira-only rows with empty MR
data. Operators must be able to detect "every join failed" via a single
log line and an optional strict-fail mode for the scheduler.

## ADDED Requirements

### Requirement: GitLab auth pre-flight SHALL probe `gl.auth()` before the join loop

The CLI MUST call `validate_gitlab_auth` on the constructed GitLab client
exactly once, BEFORE iterating over Jira issues. The probe MUST use the
SDK's `gl.auth()` round-trip and capture any `GitlabAuthenticationError`.

#### Scenario: Empty or missing token (401 → 404 returned by GitLab policy)

- **WHEN** the configured `GITLAB_PAT` is empty, missing, or rejected by GitLab
- **THEN** `validate_gitlab_auth` MUST log a single
  `dev_performance_gitlab_unavailable` ERROR line with `reason=auth_failed`,
  the failing HTTP status, and the exception message
- **AND** MUST NOT raise when `DEV_PERFORMANCE_GITLAB_REQUIRED=false`
- **AND** MUST continue with joins that resolve to `join_method="none"`

#### Scenario: Valid GitLab PAT

- **WHEN** the configured `GITLAB_PAT` is accepted by GitLab
- **THEN** `validate_gitlab_auth` MUST log a single
  `dev_performance_gitlab_available` INFO line with `user_id` and
  `username` from `gl.user`
- **AND** MUST return True without raising

#### Scenario: Strict-fail mode

- **WHEN** `DEV_PERFORMANCE_GITLAB_REQUIRED=true` and auth fails
- **THEN** `validate_gitlab_auth` MUST raise `RuntimeError` with the
  message `dev_performance_gitlab_unavailable: auth failed`
- **AND** the CLI MUST exit with a non-zero status (≥2) so DBOS marks
  the workflow `MAX_RETRIES_EXCEEDED`

### Requirement: `dev_performance_summary` log line MUST include `joined_via_none`

The summary dict (logged at INFO via `logger.info("dev_performance_summary
%s", summary)`) MUST include `joined_via_none` (an `int >= 0`) recording
the number of Jira issues whose join resolved to `join_method="none"`.

#### Scenario: All joins succeed

- **WHEN** all 137 issues resolve to `join_method="remote_link"` or
  `join_method="branch_regex"`
- **THEN** `joined_via_none` SHALL be `0`

#### Scenario: Empty token, soft-fail mode

- **WHEN** GitLab auth fails and the run continues in soft-fail mode
- **THEN** `joined_via_none` SHALL equal the count of issues processed
  (e.g. 137)
- **AND** operators MAY grep the schedule log for
  `joined_via_none=137` to detect the failure

#### Scenario: Mixed success and failure

- **WHEN** 50 issues succeed and 87 issues resolve to `none`
- **THEN** `joined_via_none` SHALL equal `87`

### Requirement: New env var `DEV_PERFORMANCE_GITLAB_REQUIRED`

The CLI MUST read `DEV_PERFORMANCE_GITLAB_REQUIRED` from the
environment after `load_tdt_env()`. The value SHALL be coerced via
`tdt_core.env.get_bool_env` with default `False`.

#### Scenario: Default unset

- **WHEN** the env var is unset
- **THEN** it SHALL be coerced to `False` (soft-fail)
- **AND** the existing behavior is preserved (no regression)

#### Scenario: Set to "true"

- **WHEN** the env var is `"true"`, `"1"`, `"yes"`, or `"on"` (case-insensitive)
- **THEN** it SHALL be coerced to `True` (strict-fail)
- **AND** a 401/404 from GitLab auth MUST abort the run

#### Scenario: Set to any other string

- **WHEN** the env var is `"no"` or `"false"` or empty
- **THEN** it SHALL be coerced to `False` (soft-fail)
