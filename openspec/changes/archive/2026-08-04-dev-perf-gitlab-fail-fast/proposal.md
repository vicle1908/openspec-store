# dev-perf-gitlab-fail-fast

## Why

`dev_performance` rows count Jira-only attributes (developer + changelog +
project key) and reports them as `rows: N` in `dev_performance_summary`. When
the scheduler's `GITLAB_PAT` is missing or empty, **all** GitLab lookups
(`find_project_by_path`, `find_project_by_key`, `fetch_mr`, `fetch_deployments`)
silently return `None` or `[]` and every join falls back to `join_method="none"`.

The 18:29 SGT and 20:01 SGT runs on 2026-07-13 produced `rows: 137` while
the actual MR data was zero — the sheet reported healthy when the GitLab
side was broken.

Three symptoms made the issue invisible:

1. The empty PAT returned 404, not 401, for `GET /projects/:encoded_path`
   (GitLab's policy of hiding private project existence from anonymous calls
   makes 404 the universal failure mode).
2. `find_project_by_path` and `find_project_by_key` catch *every* exception
   and downgrade it to a WARNING log + `None` return.
3. The `dev_performance_summary` log line does not record `join_method=none`
   count, so the absence of joined MRs doesn't show up in operator metrics.

Operators have no signal that the sheet is silently empty until they
inspect a row by hand.

## What Changes

- **Add a new capability** `dev-performance-gitlab-validation` that names the
  fail-fast contract below.
- **Pre-flight GitLab token validation.** At the start of the
  `dev_performance` CLI, validate that the constructed `GitlabClientFactory`
  can successfully call `gl.auth()` (1 round-trip, fails fast on 401). If
  auth fails, log a single `dev_performance_gitlab_unavailable` ERROR with
  the failing HTTP status, and either (a) abort the run with exit 2 if
  `DEV_PERFORMANCE_GITLAB_REQUIRED=true`, or (b) continue with joins
  returning None and a visible WARNING marker on every row, controlled by
  the existing default-fail-soft behavior.
- **Track `join_method=none` count** in `dev_performance_summary`. Operators
  can grep for `joined_via_none=137` to detect "every join failed".
- **Add a `DEV_PERFORMANCE_GITLAB_REQUIRED` env knob** (default `false` for
  backward compatibility) so scheduler ops can toggle strict-fail vs soft-fail.
- **Update env-sample** + **ops runbook** to document the new knob and the
  fail-fast behavior.

## Impact

- Affected specs: `dev-performance` (new capability), no existing specs
  altered.
- Affected code: `jira-daily-reports/src/jira_daily_reports/dev_performance/{cli.py,cli_factories.py,source.py}`,
  `jira-daily-reports/config/env-sample.env`, `tdt-meta/docs/workflows/dev-performance-runbook.md` (new).
- Adds **5 unit tests** to `jira-daily-reports/tests/dev_performance/`
  covering: empty token fail, 401 fail, valid token pass, soft-fail warning,
  strict-fail abort.

## Out of Scope

- **Restoring `GITLAB_PAT` to `~/.tdt/.env`**. The PAT was removed during a
  recent operator action. Restoration is an **operational** step outside the
  scope of this change. This change gives operators a signal to do it.
- **Wider 401 → 404 exposure**. Any GitLab client in the codebase that uses
  `find_project_by_path` and `find_project_by_key` is affected by the same
  silent-failure pattern. The fix in this change is scoped to
  `dev_performance` because that is where the data-integrity impact is
  highest (it writes to a public sheet). Other call sites will be addressed
  in a separate change if needed.

## Follow-up: regression suite uncovered while restoring GITLAB_PAT

While bringing up the scheduler post-PAT-restoration, a pre-existing
5-test failure cluster surfaced. Investigation on 2026-07-14 traced each
to a distinct root cause:

1. `tests/catalog/test_joiner.py::test_join_custom_fields_tracked_with_usage_and_metadata`
   asserts `status == Status.ACTIVE` for `last_seen=datetime(2026, 6, 10)`,
   but `_compute_status` correctly classifies >30d as `STALE` (today is
   2026-07-14, so 34 days ago → STALE). **Test-data bug**, not production.
2. `tests/dev_performance/test_stale_thresholds.py::{test_unparseable_env_falls_back_with_warning,
   test_non_positive_env_falls_back_with_warning,
   TestIsStale::test_unknown_status_is_not_stale_with_warning}` — all
   depend on pytest `caplog` capturing WARNING records from
   `jira_daily_reports.dev_performance.*`. They fail whenever any earlier
   test imports `jira_daily_reports.cli` (e.g. the catalog CLI test
   suite), because `cli.py` calls `configure_logging()` which sets
   `jira_daily_reports.propagate = False`. Once propagation is off,
   WARNING records no longer reach pytest's `caplog` handler attached to
   the root logger. **Production-logging bug**, not a test bug.
3. `tests/dev_performance/test_metrics.py::TestComputeCycleTime::test_negative_duration_clamped_to_zero`
   — same logging-propagation root cause as #2.

The right fix for #2/#3 is to **stop breaking propagation** in
`configure_logging()`. The logger-level/handler pattern that suppresses
stderr double-logging can be achieved by removing only the unwanted
handlers, not by globally disabling propagation (which silently breaks
every external log sink — pytest caplog, Datadog, ELK, etc.). For #1,
the fix is to use a relative date so the test isn't time-sensitive.

This sub-change is filed here because the cluster was uncovered *while
implementing* the fail-fast change and a separate OpenSpec change would
delay merging both fixes for unrelated reasons.
