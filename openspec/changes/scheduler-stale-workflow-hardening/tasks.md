# scheduler-stale-workflow-hardening — Tasks

> **Validation status (2026-07-07, pre-execution):** All 21 tasks validated against
> current source state. Findings:
>
> - `tdt-core/src/tdt_core/scheduler/cli.py`:521 — line 780 (`_serve`)
>   already calls `_cancel_stale_pending_workflows(engine)` and
>   `_cancel_stale_enqueued_workflows(engine)` ONCE at startup (matches
>   `docs/workflows/troubleshooting.md` "Startup-only cleanup" note). No
>   periodic cleaner exists — this change closes that gap.
> - `tdt-core/src/tdt_core/scheduler/cli.py`:305 — current
>   `_cancel_stale_error_workflows` has 4-element default tuple
>   `(ModuleNotFoundError, AttributeError, ImportError, UnpicklingError)` and
>   3-element `stale_workflow_names` (`_dbos_debouncer_workflow`,
>   `_dispatch_review_workflow`, `_dispatch_mr_workflow`).
> - `agent-core/src/agent_core/scheduler_setup.py`:74 — local
>   `_cancel_stale_pending_workflows` exists as DEAD CODE (defined but
>   never called); the live cleanup happens in
>   `tdt-core/src/tdt_core/scheduler/cli.py`. Task 2.2 will introduce a
>   NEW scheduled workflow, not call this dead function.
> - `tdt-core/tests/scheduler/test_cli.py`:208-209 — `_serve` test
>   monkeypatches the underscore-prefixed names. Task 1.4 adds a
>   parallel pair of monkeypatches targeting the public names so the
>   backward-compat wrappers stay live.
> - `tdt-core/tests/scheduler/test_serve_health_listener.py`:83-84 —
>   same monkeypatch pattern; both test files will need the public
>   names added.
> - `code-daily-scan/src/code_daily_scan/scanners/worktree.py`:58 —
>   `_default_command_runner` already uses `subprocess.run(check=True,
>   capture_output=True, text=True)` so stderr IS captured into the
>   `CompletedProcess.stderr` attribute; task 3.1 only needs to wrap
>   the raised `CalledProcessError` with a message that includes the
>   stderr text (no behavioral change to the runner itself).
> - All three sub-specs in `specs/` (`scheduler-engine/`,
>   `agent-core-scheduler-setup/`, `code-daily-scan-core/`) are
>   syntactically valid; openspec validate --strict passes.

## 1. Extend default `error_class_names` filter in `tdt-core`

- [ ] 1.1 In `tdt-core/src/tdt_core/scheduler/cli.py`, rename `_cancel_stale_error_workflows` → `cancel_stale_error_workflows` (public, module-level). Keep the original name as a thin wrapper that delegates to the new public function so the CLI subcommand `tdt-scheduler cancel-stale-errors` and any internal callers continue to work.
- [ ] 1.2 In `tdt-core/src/tdt_core/scheduler/cli.py`, rename `_cancel_stale_enqueued_workflows` → `cancel_stale_enqueued_workflows` (public, module-level). Same wrapper pattern. **Note:** `_cancel_stale_pending_workflows` is NOT renamed — it remains underscore-prefixed and is only called from `_serve()` in the same module, so no cross-module import is needed.
- [ ] 1.3 Extend the default `error_class_names` tuple (in `cancel_stale_error_workflows`, line 309 area) to include `"FileNotFoundError"`, `"OSError"`, `"subprocess.CalledProcessError"`, `"subprocess.SubprocessError"` while keeping the existing 4 entries.
- [ ] 1.4 Update internal callers in `tdt-core/src/tdt_core/scheduler/cli.py` — at minimum, the `cancel_stale_errors` CLI subcommand (line 1032) — to call the public `cancel_stale_error_workflows` and `cancel_stale_enqueued_workflows` names. Also add a NEW usage at `_serve()` line 781 where `_cancel_stale_enqueued_workflows` is called for startup cleanup.
- [ ] 1.5 In `tdt-core/tests/scheduler/test_cli.py`, add a test asserting the new exception classes are matched by default. Use the existing `_make_engine` / `fake_sa` fixture pattern at line 320-328. Recommended cases:
  - `decoded = CalledProcessError(128, ["git", "worktree", "add"], stderr=b"fatal: bad ref")` → `class_name in default_error_class_names == True`
  - `decoded = FileNotFoundError(2, "No such file")` → matches
  - `decoded = OSError(28, "No space")` → matches
- [ ] 1.6 Run `ruff check . --fix && ruff format .` and `mypy tdt-core/ --strict`.

## 2. Register `stale_workflow_cleaner` scheduled workflow in `agent-core`

- [ ] 2.1 In `agent-core/src/agent_core/scheduler_setup.py`, import the now-public `cancel_stale_error_workflows` and `cancel_stale_enqueued_workflows` from `tdt_core.scheduler.cli`. Add the imports near the top of the module (after line 52 where `_ENGINE = get_engine()` is defined).
- [ ] 2.2 Add a `@_ENGINE.scheduled_workflow(cron="*/30 * * * *", cron_timezone="UTC", name="stale_workflow_cleaner")` decorated function `stale_workflow_cleaner` that calls both cleanup functions. **Placement:** after the existing `daily_android_scan` / `daily_ios_scan` definitions (after line 284). **Engine verification:** the `_ENGINE` object is the same singleton the YAML registry loader pushes schedules through — `apply_schedules()` (called from `tdt_core/scheduler/cli.py:783`) picks up the registered spec automatically. **Body pattern:**
  ```python
  @_ENGINE.scheduled_workflow(cron="*/30 * * * *", cron_timezone="UTC", name="stale_workflow_cleaner")
  async def stale_workflow_cleaner(*args: object, **kwargs: object) -> None:
      current_version = _current_application_version_for_cleanup()
      err_count = cancel_stale_error_workflows(_ENGINE, current_version=current_version)
      enq_count = cancel_stale_enqueued_workflows(_ENGINE)
      logger.info("stale_workflow_cleaner.run", cancelled_error=err_count, cancelled_enqueued=enq_count)
  ```
  Where `_current_application_version_for_cleanup()` is a small helper that queries `dbos.application_versions` for the latest version (same logic as `tdt_core/scheduler/cli.py:56`). Alternative: import `_current_application_version` directly from `tdt_core.scheduler.cli` and call it (acceptable since the helper has no side-effects).
- [ ] 2.3 Add `structlog` entries for the cleanup run: log `cancelled_error=N`, `cancelled_enqueued=M` at INFO level. Use `logger = structlog.get_logger(__name__)` if not already imported.
- [ ] 2.4 In `agent-core/tests/test_scheduler_setup.py`, add a test that verifies `stale_workflow_cleaner` calls both public cleanup functions with correct parameters. Pattern:
  1. Monkeypatch `tdt_core.scheduler.get_engine` → returns `MagicMock` whose `_ENGINE.scheduled_workflow` is the passthrough identity decorator
  2. Monkeypatch `cancel_stale_error_workflows` and `cancel_stale_enqueued_workflows` to spy on calls
  3. Reimport `agent_core.scheduler_setup`
  4. Invoke the registered workflow function directly
  5. Assert spies were called once each with the engine + current_version
- [ ] 2.5 Add a test that verifies the cron schedule is `*/30 * * * *` and the registered name is `stale_workflow_cleaner`. The test inspects `fake_engine.schedule_registry.list()` (already returning `[]` in the existing test mock at line 23) OR asserts via a side effect on `fake_engine.scheduled_workflow.assert_called_with(...)`.
- [ ] 2.6 Run `ruff check . --fix && ruff format .` and `mypy agent-core/ --strict`.

## 3. Surface stderr from `git worktree add` in `code-daily-scan`

- [ ] 3.1 In `code-daily-scan/src/code_daily_scan/scanners/worktree.py`, update `_default_command_runner` (line 59) to wrap any `CalledProcessError` and include `stderr` in the message. The runner already calls `subprocess.run(check=True, capture_output=True, text=True)`, so the captured stderr is available on the exception's `.stderr` attribute. **Suggested implementation:**
  ```python
  try:
      return subprocess.run(
          list(args),
          cwd=str(cwd) if cwd is not None else None,
          check=True,
          capture_output=True,
          text=True,
          timeout=timeout,
      )
  except subprocess.CalledProcessError as exc:
      stderr = (exc.stderr or "").strip()
      cmd_str = " ".join(map(str, args))
      raise subprocess.CalledProcessError(
          exc.returncode,
          exc.cmd,
          output=exc.output,
          stderr=exc.stderr,
      ) from None  # or re-raise with a custom message — see note below
  ```
  **Re-raise pattern:** Python does not let you mutate a `CalledProcessError`'s message in-place, so the recommended approach is to **let the original exception propagate** and ensure the **caller** (`create()` at line 263) appends the stderr in its existing `raise RuntimeError(f"worktree creation failed: {exc}")` message at line 280. To make stderr visible in the log, change that one line to:
  ```python
  stderr_text = (getattr(exc, "stderr", None) or "").strip()
  detail = f"{exc} (stderr: {stderr_text!r})" if stderr_text else str(exc)
  raise RuntimeError(f"worktree creation failed: {detail}") from exc
  ```
  This satisfies the spec (stderr appears in the message string) without introducing a new exception class.
- [ ] 3.2 In `code-daily-scan/tests/test_worktree_manager.py`, add a `FakeRunner` variant (extending the existing `FakeRunner` at line 19) that returns a `CompletedProcess` with `returncode=128` and `stderr="fatal: invalid reference: main"`. Add a test asserting the raised `RuntimeError`'s message string contains both `"exit 128"` (or equivalent) AND `"fatal: invalid reference"`. Suggested test name: `test_create_worktree_add_failure_surfaces_stderr`.
- [ ] 3.3 Run `ruff check . --fix && ruff format .` and `mypy code-daily-scan/ --strict`.

## 4. Deploy and smoke test

- [ ] 4.1 Restart the Docker `tdt-scheduler:local` container (`docker compose -f agent-core/compose.yaml restart scheduler`).
- [ ] 4.2 Verify via `curl -s http://127.0.0.1:9100/scheduler/schedules | jq -r '.[].name'` (or `tdt-scheduler schedules list`) that `stale_workflow_cleaner` is registered. Expected alongside `daily-android-scan` and `daily-ios-scan` — total 19 schedules (was 18, +1 cleaner).
- [ ] 4.3 Trigger an immediate run via DBOS admin endpoint OR insert a synthetic stale `ERROR` row with `application_version <> current_version` and wait 30 minutes for the cron.
- [ ] 4.4 Confirm via `SELECT name, status, application_version FROM dbos.workflow_status WHERE status='CANCELLED' AND name IN ('_dbos_debouncer_workflow', '_dispatch_review_workflow', '_dispatch_mr_workflow') AND application_version <> (SELECT application_id FROM dbos.application_versions ORDER BY created_at DESC LIMIT 1) ORDER BY created_at DESC LIMIT 5;` that stale rows from previous `application_version` were cancelled. **Note:** workflow names use underscores internally (DBOS preserves the Python identifier), even though schedule names display with hyphens.
- [ ] 4.5 Run `code-daily-scan scan --platform android` manually. The current compose.yaml mounts `poems-mobile3-android` as `:rw`, so the original `.git/worktrees/` read-only failure mode is not reproducible in dev. To exercise the stderr-surfacing path, either (a) `docker compose -f agent-core/compose.yaml stop scheduler && docker run --rm -v $(pwd):/workspace -v ~/.tdt:/home/agent/.tdt agent-core:local-dev uv run python -c "from code_daily_scan.scanners.worktree import WorktreeManager; ..."` with a forced read-only bind, or (b) trust the unit test in 3.2 which directly exercises the `CalledProcessError → RuntimeError` chain. Recommended: rely on 3.2 for the proof; 4.5 is a sanity smoke test only.

## 5. Archive predecessor change

- [ ] 5.1 Add a one-line note to `tdt-meta/openspec/changes/dbos-stale-workflow-auto-cleanup/proposal.md` pointing readers to `scheduler-stale-workflow-hardening` as the canonical successor. The note should explicitly state: "the predecessor change was archived as ✓ Complete but the scheduled-workflow registration at `agent-core/scheduler_setup.py` was never actually deployed (verified 2026-07-07 — `grep` for `stale_workflow_cleaner` in `scheduler_setup.py` returns 0 matches, and `dbos.workflow_schedules` has zero entries matching `%stale%` or `%cleaner%`). The successor restores the documented intent."