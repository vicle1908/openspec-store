## 1. Full Pipeline Module (SchedulerEngine)

- [x] 1.1 Create `workflows/full_pipeline.py` with SchedulerEngine workflow and `audit_gaps()` function
- [x] 1.2 Implement `discover_all_step()` — run ScannerTool + ClassifierTool on all source files
- [x] 1.3 Implement `audit_gaps_step()` — run CheckLinksTool + EnforcerTool on all docs, return gap report
- [x] 1.4 Implement `generate_docs_step()` — use GenerationAgent with harness capabilities to fill gaps
- [x] 1.5 Implement `validate_all_step()` — run CheckLinksTool + EnforcerTool on all docs after generation
- [x] 1.6 Implement `build_report()` — aggregate step results into comprehensive report

## 2. WorkflowBuilder DAG

- [x] 2.1 Create `workflows/full_dag.py` with WorkflowBuilder DAG: discover → audit → generate → validate → report
- [x] 2.2 Implement NodeDescriptor for each phase (discover, audit, generate, validate, report)
- [x] 2.3 Implement EdgeDescriptor for sequential flow between phases
- [x] 2.4 Implement conditional routing via CommandResult (skip generate if no gaps)
- [x] 2.5 Integrate with WorkflowEngine for DAG compilation and execution

## 3. CLI Integration

- [x] 3.1 Add `--full` flag to `sync` command that calls full pipeline via SchedulerEngine
- [x] 3.2 Add `audit` command to CLI that calls audit-only pipeline (read-only, no LLM)
- [x] 3.3 Add `--full` flag to `sync-all` command that runs full pipeline per repo
- [x] 3.4 Implement comprehensive report formatter for full mode output (stats: files scanned, docs found, gaps, generated, validated)

## 4. Gap Detection Logic

- [x] 4.1 Implement source_without_docs detection: compare ScannerTool output against auto_mapping
- [x] 4.2 Implement broken_links detection: run CheckLinksTool on all docs directory
- [x] 4.3 Implement diataxis_violations detection: run EnforcerTool on each doc against assigned quadrant
- [x] 4.4 Implement confidence-based filtering: skip low-confidence classifications (< 0.5) from gap report

## 5. Multi-Repo Full Mode

- [x] 5.1 Extend `multi_repo.py` `sync_all_repos()` to accept `full=True` parameter
- [x] 5.2 Implement cross-repo aggregation: collect per-repo reports, compute ecosystem-wide stats
- [x] 5.3 Add `--full` flag to `sync-all` CLI command

## 6. Harness Integration

- [x] 6.1 Wire GenerationAgent with planning guidance from LlmConfig.planning_guidance
- [x] 6.2 Wire GenerationAgent with subagents for validation delegation
- [x] 6.3 Wire GenerationAgent with guardrails for write path validation
- [x] 6.4 Ensure ApprovalGate triggers before all doc writes

## 7. Testing

- [x] 7.1 Write unit tests for `audit_gaps()` with mock scanner/classifier output
- [x] 7.2 Write unit tests for full pipeline SchedulerEngine workflow
- [x] 7.3 Write unit tests for WorkflowBuilder DAG construction
- [x] 7.4 Write integration tests for `docs-sync audit` CLI command
- [x] 7.5 Write integration tests for `docs-sync sync --full` CLI command

## 8. Documentation

- [x] 8.1 Update `docs/cli.md` with audit command and --full flag documentation
- [x] 8.2 Update `docs/configuration.md` with full mode behavior, gap detection, and harness integration
- [x] 8.3 Add examples for audit and full sync usage in `docs/examples.md`
