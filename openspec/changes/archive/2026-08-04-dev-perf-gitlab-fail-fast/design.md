# Design — dev-perf-gitlab-fail-fast

## Architecture

Add a single validation step at the top of `dev_performance.cli.run()`,
between `build_clients()` and the roster loop:

```python
gitlab, jira, sheets = build_clients()
_validate_gitlab_auth(gitlab, mode=_gitlab_required_mode())  # NEW
...
```

`_validate_gitlab_auth` is a small helper in `source.py`:

```python
def validate_gitlab_auth(gl, *, required: bool) -> bool:
    """Validate the GitLab client can authenticate. Returns True on success.

    Logs a single ERROR on failure. When ``required=True``, raises
    RuntimeError so the CLI exits non-zero. When ``required=False``,
    returns False so the caller can log + continue.
    """
    try:
        gl.auth()
        return gl.user is not None
    except GitlabAuthenticationError as exc:
        logger.error(
            "dev_performance_gitlab_unavailable reason=auth_failed status=%s error=%s",
            "401", exc,
        )
        if required:
            raise RuntimeError(
                "dev_performance_gitlab_unavailable: auth failed; aborting run."
            ) from exc
        return False
```

## Env knob

`DEV_PERFORMANCE_GITLAB_REQUIRED` (default `false`):
- `true` → validate-gate is strict; first auth failure aborts the run.
- `false` → validate-gate warns once, then runs with empty MR data.

Soft-fail is the safe default because it matches today's behavior (no
regression) but surfaces the issue in logs for the first time.

## Tracking join_method=none

In `cli.py`:

```python
join_methods: dict[str, int] = defaultdict(int)
# ... existing loop ...
join_methods[join_result.join_method] += 1
```

Add `"joined_via_none": join_methods.get("none", 0)` to the summary
dict and to `dev_performance_summary` log line. Operators can grep
for `joined_via_none=N` to detect full-side failure.

## Tests

`tests/dev_performance/test_source_validation.py`:

```python
def test_validate_gitlab_auth_returns_true_on_200() -> None: ...
def test_validate_gitlab_auth_warns_and_returns_false_on_401() -> None: ...
def test_validate_gitlab_auth_raises_when_required() -> None: ...
def test_validate_gitlab_auth_passes_when_user_attr_missing() -> None: ...
def test_dev_performance_summary_includes_joined_via_none() -> None: ...
```

## Compatibility

- Existing call sites that build `GitlabSource` without first
  validating are unaffected (`validate_gitlab_auth` is opt-in).
- `dev_performance_summary` log gains one new key — existing log
  parsers ignore unknown keys.
- The default behavior is soft-fail with one new WARNING — no
  regression for healthy runs.

## Follow-up: logging propagation + time-sensitive test data

### Problem

`jira_daily_reports/cli.py` calls `configure_logging()` at module-import
time. The current implementation (`src/jira_daily_reports/logging_config.py:24-26`):

```python
root = logging.getLogger("jira_daily_reports")
root.setLevel(logging.INFO)
root.propagate = False
```

disables propagation on the entire `jira_daily_reports.*` logger tree.
Records emitted by `jira_daily_reports.dev_performance.stale_thresholds`
or `jira_daily_reports.dev_performance.metrics` never reach the root
logger — and therefore never reach pytest's `caplog` handler (which is
attached to the root logger).

The original intent — avoid duplicate stderr logging when a `StreamHandler`
is also attached — can be achieved **without** turning off propagation:
just don't add the stderr handler in the first place, or set the
attached `RotatingFileHandler` to suppress propagate=False only on the
*handler*, not the *logger*.

### Fix

`configure_logging()` will:

1. Leave propagation at its default (`True`).
2. Add only the `RotatingFileHandler` — never `StreamHandler`/`basicConfig`.
3. Set the *handler*'s `level=INFO`, not the logger's. This way DEBUG
   records are still routed to the file handler (for ops triage) and
   WARNING+ records still propagate to the root logger (for caplog,
   Datadog, ELK, etc.).

### Tests

Add `tests/test_logging_config.py` with 3 cases:

- `test_configure_logging_does_not_disable_propagation` — after import,
  `logging.getLogger("jira_daily_reports").propagate is True`.
- `test_warnings_propagate_to_root_logger_after_configure` — emit a
  WARNING from a child logger and assert the root logger received it.
- `test_idempotent` — calling `configure_logging()` twice does not
  double-register handlers.

The time-sensitive test fix for
`test_join_custom_fields_tracked_with_usage_and_metadata` is to use
`datetime.now(UTC) - timedelta(days=5)` for `last_seen`, matching the
pattern already used in `test_join_labels_sets_correct_usage_fields`.
