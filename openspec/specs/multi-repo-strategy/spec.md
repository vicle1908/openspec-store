# multi-repo-strategy Specification

## Purpose
Defines the strategy for cross-repository impact analysis and dependency management across the agent ecosystem.
## Requirements
### Requirement: Cross-repo impact analysis

GitNexus SHALL analyze impact across all agent repositories (agent-core, agent-harness, agent-docs-sync).

#### Scenario: Local impact

- **WHEN** a symbol is modified in one repository
- **THEN** GitNexus SHALL find all local callers and flows
- **AND** assess risk level (LOW, MEDIUM, HIGH, CRITICAL)

#### Scenario: Cross-repo impact

- **WHEN** a symbol is modified that is used by other repositories
- **THEN** GitNexus SHALL check cross-repo callers
- **AND** include them in the impact assessment
- **AND** report the full impact graph

### Requirement: Dependency management

Cross-repo dependencies SHALL be managed through workspace configuration.

#### Scenario: Dependency declaration

- **WHEN** a repository depends on another
- **THEN** the dependency SHALL be declared in the workspace manifest
- **AND** the revision SHALL be pinned
- **AND** lockfiles SHALL be consistent

#### Scenario: Dependency verification

- **WHEN** a workflow runs
- **THEN** all dependencies SHALL be verified
- **AND** version mismatches SHALL fail closed

