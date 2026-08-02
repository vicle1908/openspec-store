## ADDED Requirements

### Requirement: Human overrides take precedence over auto-discovery
The system SHALL allow human overrides in `.docs-sync-overrides.yaml` that take precedence over auto-discovery results.

#### Scenario: Quadrant override
- **WHEN** a human sets `quadrant_overrides.docs/config.md.quadrant: how-to`
- **THEN** the system uses `how-to` instead of auto-classified `reference`
- **AND** logs the override application in state file

#### Scenario: Mapping override
- **WHEN** a human adds `mapping_overrides.src/foo.py: [docs/reference/foo.md, docs/how-to/foo-guide.md]`
- **THEN** the system uses the override mapping instead of auto-mapping
- **AND** includes both targets in the final mapping

#### Scenario: Exclusion override
- **WHEN** a human adds `exclusions: [docs/legacy-api.md]`
- **THEN** the system excludes that file from discovery results
- **AND** does not generate documentation targets for it

### Requirement: Multi-level override resolution
The system SHALL resolve overrides from multiple sources in order of specificity.

#### Scenario: Repo-level override
- **WHEN** `.docs-sync-overrides.yaml` exists in the repo root
- **THEN** the system uses repo-level overrides first
- **AND** ignores ecosystem and global overrides for conflicting paths

#### Scenario: Ecosystem-level override
- **WHEN** no repo-level override exists but `~/.tdt/docs-sync/overrides.yaml` exists
- **THEN** the system uses ecosystem-level overrides
- **AND** ignores global overrides for conflicting paths

#### Scenario: Global-level override
- **WHEN** no repo or ecosystem overrides exist but `~/.config/docs-sync/overrides.yaml` exists
- **THEN** the system uses global-level overrides

### Requirement: Override files are gitignored
The system SHALL treat `.docs-sync-overrides.yaml` as gitignored (not committed to version control).

#### Scenario: Override file present
- **WHEN** `.docs-sync-overrides.yaml` exists in the repo
- **THEN** the system reads and applies overrides
- **AND** does not commit the file to git

#### Scenario: Override file absent
- **WHEN** `.docs-sync-overrides.yaml` does not exist
- **THEN** the system proceeds with auto-discovery only
- **AND** does not create the override file

### Requirement: Log override conflicts
The system SHALL log conflicts between auto-discovery and human overrides.

#### Scenario: Conflict detected
- **WHEN** auto-discovery classifies `docs/config.md` as `reference`
- **AND** human override classifies it as `how-to`
- **THEN** the system applies the human override
- **AND** logs the conflict in `override_conflicts` section of state file
- **AND** marks the conflict as `reviewed: false`

#### Scenario: Conflict review
- **WHEN** a user runs `docs-sync discover --review-overrides`
- **THEN** the system lists all unreviewed conflicts
- **AND** allows the user to accept or reject each override

### Requirement: Priority overrides for multi-quadrant documents
The system SHALL allow humans to set primary and secondary quadrants for documents serving multiple quadrants.

#### Scenario: Primary/secondary set
- **WHEN** a human sets `priority_overrides.README.md.primary: tutorial` and `secondary: [reference, explanation]`
- **THEN** the system uses `tutorial` as primary quadrant for file-level classification
- **AND** stores secondary quadrants for section-level classification

#### Scenario: No priority override
- **WHEN** no priority override is set for a multi-quadrant document
- **THEN** the system uses auto-classification with highest confidence quadrant as primary

### Requirement: Override history tracking
The system SHALL track when overrides were applied and why.

#### Scenario: Override applied
- **WHEN** an override is applied
- **THEN** the system adds an entry to `override_applied` section
- **AND** includes path, auto classification, override classification, date, and reason

#### Scenario: Override removed
- **WHEN** an override is removed from the override file
- **THEN** the system removes the entry from `override_applied`
- **AND** re-evaluates the classification using auto-discovery

### Requirement: Implement StateTool with override loading
The system SHALL provide a StateTool that loads overrides from multiple paths and applies them with conflict detection.

#### Scenario: Override resolution order
- **WHEN** StateTool.load_overrides() is called
- **THEN** the tool checks repo_root/.docs-sync-overrides.yaml first
- **AND** falls back to ~/.tdt/docs-sync/overrides.yaml
- **AND** falls back to ~/.config/docs-sync/overrides.yaml

#### Scenario: StateTool applies quadrant override
- **WHEN** StateTool.apply_overrides() is called with overrides and auto_mapping
- **THEN** the tool applies quadrant_overrides to change classifications
- **AND** logs conflicts in override_conflicts section

#### Scenario: StateTool applies mapping override
- **WHEN** StateTool.apply_overrides() is called with mapping_overrides
- **THEN** the tool adds/replaces mapping entries
- **AND** returns updated auto_mapping with overrides applied

#### Scenario: StateTool applies exclusion override
- **WHEN** StateTool.apply_overrides() is called with exclusions
- **THEN** the tool removes excluded paths from auto_mapping
- **AND** adds them to excluded_paths section

#### Scenario: StateTool detects override conflict
- **WHEN** StateTool.apply_overrides() detects auto classification differs from override
- **THEN** the tool logs conflict in override_conflicts section
- **AND** marks conflict as reviewed=false
