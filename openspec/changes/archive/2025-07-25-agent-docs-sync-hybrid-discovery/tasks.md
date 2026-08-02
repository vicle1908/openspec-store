# Tasks — agent-docs-sync-hybrid-discovery

## 1. Discovery Tools (Reusable, Deterministic)

- [x] 1.1 Create `src/agent_docs_sync/tools/scanner.py` — ScannerTool with ScannerArgs(BaseModel) and ToolMetadata(name="scanner", source="local")
- [x] 1.2 Create `src/agent_docs_sync/tools/gitnexus_loader.py` — GitNexusLoaderTool with GitNexusLoaderArgs and compare_hashes() method
- [x] 1.3 Create `src/agent_docs_sync/tools/graphify_loader.py` — GraphifyLoaderTool with GRAPH_REPORT.md parsing
- [x] 1.4 Create `src/agent_docs_sync/tools/classifier.py` — ClassifierTool with CLASSIFICATION_RULES dict and location/name/content heuristics
- [x] 1.5 Create `src/agent_docs_sync/tools/enforcer.py` — EnforcerTool with ENFORCEMENT_RULES dict and tier-based thresholds
- [x] 1.6 Create `src/agent_docs_sync/tools/state.py` — StateTool with atomic writes and dual-key cache invalidation
- [x] 1.7 Update `src/agent_docs_sync/tools/__init__.py` to export ScannerTool, GitNexusLoaderTool, GraphifyLoaderTool, ClassifierTool, EnforcerTool, StateTool
- [x] 1.8 Write unit tests for ScannerTool (test Dockerfile, compose, skills detection, missing directory)
- [x] 1.9 Write unit tests for GitNexusLoaderTool (test hash loading, structural change detection, missing index)
- [x] 1.10 Write unit tests for GraphifyLoaderTool (test manifest loading, god node parsing, isolated node parsing)
- [x] 1.11 Write unit tests for ClassifierTool (test location heuristic, name heuristic, ambiguity detection)
- [x] 1.12 Write unit tests for EnforcerTool (test required sections, max words, forbidden elements, tier thresholds)
- [x] 1.13 Write unit tests for StateTool (test load/save, atomic writes, staleness check, history preservation)

## 2. Discovery Agents (Compose Tools + Optional LLM)

- [x] 2.1 Create `src/agent_docs_sync/agents/discovery.py` — DiscoveryAgent using BaseAgent(name="discovery-agent", gateway=gateway, tool_registry=registry, flavors=[discovery_flavor])
- [x] 2.2 Create `src/agent_docs_sync/agents/validation.py` — ValidationAgent using BaseAgent(name="validation-agent", tool_registry=registry, flavors=[validator_flavor])
- [x] 2.3 Add discovery_flavor to flavors.py with Flavor(name="discovery", prompts=[FlavorPrompt(content="...", position="prepend")], tool_policy=FlavorToolPolicy(allow=["scanner", "gitnexus_loader", "graphify_loader", "classifier", "state"]))
- [x] 2.4 Add validator_flavor to flavors.py with Flavor(name="validator", prompts=[FlavorPrompt(content="...", position="prepend")], tool_policy=FlavorToolPolicy(allow=["enforcer", "check_links", "read_doc"]))
- [x] 2.5 Update `src/agent_docs_sync/agents/__init__.py` to export DiscoveryAgent, ValidationAgent
- [x] 2.6 Write integration tests for DiscoveryAgent (test full discovery flow with mocked tools, cache fresh scenario, partial failure)
- [x] 2.7 Write integration tests for ValidationAgent (test single doc validation, directory validation, aggregate report)

## 3. Discovery Workflow (DAG Orchestration)

- [x] 3.1 Create `src/agent_docs_sync/workflows/discovery_pipeline.py` — DiscoveryPipeline using WorkflowBuilder(name="discovery-pipeline")
- [x] 3.2 Define DAG nodes: check_stale (NodeKind.TOOL), scan_parallel (NodeKind.SUBGRAPH), classify (NodeKind.TOOL), save (NodeKind.TOOL), validate (NodeKind.AGENT), report (NodeKind.TOOL)
- [x] 3.3 Define DAG edges: check_stale → scan_parallel (EdgeCondition.ON_SUCCESS), scan_parallel → classify (EdgeCondition.ALWAYS), classify → save (EdgeCondition.ALWAYS), save → validate (EdgeCondition.ALWAYS), validate → report (EdgeCondition.ALWAYS)
- [x] 3.4 Implement scan_parallel SUBGRAPH with GitNexusLoaderTool, GraphifyLoaderTool, ScannerTool executing concurrently using parallel()
- [x] 3.5 Implement error handling with retry_max=3 and exponential backoff for tool failures
- [x] 3.6 Update `src/agent_docs_sync/workflows/__init__.py` to export DiscoveryPipeline
- [x] 3.7 Write workflow integration tests (test DAG execution, parallel scanning, error handling)

## 4. Override System

- [x] 4.1 Implement StateTool.load_overrides() with multi-level resolution (repo → ecosystem → global)
- [x] 4.2 Implement StateTool.apply_quadrant_overrides() to change classifications
- [x] 4.3 Implement StateTool.apply_mapping_overrides() to add/replace mapping entries
- [x] 4.4 Implement StateTool.apply_exclusion_overrides() to remove excluded paths
- [x] 4.5 Implement StateTool.apply_inclusion_overrides() to force-include files
- [x] 4.6 Implement StateTool.apply_priority_overrides() for primary/secondary quadrants
- [x] 4.7 Implement StateTool.detect_override_conflicts() to log auto vs override differences
- [x] 4.8 Add `.docs-sync-overrides.yaml` to `.gitignore`
- [x] 4.9 Write unit tests for override resolution (test multi-level loading, conflict detection, each override type)

## 5. Diátaxis Enforcement

- [x] 5.1 Define ENFORCEMENT_RULES in EnforcerTool with required_sections, max_words, forbidden_elements, must_have per quadrant
- [x] 5.2 Implement EnforcerTool.validate_required_sections() with 70% threshold (Tier 2 default)
- [x] 5.3 Implement EnforcerTool.validate_max_words() with 150% threshold (Tier 2 default)
- [x] 5.4 Implement EnforcerTool.validate_forbidden_elements() with hard block (any tier)
- [x] 5.5 Implement EnforcerTool.validate_must_have() with info suggestion (any tier)
- [x] 5.6 Implement EnforcerTool.get_thresholds() for tier-based adjustment (Tier 1: 80%/120%, Tier 2: 70%/150%, Tier 3: 60%/200%)
- [x] 5.7 Implement EnforcerTool.generate_report() with ERROR/WARNING/INFO output
- [x] 5.8 Write unit tests for enforcement rules (test each quadrant, each tier, edge cases, forbidden elements)

## 6. CLI Integration

- [x] 6.1 Add `docs-sync discover` command to CLI with Typer
- [x] 6.2 Add `--repo` option (default: ".") with help text
- [x] 6.3 Add `--format` option (text, json, yaml) with default "text"
- [x] 6.4 Add `--force` option to skip cache and re-run discovery
- [x] 6.5 Add `--use-llm` option to enable LLM classification fallback
- [x] 6.6 Add `--review-overrides` option to show conflict review
- [x] 6.7 Add `--all-repos` option for multi-repo discovery
- [x] 6.8 Add `--discover` flag to `docs-sync sync` command (default: true)
- [x] 6.9 Wire CLI to DiscoveryAgent (instantiate agent, call agent.run(), format output)
- [x] 6.10 Write CLI integration tests (test command invocation, option parsing, output formats)

## 7. Pipeline Integration

- [x] 7.1 Add discover step to sync pipeline (before detect_changes)
- [x] 7.2 Update `analyze_impact` to use auto_mapping from StateTool instead of doc-mapping.yaml
- [x] 7.3 Update `validate` step to use EnforcerTool for Diátaxis validation
- [x] 7.4 Update `report` step to include Diátaxis coverage report from state
- [x] 7.5 Add fallback to `doc-mapping.yaml` when state file missing (backward compatibility)
- [x] 7.6 Write integration tests for enhanced pipeline (test discover → analyze → generate → validate → report)

## 8. Node Importance Scoring

- [x] 8.1 Implement GraphifyLoaderTool.calculate_importance_score() with formula (edges * 0.4 + centrality * 0.3 + process * 0.2 + cohesion * 0.1)
- [x] 8.2 Implement GraphifyLoaderTool.assign_tier() with thresholds (Tier 1: >= 0.8, Tier 2: 0.5-0.8, Tier 3: 0.2-0.5, Tier 4: < 0.2)
- [x] 8.3 Implement GraphifyLoaderTool.prioritize_isolated_nodes() sorted by importance score descending
- [x] 8.4 Implement GraphifyLoaderTool.detect_god_nodes() with edge count >= 10
- [x] 8.5 Store importance scores in state file under doc_gaps section
- [x] 8.6 Write unit tests for importance scoring (test formula calculation, tier assignment, edge cases)

## 9. Multi-Language Support

- [x] 9.1 Enhance ParseSourceTool for Python AST extraction (existing, add type hints extraction)
- [x] 9.2 Add GitNexusLoaderTool.extract_swift_symbols() via gitnexus tree-sitter
- [x] 9.3 Add GitNexusLoaderTool.extract_kotlin_symbols() via gitnexus tree-sitter
- [x] 9.4 Add GitNexusLoaderTool.extract_typescript_symbols() via gitnexus tree-sitter
- [x] 9.5 Add GitNexusLoaderTool.extract_go_symbols() via gitnexus tree-sitter
- [x] 9.6 Add GitNexusLoaderTool.extract_rust_symbols() via gitnexus tree-sitter
- [x] 9.7 Add DiscoveryAgent.llm_extraction_fallback() for unsupported languages
- [x] 9.8 Write unit tests for multi-language extraction (test each language, fallback behavior)

## 10. Multi-Platform Deployment Detection

- [x] 10.1 Implement ScannerTool.detect_docker() for Dockerfile, docker-compose.yaml, .dockerignore
- [x] 10.2 Implement ScannerTool.detect_launchd() for *.plist in LaunchAgents/LaunchDaemons
- [x] 10.3 Implement ScannerTool.detect_systemd() for *.service files
- [x] 10.4 Implement ScannerTool.detect_github_actions() for .github/workflows/*.yml
- [x] 10.5 Implement ScannerTool.detect_gitlab_ci() for .gitlab-ci.yml
- [x] 10.6 Implement ScannerTool.detect_procfile() for Procfile (Heroku)
- [x] 10.7 Implement ScannerTool.detect_vercel_netlify() for vercel.json, netlify.toml
- [x] 10.8 Map each platform to how-to documentation target in ClassifierTool
- [x] 10.9 Write unit tests for deployment detection (test each platform, edge cases, multiple platforms)

## 11. Documentation

- [x] 11.1 Update `docs/configuration.md` with discovery configuration options (state file, overrides, thresholds)
- [x] 11.2 Update `docs/cli.md` with `discover` command documentation (options, examples, output formats)
- [x] 11.3 Create `docs/reference/discovery-api.md` for ScannerTool, GitNexusLoaderTool, GraphifyLoaderTool, ClassifierTool, EnforcerTool, StateTool API
- [x] 11.4 Create `docs/how-to/configure-overrides.md` for override system usage (multi-level, conflict resolution)
- [x] 11.5 Create `docs/explanation/diataxis-enforcement.md` for enforcement rules explanation (thresholds, tiers, soft enforcement)
- [x] 11.6 Update `README.md` with discovery feature overview (auto-discovery, Diátaxis, overrides)
- [x] 11.7 Update `AGENTS.md` with DiscoveryAgent and ValidationAgent capabilities
