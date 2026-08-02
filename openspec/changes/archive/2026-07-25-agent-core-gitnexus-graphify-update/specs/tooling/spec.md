## ADDED Requirements

### Requirement: GitNexus index reflects current codebase

The GitNexus index SHALL accurately reflect the current state of the agent-core repository.

#### Scenario: Index is fresh
- **WHEN** a developer runs `node .gitnexus/run.cjs status`
- **THEN** the status SHALL show "fresh" (not "stale")
- **AND** the indexed commit SHALL match the current HEAD commit

#### Scenario: Symbols and relationships are populated
- **WHEN** the GitNexus index is fresh
- **THEN** the symbol count SHALL be > 0
- **AND** the relationship count SHALL be > 0
- **AND** the process count SHALL be > 0

#### Scenario: Impact analysis works
- **WHEN** a developer runs impact analysis on a symbol
- **THEN** the analysis SHALL return accurate caller/callee information

### Requirement: Graphify knowledge graph exists

A Graphify knowledge graph SHALL exist for agent-core.

#### Scenario: Graphify output directory exists
- **WHEN** a developer runs `ls graphify-out/`
- **THEN** the directory SHALL contain:
  - `graph.json` (queryable graph)
  - `graph.html` (interactive visualization)
  - `GRAPH_REPORT.md` (analysis report)

#### Scenario: Graphify version is current
- **WHEN** a developer runs `graphify --version`
- **THEN** the version SHALL be >= 0.9.14

#### Scenario: Graphify is registered with Claude Code
- **WHEN** a developer runs `/graphify` in Claude Code
- **THEN** the skill SHALL be available and functional

### Requirement: Documentation references tools

AGENTS.md SHALL reference GitNexus and Graphify with current usage patterns.

#### Scenario: AGENTS.md includes GitNexus reference
- **WHEN** a developer reads AGENTS.md
- **THEN** GitNexus SHALL be referenced for symbol-level impact analysis
- **AND** re-index command SHALL be provided

#### Scenario: AGENTS.md includes Graphify reference
- **WHEN** a developer reads AGENTS.md
- **THEN** Graphify SHALL be referenced for concept-level exploration
- **AND** query/path/explain commands SHALL be provided
