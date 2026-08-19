## Purpose

Define the authoritative freshness classification used by workspace knowledge-index status reporting so agents, operators, and readiness checks all rely on the same commit-first signal. This contract applies to both `knowledge-status.sh` and `refresh-knowledge-indexes.sh --check` and supersedes any prior timestamp-only freshness classification.

## ADDED Requirements

### Requirement: Commit-equality freshness primary rule

Workspace freshness reporting SHALL classify GitNexus and Graphify freshness primarily by comparing the recorded indexed revision against the current repository HEAD revision.

#### Scenario: Indexed revision matches HEAD

- **WHEN** a repository has a recorded indexed commit for a provider and the repository HEAD equals that recorded commit
- **THEN** freshness reporting SHALL classify that provider as **FRESH**

#### Scenario: Indexed revision does not match HEAD

- **WHEN** a repository has a recorded indexed commit for a provider and the repository HEAD does not equal that recorded commit
- **THEN** freshness reporting SHALL classify that provider as **STALE**

#### Scenario: No recorded revision — human dashboard

- **WHEN** a repository has index state but no recorded indexed commit for the provider
- **THEN** the human dashboard SHALL classify the provider as **UNKNOWN**
- **AND** the dashboard SHALL NOT classify the provider as **FRESH** based on timestamp recency

#### Scenario: No recorded revision — machine-readable output

- **WHEN** a repository has index state but no recorded indexed commit for the provider
- **THEN** the machine-readable output SHALL classify the provider as **UNKNOWN**
- **AND** the output SHALL include a `reason` field with value `missing_recorded_revision`
- **AND** the output SHALL NOT classify the provider as **FRESH** regardless of timestamp

### Requirement: Consistent revision exposure

Status reporting SHALL expose the repository HEAD, the recorded indexed revision, and the resulting freshness classification together for every evaluated provider.

#### Scenario: Human status is requested

- **WHEN** a developer runs `knowledge-status.sh`
- **THEN** the command SHALL list the current HEAD and recorded indexed revision alongside the freshness classification for GitNexus and Graphify

#### Scenario: Machine status is requested

- **WHEN** a developer runs `knowledge-status.sh --json`
- **THEN** the JSON output SHALL include HEAD, indexed revision, and freshness classification fields for each provider row

### Requirement: Check and status consistency

The workspace freshness check view and the workspace status view SHALL report the same freshness classification for the same repository and provider at the same moment.

#### Scenario: Both commands inspect the same repository

- **WHEN** `refresh-knowledge-indexes.sh --check` and `knowledge-status.sh` run against the same inventory state and repository HEAD
- **THEN** both commands SHALL produce the same freshness classification for each provider

#### Scenario: Timestamp-only fallback is used

- **WHEN** timestamp fallback is used at all
- **THEN** both commands SHALL apply the same fallback rule
- **AND** the result SHALL be surfaced as degraded or lower-confidence rather than as the authoritative freshness answer
