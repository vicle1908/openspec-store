## Why

`code-daily-scan` hangs silently when prior scan runs were killed (SIGKILL, SIGTERM, `timeout` expiry). Each kill leaves a "prunable" entry in `poems-mobile3-android/.git/worktrees/<name>/gitdir` pointing at a non-existent path. The next `git worktree add --detach` call from `WorktreeManager.create()` then blocks indefinitely with no output, because:

1. `WorktreeManager._default_command_runner` calls `subprocess.run(check=True)` with **no `timeout=`** argument on `git worktree add`, `git worktree remove`, or the `npx gitnexus status` freshness check.
2. `git` itself has no timeout — it waits indefinitely for the stale entry to resolve.
3. `capture_output=True` means no stdout/stderr reaches the parent until the child exits (or the outer `timeout` kills everything).

The result: a 5-minute outer `timeout` fires, the scan reports exit 124 with **zero observable output**, and the operator has no diagnostic information about which step failed. The application-level `state/<platform>-scan.lock` is orthogonal — clearing it does not affect the git worktree registry at all.

## What Changes

### 1. Proactive worktree prune before creation

`WorktreeManager.create()` will call `git worktree prune` (with a 30-second timeout) before every `git worktree add`. This removes stale entries left by previous crashes before they can cause a new `add` to hang. The prune is best-effort: a failure is logged and swallowed so the existing `add` still runs.

### 2. Timeouts on all subprocess calls

`_default_command_runner` will accept an optional `timeout` parameter and pass it through to `subprocess.run`. All callers in `WorktreeManager` will pass explicit timeouts:

| Call | Timeout |
|------|---------|
| `git worktree add` | 300 s |
| `git worktree remove` | 60 s |
| `git worktree prune` | 30 s |
| `git rev-parse` | 10 s |
| `npx gitnexus status` | 20 s (already present in `phase3.py`, but the worktree freshness check was using the un-timed runner) |

### 3. Diagnostic output before blocking calls

`managed_worktree()` will emit a structlog INFO line immediately before `create()` and immediately after, so the operator always has a visible log entry bracketing the worktree operation even if the scan hangs or is killed.

## Capabilities

### New Capabilities

- `worktree-prune-before-create`: `WorktreeManager.create()` proactively removes stale worktree entries before attempting to create a new one, preventing hangs from prior crash residue.
- `worktree-subprocess-timeouts`: All `subprocess.run` calls inside `WorktreeManager` carry explicit `timeout=` arguments, so any blocking git operation fails fast rather than hanging indefinitely.
- `worktree-diagnostic-logging`: `managed_worktree()` emits INFO log entries bracketing the create/teardown lifecycle, giving operators visible diagnostic markers even when the outer process is killed.

### Modified Capabilities

- `code-daily-scan-core`: Worktree lifecycle hardening — no change to external CLI behaviour, but the scan now fails fast (with a meaningful error) instead of silently hanging.

## Impact

Modified files:

- `code-daily-scan/src/code_daily_scan/scanners/worktree.py` — add `_prune_stale_worktrees()` method, add `timeout` parameter to `_default_command_runner`, update all call sites to pass timeouts, add `structlog` INFO lines around `managed_worktree`.
- `code-daily-scan/tests/test_worktree_manager.py` — add `FakeRunner` variants for prune-call tracking; add tests for: prune runs before add, timeouts are passed through, stale entry after prune still surfaces in `git worktree add` error (not hang).

## Non-goals

- We are NOT adding a retry loop for `git worktree add` failures. If `add` fails after pruning (e.g. branch does not exist), the error surfaces as a `RuntimeError` from `create()` and propagates to the CLI as a non-zero exit — this is the correct behaviour.
- We are NOT changing the application-level lock (`state/<platform>-scan.lock`). The two locks serve different purposes and neither replaces the other.
- We are NOT modifying the Phase3 `GitNexusEnricher` which already has a 20-second timeout on its subprocess calls.
- We are NOT touching `orchestrator.py`, `cli.py`, `phase3.py`, or any plugin files.
- We are NOT adding a new preflight CLI command. The prune is called automatically inside `create()`.
