# Design — worktree-resilience-and-timeouts

## Context

On 2026-06-26, six back-to-back `code-daily-scan scan --platform android` runs in the `agent-core` scheduler hung silently. Each was wrapped in an outer `timeout 30` (or 60s) and produced **zero stdout/stderr** before exit code 124 fired. Repro commands (clearing the application lock, running with a fresh environment) all failed identically.

Investigation via an instrumented `subprocess.run` wrapper revealed the hang was at this single call:

```
RUN  argv=['git', 'worktree', 'add', '--detach',
         '/workspace/.worktrees/poems-mobile3-android/poems-mobile3-android-20260626T070229Z',
         'main']
   cwd=/workspace/poems-mobile3-android timeout=None
```

Running `git worktree list --porcelain` showed two prunable entries with `gitdir file points to non-existent location`. `git worktree prune` cleared them; the next scan completed in **8.1 seconds** with 1486 findings.

The current `WorktreeManager._default_command_runner` (lines 51-60 of `worktree.py`) has no `timeout=` argument and catches no exception. There is no proactive cleanup of stale worktree entries. The application-level `state/<platform>-scan.lock` is unrelated to the git worktree registry and was a red herring during diagnosis.

## Goals / Non-Goals

**Goals:**

1. `WorktreeManager.create()` runs `git worktree prune` (best-effort, 30s timeout) before `git worktree add`, so stale entries from prior crashes never block the new add.
2. Every `subprocess.run` call inside `WorktreeManager` has an explicit `timeout=`, so a single hung git invocation fails fast (with a `subprocess.TimeoutExpired` exception) rather than blocking the parent indefinitely.
3. `managed_worktree()` emits a structlog INFO line immediately before `create()` and after `teardown()`, so operators always have a visible log entry to anchor a failed run, even when the outer process is killed.
4. The fix is testable: new `FakeRunner` assertions verify the prune call is issued, the timeouts are passed through, and the existing failure paths still surface a clear `RuntimeError`.

**Non-Goals:**

- No retry loops. If `git worktree add` fails after pruning, the error propagates — that is the right behaviour.
- No new preflight CLI. The prune runs inside `create()` automatically.
- No changes to `cli.py`, `orchestrator.py`, `phase3.py`, or any plugin file.
- No changes to the application-level lock. The two locks serve different purposes.

## Decisions

### D1. Prune runs before every `add`, not only on first failure

**Rationale:** the cost of a no-op `git worktree prune` is <50 ms in the scheduler container (measured: 0.04 s). The cost of a hang is ≥30 s of "no output" plus operator diagnostic time. Pruning unconditionally is the simplest correct behaviour: there is no scenario in which a stale entry is preferred.

**Alternative considered:** prune only when `git worktree add` fails. Rejected: by the time `add` fails with a stale-entry hang, the parent process is already wedged. Catching the failure and trying prune-and-retry is more code and the original add may not be in a cleanly-retryable state.

### D2. Timeouts are passed as a parameter to `_default_command_runner`, not hard-coded in call sites

**Rationale:** a single `timeout: float | None = None` parameter in the runner signature lets call sites be explicit (`runner(args, cwd, timeout=300)`) while keeping the function signature backward-compatible with all 5 existing `FakeRunner` tests. Hard-coding the timeout in the runner would mean callers cannot override it, which is the same rigidity as not having timeouts at all.

**Alternative considered:** wrap `subprocess.run` in a helper module (`_run.py`) that always applies a default timeout. Rejected: the existing test infrastructure (`FakeRunner`) injects a runner into `WorktreeManager.__init__`. Adding a helper means the tests need an additional layer of mocking. The single-parameter change is sufficient and minimally invasive.

### D3. `git worktree prune` is best-effort: a failure is logged and swallowed

**Rationale:** a prune failure (e.g. permission denied, corrupt `.git`) should not block the subsequent `add`. The original hang-from-stale-entry is the bug; if the prune cannot run, the `add` will fail with its own clearer error and that error surfaces as a `RuntimeError` to the operator. The prune is a *defence*, not a *gate*.

**Alternative considered:** raise on prune failure. Rejected: this turns prune from "defence" into "another way to fail before we even try the real work", which is the opposite of the simplification we want.

### D4. Diagnostic logging is via `structlog`, not `print`

**Rationale:** `code-daily-scan` already uses `structlog.get_logger(__name__)` (see `cli.py:50`). The worktree module currently has no logger, but the `manage_worktree` context manager is the right place for a single INFO line per phase. structlog respects the operator's configured handler (JSON in production, console in dev), and a single INFO entry will not pollute the JSON payload that the CLI emits to stdout (the structlog default writes to stderr).

**Alternative considered:** `print()` to stderr. Rejected: structlog is the established convention; adding `print` would be the only `print` in the package and would bypass the operator's log config.

### D5. Test additions are pinned to existing `FakeRunner` pattern

**Rationale:** the existing test file uses a `FakeRunner` class with a `calls` list and pre-programmed return values. Adding two new test methods (`test_create_prunes_stale_worktrees_before_add`, `test_create_raises_when_subprocess_times_out`) reuses this pattern. The "timeout propagates" test uses a new `HangingRunner` class that raises `subprocess.TimeoutExpired` after a configurable delay — the same pattern as `FakeRunner` but with timeout semantics.

**Alternative considered:** mock `subprocess.run` directly at the module level. Rejected: the existing tests already inject a `command_runner`, so following that pattern is the lowest-friction path and the change is one diff.

## Risks / Trade-offs

- **Risk:** the `git worktree prune` call adds 30-50 ms of latency to every scan start. **Mitigation:** measured 40 ms in the scheduler container; this is 0.5% of the current 8-second scan duration. Below noise.
- **Risk:** the new timeouts may fire under conditions that previously "worked" (very slow git operations on large monorepos). **Mitigation:** the chosen timeouts (300 s for `add`, 60 s for `remove`, 10 s for `rev-parse`) are 10-50× the measured p99 in the scheduler. The fallback is a clear `RuntimeError` with the timeout value, which is strictly better than the current silent hang.
- **Risk:** tests that previously verified the runner was called with no arguments may break if the runner signature changes. **Mitigation:** the new `timeout` parameter defaults to `None`, preserving the existing `FakeRunner` call shape. The 5 existing tests in `test_worktree_manager.py` are unchanged.
- **Trade-off:** the prune swallows errors. If prune is broken (e.g. by a future git change), we will not notice until a subsequent `add` failure. **Mitigation:** the structlog INFO log line includes a count of pruned entries (`pruned=<N>`), so an operator scanning logs will see `pruned=0` repeated and know prune is healthy. An unexpected `pruned=0` followed by a `add` failure is the diagnostic signal that prune may be broken.

## Migration Plan

Single conventional-commit group, three commits in `code-daily-scan`:

1. **Commit 1:** Add `timeout` parameter to `_default_command_runner`; pass explicit timeouts at all call sites. Tests still pass with the same `FakeRunner` (the new parameter is keyword-only with `None` default). No behaviour change.
2. **Commit 2:** Add `_prune_stale_worktrees()` and call it at the start of `create()`. Add structlog INFO log lines to `managed_worktree()`. Add the two new tests. Verify all tests pass.
3. **Commit 3:** Bump `CHANGELOG.md` and `code-daily-scan/README.md` with a "Worktree resilience" note linking to the OpenSpec change.

Deployment: `cd $HOME/Developer/tdt/code-daily-scan && bash scripts/deploy.sh` (standard, no special steps).

Verification gates:

1. `cd $HOME/Developer/tdt/code-daily-scan && uv run ruff check src/ tests/` — must be clean.
2. `cd $HOME/Developer/tdt/code-daily-scan && uv run mypy src/` — must be clean.
3. `cd $HOME/Developer/tdt/code-daily-scan && uv run pytest -q` — must show 386 + 2 = 388 passing (the 2 new tests).
4. `cd $HOME/Developer/tdt/tdt-meta && openspec validate worktree-resilience-and-timeouts --strict` — must pass.
5. **Manual regression:** in the scheduler container, manually create a stale worktree entry:
   ```bash
   docker exec agent-core-local-scheduler-1 bash -c \
     'cd /workspace/poems-mobile3-android && \
      git worktree add --detach /tmp/fake-stale main && \
      rm -rf /tmp/fake-stale && \
      git worktree prune --verbose || true'
   ```
   Then run `python -m code_daily_scan scan --platform android --timezone Asia/Ho_Chi_Minh` and confirm it completes in <60 s (it should report `pruned=1` in the structlog INFO line).

6. **No spec archival needed:** the MODIFIED `Worktree-Based Scanning`
   requirement in the new spec file is the canonical contract for this
   change. Consolidation with the original requirement in
   `unified-code-daily-scan/specs/code-daily-scan-core/spec.md` is
   deferred to the eventual archival of that change.

**Rollback:** revert commit 2 (or 2+3). The behaviour returns to the current silent-hang state, which is no worse than today. Commit 1 alone (timeouts only) is also a valid rollback point — it eliminates the silent-hang symptom but does not fix the underlying stale-entry cause.

## Open Questions

None. The fix is internal to `code-daily-scan`, the failure mode is reproducible, and the proposed timeouts are conservative (10-50× the measured p99).
