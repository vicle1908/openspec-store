## Purpose

Wires code repos to the shared OpenSpec store via `store:` pointers, adds a
git remote for team sharing, and cleans up the store root structure.

## MODIFIED Requirements

### Requirement: Code repos SHALL declare a store pointer

Each code repo without a local `openspec/specs/` planning root SHALL include
`store: openspec-store` in its `openspec/config.yaml`.

#### Scenario: Store pointer resolves automatically

- **GIVEN** a code repo whose `openspec/config.yaml` contains `store: openspec-store`
- **WHEN** an OpenSpec command runs in that repo without `--store`
- **THEN** the command SHALL resolve to `openspec-store` and the root banner SHALL report `source: "declared"`

#### Scenario: Local root takes precedence over pointer

- **GIVEN** a code repo has both a local `openspec/` directory and a `store:` pointer
- **WHEN** an OpenSpec command runs in that repo
- **THEN** the command SHALL use the local root and emit a warning that the pointer is ignored

### Requirement: The store SHALL have a git remote for team sharing

The store's git repository SHALL have a configured remote so that `openspec store
doctor` can print clone and register instructions.

#### Scenario: Doctor prints actionable clone instructions

- **GIVEN** the store has a git remote configured
- **WHEN** a teammate runs `openspec store doctor openspec-store` on a machine without the store
- **THEN** the output SHALL include the git clone URL and `openspec store register` command

#### Scenario: store.yaml records the remote URL

- **GIVEN** the store has a git remote
- **WHEN** reading `.openspec-store/store.yaml`
- **THEN** the file SHALL contain a `remote` field with the canonical clone URL

### Requirement: The openspec/ root SHALL contain only official artifacts

The `openspec/` root directory SHALL contain only `config.yaml`, `specs/`,
`changes/`, and optionally `schemas/`. Non-standard files SHALL be relocated
to `docs/governance/`.

#### Scenario: Root contains only official artifacts

- **GIVEN** the store's `openspec/` directory
- **WHEN** listing the root contents
- **THEN** the only items SHALL be `config.yaml`, `specs/`, `changes/`, and optionally `schemas/`

#### Scenario: Governance docs are accessible at their new path

- **GIVEN** non-standard files have been moved to `docs/governance/`
- **WHEN** a reader navigates to `docs/governance/`
- **THEN** all relocated files SHALL be present and cross-references SHALL resolve
