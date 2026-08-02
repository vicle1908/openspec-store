# repository-registry-and-module-delivery Specification

## Purpose

Defines how TDT records repository identity and safely delivers shared agent modules without relying on hard-coded local paths or mutating sibling repositories during validation.

## Requirements

### Requirement: Repository registry grammar

TDT SHALL maintain a tracked repository registry that declares each governed repository with a unique name, relative root, repository type, module-delivery role, and requiredness. Registry roots MUST be relative paths beneath the selected workspace root and MUST NOT contain absolute paths, parent traversal, empty components, or shell expansion.

#### Scenario: Valid registry row
- **WHEN** registry validation reads a row after the header
- **THEN** the row SHALL declare exactly the required fields
- **AND** the repository name SHALL be unique and kebab-case compatible
- **AND** the root SHALL resolve beneath the selected workspace root

#### Scenario: Invalid registry path
- **WHEN** a row contains an absolute path, parent traversal, an empty root, or shell expansion
- **THEN** registry validation SHALL fail with the row number and SHALL NOT inspect or mutate the target path

#### Scenario: Duplicate repository identity
- **WHEN** two rows declare the same repository name or root
- **THEN** registry validation SHALL fail with both identities before any module-delivery action runs

### Requirement: Module delivery modes

The module installer SHALL support preview, verification, and repair as explicit modes. Preview and verification MUST NOT create directories, replace links, delete files, or mutate sibling repositories. Repair MAY create or replace module symlinks only for present target repositories and only when invoked explicitly.

#### Scenario: Dry-run preview
- **WHEN** the installer runs in dry-run mode
- **THEN** it SHALL report the source module root, selected registry, present targets, skipped absent targets, and planned link changes without changing filesystem state

#### Scenario: Verify mode
- **WHEN** the installer runs in verify mode
- **THEN** it SHALL fail when an expected module link is missing, stale, non-symlink, or resolves outside the canonical module root
- **AND** it SHALL skip absent optional repositories without creating them

#### Scenario: Repair mode
- **WHEN** the installer runs in repair mode for a present target repository
- **THEN** it SHALL create the target module directory when needed
- **AND** it SHALL create missing module symlinks and replace stale symlinks that are confined to the target module directory
- **AND** it SHALL refuse to overwrite regular files or directories

### Requirement: Symlink confinement

Module delivery SHALL confine source modules to the canonical shared module directory and target links to each selected repository's `.agents/modules/` directory. Verification and repair MUST fail closed when a repository root, module source, target directory, or existing symlink cannot be resolved safely.

#### Scenario: Existing link escapes canonical modules
- **WHEN** verification encounters an existing module symlink whose resolved target is outside the canonical shared module directory
- **THEN** verification SHALL fail and report the repository and module name

#### Scenario: Target path escapes repository
- **WHEN** the target `.agents/modules/` path does not resolve beneath the selected repository root
- **THEN** installer verification and repair SHALL stop for that repository and report the confinement failure

#### Scenario: Canonical source is missing
- **WHEN** the shared module source directory is missing or contains no module files
- **THEN** every installer mode SHALL fail before evaluating target repositories

### Requirement: Standalone clone behavior

Registry validation and installer preview SHALL work from a standalone `tdt-meta` clone where sibling repositories are absent. Missing optional repositories SHALL be reported as skipped targets, and mutating modes SHALL NOT create sibling repository roots.

#### Scenario: Optional sibling repository absent
- **WHEN** a registry row is marked optional and its root does not exist
- **THEN** validation and dry-run SHALL report it as absent and continue
- **AND** verify and repair SHALL skip it without creating the root directory

#### Scenario: Required repository absent
- **WHEN** a registry row is marked required and its root does not exist
- **THEN** registry validation SHALL fail before module verification or repair

### Requirement: Disposable registry fixtures

TDT SHALL validate registry and module-delivery behavior with disposable fixtures that exercise valid registries, malformed rows, duplicate identities, absent optional repositories, missing required repositories, non-symlink conflicts, stale links, and escaping links.

#### Scenario: Fixture suite runs
- **WHEN** the registry fixture runner executes
- **THEN** valid fixtures SHALL exit successfully
- **AND** invalid fixtures SHALL exit non-zero
- **AND** source fixtures SHALL remain unchanged
