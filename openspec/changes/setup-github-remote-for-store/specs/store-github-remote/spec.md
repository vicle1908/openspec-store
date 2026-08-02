## Purpose

Configures the store's git remote for team sharing and updates store.yaml
with the canonical clone URL so `openspec store doctor` can print actionable
onboarding instructions.

## ADDED Requirements

### Requirement: The store SHALL have a git remote configured

The store's git repository SHALL have a configured remote pointing to the
canonical GitHub repository.

#### Scenario: Remote is configured and accessible

- **GIVEN** the store has been pushed to GitHub
- **WHEN** running `git remote -v` from the store directory
- **THEN** the output SHALL show an `origin` remote with the GitHub URL

### Requirement: store.yaml SHALL record the remote URL

The `.openspec-store/store.yaml` file SHALL contain a `remote` field with
the canonical clone URL for the store.

#### Scenario: store.yaml has remote field

- **GIVEN** the store has a git remote configured
- **WHEN** reading `.openspec-store/store.yaml`
- **THEN** the file SHALL contain a `remote` field with the git clone URL

#### Scenario: Doctor prints actionable instructions

- **GIVEN** the store has a remote configured and store.yaml has the remote field
- **WHEN** a teammate runs `openspec store doctor openspec-store` on a machine without the store
- **THEN** the output SHALL include the git clone URL and `openspec store register` command
