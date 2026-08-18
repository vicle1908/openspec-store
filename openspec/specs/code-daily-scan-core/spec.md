# code-daily-scan-core Specification

## Purpose
TBD - created by archiving change scheduler-stale-workflow-hardening. Update Purpose after archive.

## Requirements

### Requirement: WorktreeManager subprocess error surfacing

The system SHALL surface stderr from failed `git worktree` subprocess calls at
the `WorktreeManager.create()` error boundary. The default command runner
SHALL capture stderr and accept an optional `timeout=` parameter, and a failed
worktree creation SHALL raise the existing `RuntimeError` wrapper with the
subprocess return code and captured stderr in its message.

#### Scenario: Failed git command surfaces stderr

- **WHEN** `WorktreeManager.create()` invokes `git worktree add` and the
  command exits with a non-zero status and non-empty stderr
- **THEN** the raised `RuntimeError` SHALL have a message containing both the
  command's `returncode` AND the captured stderr text (e.g.
  `"worktree creation failed: ... exit status 128 ... fatal: invalid reference: main"`)

#### Scenario: Successful git command is unchanged

- **WHEN** the default command runner executes a successful `git worktree add`
  command
- **THEN** it SHALL return the `CompletedProcess` unchanged and no exception
  SHALL be raised

#### Scenario: Timeout still propagates as TimeoutExpired

- **WHEN** the default command runner is called with a `timeout=` argument and
  the command exceeds the timeout
- **THEN** `subprocess.TimeoutExpired` SHALL be raised (not wrapped in any
  other exception class) so callers' existing timeout handlers continue to
  work
