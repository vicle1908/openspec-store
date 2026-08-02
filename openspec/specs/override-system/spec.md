# Override System

## Purpose

Allow human overrides for discovery results via gitignored files, with multi-level resolution and conflict detection.

## Requirements

### Requirement: Human overrides take precedence over auto-discovery
The system SHALL allow human overrides in `.docs-sync-overrides.yaml` that take precedence over auto-discovery results.

#### Scenario: Quadrant override
- **WHEN** a human sets `quadrant_overrides.docs/config.md.quadrant: how-to`
- **THEN** the system uses `how-to` instead of auto-classified `reference`
- **AND** logs the override application in state file

### Requirement: Multi-level override resolution
The system SHALL resolve overrides from multiple sources in order of specificity.

#### Scenario: Repo-level override
- **WHEN** `.docs-sync-overrides.yaml` exists in the repo root
- **THEN** the system uses repo-level overrides first
- **AND** ignores ecosystem and global overrides for conflicting paths

### Requirement: Override files are gitignored
The system SHALL treat `.docs-sync-overrides.yaml` as gitignored (not committed to version control).

#### Scenario: Override file present
- **WHEN** `.docs-sync-overrides.yaml` exists in the repo
- **THEN** the system reads and applies overrides
- **AND** does not commit the file to git

### Requirement: Log override conflicts
The system SHALL log conflicts between auto-discovery and human overrides.

#### Scenario: Conflict detected
- **WHEN** auto-discovery classifies `docs/config.md` as `reference`
- **AND** human override classifies it as `how-to`
- **THEN** the system applies the human override
- **AND** logs the conflict in `override_conflicts` section of state file
