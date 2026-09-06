## Purpose

Define the approval-gated migration workflow for moving iCloud code projects into ~/Developer and cleaning only explicitly approved cloud or local migration artifacts.

## ADDED Requirements

### Requirement: Pre-action inventory must be recorded before any mutation

The workflow MUST record exact path existence, size, timestamp, ownership classification, and proposed action for every iCloud, Google Drive, Desktop, and Documents candidate before any destructive or relocating operation.

#### Scenario: Successful read-only inventory capture
- **WHEN** the migration workflow is started
- **THEN** it MUST produce evidence containing path, owner classification, size, timestamp, and proposed action for every candidate path, and it MUST NOT execute deletion or move commands.

### Requirement: User must approve exact destructive paths before mutation

The workflow MUST NOT delete or move data until the user explicitly approves the exact paths to be mutated.

#### Scenario: Pending approval blocks mutations
- **WHEN** exact path-level approval has not been recorded
- **THEN** the workflow MUST remain blocked on all mutation tasks.

### Requirement: Approved iCloud code projects must be moved only when destination and source can be verified

Each approved iCloud project MUST be moved only when the workflow can verify destination presence and source absence after the move.

#### Scenario: Approved move verification
- **WHEN** an approved iCloud code project is migrated to ~/Developer
- **THEN** the destination path MUST exist with verified contents and the original iCloud path MUST no longer exist.

### Requirement: Google Drive cleanup must respect documentation and personal preservation rules

The workflow MUST preserve documentation, rollback bundles, personal-looking paths, and unknown-ownership paths unless the user explicitly approves them for deletion.

#### Scenario: Documentation kept during Google Drive cleanup
- **WHEN** Google Drive cleanup runs on approved paths
- **THEN** keep-listed documentation and personal paths MUST remain present.

### Requirement: Final verification must record actual post-action state

After approved operations, the workflow MUST re-check destination/source presence, cloud or mirror state, and disk usage evidence without claiming unmeasured APFS free-space recovery as deleted bytes.

#### Scenario: Post-action evidence recorded
- **WHEN** approved operations complete
- **THEN** the workflow MUST record actual source/destination state and disk usage evidence.
