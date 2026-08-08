## Purpose

Define code intelligence capabilities for docs-sync: source file parsing, GitNexus/Graphify graph queries, AST-based API extraction, and codebase scanning to determine which documentation is affected by code changes.

## Requirements

### Requirement: GitNexus indexing

The system SHALL index agent-docs-sync with gitnexus for symbol-level code intelligence.

#### Scenario: Initial indexing
- **WHEN** `npx gitnexus analyze` is run from the agent-docs-sync root
- **THEN** the system SHALL create `.gitnexus/` directory with gitnexus.json, meta.json, lbug, and run.cjs
- **AND** it SHALL parse all 25 Python source files
- **AND** it SHALL extract symbols, relationships, and execution flows
- **AND** `npx gitnexus status` SHALL report the index as current

#### Scenario: Index reflects project structure
- **WHEN** gitnexus indexing completes
- **THEN** the index SHALL contain entries for all public classes and functions in agents/, llm/, tools/, and workflows/
- **AND** it SHALL capture imports between sub-packages (e.g., cli.py importing from agents/, llm/)
- **AND** it SHALL identify the pipeline execution flow (detect_changes → analyze_impact → generate_updates → validate → report)

#### Scenario: Impact analysis works
- **WHEN** `npx gitnexus impact "CheckLinksTool" -d upstream -r agent-docs-sync` is run
- **THEN** the system SHALL return callers of CheckLinksTool
- **AND** it SHALL report risk level (LOW/MEDIUM/HIGH)
- **AND** it SHALL list affected processes

### Requirement: Graphify graph generation

The system SHALL generate an architecture-level knowledge graph for agent-docs-sync.

#### Scenario: Graph generation
- **WHEN** `graphify update .` is run from the agent-docs-sync root
- **THEN** the system SHALL create `.graphify/graph.json` and `.graphify/manifest.json`
- **AND** it SHALL create `.graphify/cache/` for analysis caching
- **AND** the graph SHALL contain nodes for all modules, classes, and key functions

#### Scenario: Pipeline flow visible in graph
- **WHEN** the graph is generated
- **THEN** graphify query "sync pipeline" SHALL return the detect_changes → analyze_impact → generate_updates → validate → report flow
- **AND** graphify path "cli.py" "sync_pipeline.py" SHALL return a valid path
- **AND** graphify explain "CheckLinksTool" SHALL describe the tool and its connections

#### Scenario: Cross-package relationships
- **WHEN** the graph is generated
- **THEN** edges SHALL connect cli.py → workflows/sync_pipeline.py (CLI calls pipeline)
- **AND** edges SHALL connect workflows/sync_pipeline.py → agents/generation.py (pipeline uses agent)
- **AND** edges SHALL connect agents/generation.py → llm/model.py (agent uses the configured model)
- **AND** edges SHALL connect tools/ → workflows/ (tools used by pipeline steps)

### Requirement: Tool availability verification

Both gitnexus and graphify tools SHALL be queryable for agent-docs-sync after setup.

#### Scenario: GitNexus query
- **WHEN** `npx gitnexus query "doc generation" -r agent-docs-sync` is run
- **THEN** it SHALL return relevant symbols from the agent-docs-sync codebase
- **AND** results SHALL include the generation agent and related tools

#### Scenario: Graphify query
- **WHEN** `graphify query "documentation" --graph .graphify/graph.json` is run
- **THEN** it SHALL return nodes related to documentation sync functionality
- **AND** results SHALL include workflow nodes and tool nodes

### Requirement: Post-commit index refresh

The system SHALL refresh gitnexus and graphify indexes automatically after each git commit.

#### Scenario: Graphify incremental rebuild on commit
- **WHEN** a commit is made in agent-docs-sync
- **THEN** the graphify post-commit hook SHALL call `_rebuild_code()` for incremental AST-only rebuild
- **AND** it SHALL NOT run a full `graphify update` (incremental is faster and sufficient)
- **AND** the rebuild SHALL run in background via `nohup` + `disown` (non-blocking)

#### Scenario: GitNexus full re-index on commit
- **WHEN** a commit is made in agent-docs-sync
- **THEN** the gitnexus refresh section SHALL run `npx gitnexus analyze` in background
- **AND** it SHALL complete within 30 seconds for a 25-file repo
- **AND** it SHALL NOT block the commit prompt

#### Scenario: Hook handles missing tools gracefully
- **WHEN** gitnexus CLI is not available on PATH
- **THEN** the gitnexus refresh section SHALL print a warning and skip
- **AND** it SHALL NOT fail the commit
- **AND** the graphify refresh SHALL still run independently

#### Scenario: Hook is idempotent
- **WHEN** `graphify hook install` is run multiple times
- **THEN** it SHALL NOT duplicate hook sections (marker-based detection)
- **AND** re-running SHALL produce the same result as first install

#### Scenario: Hook does not commit generated files
- **WHEN** the hook generates .gitnexus/ and .graphify/ artifacts
- **THEN** these artifacts SHALL be in .gitignore
- **AND** the hook SHALL NOT run `git add` on generated files
- **AND** the working tree SHALL remain clean after hook completes
