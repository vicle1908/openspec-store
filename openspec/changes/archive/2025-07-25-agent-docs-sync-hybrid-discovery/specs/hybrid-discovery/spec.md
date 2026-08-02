## ADDED Requirements

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

#### Scenario: Skill file detected
- **WHEN** a `.agents/skills/*/SKILL.md` file exists
- **THEN** the discovery engine detects the skill via file system scan
- **AND** maps it to `reference/skills.md`
- **AND** classifies it as `reference` quadrant

### Requirement: Leverage gitnexus structural analysis
The system SHALL use gitnexus file hashes (ast_hash) to detect structural changes in source code.

#### Scenario: AST structure changed
- **WHEN** a source file's ast_hash changes between gitnexus indexes
- **THEN** the discovery engine marks the file as structurally changed
- **AND** triggers documentation re-evaluation for that file

#### Scenario: Only cosmetic change
- **WHEN** a source file's mtime changes but ast_hash remains the same
- **THEN** the discovery engine skips documentation re-evaluation
- **AND** does not update the mapping

### Requirement: Leverage graphify community detection
The system SHALL use graphify communities to identify functional areas and map them to documentation targets.

#### Scenario: Community detected
- **WHEN** graphify identifies a community (e.g., "cli.py", "Hooks", "Tools")
- **THEN** the discovery engine maps the community to a documentation target
- **AND** assigns a Diátaxis quadrant based on community characteristics

#### Scenario: God node identified
- **WHEN** graphify identifies a node with high edge count (>= 10 edges)
- **THEN** the discovery engine marks it as a core abstraction
- **AND** prioritizes it for documentation (Tier 1 or Tier 2)

#### Scenario: Isolated node detected
- **WHEN** graphify identifies a node with <= 1 connection
- **THEN** the discovery engine marks it as a documentation gap
- **AND** adds it to the recommended documentation targets

### Requirement: Support multi-language source code
The system SHALL discover documentation needs for Python, Swift, Kotlin, TypeScript, Go, and Rust source files.

#### Scenario: Python source file
- **WHEN** a `.py` file is detected
- **THEN** the system uses gitnexus tree-sitter or AST parsing to extract symbols
- **AND** maps to reference documentation

#### Scenario: Swift source file
- **WHEN** a `.swift` file is detected
- **THEN** the system uses gitnexus tree-sitter to extract symbols
- **AND** maps to reference documentation

#### Scenario: Unsupported language
- **WHEN** a source file is in an unsupported language (e.g., Zig)
- **THEN** the system uses LLM extraction as fallback
- **AND** extracts functions, classes, and docstrings
- **AND** maps to reference documentation

### Requirement: Support multi-platform deployment artifacts
The system SHALL detect and map deployment artifacts for Docker, launchd, systemd, GitHub Actions, GitLab CI, Procfile, Vercel, and Netlify.

#### Scenario: Docker deployment
- **WHEN** Dockerfile or docker-compose.yaml exists
- **THEN** the system maps to `how-to/deployment-docker.md`

#### Scenario: macOS launchd
- **WHEN** a `.plist` file exists in a launchd directory
- **THEN** the system maps to `how-to/deployment-launchd.md`

#### Scenario: GitHub Actions CI
- **WHEN** `.github/workflows/*.yml` files exist
- **THEN** the system maps to `how-to/ci-cd-github.md`

### Requirement: Generate auto_mapping in state file
The system SHALL generate an `auto_mapping` section in `.docs-sync-state.yaml` that replaces manual `doc-mapping.yaml`.

#### Scenario: Auto-mapping generated
- **WHEN** discovery completes
- **THEN** the state file contains `auto_mapping` with source→doc mappings
- **AND** each mapping includes `target`, `quadrant`, `confidence`, and `source` fields

#### Scenario: Fallback to doc-mapping.yaml
- **WHEN** gitnexus/graphify are not available
- **THEN** the system falls back to `doc-mapping.yaml` if it exists
- **AND** logs a warning that auto-discovery is degraded

### Requirement: Implement ScannerTool following BaseTool interface
The system SHALL provide a ScannerTool that implements the agent-core BaseTool interface for detecting deployment artifacts, config files, and skills via file system scanning.

#### Scenario: ScannerArgs schema
- **WHEN** ScannerTool is instantiated
- **THEN** the tool has args_schema = ScannerArgs(BaseModel) with repo_root: str field

#### Scenario: ScannerTool metadata
- **WHEN** ScannerTool.metadata is accessed
- **THEN** the tool returns ToolMetadata(name="scanner", description="...", source="local")

#### Scenario: ScannerTool detects Docker artifacts
- **WHEN** ScannerTool.execute() is called with ScannerArgs(repo_root="/path/to/repo")
- **THEN** the tool scans for Dockerfile, docker-compose.yaml, .dockerignore
- **AND** returns ToolResult(success=True, output={dockerfile: bool, compose: bool, ...})

#### Scenario: ScannerTool detects skill files
- **WHEN** ScannerTool.execute() is called with ScannerArgs(repo_root="/path/to/repo")
- **THEN** the tool scans for .agents/skills/*/SKILL.md
- **AND** returns ToolResult(success=True, output={skills: [{path: str, name: str}]})

#### Scenario: ScannerTool handles missing directory
- **WHEN** ScannerTool.execute() is called with non-existent repo_root
- **THEN** the tool returns ToolResult(success=False, error="Path not found: ...")

### Requirement: Implement GitNexusLoaderTool following BaseTool interface
The system SHALL provide a GitNexusLoaderTool that loads gitnexus.json for file hash tracking and structural change detection.

#### Scenario: GitNexusLoaderArgs schema
- **WHEN** GitNexusLoaderTool is instantiated
- **THEN** the tool has args_schema = GitNexusLoaderArgs(BaseModel) with repo_root: str field

#### Scenario: GitNexusLoaderTool metadata
- **WHEN** GitNexusLoaderTool.metadata is accessed
- **THEN** the tool returns ToolMetadata(name="gitnexus_loader", description="...", source="local")

#### Scenario: GitNexusLoaderTool loads index
- **WHEN** GitNexusLoaderTool.execute() is called with GitNexusLoaderArgs(repo_root="/path/to/repo")
- **THEN** the tool reads .gitnexus/gitnexus.json
- **AND** returns ToolResult(success=True, output={file_hashes: dict, meta: dict})

#### Scenario: GitNexusLoaderTool detects index missing
- **WHEN** GitNexusLoaderTool.execute() is called on repo without gitnexus index
- **THEN** the tool returns ToolResult(success=False, error="GitNexus index not found")

#### Scenario: GitNexusLoaderTool detects structural changes
- **WHEN** GitNexusLoaderTool.compare_hashes() is called with old/new file_hashes
- **THEN** the tool returns list of files where ast_hash changed (structural) vs mtime only (cosmetic)

### Requirement: Implement GraphifyLoaderTool following BaseTool interface
The system SHALL provide a GraphifyLoaderTool that loads graphify manifest.json for community detection and gap analysis.

#### Scenario: GraphifyLoaderArgs schema
- **WHEN** GraphifyLoaderTool is instantiated
- **THEN** the tool has args_schema = GraphifyLoaderArgs(BaseModel) with repo_root: str field

#### Scenario: GraphifyLoaderTool metadata
- **WHEN** GraphifyLoaderTool.metadata is accessed
- **THEN** the tool returns ToolMetadata(name="graphify_loader", description="...", source="local")

#### Scenario: GraphifyLoaderTool loads manifest
- **WHEN** GraphifyLoaderTool.execute() is called with GraphifyLoaderArgs(repo_root="/path/to/repo")
- **THEN** the tool reads graphify-out/manifest.json
- **AND** returns ToolResult(success=True, output={stats: dict, capabilities: dict})

#### Scenario: GraphifyLoaderTool identifies god nodes
- **WHEN** GraphifyLoaderTool.execute() is called with repo_root
- **THEN** the tool reads GRAPH_REPORT.md and extracts god_nodes section
- **AND** returns list of nodes with edge counts >= 10

#### Scenario: GraphifyLoaderTool identifies isolated nodes
- **WHEN** GraphifyLoaderTool.execute() is called with repo_root
- **THEN** the tool reads GRAPH_REPORT.md and extracts knowledge_gaps section
- **AND** returns list of isolated nodes with <= 1 connection

### Requirement: Implement ClassifierTool following BaseTool interface
The system SHALL provide a ClassifierTool that implements rule-based Diátaxis classification without LLM dependency.

#### Scenario: ClassifierArgs schema
- **WHEN** ClassifierTool is instantiated
- **THEN** the tool has args_schema = ClassifierArgs(BaseModel) with file_path: str, content: str | None, artifact_type: str | None fields

#### Scenario: ClassifierTool metadata
- **WHEN** ClassifierTool.metadata is accessed
- **THEN** the tool returns ToolMetadata(name="classifier", description="...", source="local")

#### Scenario: ClassifierTool classifies by file location
- **WHEN** ClassifierTool.execute() is called with file_path="examples/getting-started.py"
- **THEN** the tool returns ToolResult(success=True, output={quadrant: "tutorial", confidence: 0.9, source: "location_heuristic"})

#### Scenario: ClassifierTool classifies by file name
- **WHEN** ClassifierTool.execute() is called with file_path="README.md"
- **THEN** the tool returns ToolResult(success=True, output={quadrant: "tutorial", confidence: 0.85, source: "name_heuristic"})

#### Scenario: ClassifierTool detects ambiguity
- **WHEN** ClassifierTool.execute() is called with ambiguous file (config that could be reference or how-to)
- **THEN** the tool returns ToolResult(success=True, output={quadrant: "reference", confidence: 0.6, needs_llm: true})

### Requirement: Implement EnforcerTool following BaseTool interface
The system SHALL provide an EnforcerTool that validates documents against Diátaxis rules with configurable thresholds.

#### Scenario: EnforcerArgs schema
- **WHEN** EnforcerTool is instantiated
- **THEN** the tool has args_schema = EnforcerArgs(BaseModel) with doc_path: str, quadrant: str, tier: int | None fields

#### Scenario: EnforcerTool metadata
- **WHEN** EnforcerTool.metadata is accessed
- **THEN** the tool returns ToolMetadata(name="enforcer", description="...", source="local")

#### Scenario: EnforcerTool validates tutorial
- **WHEN** EnforcerTool.execute() is called with doc_path="docs/tutorials/getting-started.md", quadrant="tutorial"
- **THEN** the tool checks required sections (prerequisites, steps, what_you_learned)
- **AND** returns ToolResult(success=True, output={valid: bool, violations: list, warnings: list, score: float})

#### Scenario: EnforcerTool enforces forbidden elements
- **WHEN** EnforcerTool.execute() is called with tutorial containing API signatures
- **THEN** the tool returns ToolResult(success=True, output={valid: false, violations: ["Forbidden element: api_signatures"]})

#### Scenario: EnforcerTool adjusts thresholds by tier
- **WHEN** EnforcerTool.execute() is called with tier=1 (CRITICAL)
- **THEN** the tool uses 80% required sections threshold (stricter)

### Requirement: Implement StateTool following BaseTool interface
The system SHALL provide a StateTool that manages .docs-sync-state.yaml load/save operations with cache invalidation.

#### Scenario: StateArgs schema
- **WHEN** StateTool is instantiated
- **THEN** the tool has args_schema = StateArgs(BaseModel) with repo_root: str, action: str (load|save|check_stale), state: dict | None fields

#### Scenario: StateTool metadata
- **WHEN** StateTool.metadata is accessed
- **THEN** the tool returns ToolMetadata(name="state", description="...", source="local")

#### Scenario: StateTool loads existing state
- **WHEN** StateTool.execute() is called with action="load" and repo_root
- **THEN** the tool reads .docs-sync-state.yaml if it exists
- **AND** returns ToolResult(success=True, output={state: dict})

#### Scenario: StateTool saves state
- **WHEN** StateTool.execute() is called with action="save", repo_root, and state dict
- **THEN** the tool writes .docs-sync-state.yaml atomically (write to temp, then rename)
- **AND** returns ToolResult(success=True, output={bytes_written: int})

#### Scenario: StateTool checks staleness
- **WHEN** StateTool.execute() is called with action="check_stale" and repo_root
- **THEN** the tool compares current git commit and gitnexus/graphify timestamps with state
- **AND** returns ToolResult(success=True, output={is_stale: bool, reasons: list})

### Requirement: Implement DiscoveryAgent using agent-core BaseAgent pattern
The system SHALL provide a DiscoveryAgent that composes tools using agent-core's BaseAgent with Flavor and ToolRegistry.

#### Scenario: DiscoveryAgent instantiation with BaseAgent
- **WHEN** DiscoveryAgent is instantiated
- **THEN** the agent uses BaseAgent(name="discovery-agent", gateway=gateway, tool_registry=registry, flavors=[discovery_flavor])
- **AND** registers ScannerTool, GitNexusLoaderTool, GraphifyLoaderTool, ClassifierTool, StateTool in ToolRegistry

#### Scenario: DiscoveryAgent flavor definition
- **WHEN** discovery_flavor is defined
- **THEN** the flavor uses Flavor(name="discovery", prompts=[FlavorPrompt(content="...", position="prepend")], tool_policy=FlavorToolPolicy(allow=["scanner", "gitnexus_loader", "graphify_loader", "classifier", "state"]))

#### Scenario: DiscoveryAgent runs full discovery
- **WHEN** DiscoveryAgent.run() is called with "Discover documentation needs for this repository"
- **THEN** the agent executes: check_stale → (scan || gitnexus || graphify) → classify → save
- **AND** returns AgentResult with auto_mapping, diataxis coverage, and doc_gaps

#### Scenario: DiscoveryAgent skips when cache fresh
- **WHEN** DiscoveryAgent.run() is called and state is not stale
- **THEN** the agent returns cached state without re-scanning
- **AND** logs "Cache fresh, skipping discovery"

#### Scenario: DiscoveryAgent handles partial failures
- **WHEN** GitNexusLoaderTool fails but GraphifyLoaderTool succeeds
- **THEN** the agent continues with available data
- **AND** logs warning "GitNexus unavailable, using file scan only"

### Requirement: Implement ValidationAgent using agent-core BaseAgent pattern
The system SHALL provide a ValidationAgent that composes tools using agent-core's BaseAgent with Flavor and ToolRegistry.

#### Scenario: ValidationAgent instantiation with BaseAgent
- **WHEN** ValidationAgent is instantiated
- **THEN** the agent uses BaseAgent(name="validation-agent", tool_registry=registry, flavors=[validator_flavor])
- **AND** registers EnforcerTool, CheckLinksTool, ReadDocTool in ToolRegistry

#### Scenario: ValidationAgent flavor definition
- **WHEN** validator_flavor is defined
- **THEN** the flavor uses Flavor(name="validator", prompts=[FlavorPrompt(content="...", position="prepend")], tool_policy=FlavorToolPolicy(allow=["enforcer", "check_links", "read_doc"]))

#### Scenario: ValidationAgent validates single doc
- **WHEN** ValidationAgent.run() is called with "Validate docs/tutorials/getting-started.md as tutorial"
- **THEN** the agent reads doc, enforces Diátaxis rules, checks links
- **AND** returns AgentResult with validation report (valid, violations, warnings, score)

#### Scenario: ValidationAgent validates directory
- **WHEN** ValidationAgent.run() is called with "Validate all docs in docs/"
- **THEN** the agent validates all .md files in directory
- **AND** returns aggregate report with per-file results and overall score

### Requirement: Implement DiscoveryPipeline using agent-core WorkflowBuilder pattern
The system SHALL provide a DiscoveryPipeline workflow that orchestrates DiscoveryAgent and ValidationAgent using agent-core's WorkflowBuilder with NodeDescriptor and EdgeDescriptor.

#### Scenario: WorkflowBuilder instantiation
- **WHEN** DiscoveryPipeline is created
- **THEN** the workflow uses WorkflowBuilder(name="discovery-pipeline")
- **AND** defines nodes using NodeDescriptor(name="...", kind=NodeKind.TOOL|AGENT)

#### Scenario: Workflow node definitions
- **WHEN** DiscoveryPipeline defines nodes
- **THEN** the workflow includes:
  - check_stale (NodeKind.TOOL)
  - scan_parallel (NodeKind.SUBGRAPH with parallel execution)
  - classify (NodeKind.TOOL)
  - save (NodeKind.TOOL)
  - validate (NodeKind.AGENT)
  - report (NodeKind.TOOL)

#### Scenario: Workflow edge definitions
- **WHEN** DiscoveryPipeline defines edges
- **THEN** the workflow uses EdgeDescriptor(source="...", target="...", condition=EdgeCondition.ALWAYS|ON_SUCCESS)
- **AND** defines: check_stale → scan_parallel (ON_SUCCESS), scan_parallel → classify (ALWAYS), classify → save (ALWAYS), save → validate (ALWAYS), validate → report (ALWAYS)

#### Scenario: Workflow executes discovery pipeline
- **WHEN** DiscoveryPipeline.execute() is called with repo_root
- **THEN** the workflow runs: check_stale → scan (parallel) → classify → save → validate → report
- **AND** returns WorkflowResult with final state

#### Scenario: Workflow handles agent failure
- **WHEN** DiscoveryAgent fails during workflow execution
- **THEN** the workflow retries up to 3 times with exponential backoff
- **AND** returns WorkflowResult with error if all retries fail

#### Scenario: Workflow enables parallel scanning
- **WHEN** DiscoveryPipeline.execute() runs scan step
- **THEN** GitNexusLoaderTool, GraphifyLoaderTool, and ScannerTool execute concurrently in SUBGRAPH node
- **AND** results are merged before classify step
