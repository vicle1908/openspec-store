## ADDED Requirements

### Requirement: Bounded workspace registry

The harness SHALL build a registry from public workspace discovery plus explicit typed repository configuration.

#### Scenario: Repository discovery

- **WHEN** startup discovers repositories
- **THEN** it SHALL resolve canonical roots and merge only explicitly allowed entries
- **AND** duplicate names, missing roots, or roots outside the approved workspace SHALL fail validation

#### Scenario: Read-only repository access

- **WHEN** a stage reads repository content
- **THEN** the resolved path SHALL remain inside that repository root
- **AND** the harness SHALL expose no source-write operation

### Requirement: GitNexus MCP integration

GitNexus queries SHALL use the MCP router tools as the primary code-intelligence interface.

#### Scenario: Symbol context

- **WHEN** a stage needs a symbol's callers/callees or execution-flow participation
- **THEN** it SHALL call GitNexus MCP `context` with the selected repository and UID or disambiguation fields

#### Scenario: Change impact

- **WHEN** a planning artifact proposes modifying an existing symbol
- **THEN** it SHALL call GitNexus MCP `impact` upstream
- **AND** HIGH or CRITICAL risk SHALL require an explicit human disposition in the planning trace

#### Scenario: Multi-repository query

- **WHEN** a ticket spans repositories
- **THEN** each result SHALL retain its source repository and index commit
- **AND** aggregation SHALL not merge same-named symbols without identity evidence

### Requirement: Graphify structural integration

Graphify SHALL provide bounded repository-local traversal and path evidence.

#### Scenario: Graph query

- **WHEN** a stage needs component relationships
- **THEN** the adapter SHALL execute only supported `query` or `path` operations against the configured graph file
- **AND** arbitrary shell arguments SHALL not be accepted

#### Scenario: Cross-repository relationship

- **WHEN** a relationship crosses repositories
- **THEN** repository-local Graphify paths SHALL be combined only with an explicit interface/dependency reference
- **AND** Graphify alone SHALL not assert a cross-repository runtime call

### Requirement: Current index evidence

The workspace registry SHALL report current GitNexus/Graphify readiness from live metadata.

#### Scenario: Missing or stale index

- **WHEN** an index is unavailable or behind repository HEAD
- **THEN** the affected validation SHALL be marked unavailable/stale
- **AND** the workflow SHALL follow its configured refresh, needs-human, or blocked policy

### Requirement: Read-only fallback

Fallback evidence SHALL remain bounded and shall not inflate confidence.

#### Scenario: Index unavailable

- **WHEN** policy permits bounded file fallback
- **THEN** approved read/search tools MAY collect file evidence inside repository roots
- **AND** the result SHALL remain lower-confidence than current symbol/graph evidence

### Requirement: Resilient external calls

Transient code-intelligence and Jira reads SHALL use bounded retry/circuit policy without retrying deterministic invalid input.

#### Scenario: Transient failure

- **WHEN** a call fails due to timeout, rate limit, or temporary service unavailability
- **THEN** it MAY retry with finite attempts and jitter
- **AND** final failure SHALL produce explicit unavailable evidence

#### Scenario: Invalid repository or query

- **WHEN** validation detects an invalid root, repository name, target, or argument
- **THEN** the call SHALL fail immediately
- **AND** no fallback shall bypass the policy
