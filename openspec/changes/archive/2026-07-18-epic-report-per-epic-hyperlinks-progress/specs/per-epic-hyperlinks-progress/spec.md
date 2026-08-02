# per-epic-hyperlinks-progress Specification

## Purpose

Enhance the per-epic spreadsheet tab with clickable hyperlinks in platform columns and a progress percentage column showing weighted subtask completion per parent ticket.

## Requirements

### Requirement: Hyperlinks in platform columns

The iOS, Android, and QA columns SHALL display clickable Jira hyperlinks using the `=HYPERLINK(url, display)` formula format. The display text SHALL show `STATUS (KEY)` format.

#### Scenario: Subtask exists
- **WHEN** a parent task has an iOS subtask RMD-4555 with status "CODE REVIEW"
- **THEN** the iOS cell contains `=HYPERLINK("https://psplit.atlassian.net/browse/RMD-4555", "CODE REVIEW (RMD-4555)")`

#### Scenario: No subtask
- **WHEN** a parent task has no iOS subtask
- **THEN** the iOS cell contains "—"

### Requirement: Progress column

A Progress column SHALL be added after the QA column showing weighted progress percentage for each parent ticket.

#### Scenario: Parent has subtasks
- **WHEN** a parent task has iOS subtask at CODE REVIEW (75%) and Android subtask at In Progress (70%)
- **THEN** the Progress column shows 73% (weighted average)

#### Scenario: Parent has no subtasks
- **WHEN** a parent task has no subtasks
- **THEN** the Progress column shows the parent task's weighted status (e.g., In Progress = 70%)

#### Scenario: Only one platform has subtasks
- **WHEN** a parent task has only iOS subtasks at Done (100%)
- **THEN** the Progress column shows 100% (iOS only contributes)

### Requirement: Progress computation uses existing weights

The Progress column SHALL use the existing `COMPLETION_WEIGHTS` mapping (Done=100, Code Review=75, In Progress=70, SIT=65, To Do=20, etc.).

#### Scenario: Consistent with epic completion
- **WHEN** the epic-level completion uses COMPLETION_WEIGHTS
- **THEN** the per-ticket Progress column uses the same weights

### Requirement: Backward compatibility

Existing columns A-K (Key through Impact Radius) SHALL remain unchanged. New columns L-O (iOS, Android, QA, Progress) are appended.

#### Scenario: Existing consumers
- **WHEN** an existing consumer reads the per-epic tab
- **THEN** columns A-K remain unchanged, new columns start at L
