# Hybrid Discovery

## Purpose

Auto-discover documentation needs by combining gitnexus structural analysis, graphify community detection, and file system scanning, replacing manual `doc-mapping.yaml` configuration.

## Requirements

### Requirement: Auto-discover source-to-documentation mappings
The system SHALL automatically discover which source files need documentation and map them to appropriate documentation targets without manual configuration.

#### Scenario: New Python file added
- **WHEN** a new `.py` file is added to the repository
- **THEN** the discovery engine detects the file via gitnexus ast_hash change
- **AND** maps it to the appropriate documentation target based on community classification
- **AND** stores the mapping in `.docs-sync-state.yaml`

#### Scenario: Deployment artifact detected
- **WHEN** a Dockerfile or docker-compose.yaml is present in the repository
- **THEN** the discovery engine detects the artifact via file system scan
- **AND** maps it to `how-to/deployment-docker.md`
- **AND** classifies it as `how-to` quadrant

### Requirement: Leverage gitnexus structural analysis
The system SHALL use gitnexus file hashes (ast_hash) to detect structural changes in source code.

#### Scenario: AST structure changed
- **WHEN** a source file's ast_hash changes between gitnexus indexes
- **THEN** the discovery engine marks the file as structurally changed
- **AND** triggers documentation re-evaluation for that file

### Requirement: Leverage graphify community detection
The system SHALL use graphify communities to identify functional areas and map them to documentation targets.

#### Scenario: God node identified
- **WHEN** graphify identifies a node with high edge count (>= 10 edges)
- **THEN** the discovery engine marks it as a core abstraction
- **AND** prioritizes it for documentation (Tier 1 or Tier 2)

### Requirement: Support multi-language source code
The system SHALL discover documentation needs for Python, Swift, Kotlin, TypeScript, Go, and Rust source files.

#### Scenario: Python source file
- **WHEN** a `.py` file is detected
- **THEN** the system uses gitnexus tree-sitter or AST parsing to extract symbols
- **AND** maps to reference documentation

### Requirement: Support multi-platform deployment artifacts
The system SHALL detect and map deployment artifacts for Docker, launchd, systemd, GitHub Actions, GitLab CI, Procfile, Vercel, and Netlify.

#### Scenario: Docker deployment
- **WHEN** Dockerfile or docker-compose.yaml exists
- **THEN** the system maps to `how-to/deployment-docker.md`

### Requirement: Use agent-core planning for LLM classification
The system SHALL use agent-core's planning capability to decompose complex classification tasks.

#### Scenario: Planning guidance configured
- **WHEN** planning.guidance is set in config.yaml
- **THEN** the DiscoveryAgent uses planning to decompose classification tasks
- **AND** caches plans for cache_ttl duration

### Requirement: Use agent-core subagents for delegated tasks
The system SHALL use agent-core's subagents to delegate specialized tasks.

#### Scenario: Validation delegation
- **WHEN** DiscoveryAgent needs to validate a document
- **THEN** it delegates to a validator subagent
- **AND** subagent inherits parent tools

### Requirement: Use agent-core guardrails for input validation
The system SHALL use agent-core's guardrails to validate inputs before execution.

#### Scenario: Path validation
- **WHEN** a tool execution is requested
- **THEN** the guardrail validates the path is within allowed directories
- **AND** blocks execution if path is invalid

### Requirement: Generate auto_mapping in state file
The system SHALL generate an `auto_mapping` section in `.docs-sync-state.yaml` that replaces manual `doc-mapping.yaml`.

#### Scenario: Auto-mapping generated
- **WHEN** discovery completes
- **THEN** the state file contains `auto_mapping` with source→doc mappings
- **AND** each mapping includes `target`, `quadrant`, `confidence`, and `source` fields

### Requirement: Implement ScannerTool following BaseTool interface
The system SHALL provide a ScannerTool that implements the agent-core BaseTool interface for detecting deployment artifacts, config files, and skills via file system scanning.

#### Scenario: ScannerTool detects Docker artifacts
- **WHEN** ScannerTool.execute() is called with ScannerArgs(repo_root="/path/to/repo")
- **THEN** the tool scans for Dockerfile, docker-compose.yaml, .dockerignore
- **AND** returns ToolResult(success=True, output={dockerfile: bool, compose: bool, ...})

### Requirement: Implement GitNexusLoaderTool following BaseTool interface
The system SHALL provide a GitNexusLoaderTool that loads gitnexus.json for file hash tracking and structural change detection.

#### Scenario: GitNexusLoaderTool loads index
- **WHEN** GitNexusLoaderTool.execute() is called with GitNexusLoaderArgs(repo_root="/path/to/repo")
- **THEN** the tool reads .gitnexus/gitnexus.json
- **AND** returns ToolResult(success=True, output={file_hashes: dict, meta: dict})

### Requirement: Implement GraphifyLoaderTool following BaseTool interface
The system SHALL provide a GraphifyLoaderTool that loads graphify manifest.json for community detection and gap analysis.

#### Scenario: GraphifyLoaderTool loads manifest
- **WHEN** GraphifyLoaderTool.execute() is called with GraphifyLoaderArgs(repo_root="/path/to/repo")
- **THEN** the tool reads graphify-out/graph.json
- **AND** returns ToolResult(success=True, output={stats: dict, god_nodes: list})

### Requirement: Implement ClassifierTool following BaseTool interface
The system SHALL provide a ClassifierTool that implements rule-based Diátaxis classification without LLM dependency.

#### Scenario: ClassifierTool classifies by file location
- **WHEN** ClassifierTool.execute() is called with file_path="examples/getting-started.py"
- **THEN** the tool returns ToolResult(success=True, output={quadrant: "tutorial", confidence: 0.9, source: "location_heuristic"})

### Requirement: Implement EnforcerTool following BaseTool interface
The system SHALL provide an EnforcerTool that validates documents against Diátaxis rules with configurable thresholds.

#### Scenario: EnforcerTool validates tutorial
- **WHEN** EnforcerTool.execute() is called with doc_path="docs/tutorials/getting-started.md", quadrant="tutorial"
- **THEN** the tool checks required sections (prerequisites, steps, what_you_learned)
- **AND** returns ToolResult(success=True, output={valid: bool, violations: list, warnings: list, score: float})

### Requirement: Implement StateTool following BaseTool interface
The system SHALL provide a StateTool that manages .docs-sync-state.yaml load/save operations with cache invalidation.

#### Scenario: StateTool saves state
- **WHEN** StateTool.execute() is called with action="save", repo_root, and state dict
- **THEN** the tool writes .docs-sync-state.yaml atomically (write to temp, then rename)
- **AND** returns ToolResult(success=True, output={bytes_written: int})

### Requirement: Implement DiscoveryAgent using agent-core BaseAgent pattern
The system SHALL provide a DiscoveryAgent that composes tools using agent-core's BaseAgent with Flavor and ToolRegistry.

#### Scenario: DiscoveryAgent runs full discovery
- **WHEN** DiscoveryAgent.run() is called with "Discover documentation needs for this repository"
- **THEN** the agent executes: check_stale → (scan || gitnexus || graphify) → classify → save
- **AND** returns AgentResult with auto_mapping, diataxis coverage, and doc_gaps

### Requirement: Implement ValidationAgent using agent-core BaseAgent pattern
The system SHALL provide a ValidationAgent that composes tools using agent-core's BaseAgent with Flavor and ToolRegistry.

#### Scenario: ValidationAgent validates single doc
- **WHEN** ValidationAgent.run() is called with "Validate docs/tutorials/getting-started.md as tutorial"
- **THEN** the agent reads doc, enforces Diátaxis rules, checks links
- **AND** returns AgentResult with validation report (valid, violations, warnings, score)

### Requirement: Implement DiscoveryPipeline using agent-core WorkflowBuilder pattern
The system SHALL provide a DiscoveryPipeline workflow that orchestrates DiscoveryAgent and ValidationAgent using agent-core's WorkflowBuilder with NodeDescriptor and EdgeDescriptor.

#### Scenario: Workflow executes discovery pipeline
- **WHEN** DiscoveryPipeline.execute() is called with repo_root
- **THEN** the workflow runs: check_stale → scan (parallel) → classify → save → validate → report
- **AND** returns WorkflowResult with final state
