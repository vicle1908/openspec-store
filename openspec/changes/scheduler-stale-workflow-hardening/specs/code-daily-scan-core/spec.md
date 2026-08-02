## MODIFIED Requirements

### Requirement: WorktreeManager subprocess error surfacing

The system SHALL surface stderr from failed `git` subprocess calls inside
`WorktreeManager._default_command_runner`. Specifically, when
`subprocess.run(check=True)` raises `subprocess.CalledProcessError`, the
exception raised to the caller SHALL include the captured stderr text in its
message string. The default `_default_command_runner` accepts an optional
`timeout=` parameter and passes it through to `subprocess.run`.

#### Scenario: Failed git command surfaces stderr

- **WHEN** `WorktreeManager._default_command_runner` is called with `["git",
  "worktree", "add", ...]` and the command exits with a non-zero status and
  non-empty stderr
- **THEN** the raised exception SHALL have a message containing both the
  command's `returncode` AND the captured stderr text (e.g.
  `"git worktree ... failed (exit=128): fatal: invalid reference: main"`)

#### Scenario: Successful git command is unchanged

- **WHEN** `WorktreeManager._default_command_runner` is called with `["git",
  "worktree", "add", ...]` and the command exits with status 0
- **THEN** the function SHALL return the `CompletedProcess` unchanged and no
  exception SHALL be raised

#### Scenario: Timeout still propagates as TimeoutExpired

- **WHEN** `WorktreeManager._default_command_runner` is called with a
  `timeout=` argument and the command exceeds the timeout
- **THEN** `subprocess.TimeoutExpired` SHALL be raised (not wrapped in any
  other exception class) so callers' existing timeout handlers continue to
  work