# shb-schedule-reproducible-dependencies Specification

## Purpose
This capability guarantees that clean clones and container builds retain the exact scheduler dependency lock required for reproducible installation.

## Requirements

### Requirement: Committed Scheduler Dependency Lock
The scheduler repository SHALL track `uv.lock` in version control and SHALL preserve the lockfile through clean-clone and container-build workflows.

#### Scenario: Clean clone retains the lockfile
- **WHEN** a fresh checkout of the scheduler repository is created
- **THEN** `uv.lock` SHALL be present and tracked
- **AND** the repository's generic local-state lock ignore rule SHALL NOT hide it

#### Scenario: Frozen container installation uses the lockfile
- **WHEN** the scheduler image build runs `uv sync --frozen`
- **THEN** the build SHALL read the committed `uv.lock`
- **AND** the installation SHALL NOT regenerate the lockfile or re-resolve dependencies

#### Scenario: Lockfile metadata validation
- **WHEN** `uv lock --check` is run before frozen installation
- **THEN** stale project metadata SHALL cause a non-zero validation result without rewriting `uv.lock`
- **AND** frozen installation SHALL not be represented as a freshness check

### Requirement: Runtime Lock Ignore Boundary
The repository SHALL continue ignoring local runtime lock files and database state without excluding the committed dependency lockfile.

#### Scenario: Local runtime state remains ignored
- **WHEN** the scheduler creates runtime lock, SQLite, or WAL files
- **THEN** those generated files SHALL remain ignored
- **AND** `uv.lock` SHALL remain trackable independently
