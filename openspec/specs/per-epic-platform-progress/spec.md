# per-epic-platform-progress Specification

## Purpose

Add platform-specific (iOS, Android, QA) progress tracking to the per-epic spreadsheet tab. For each parent task, show the status and key of its iOS, Android, and QA subtasks. Compute per-platform weighted progress and display a summary at the top of the tab.

## Requirements

### Requirement: Fetch subtasks for parent tasks

The system SHALL fetch subtasks for each parent task in the per-epic tab when subtasks are available. Subtasks SHALL be classified by platform based on summary tag parsing.

#### Scenario: Parent task has subtasks
- **WHEN** a parent task (Story or Task) has subtasks referenced in Jira
- **THEN** the system fetches those subtasks and classifies them by platform

#### Scenario: Parent task has no subtasks
- **WHEN** a parent task has no subtask references
- **THEN** the iOS, Android, QA columns show "—" for that row

### Requirement: Classify subtasks by platform

The system SHALL classify subtasks into platform categories by parsing the subtask summary for platform tags: `[IOS]`, `[Android]`, `[QA]`, `[TEST]`. Classification is case-insensitive.

#### Scenario: iOS subtask
- **WHEN** a subtask summary contains `[IOS` (case-insensitive)
- **THEN** the subtask is classified as iOS

#### Scenario: Android subtask
- **WHEN** a subtask summary contains `[ANDROID` (case-insensitive)
- **THEN** the subtask is classified as Android

#### Scenario: QA subtask
- **WHEN** a subtask summary contains `QA` or `TEST` (case-insensitive)
- **THEN** the subtask is classified as QA

#### Scenario: Unclassified subtask
- **WHEN** a subtask summary does not match any platform tag
- **THEN** the subtask is classified as "other" and not shown in platform columns

### Requirement: Display platform columns

The per-epic tab SHALL include three new columns after the Status column: iOS, Android, QA. Each cell shows `STATUS (KEY)` format where KEY is a clickable Jira issue key.

#### Scenario: Parent task has iOS and Android subtasks
- **WHEN** RMD-4161 has subtasks RMD-4555 (iOS, CODE REVIEW) and RMD-4556 (Android, CODE REVIEW)
- **THEN** the row shows iOS="CODE REVIEW (RMD-4555)" and Android="CODE REVIEW (RMD-4556)"

#### Scenario: Parent task has no QA subtask
- **WHEN** a parent task has no QA-classified subtask
- **THEN** the QA column shows "—"

### Requirement: Compute per-platform progress

The system SHALL compute per-platform weighted progress using the existing `COMPLETION_WEIGHTS` mapping (Done=100, Code Review=75, In Progress=70, SIT=65, To Do=20, etc.).

#### Scenario: iOS progress computation
- **WHEN** a parent task has iOS subtasks with statuses [CODE REVIEW, In Progress, To Do]
- **THEN** iOS progress = (75 + 70 + 20) / 3 = 55%

#### Scenario: Overall platform progress
- **WHEN** iOS progress is 44% and Android progress is 69%
- **THEN** overall platform progress = (44% + 69%) / 2 = 56%

### Requirement: Display platform summary at top

The per-epic tab SHALL display a platform progress summary section between the metadata header and the task table. The summary shows iOS, Android, QA progress percentages.

#### Scenario: Summary with all platforms
- **WHEN** the epic has iOS (44%), Android (69%), and QA (80%) progress
- **THEN** the summary shows "iOS: 44% | Android: 69% | QA: 80%"

#### Scenario: Summary without QA
- **WHEN** the epic has no QA subtasks
- **THEN** the QA section is omitted from the summary

### Requirement: Backward compatibility

The existing per-epic tab columns (Key, Type, Summary, Status, Assignee, Sprint, Story Points, Blocked By, Blocks, Chain Depth, Impact Radius) SHALL be preserved. New platform columns are appended after Status.

#### Scenario: Existing consumers
- **WHEN** an existing consumer reads the per-epic tab
- **THEN** columns A-K remain unchanged, new columns start at L
