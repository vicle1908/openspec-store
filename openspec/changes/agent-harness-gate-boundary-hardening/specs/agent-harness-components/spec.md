## ADDED Requirements

### Requirement: Symlink-safe artifact root validation

`validate_artifact_root()` SHALL scan user-supplied path components for symlinks before canonical resolution. The validation SHALL reject paths where any component is a symlink, using the expanded (not resolved) path.

#### Scenario: Symlink component rejected

- **GIVEN** an artifact root path containing a symlink component
- **WHEN** `validate_artifact_root()` is called
- **THEN** a `ValueError` SHALL be raised identifying the symlink component

#### Scenario: Direct symlink root rejected

- **GIVEN** the artifact root itself is a symlink
- **WHEN** `validate_artifact_root()` is called
- **THEN** a `ValueError` SHALL be raised

#### Scenario: Clean path accepted

- **GIVEN** an artifact root path with no symlink components
- **WHEN** `validate_artifact_root()` is called
- **THEN** the canonical resolved path SHALL be returned
