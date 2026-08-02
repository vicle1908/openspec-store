# unified-code-daily-scan

## ADDED Requirements

### Requirement: Unified Code Quality Scanning

The TDT ecosystem SHALL provide a unified `code-daily-scan` CLI that dispatches platform-specific scanning (Android, iOS) through shared worktree-aware core modules. Scanning results SHALL be consistent regardless of platform.

#### Scenario: Platform dispatch routes to correct scanner

- **WHEN** the `code-daily-scan` CLI is invoked with a worktree path
- **THEN** it SHALL detect the platform (Android/iOS) from the worktree
- **AND** it SHALL dispatch to the appropriate platform plugin
- **AND** core modules (worktree, phase3, locks, retry, gitlab_mr) SHALL be shared across platforms
