## 1. Repo Structure & Agent Wiring

- [x] 1.1 Create agent-docs-sync directory and pyproject.toml (Python >=3.14,<3.15)
- [x] 1.2 Add agent-core dependency (BaseAgent, ToolRegistry, HookRegistry, Flavor)
- [x] 1.3 Implement `build_doc_sync_agent()` with three modes (check, generate, full_sync)
- [x] 1.4 Create flavor definitions in `flavors.py` (doc_checker, doc_generator, doc_full_sync)
- [x] 1.5 Wire `otel_metrics` and `structured_audit` hooks
- [x] 1.6 Verify all dependencies install on Python 3.14

## 2. Tool Implementation

- [x] 2.1 Implement `GitDiffTool` (git diff analysis via GitPython 3.1.55)
- [x] 2.2 Implement `ReadDocTool` (markdown parsing via markdown-it-py 4.2.0)
- [x] 2.3 Implement `WriteDocTool` (with `requires_approval=True` for ApprovalGate)
- [x] 2.4 Implement `CheckLinksTool` (link validation via httpx 0.28.1)
- [x] 2.5 Implement `ParseSourceTool` (AST-based API extraction via stdlib ast)
- [x] 2.6 Implement `SyncSpecTool` (delta spec merging with approval gate)
- [x] 2.7 Register all tools in ToolRegistry

## 3. Hook Implementation

- [x] 3.1 Implement `validate_write_path` (before-write guard with tool_filter=["write_doc"])
- [x] 3.2 Implement `audit_doc_writes` (after-write audit trail with tool_filter=["write_doc"])
- [x] 3.3 Implement `on_tool_error` (retry logic for transient failures, timeout_seconds=5.0)
- [x] 3.4 Register all hooks with HookRegistry

## 4. Workflow Pipeline (WorkflowBuilder)

- [x] 4.1 Implement `detect_changes` step (git diff → categorize files)
- [x] 4.2 Implement `analyze_impact` step (map source changes to affected docs)
- [x] 4.3 Implement `generate_updates` step (LLM-assisted doc generation)
- [x] 4.4 Implement `validate` step (link checking, openspec validate)
- [x] 4.5 Implement `report` step (generate sync summary)
- [x] 4.6 Wire pipeline with `WorkflowBuilder.add_node/add_edge/set_entry`

## 5. Durable Execution (SchedulerEngine)

- [x] 5.1 Create `durable.py` with `@workflow/@step` decorators
- [x] 5.2 Implement `detect_changes_step` (max_retries=3)
- [x] 5.3 Implement `analyze_impact_step` (max_retries=2)
- [x] 5.4 Implement `generate_updates_step` (max_retries=2)
- [x] 5.5 Implement `validate_docs_step` (max_retries=3)
- [x] 5.6 Implement `sync_specs_step` (max_retries=2)
- [x] 5.7 Wire `doc_sync_workflow` with timeout_seconds=600

## 6. Multi-Repo Support

- [x] 6.1 Define `TDT_REPOS` registry (agent-core, ai-review, jira-skill, etc.)
- [x] 6.2 Define `DOC_MAPPING` per repo
- [x] 6.3 Implement `sync_all_repos()` orchestrator
- [x] 6.4 Add `--repo` flag to CLI commands

## 7. CLI (Typer 0.27.0)

- [x] 7.1 Implement `docs-sync check` command
- [x] 7.2 Implement `docs-sync update` command (with `--dry-run`)
- [x] 7.3 Implement `docs-sync validate` command
- [x] 7.4 Implement `docs-sync sync` command (with `--durable` flag)
- [x] 7.5 Implement `docs-sync sync-all` command (multi-repo)

## 8. Configuration (ruamel.yaml 0.19.1)

- [x] 8.1 Create `doc-mapping.yaml` schema
- [x] 8.2 Implement `load_doc_mapping()` resolver
- [x] 8.3 Support per-repo override files
- [x] 8.4 Add default mappings for agent-core, ai-review, jira-skill

## 9. Tests

- [x] 9.1 Unit tests for all tools (GitDiffTool, ReadDocTool, etc.)
- [x] 9.2 Unit tests for all hooks
- [x] 9.3 Integration tests for WorkflowBuilder pipeline
- [x] 9.4 Integration tests for SchedulerEngine durable pipeline
- [x] 9.5 End-to-end tests with real repos
- [x] 9.6 Test flavor composition and tool policy enforcement
- [x] 9.7 Test Python 3.14 compatibility

## 9.1 Test Directory Structure

- [x] 9.1.1 Create `tests/test_workflows/__init__.py`
- [x] 9.1.2 Create `tests/test_cli/__init__.py`
- [x] 9.1.3 Create `tests/test_workflows/test_sync_pipeline.py` (WorkflowBuilder integration tests)
- [x] 9.1.4 Create `tests/test_cli/test_cli.py` (CLI command tests)

## 9.2 Additional Tool Tests

- [x] 9.2.1 Add unit tests for `GitDiffTool` in `tests/test_tools/test_git_diff.py`
- [x] 9.2.2 Add unit tests for `WriteDocTool` in `tests/test_tools/test_write_doc.py`
- [x] 9.2.3 Add unit tests for `CheckLinksTool` in `tests/test_tools/test_check_links.py`
- [x] 9.2.4 Add unit tests for `SyncSpecTool` in `tests/test_tools/test_sync_spec.py`

## 10. Documentation

- [x] 10.1 Create README.md with usage examples
- [x] 10.2 Create `docs/architecture.md` with diagrams
- [x] 10.3 Create `docs/configuration.md` for doc-mapping.yaml
- [x] 10.4 Create API reference

## 10.1 Documentation Folder Structure

- [x] 10.1.1 Create `docs/` directory
- [x] 10.1.2 Create `docs/architecture.md` with system diagrams and data flow
- [x] 10.1.3 Create `docs/configuration.md` for doc-mapping.yaml schema and examples
- [x] 10.1.4 Create `docs/tools.md` documenting all 6 tools (GitDiffTool, ReadDocTool, etc.)
- [x] 10.1.5 Create `docs/hooks.md` documenting hook implementations and usage
- [x] 10.1.6 Create `docs/cli.md` with CLI command reference and examples
