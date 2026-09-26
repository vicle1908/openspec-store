# Spec Delta: uv-runtime-management

## MODIFIED Requirements

### Requirement: Reproducible uv-managed dependencies
All Python repositories in the workspace SHALL maintain authoritative `uv.lock` files locked against modern, unconstrained dependency specifications, and SHALL NOT enforce legacy upper bounds (`<`).

#### Scenario: Developer setup uses locked environment
- **WHEN** a developer prepares any Python repository in the workspace
- **THEN** they SHALL run `uv sync --locked --all-extras` from that repo root
- **AND** commands SHALL run via `uv run ...`
- **AND** the lockfile SHALL resolve to latest remote package releases without artificial version ceilings.

#### Scenario: Lockfile validity is checked before rollout
- **WHEN** deployment verification is performed
- **THEN** `uv lock --check` SHALL pass in all repositories across the workspace
- **AND** deployment SHALL fail fast if any lockfile is stale.
