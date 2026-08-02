# Discovery State

## Purpose

Manage discovery state with atomic writes, dual-key cache invalidation, and history tracking.

## Requirements

### Requirement: Cache state in .docs-sync-state.yaml
The system SHALL store discovery results in `.docs-sync-state.yaml` committed to version control.

#### Scenario: State file created
- **WHEN** discovery runs for the first time
- **THEN** the system creates `.docs-sync-state.yaml` with all discovery sections
- **AND** the file is committed to git

### Requirement: Dual-key cache invalidation
The system SHALL invalidate cache using git commit hash and gitnexus/graphify manifest timestamps.

#### Scenario: Git commit changed
- **WHEN** the current git commit differs from `invalidation.git_commit`
- **THEN** the system re-runs discovery
- **AND** updates the state file with new results

### Requirement: Track structural changes
The system SHALL track which files have structural changes (ast_hash) vs cosmetic changes (mtime only).

#### Scenario: Structural change detected
- **WHEN** a file's ast_hash changes between gitnexus indexes
- **THEN** the system adds the file to `structural.file_changes`
- **AND** sets `change_type: "structural"`

### Requirement: Report documentation coverage gaps
The system SHALL report which Diátaxis quadrants are populated and which are missing.

#### Scenario: Coverage report generated
- **WHEN** discovery completes
- **THEN** the state file contains `diataxis` section with coverage percentages
- **AND** lists existing and recommended docs per quadrant

### Requirement: Implement StateTool with atomic writes
The system SHALL provide a StateTool that manages state file operations with atomic writes.

#### Scenario: StateTool atomic write
- **WHEN** StateTool.execute() is called with action="save"
- **THEN** the tool writes to .docs-sync-state.yaml.tmp first
- **AND** renames to .docs-sync-state.yaml (atomic on POSIX)
- **AND** returns ToolResult(success=True, bytes_written=N)
