## ADDED Requirements

### Requirement: Tier 1 code-existence evidence

Every claimed API, symbol, file, route, or execution flow SHALL have current repository evidence before it is marked verified.

#### Scenario: Symbol or caller claim

- **WHEN** an artifact references a class, function, method, or caller
- **THEN** the harness SHALL use GitNexus MCP `context`, `query`, or `impact` as appropriate
- **AND** it SHALL record repository, index commit, symbol UID when available, tool/query, and evidence timestamp

#### Scenario: Structural relationship

- **WHEN** an artifact claims a path or component relationship
- **THEN** the harness SHALL use Graphify query/path evidence from the selected repository graph
- **AND** it SHALL record the graph source and freshness

#### Scenario: File claim

- **WHEN** an artifact references a file
- **THEN** a bounded read-only file check SHALL resolve inside a configured repository root
- **AND** a missing or escaped path SHALL fail validation

### Requirement: Index freshness affects confidence

Missing or stale indexes SHALL produce an explicit incomplete-evidence result.

#### Scenario: Stale GitNexus index

- **WHEN** the indexed commit differs from repository HEAD
- **THEN** the evidence SHALL be marked stale
- **AND** HIGH/CRITICAL impact claims SHALL not be treated as verified until the index is refreshed

#### Scenario: Missing Graphify graph

- **WHEN** no usable graph exists
- **THEN** structural validation SHALL be marked unavailable
- **AND** the model SHALL not infer a verified path

### Requirement: Tier 2 semantic validation

Schema-valid artifacts SHALL be checked against evidenced repository conventions and patterns.

#### Scenario: Pattern comparison

- **WHEN** a design or API artifact proposes a pattern
- **THEN** the validator SHALL compare it with retrieved current examples
- **AND** deviations SHALL cite evidence and require revision or human disposition

### Requirement: Tier 3 cross-artifact validation

Downstream artifacts SHALL cover the accepted requirements and upstream decisions.

#### Scenario: Requirement coverage

- **WHEN** design, API, implementation, or test artifacts are produced
- **THEN** each accepted requirement SHALL map to the relevant downstream entries
- **AND** missing mappings SHALL fail structural validation

#### Scenario: Test-plan coverage

- **WHEN** the test plan is produced
- **THEN** every acceptance criterion SHALL have at least one planned test
- **AND** each planned test SHALL reference its criterion

### Requirement: Bounded validation recovery

Validation failures SHALL use bounded revision flow rather than blind retries or fabricated fallback evidence.

#### Scenario: Correctable failure

- **WHEN** a validation failure includes actionable evidence
- **THEN** the graph MAY route to the producing stage with that evidence
- **AND** revision count SHALL not exceed the configured maximum

#### Scenario: Revision limit reached

- **WHEN** the revision limit is exhausted
- **THEN** the workflow SHALL enter `needs_human` or `blocked`
- **AND** it SHALL not synthesize a passing result
