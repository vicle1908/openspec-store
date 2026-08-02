## Purpose

This specification defines requirements for Configuration.

## Requirements

### Requirement: Typed HarnessConfig

The harness SHALL use a typed configuration model composed with the public agent-core consumer configuration.

#### Scenario: Required fields

- **WHEN** configuration is loaded
- **THEN** it SHALL validate consumer/model policy, workspace repositories, artifact root, gate policy, validation limits, persistence mode, budgets, and retention
- **AND** invalid configuration SHALL stop startup

### Requirement: Canonical TDT_HOME loading

Configuration and secrets SHALL use the workspace-wide `TDT_HOME` contract.

#### Scenario: Config precedence

- **WHEN** the harness starts
- **THEN** effective configuration SHALL follow environment overrides, `$TDT_HOME/.env`, `$TDT_HOME/harness/config.yaml`, `$TDT_HOME/harness/workspace.yaml`, and documented defaults
- **AND** `TDT_HOME` SHALL be expanded and re-evaluated according to the shared loader contract

#### Scenario: Secret handling

- **WHEN** credentials are required
- **THEN** they SHALL come from `$TDT_HOME/.env` or the shared factory
- **AND** they SHALL not appear in YAML, logs, prompts, artifacts, or errors

### Requirement: Workspace repository schema

Each configured repository SHALL declare identity and bounded path information; live index status SHALL be discovered rather than trusted from static booleans.

#### Scenario: Repository entry

- **WHEN** a repository is configured
- **THEN** it SHALL include a unique name, resolved root, repository type, optional GitNexus index name, optional Graphify graph path, and access mode
- **AND** the root SHALL exist and remain inside an administrator-approved workspace root

#### Scenario: Index state

- **WHEN** startup checks a repository
- **THEN** GitNexus and Graphify availability/freshness SHALL be derived from their current metadata and files
- **AND** stale YAML flags SHALL not mark an index current

### Requirement: Gate configuration

Each gate SHALL have a typed, validated policy.

#### Scenario: Gate fields

- **WHEN** a gate is configured
- **THEN** it SHALL declare stage, required flag, authorized actors/groups, expiry, reject/escalate behavior, permitted backtrack targets, and optional deterministic auto-approval rule

#### Scenario: Unsafe auto-approval

- **WHEN** an auto-approval rule is an untyped expression, model prompt, or unknown callback
- **THEN** configuration SHALL fail

### Requirement: Authority profile

The initial configuration SHALL be read-only outside the harness artifact root.

#### Scenario: Prohibited authority

- **WHEN** configuration requests source writes, shell/code execution, runtime authoring, external mutation, or an artifact root outside the approved TDT_HOME subtree
- **THEN** startup SHALL reject it
- **AND** a new reviewed OpenSpec change SHALL be required to add that authority

### Requirement: Finite limits

Model, workflow, revision, validation, and persistence operations SHALL have finite limits.

#### Scenario: Limit validation

- **WHEN** configuration is loaded
- **THEN** request/token budgets, stage timeouts, maximum revisions, query fan-out, artifact size, and gate expiry SHALL be positive and bounded
- **AND** unlimited values SHALL be rejected in the initial release
