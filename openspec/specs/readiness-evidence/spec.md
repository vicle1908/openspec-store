# readiness-evidence Specification

## Purpose
Provides reproducible, source-complete evidence so a readiness claim describes the exact public behavior and committed source that users can run.
## Requirements
### Requirement: Complete source identity

Readiness evidence SHALL identify the repository revision and hash the complete production-relevant source set, including untracked files present during a run.

#### Scenario: Clean checkout

- **WHEN** a readiness run starts from a clean checkout
- **THEN** the manifest SHALL record the commit, sorted production path set, and content digest for every included file
- **AND** the run SHALL fail if unexpected production files appear after the manifest is created

#### Scenario: Dirty or incomplete source

- **WHEN** tracked or untracked production files differ from the recorded manifest
- **THEN** readiness SHALL be incomplete
- **AND** a commit hash alone SHALL not certify the source

### Requirement: Public-boundary semantic evidence

Each semantic readiness gate SHALL execute through the supported public CLI or documented process boundary with production configuration and a disposable bounded fixture.

#### Scenario: Public fixture passes

- **WHEN** a fixture exercises a lifecycle through the public boundary
- **THEN** the manifest SHALL record the exact command, repository, fixture identity, source identity, exit status, and sanitized result
- **AND** injected services alone SHALL not satisfy the gate

#### Scenario: Public fixture fails

- **WHEN** the public boundary produces empty, fabricated, or policy-invalid output
- **THEN** the gate SHALL fail with the unmet contract and readiness SHALL remain incomplete

### Requirement: Pre-archive revalidation

The verification owner SHALL revalidate source identity, required dependencies, provider bindings, and actor policy immediately before archiving a readiness change.

#### Scenario: Source drift before archive

- **WHEN** any covered source, provider binding, or policy changes after a gate passes
- **THEN** the affected evidence SHALL be invalidated and the gate SHALL rerun

#### Scenario: Evidence is complete

- **WHEN** all required gates pass against the same complete source manifest
- **THEN** the change MAY be marked ready for archive with a cross-reference to the immutable manifest

