## ADDED Requirements

### Requirement: Worktree Prune Before Create

The system SHALL call `git worktree prune` (with a 30-second timeout) immediately before every `git worktree add` invocation in `WorktreeManager.create()`. The prune is best-effort: a non-zero exit, timeout, or unexpected exception MUST be logged at WARN level via structlog and MUST NOT prevent the subsequent `git worktree add` from running.

The prune MUST complete within its 30-second timeout under normal conditions. A prune that returns within the timeout is logged at INFO level with the count of removed entries (extracted from git's `--verbose` output when available, otherwise `pruned=unknown`).

#### Scenario: Prune runs first, then add

- **WHEN** `WorktreeManager.create()` is invoked
- **THEN** the command runner SHALL observe a `["git", "worktree", "prune", "--verbose"]` call issued before any `["git", "worktree", "add", ...]` call

#### Scenario: Prune failure does not block add

- **WHEN** `git worktree prune` exits with a non-zero code, raises `subprocess.TimeoutExpired`, or raises any other exception
- **THEN** `WorktreeManager.create()` MUST log a WARN entry and proceed to call `git worktree add` regardless

#### Scenario: Prune timeout surfaces as WARN

- **WHEN** `git worktree prune` does not exit within 30 seconds
- **THEN** the system MUST log a WARN entry containing the timeout value, swallow the `subprocess.TimeoutExpired`, and proceed to `git worktree add`

### Requirement: Subprocess Timeouts On All Worktree Operations

`WorktreeManager._default_command_runner` MUST accept a `timeout` parameter and pass it through to `subprocess.run`. All git invocations inside `WorktreeManager` MUST pass an explicit timeout. The minimum timeouts are:

| Operation | Minimum timeout |
|-----------|-----------------|
| `git worktree add` | 300 s |
| `git worktree prune` | 30 s |
| `git worktree remove` | 60 s |
| `git rev-parse --verify` | 10 s |
| `npx gitnexus status` | 20 s |

A `subprocess.TimeoutExpired` raised inside `WorktreeManager` MUST propagate to the caller as a `RuntimeError` with a message that includes the argv, the timeout value, and the elapsed time, so the operator can see which step timed out and how long the system waited.

#### Scenario: Add operation has timeout

- **WHEN** `WorktreeManager.create()` is invoked
- **THEN** the `git worktree add` call SHALL be made with `timeout=300` (or higher)

#### Scenario: Timeout surfaces as RuntimeError

- **WHEN** any git invocation in `WorktreeManager` exceeds its configured timeout
- **THEN** the system MUST raise `RuntimeError` whose message includes the full argv, the configured timeout in seconds, and the elapsed time, and MUST NOT block indefinitely

#### Scenario: Backward-compatible runner signature

- **WHEN** a test or production caller invokes the runner without a `timeout` keyword
- **THEN** the runner MUST behave exactly as before (no `timeout` argument passed to `subprocess.run`, preserving backward compatibility with existing `FakeRunner` test infrastructure)

### Requirement: Worktree Lifecycle Diagnostic Logging

`WorktreeManager.managed_worktree()` MUST emit two structlog INFO log entries per scan: one immediately before `create()` returns and one immediately after `teardown()` returns. The log entries MUST include:

- `platform`: derived from `repo_path.name`
- `worktree_path`: the resolved worktree path (or `None` for the pre-`create()` line)
- `gitnexus_index_fresh`: the value from the session (or `None` for the pre-`create()` line)

The log entries MUST go to structlog's default handler (stderr) and MUST NOT appear in the JSON payload emitted by the CLI to stdout.

#### Scenario: Create log entry appears

- **WHEN** a scan begins and `managed_worktree()` is entered
- **THEN** a structlog INFO entry with event=`worktree.create.begin` SHALL be emitted before `create()` runs

#### Scenario: Teardown log entry appears

- **WHEN** `managed_worktree()` exits normally or via exception
- **THEN** a structlog INFO entry with event=`worktree.teardown.end` SHALL be emitted after `teardown()` completes

#### Scenario: Logging never blocks the JSON payload

- **WHEN** the CLI emits its final JSON payload to stdout
- **THEN** the payload MUST NOT contain the worktree log entries (they go to stderr via structlog)

## MODIFIED Requirements

### Requirement: Worktree-Based Scanning

The system SHALL run each scan against a git worktree of the target repository, created before scanning and removed after scanning. The worktree-creation pipeline MUST proactively prune stale worktree entries before every `git worktree add` and MUST bound every git subprocess call with an explicit timeout so that a single hung operation fails fast with a meaningful `RuntimeError` rather than blocking the parent process indefinitely. Lifecycle events SHALL be logged at INFO via structlog so operators have visible diagnostic markers even when the outer scan is killed.

#### Scenario: Stale worktree entries are pruned before each add

- **WHEN** `WorktreeManager.create()` runs after a previous scan was killed (leaving a `prunable` entry in the repo's `.git/worktrees/`)
- **THEN** the system SHALL invoke `git worktree prune --verbose` (with a 30-second timeout) before invoking `git worktree add`
- **AND** the subsequent `git worktree add` SHALL complete without hanging on the stale entry

#### Scenario: Hung git operation fails fast

- **WHEN** any git invocation inside `WorktreeManager` (e.g. `git worktree add`, `git worktree remove`, `git rev-parse`) does not return within its configured timeout
- **THEN** the system MUST raise `RuntimeError` with a message that includes the argv, the timeout value in seconds, and the elapsed time, rather than blocking indefinitely

#### Scenario: Worktree lifecycle is logged

- **WHEN** a scan begins and `managed_worktree()` is entered, and again when it exits
- **THEN** the system SHALL emit two structlog INFO entries (one for `worktree.create.begin`, one for `worktree.teardown.end`) to stderr, with the worktree path and the GitNexus freshness verdict
