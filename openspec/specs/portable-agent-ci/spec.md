# portable-agent-ci Specification

## Purpose

Makes agent-repository verification reproducible from reviewed local repositories without depending on ambient sibling paths, normalized Python declarations, configured remotes, or mutable verification state.

## Requirements

### Requirement: Verified local dependency manifest

The local verifier SHALL accept an explicit workspace root and a reviewed manifest that declares the complete `tdt-core`, `agent-core`, `agent-docs-sync`, and `agent-harness` topology. Each entry SHALL declare its canonical sibling destination, exact local Git revision, lockfile digest, Python declaration, dependency edges, stable import, and public CLI smoke target.

#### Scenario: Complete local topology

- **WHEN** all required local repositories and manifest entries are present
- **THEN** the verifier SHALL prove canonical repository identity, exact revision availability, unique sibling destinations, lockfile digests, Python declarations, and transitive path-source edges before synchronization
- **AND** it SHALL emit only allowlisted repository names, revisions, dependency edges, versions, and digests as provenance

#### Scenario: Local dependency is invalid

- **WHEN** a required repository, revision, lockfile, Python declaration, destination, or dependency edge is missing or mismatched
- **THEN** verification SHALL fail with an actionable local dependency error
- **AND** it SHALL not guess a remote identifier, normalize a Python declaration, regenerate a lockfile, or fall back to an ambient editable path

### Requirement: Disposable local acquisition

The verifier SHALL materialize every declared revision from its corresponding local Git repository into a new disposable workspace without copying uncommitted files, using the aggregator workspace as an import path, or requiring a configured remote.

#### Scenario: Exact local revision is staged

- **WHEN** a declared revision exists in its canonical local repository
- **THEN** the verifier SHALL stage that exact revision at the declared sibling destination
- **AND** the staged repository SHALL be clean, non-symlinked, and contained by the disposable workspace

#### Scenario: Ambient source would influence verification

- **WHEN** a staged checkout is dirty, symlinked, outside the disposable workspace, or resolves a path source outside the declared topology
- **THEN** verification SHALL fail before dependency synchronization
- **AND** no ambient source path SHALL be added to `PYTHONPATH` or package configuration

### Requirement: Clean-runner compatibility matrix

The ecosystem SHALL verify supported `agent-core`, `agent-docs-sync`, and `agent-harness` combinations from disposable local checkouts using `uv sync --locked` and each repository's recorded Python declaration. `--locked` SHALL be used to reject lock/project drift; `--frozen` SHALL NOT be represented as validating lock freshness.

#### Scenario: Supported combination

- **WHEN** a declared compatibility combination is tested
- **THEN** dependency sync, imports, public CLI smoke tests, repository quality gates, and applicable local secret checks SHALL pass without undeclared sibling state
- **AND** Python patch declarations SHALL remain independent matrix dimensions when repositories declare different values

#### Scenario: Lock or Python mismatch

- **WHEN** the lockfile, Python declaration, or dependency provenance differs from the matrix
- **THEN** verification SHALL fail and SHALL not regenerate or update dependencies automatically

### Requirement: Isolated distribution verification

Each distributable agent package SHALL build both a wheel and source distribution from its disposable local checkout and test each artifact in a new empty local environment without source checkouts, editable installs, or the aggregator workspace on the import path.

#### Scenario: Distribution is self-contained

- **WHEN** local verification checks a built wheel or source distribution
- **THEN** installation, stable public imports, and public CLI smoke tests SHALL pass using only declared package dependencies
- **AND** the evidence SHALL record the artifact digest, build command, Python version, and installed dependency versions

#### Scenario: Distribution relies on ambient source

- **WHEN** an import or CLI succeeds only because an undeclared checkout, editable source, or workspace path is visible
- **THEN** isolated verification SHALL fail
- **AND** verification SHALL not substitute that ambient source for a declared package dependency

#### Scenario: Distribution contains a workstation-specific link

- **WHEN** a wheel or source distribution contains an absolute link or a link that escapes the packaged tree
- **THEN** distribution verification SHALL fail
- **AND** the package SHALL replace it with a portable relative link or packaged regular file before the artifact is accepted

#### Scenario: Local dependency cache is incomplete

- **WHEN** an isolated install requires a declared public dependency that is absent from the local cache
- **THEN** verification SHALL fail closed by default with a sanitized offline-prerequisite classification
- **AND** it SHALL access the package index only when the operator supplies the explicit network opt-in and contemporaneous authorization
- **AND** the opt-in SHALL remain limited to dependency downloads into disposable verification environments without transmitting source content, credentials, or environment values

### Requirement: Remote operations are deferred

Local verification SHALL NOT require or perform remote repository acquisition, hosted workflow edits or execution, package publication, artifact upload, release, or any other shared-state operation. Those capabilities SHALL remain unavailable until immutable repository identifiers, reviewed provider bindings, and separate action-specific authorization exist.

#### Scenario: Remote prerequisite is absent

- **WHEN** a local repository has no configured remote identifier or a package has no approved publication source
- **THEN** the local matrix SHALL continue using exact local revisions
- **AND** evidence SHALL record the remote capability as deferred rather than guessing an identifier or weakening a local verification gate
