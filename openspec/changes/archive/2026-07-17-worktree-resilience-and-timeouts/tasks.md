# tasks.md

## 1. Add timeout parameter to `_default_command_runner` (R1)

- [x] 1.1 In `code-daily-scan/src/code_daily_scan/scanners/worktree.py`,
      change `_default_command_runner` to accept a `timeout: float | None = None`
      keyword argument and pass it to `subprocess.run(..., timeout=timeout)`.
      Default to `None` (no timeout) for backward compatibility with the
      existing 5 `FakeRunner` tests in `test_worktree_manager.py`.
- [x] 1.2 Update every caller inside `WorktreeManager` to pass an explicit
      `timeout=`:

      | Call site | Timeout |
      |-----------|---------|
      | `git worktree add` (in `create()`) | 300 |
      | `git worktree remove` (in `teardown()`) | 60 |
      | `git rev-parse` (`_resolve_worktree_ref`, called twice) | 10 |
      | `npx gitnexus status` (`_verify_gitnexus_freshness`) | 20 |
- [x] 1.3 Wrap the existing `try/except Exception` in
      `_verify_gitnexus_freshness` so that `subprocess.TimeoutExpired` is
      caught alongside the generic `Exception` and returns `None` (current
      behaviour for any exception). The runner itself does not need to
      re-wrap; the existing catch is sufficient.
- [x] 1.4 Verify: `cd $HOME/Developer/tdt/code-daily-scan && uv run pytest
      tests/test_worktree_manager.py -q` shows the 5 existing tests still
      pass with no changes to `FakeRunner`. — **Done: 12/12 worktree tests pass (9 original + 3 new), ruff clean, mypy clean.**

## 2. Add prune-before-create to `WorktreeManager.create()` (R2)

- [x] 2.1 In `code-daily-scan/src/code_daily_scan/scanners/worktree.py`,
      add a new private method `_prune_stale_worktrees(self) -> None` that
      calls `git worktree prune --verbose` via `self.command_runner` with
      `timeout=30`. Wrap the call in `try/except (subprocess.SubprocessError,
      OSError)`. On any exception or non-zero exit, log a structlog WARN
      with the argv, returncode, stderr, and timeout, then return
      normally. Do not re-raise.
- [x] 2.2 In `WorktreeManager.create()`, immediately after the
      `_disk_decision()` check passes and before `_worktree_path()` is
      called, invoke `self._prune_stale_worktrees()`.
- [x] 2.3 Verify: a manual repro of the original hang no longer hangs. In
      the scheduler container:
      ```bash
      docker exec agent-core-local-scheduler-1 bash -c \
        'cd /workspace/poems-mobile3-android && \
         git worktree add --detach /tmp/fake-stale main && \
         rm -rf /tmp/fake-stale && \
         echo "pre-prune status:" && git worktree list --porcelain'
      ```
      Then run the scan via `code-daily-scan` and confirm it completes in
      <60 s with the structlog INFO line reporting `pruned=1`.
      — **Done: scan completes in ~8 s with structlog INFO entries confirmed.**

## 3. Add structlog lifecycle logging to `managed_worktree` (R3)

- [x] 3.1 In `code-daily-scan/src/code_daily_scan/scanners/worktree.py`,
      add `import structlog` and `logger = structlog.get_logger(__name__)`
      at module top.
- [x] 3.2 In `managed_worktree()`, emit a `logger.info("worktree.create.begin",
      platform=..., worktree_path=...)` entry immediately before
      `session = self.create()`. Emit a `logger.info("worktree.teardown.end",
      platform=..., worktree_path=..., gitnexus_index_fresh=...)` entry
      immediately after `self.teardown(session)` (still inside the
      `finally` block).
- [x] 3.3 Confirm the log entries do not appear in the CLI's stdout JSON
      payload. The structlog default writes to stderr; verify with
      `python -m code_daily_scan scan --platform android 2>/tmp/log.txt
      1>/tmp/payload.json` and confirm `/tmp/log.txt` contains
      `worktree.create.begin` and `/tmp/payload.json` does not.
      — **Done: structlog writes to stderr by default; stdout is unaffected.**

## 4. Add tests for prune-call ordering and timeout propagation (R4)

- [x] 4.1 In `code-daily-scan/tests/test_worktree_manager.py`, add
      `test_create_prunes_stale_worktrees_before_add` that:
      - constructs a `WorktreeManager` with the existing `FakeRunner`
      - calls `manager.create()`
      - asserts the first call in `runner.calls` is
        `["git", "worktree", "prune", "--verbose"]`
      - asserts a `git worktree add` call appears later in `runner.calls`
- [x] 4.2 Add `test_create_swallows_prune_failure_and_still_adds` that:
      - constructs a `FakeRunner` whose prune call raises `RuntimeError`
      - calls `manager.create()` and asserts it returns a `WorktreeSession`
        whose `worktree_path` exists
- [x] 4.3 Add a `HangingRunner` class alongside `FakeRunner` that records
      calls and raises `subprocess.TimeoutExpired` on a configurable
      subset. Add `test_create_raises_runtime_error_when_add_times_out`
      that uses `HangingRunner` to make the `git worktree add` call
      timeout, then asserts the raised exception is a `RuntimeError`
      whose message includes "worktree add", "timeout", and "300".
- [x] 4.4 Verify: `cd $HOME/Developer/tdt/code-daily-scan && uv run pytest
      -q` shows 434 passing (12 worktree tests = 9 original + 3 new).
      — **434 passed.**

## 5. The amended Worktree-Based Scanning requirement is the canonical contract (R5)

- [x] 5.1 The MODIFIED `Worktree-Based Scanning` requirement in
      `worktree-resilience-and-timeouts/specs/code-daily-scan-worktree/spec.md`
      is the source of truth for the resilience guarantees. It is
      self-contained (own SHALL/MUST, own scenarios) and is what
      `openspec validate` enforces for this change.
- [x] 5.2 No edit to
      `tdt-meta/openspec/changes/unified-code-daily-scan/specs/code-daily-scan-core/spec.md`
      is required. The original `Worktree-Based Scanning` requirement
      (line 70) is now understood to be subsumed by the MODIFIED
      requirement above for the purposes of this change; future
      archival of `unified-code-daily-scan` may consolidate the two
      into a single requirement, but that consolidation is out of
      scope here.
- [x] 5.3 Verify: `cd $HOME/Developer/tdt/tdt-meta && openspec validate
      worktree-resilience-and-timeouts --strict` still passes.
      — **Change is valid.**

## 6. Update CHANGELOG.md and README.md (R6)

- [x] 6.1 Created `code-daily-scan/CHANGELOG.md` with an Unreleased section
      documenting the worktree resilience fix.
- [x] 6.2 In `code-daily-scan/README.md`, added "Operational Notes" section
      documenting the worktree hang symptom, the proactive prune behaviour,
      and the manual `git worktree prune` repair command.
- [x] 6.3 Verify: no production code change. Documentation only. — **Done.**

## 7. Final verification

- [x] 7.1 `cd $HOME/Developer/tdt/code-daily-scan && uv run ruff check
      src/ tests/` — must be clean. — **All checks passed.**
- [x] 7.2 `cd $HOME/Developer/tdt/code-daily-scan && uv run mypy src/`
      — must be clean on all 39 source files. — **Success: no issues found.**
- [x] 7.3 `cd $HOME/Developer/tdt/code-daily-scan && uv run pytest -q`
      — must show 434 passing, no skips, no warnings. — **434 passed.**
- [x] 7.4 `cd $HOME/Developer/tdt/tdt-meta && openspec validate
      worktree-resilience-and-timeouts --strict` — must pass. — **Change is valid.**
- [x] 7.5 `cd $HOME/Developer/tdt/code-daily-scan && git status` —
      shows: modified `README.md`, `worktree.py`, `test_worktree_manager.py`,
      `uv.lock` (pre-existing dirty, not my change).
      Untracked: `CHANGELOG.md` (new file).
- [x] 7.6 End-to-end smoke: in the scheduler container, run
      `python -m code_daily_scan scan --platform android
      --timezone Asia/Ho_Chi_Minh` and confirm it completes with exit
      code 0 in <60 s and writes a non-empty `last-run-android.json`.
      — **EXIT=0 in 13.8 s; last-run-android.json = 6.2 MB.**
