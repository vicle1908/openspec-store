## ADDED Requirements

### Requirement: Canonical workspace location

All active TDT development SHALL occur under `$HOME/Developer/tdt/`. The workspace root is a local APFS container, not a Git repository and not a uv workspace.

#### Scenario: Developer machine layout

- **WHEN** inspecting a migrated developer machine
- **THEN** `$HOME/Developer/tdt/` SHALL exist as a real directory
- **AND** source projects SHALL each live in their own Git repository under that root
- **AND** a metadata repository named `tdt-meta` SHALL exist under that root
- **AND** the legacy legacy cloud path SHALL NOT be used for active development.

#### Scenario: Root compatibility paths

- **WHEN** a tool reads root-level paths such as `AGENTS.md`, `docs/`, `openspec/`, `.agents/`, `config/`, `skills/`, `openapi/`, `examples/`, or `tools/`
- **THEN** those paths SHALL resolve through symlinks into `tdt-meta/`
- **AND** writes through those symlinks SHALL update Git-tracked files in `tdt-meta`.

### Requirement: Git-backed workspace metadata

Workspace-level knowledge and shared tooling SHALL live in a Git repository named `tdt-meta`, hosted on `git.ecomedic.vn/tdt/tdt-meta`.

#### Scenario: Metadata contents

- **WHEN** `tdt-meta` is inspected
- **THEN** it SHALL contain shared docs, OpenSpec files, agent config, workspace config, shared tools, root guidance files, and workspace editor/CI config
- **AND** it SHALL NOT contain secrets, virtual environments, generated caches, code-intelligence indexes, or runtime-only state.

#### Scenario: Metadata propagation between machines

- **WHEN** a developer changes `AGENTS.md`, OpenSpec artifacts, docs, skills, or shared scripts
- **THEN** the change SHALL propagate through `git commit` and `git push` in `tdt-meta`
- **AND** other machines SHALL receive it through `git fetch` or `git pull`
- **AND** legacy cloud SHALL NOT be required.

### Requirement: Complete migration cutover

The migration SHALL be a one-way cutover for supported workflows. After verification passes, future development SHALL happen only from `$HOME/Developer/tdt/`.

#### Scenario: Legacy path decommissioned

- **WHEN** cutover verification completes
- **THEN** shell hooks, deploy defaults, docs, scripts, automations, and agent guidance SHALL no longer reference the legacy legacy cloud workspace as an active path
- **AND** the legacy path MAY be deleted or retained only as an inert operator backup
- **AND** no supported rollback workflow SHALL be documented by this change.

#### Scenario: Development attempted from legacy cloud

- **WHEN** tests, `uv` commands, deployment, or feature work are started from a path under `legacy workspace` or `legacy-cloud-workspace`
- **THEN** the workflow SHALL fail fast or warn as a policy violation
- **AND** agents SHALL direct development back to `$HOME/Developer/tdt/`.

### Requirement: Migration script idempotence

A migration script SHALL perform the complete cutover from the legacy legacy cloud workspace to the canonical Git-backed workspace.

#### Scenario: First-time migration

- **WHEN** the migration script runs on a machine still using the legacy workspace
- **THEN** it SHALL verify clean and pushed repos, required tooling, writable destination, and adequate disk space
- **AND** it SHALL create or reuse `tdt-meta`
- **AND** it SHALL migrate metadata into `tdt-meta`
- **AND** it SHALL clone all source repositories into `$HOME/Developer/tdt/`
- **AND** it SHALL create root compatibility symlinks
- **AND** it SHALL trigger venv relocation and verification steps.

#### Scenario: Re-running after partial completion

- **WHEN** the migration script is re-run after an interrupted attempt
- **THEN** it SHALL detect existing repos, symlinks, metadata commits, and relocated venvs
- **AND** it SHALL skip completed steps without overwriting uncommitted work
- **AND** it SHALL exit successfully if the target state is already satisfied.

### Requirement: Path-bound cache and index invalidation

All caches and indexes that embed absolute paths SHALL be rebuilt after relocation.

#### Scenario: Code-intelligence rebuild

- **WHEN** source repositories have been cloned to `$HOME/Developer/tdt/`
- **THEN** GitNexus indexes SHALL be rebuilt or re-pointed from the new path
- **AND** Graphify output SHALL be regenerated from the new path
- **AND** stale indexes referencing the legacy legacy cloud path SHALL not be used.

#### Scenario: IDE cache refresh

- **WHEN** Xcode or Android Studio is opened from the new workspace
- **THEN** stale absolute-path caches SHALL be regenerated or cleared as needed
- **AND** regenerated runtime state SHALL not be committed unless intentionally shared configuration.

## MODIFIED Requirements

### Requirement: Development venvs outside legacy cloud workspace

Development virtual environments SHALL live outside legacy cloud workspace and use unique per-repo paths.

#### Scenario: Per-repo venv relocation

- **WHEN** a Python repository is located under `$HOME/Developer/tdt/`
- **THEN** `UV_PROJECT_ENVIRONMENT` SHALL resolve to a unique path such as `$HOME/.tdt/venvs/<repo-name>`
- **AND** `PYTHONPYCACHEPREFIX` SHALL resolve to `$HOME/.tdt/pycache/<repo-name>` unless explicitly overridden
- **AND** `<repo>/.venv` MAY be a symlink to the relocated venv for IDE discovery
- **AND** no two repos SHALL share the same absolute environment path.

#### Scenario: Cross-repo path dependencies

- **WHEN** repo A depends on repo B via a local path dependency
- **THEN** editable install `.pth` files SHALL reference `$HOME/Developer/tdt/...`
- **AND** they SHALL contain exactly one path per line
- **AND** subsequent `uv sync` operations in other repos SHALL not corrupt them.

### Requirement: Deployment verification is mandatory

Cutover verification SHALL prove the new workspace is the active and healthy source of truth before the migration is declared complete.

#### Scenario: Verification harness

- **WHEN** cutover verification runs
- **THEN** tests SHALL pass from relocated venvs
- **AND** Jira and GitLab live SDK smoke checks SHALL pass
- **AND** `webhook-receiver` deployment and `/health` SHALL pass from `$HOME/Developer/tdt/webhook-receiver`
- **AND** GitNexus, Graphify, Docker bind mounts, Xcode, and Android Studio SHALL be validated from the new path.
