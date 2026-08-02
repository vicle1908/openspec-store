# dev-perf-merged-at-fallback — Spec

## Added Requirements

### Requirement: Fall back to MR.merged_at when the Deployments API returns no results

When `fetch_deployments()` returns an empty list for a merged MR, the system SHALL use the MR's `merged_at` timestamp as a fallback for `first_deploy_at` if all of the following are true:

1. `DEV_PERFORMANCE_USE_MERGED_AT_FALLBACK` is set to a truthy value (`true`, `1`, `yes`, `on`, case-insensitive). Defaults to `true`.
2. The MR's `state` is `merged`.
3. The MR has a non-null `merged_at` timestamp.

The fallback SHALL NOT be applied when `fetch_deployments()` raises an exception (e.g. HTTP 404 or 401 from the Deployments API). In that case, the system SHALL log a warning and continue with `first_deploy_at = None`.

#### Scenario: Deployments API returns empty for a merged MR
- **WHEN** `fetch_deployments()` returns `[]` for a merged MR
- **AND** `DEV_PERFORMANCE_USE_MERGED_AT_FALLBACK=true`
- **THEN** the system SHALL use `merged_at` as `first_deploy_at`
- **AND** the system SHALL emit a `dev_performance_merged_at_fallback` INFO log line for that issue
- **AND** the `first_deploy_at` field SHALL NOT be `None` in the result

#### Scenario: Deployments API raises an exception
- **WHEN** `fetch_deployments()` raises (e.g. `GitlabHttpError 404`)
- **THEN** the system SHALL NOT fall back to `merged_at`
- **AND** the system SHALL log a `dev_performance_fetch_deployments_failed` WARNING
- **AND** `first_deploy_at` SHALL be `None` for that MR

#### Scenario: MR is not in `merged` state
- **WHEN** `fetch_deployments()` returns `[]` but the MR `state` is `opened`
- **THEN** the system SHALL NOT fall back to `merged_at`
- **AND** `first_deploy_at` SHALL remain `None`

#### Scenario: Fallback is disabled via env var
- **WHEN** `DEV_PERFORMANCE_USE_MERGED_AT_FALLBACK=false`
- **THEN** the system SHALL NOT fall back to `merged_at` even when deployments are unavailable
- **AND** `first_deploy_at` SHALL be `None` for all MRs without deployments

### Requirement: Merge-at fallback is surfaced in the reconciliation log

The `dev_performance_summary` INFO log line SHALL include a `merged_at_fallback` counter reporting how many rows used `merged_at` as the deploy signal.

#### Scenario: Summary log includes merged_at_fallback counter
- **WHEN** a run completes
- **THEN** the `dev_performance_summary` log line SHALL include `merged_at_fallback=N`
- **AND** `N` SHALL equal the count of rows where `merged_at` was used instead of a deployment record
