## Context

agent-docs-sync currently has two modes:
- **Default sync**: `docs-sync sync` runs detect → analyze → generate → validate → report using `git diff` to find changed files
- **Full mode**: `docs-sync sync --full` prints "not yet implemented"

The key limitation: `detect_changes()` in `sync_pipeline.py` only runs `git diff --name-only HEAD~1`. Documentation gaps — source code that never had docs, broken links, Diátaxis violations — go undetected.

**agent-core provides:**
- `SchedulerEngine` — durable step-by-step execution with retry (used in `durable.py`)
- `WorkflowBuilder/WorkflowEngine` — LangGraph-based DAG orchestration
- `BaseAgent` — ReAct run loop with harness capabilities (planning, subagents, guardrails, DynamicWorkflow)
- `ApprovalGate` — user confirmation for write operations
- `HookRegistry` — lifecycle hooks (audit_doc_writes, validate_write_path)
- `ToolRegistry` — tool registration and management

All building blocks exist as individual tools:
- `ScannerTool` scans ALL source files by language
- `ClassifierTool` classifies files into Diátaxis quadrants
- `EnforcerTool` validates docs against Diátaxis rules
- `CheckLinksTool` validates all links in markdown files
- `GenerationAgent` generates docs via LLM with harness capabilities
- `run_discovery_pipeline` composes scanner + classifier + graphify + gitnexus

## Goals / Non-Goals

**Goals:**
1. `docs-sync sync --full` scans ALL source code and ALL docs (not just git diff)
2. `docs-sync audit` provides a read-only comprehensive doc audit
3. Multi-repo full mode (`sync-all --full`) runs across all TDT repos
4. Gap detection: source files without docs, broken links, Diátaxis violations
5. Leverage agent-core's `SchedulerEngine` for durable full pipeline execution
6. Leverage agent-core's `WorkflowBuilder` for DAG-based pipeline orchestration
7. Leverage harness capabilities (planning, subagents, guardrails) for the generation phase

**Non-Goals:**
1. Replacing git-diff-based sync (default mode stays)
2. Changing existing tool implementations
3. New dependencies or providers
4. Real-time or incremental monitoring

## Decisions

### Decision 1: Full pipeline as new SchedulerEngine workflow

**Choice:** Create `workflows/full_pipeline.py` using agent-core's `SchedulerEngine` with durable step-by-step execution.

**Rationale:**
- `SchedulerEngine` provides retry, checkpointing, and observability out of the box
- Follows the same pattern as `durable.py` (existing doc sync pipeline)
- Steps can be individually retried on failure
- Durable execution enables crash recovery for long-running full scans

**Implementation:**
```python
@engine.workflow(name="doc-full-pipeline", timeout_seconds=1200.0)
async def full_sync_workflow(repo_root: str) -> dict[str, Any]:
    # Step 1: Discover (scan all code)
    discover_result = await discover_all_step(repo_root)
    # Step 2: Audit (find gaps)
    audit_result = await audit_gaps_step(repo_root, discover_result.output)
    # Step 3: Generate (LLM agent fills gaps)
    generate_result = await generate_docs_step(audit_result.output)
    # Step 4: Validate (verify everything)
    validate_result = await validate_all_step(repo_root)
    # Step 5: Report
    return build_report(discover_result, audit_result, generate_result, validate_result)
```

### Decision 2: Use WorkflowBuilder for DAG orchestration

**Choice:** Use agent-core's `WorkflowBuilder` with `NodeDescriptor` and `EdgeDescriptor` for the full pipeline DAG.

**Rationale:**
- `WorkflowBuilder` provides declarative graph construction
- `WorkflowEngine` compiles and runs with `PostgresSaver` checkpointing
- Supports conditional routing via `CommandResult`
- Supports subgraphs for complex nested workflows

**Implementation:**
```python
builder = WorkflowBuilder(name="full-sync-dag")
builder.add_node(NodeDescriptor(name="discover", kind=NodeKind.TOOL))
builder.add_node(NodeDescriptor(name="audit", kind=NodeKind.TOOL))
builder.add_node(NodeDescriptor(name="generate", kind=NodeKind.AGENT))
builder.add_node(NodeDescriptor(name="validate", kind=NodeKind.TOOL))
builder.add_node(NodeDescriptor(name="report", kind=NodeKind.TOOL))
builder.add_edge(EdgeDescriptor(source="discover", target="audit"))
builder.add_edge(EdgeDescriptor(source="audit", target="generate"))
builder.add_edge(EdgeDescriptor(source="generate", target="validate"))
builder.add_edge(EdgeDescriptor(source="validate", target="report"))
builder.set_entry("discover")
```

### Decision 3: Generation phase uses existing GenerationAgent with harness

**Choice:** The generate phase reuses the existing `GenerationAgent` with its harness capabilities (planning, subagents, guardrails).

**Rationale:**
- `GenerationAgent` already has planning guidance for Diátaxis classification
- SubAgents enable delegation of validation tasks
- Guardrails prevent writes outside allowed directories
- No need to duplicate agent configuration

**Integration:**
- GenerationAgent is built via `build_generation_agent(gateway, config)`
- `config.harness_config` provides planning, subagents, guardrails
- ApprovalGate ensures user confirmation before writes
- HookRegistry provides audit trail for all doc modifications

### Decision 4: Audit as deterministic phase (no LLM)

**Choice:** The audit phase is purely rule-based — no LLM calls.

**Rationale:**
- Gap detection is deterministic: file exists? link resolves? Diátaxis rules pass?
- LLM is only needed for generation (which comes after audit)
- Keeps audit fast, cheap, and reproducible
- Audit results drive the generate phase

**Implementation:** New `audit_gaps()` function that:
1. Takes `auto_mapping` from discover (file → quadrant mapping)
2. Scans all docs directory for `.md` files
3. Runs `CheckLinksTool` on all docs
4. Runs `EnforcerTool` on each doc against its assigned quadrant
5. Returns gap report: `{source_without_docs, broken_links, violations, stats}`

### Decision 5: Multi-repo uses sequential full pipeline per repo

**Choice:** For `sync-all --full`, run full pipeline per repo sequentially, aggregate results.

**Rationale:**
- Each repo has independent doc state
- Sequential execution avoids overwhelming the LLM gateway
- Aggregated report shows ecosystem-wide doc health
- SchedulerEngine provides retry and observability per repo

### Decision 6: ApprovalGate for all write operations

**Choice:** All doc generation and updates go through agent-core's ApprovalGate.

**Rationale:**
- User confirmation before writing files
- Consistent with existing sync pipeline behavior
- Audit trail via HookRegistry (audit_doc_writes hook)
- Validation via validate_write_path hook

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Full scan is slow on large repos | Cache discovery state; skip unchanged repos |
| Audit may produce false positives | Use classifier confidence thresholds |
| Generation may produce low-quality docs | Use existing planning_guidance; validate generated docs |
| SchedulerEngine overhead for simple runs | Passthrough mode (enabled=False) for local dev |
| LLM gateway may be unavailable | Graceful degradation: audit works without LLM |

## Migration Plan

1. Create `workflows/full_pipeline.py` with SchedulerEngine workflow
2. Create `workflows/full_dag.py` with WorkflowBuilder DAG
3. Add `--full` flag handling in `cli.py` sync command
4. Add `audit` command to CLI
5. Add `--full` flag to `sync-all` command
6. Write tests
7. Update docs

No migration needed — new features only, no breaking changes.
