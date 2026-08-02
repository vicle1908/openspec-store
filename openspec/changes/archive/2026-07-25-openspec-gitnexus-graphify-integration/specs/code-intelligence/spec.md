## ADDED Requirements

### Requirement: OpenSpec apply includes impact analysis

The openspec-apply-change skill SHALL run GitNexus impact analysis before each code change.

#### Scenario: Impact analysis before code change
- **WHEN** a developer is about to edit a function, class, or method
- **THEN** the skill SHALL run `impact({target: "symbolName", direction: "upstream"})`
- **AND** if impact returns HIGH or CRITICAL, the skill SHALL pause and report to the user
- **AND** the skill SHALL NOT proceed with the edit until user confirms

#### Scenario: Impact analysis skipped for non-code files
- **WHEN** a developer is editing documentation, config, or test files
- **THEN** the skill SHALL skip impact analysis
- **AND** proceed with the edit directly

### Requirement: OpenSpec apply includes change detection

The openspec-apply-change skill SHALL run GitNexus detect_changes after each code change.

#### Scenario: Change detection after code change
- **WHEN** a developer has completed a code edit
- **THEN** the skill SHALL run `detect_changes()` to verify scope
- **AND** if unexpected symbols are affected, the skill SHALL report to the user
- **AND** the skill SHALL verify scope matches design artifacts

### Requirement: OpenSpec explore includes code intelligence

The openspec-explore skill SHALL integrate GitNexus and Graphify for code exploration.

#### Scenario: Code exploration with GitNexus
- **WHEN** a developer is exploring codebase
- **THEN** the skill SHALL use GitNexus `query` and `context` tools
- **AND** reference gitnexus-exploring skill for workflow

#### Scenario: Architecture exploration with Graphify
- **WHEN** a developer is exploring architecture
- **THEN** the skill SHALL use Graphify `query`, `path`, and `explain` tools
- **AND** reference graphify skill for workflow

### Requirement: OpenSpec propose includes blast radius

The openspec-propose skill SHALL include GitNexus impact analysis in proposals.

#### Scenario: Blast radius in proposal
- **WHEN** a developer proposes a change affecting code symbols
- **THEN** the skill SHALL run impact analysis on affected symbols
- **AND** include blast radius assessment in the proposal
- **AND** assess risk level (LOW/MEDIUM/HIGH/CRITICAL)

### Requirement: OpenSpec verify includes scope verification

The openspec-verify-change skill SHALL use GitNexus detect_changes for scope verification.

#### Scenario: Scope verification
- **WHEN** a developer verifies implementation
- **THEN** the skill SHALL run `detect_changes()` to verify scope
- **AND** compare affected symbols with design artifacts
- **AND** verify no scope creep
