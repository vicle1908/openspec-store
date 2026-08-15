## Purpose

Define code intelligence capabilities for docs-sync: source file parsing, GitNexus/Graphify graph queries, AST-based API extraction, and codebase scanning to determine which documentation is affected by code changes.

## Requirements

### Requirement: GitNexus indexing

The system SHALL index agent-docs-sync with gitnexus for symbol-level code intelligence.

#### Scenario: Initial indexing
- **WHEN** `npx gitnexus analyze` is run from the agent-docs-sync root
- **THEN** the system SHALL create `.gitnexus/` directory with gitnexus.json, meta.json, lbug, and run.cjs
- **AND** it SHALL parse all tracked Python source files
- **AND** it SHALL extract symbols, relationships, and execution flows
- **AND** `npx gitnexus status` SHALL report the index as current

#### Scenario: Index reflects project structure
- **WHEN** gitnexus indexing completes
- **THEN** the index SHALL contain entries for all public classes and functions in agents/, llm/, tools/, and workflows/
- **AND** it SHALL capture imports between sub-packages (e.g., cli.py importing from agents/, llm/)
- **AND** it SHALL identify the pipeline execution flow (detect_changes → analyze_impact → generate_updates → validate → report)

#### Scenario: Impact analysis works
- **WHEN** `gitnexus impact "CheckLinksTool" -d upstream -r agent-docs-sync` is run
- **THEN** the system SHALL return callers of CheckLinksTool
- **AND** it SHALL report risk level (LOW/MEDIUM/HIGH)
- **AND** it SHALL list affected processes

### Requirement: Graphify graph generation

The system SHALL generate an architecture-level knowledge graph for agent-docs-sync.

#### Scenario: Graph generation
- **WHEN** `graphify update .` is run from the agent-docs-sync root
- **THEN** the system SHALL create `graphify-out/graph.json` and `graphify-out/manifest.json`
- **AND** it SHALL create provider-managed cache state under `graphify-out/`
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
- **WHEN** `gitnexus query "doc generation" -r agent-docs-sync` is run
- **THEN** it SHALL return relevant symbols from the agent-docs-sync codebase
- **AND** results SHALL include the generation agent and related tools

#### Scenario: Graphify query
- **WHEN** `graphify query "documentation" --graph graphify-out/graph.json` is run
- **THEN** it SHALL return nodes related to documentation sync functionality
- **AND** results SHALL include workflow nodes and tool nodes

### Requirement: Workspace-managed index refresh

The system SHALL refresh GitNexus and Graphify through the reviewed workspace inventory rather than claiming an unbounded per-commit hook.

#### Scenario: Local post-merge dispatch
- **WHEN** a local merge or merge-based pull completes on the configured default branch
- **THEN** the managed post-merge block SHALL dispatch the central refresh script asynchronously
- **AND** it SHALL apply inventory, dirty-tree, lock, timeout, and revision checks
- **AND** it SHALL not block the merge or pull operation

#### Scenario: Scheduled refresh
- **WHEN** the LaunchAgent fires
- **THEN** it SHALL enumerate only approved inventory repositories
- **AND** it SHALL run GitNexus and Graphify independently for clean eligible repositories
- **AND** it SHALL report provider failures without modifying source files or credentials

#### Scenario: Hook and generated-state safety
- **WHEN** the central refresh or managed hook runs
- **THEN** it SHALL not run `git add` on generated files
- **AND** Graphify output SHALL use `graphify-out/`
- **AND** GitNexus state SHALL use `.gitnexus/`
- **AND** dirty repositories, active Graphify watchers, and non-default branches SHALL be skipped explicitly
