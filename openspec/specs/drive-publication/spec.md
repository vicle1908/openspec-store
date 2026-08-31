# drive-publication Specification

## Purpose
Defines the drive publication contract: publication process SHALL upload exactly the seven files specified by the keynote public-package allowlist and SHALL exclude all evidence, tests, scripts, OpenSpec, Git, and worktree content. (governing requirement: Drive publication SHALL upload only the public keynote package).


## Requirements

### Requirement: Drive publication SHALL upload only the public keynote package

The publication process SHALL upload exactly the seven files specified by the keynote public-package allowlist and SHALL exclude all evidence, tests, scripts, OpenSpec, Git, and worktree content.

#### Scenario: Explicit allowlist is enforced

- **WHEN** the sync-up script validates the source repository
- **THEN** all seven allowlisted files SHALL exist
- **AND** no non-allowlisted file SHALL be passed to rclone
- **AND** the planned or completed upload SHALL report file count 7

#### Scenario: Private content is excluded

- **WHEN** the Drive version folder is listed recursively after upload
- **THEN** it SHALL contain no `evidence/`, `tests/`, `scripts/`, `openspec/`, `.git/`, `.worktrees/`, or credential-bearing file
- **AND** the upload SHALL fail before mutation if an allowlisted source file is missing

### Requirement: Each upload SHALL use an immutable versioned destination

The publication SHALL create a root folder and a child folder derived from the committed source SHA and canonical package digest, and SHALL not overwrite a different object at the same version path.

#### Scenario: New candidate creates a separate version folder

- **WHEN** the source HEAD or canonical digest changes
- **THEN** the destination child path SHALL change
- **AND** existing Drive folders and files SHALL remain untouched

#### Scenario: Same candidate is rerun

- **WHEN** the same source commit and digest are uploaded again
- **THEN** identical remote files SHALL be treated as idempotent
- **AND** differing same-name remote objects SHALL cause a fail-closed conflict

### Requirement: The sync-up mechanism SHALL be one-way and non-destructive

The repository sync script SHALL use `rclone copy` with an explicit file list and SHALL never delete, purge, move, or change permissions on the remote.

#### Scenario: Dry run has no external side effect

- **WHEN** the script is run with `--dry-run`
- **THEN** it SHALL validate source files, commit state, and digest
- **AND** it SHALL report the planned destination
- **AND** it SHALL not create or modify a Drive folder or file

#### Scenario: Sync-up preserves unrelated remote content

- **WHEN** a normal sync-up completes
- **THEN** it SHALL not invoke `rclone sync`, `delete`, or `purge`
- **AND** files outside the exact versioned child path SHALL remain unchanged

### Requirement: Upload results SHALL be verified and recorded

The process SHALL read back the exact destination listing and record the source commit, package digest, destination path, file count, remote object names, and verification result without exposing credentials.

#### Scenario: Remote read-back matches the public package

- **WHEN** the upload completes
- **THEN** recursive remote read-back SHALL find exactly seven expected relative paths
- **AND** local and remote object sizes SHALL match
- **AND** the result SHALL identify the Drive remote and versioned path

#### Scenario: Authentication failure is explicit

- **WHEN** the configured Drive remote cannot authenticate
- **THEN** the process SHALL return a non-zero status
- **AND** it SHALL identify authentication as the blocker without printing tokens or client secrets
- **AND** no partial release claim SHALL be recorded

### Requirement: Source synchronization SHALL be reproducible and credential-safe

The sync script SHALL derive its source root from its own location, require a clean committed worktree, and use only a named configured remote.

#### Scenario: Dirty source is rejected

- **WHEN** local tracked or untracked changes are present
- **THEN** the script SHALL fail before Drive mutation
- **AND** it SHALL instruct the operator to commit or clean the source

#### Scenario: Credentials remain outside repository scope

- **WHEN** the script runs
- **THEN** it SHALL read only the remote name and ordinary source metadata
- **AND** it SHALL not print, write, or commit OAuth tokens, client secrets, or rclone configuration values
- **AND** the repository diff SHALL contain no secret-shaped value
