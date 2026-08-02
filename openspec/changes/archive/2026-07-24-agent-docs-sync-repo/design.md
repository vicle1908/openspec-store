## Context

TDT workspace has 10+ repos with documentation that drifts from code. An automated agent using agent-core features would keep docs in sync. All dependencies verified on Python 3.14.5.

## Goals / Non-Goals

**Goals:**
- Automated doc sync on commits
- Multi-repo support
- Use agent-core features (BaseAgent, ToolRegistry, HookRegistry, Flavor, WorkflowBuilder, SchedulerEngine)
- Production-ready with observability (otel_metrics, structured_audit)

**Non-Goals:**
- Replacing manual doc writing (agent assists, not replaces)
- Real-time streaming sync (batch is sufficient)
- Complex AI reasoning beyond doc generation (pattern matching + LLM for generation)

## Decisions

### Decision 1: Dedicated repo (not inside agent-core)

agent-docs-sync is a standalone tool that uses agent-core as a dependency. Benefits: independent releases, multi-repo support, clean separation.

### Decision 2: WorkflowBuilder for sync pipeline

```
detect_changes → analyze_impact → generate_updates → validate → report
```

Each step is a focused function, composable and testable. WorkflowBuilder provides LangGraph-style DAG execution.

### Decision 3: ToolRegistry for doc operations

Custom tools: `read_doc`, `write_doc`, `check_links`, `parse_source`, `sync_spec`, `git_diff`.

Tools with `requires_approval=True` trigger pydantic-ai's ApprovalGate for write operations.

### Decision 4: SchedulerEngine for durable execution

Uses `@workflow`/`@step` decorators from tdt_core.scheduler (not "DBOSDurability" which doesn't exist).

- **Passthrough mode** (default): In-memory execution, no DB
- **Durable mode** (`--durable`): DBOS-backed, crash-recoverable

### Decision 5: Flavor-based mode selection

Three modes via Flavor composition:
- `doc_checker`: Read-only validation
- `doc_generator`: Write docs with approval gates
- `doc_full_sync`: Complete pipeline with all features

### Decision 6: HookRegistry for cross-cutting concerns

- `validate_write_path`: Before-write guard
- `audit_doc_writes`: After-write audit trail
- `on_tool_error`: Retry logic for transient failures

### Decision 7: ruamel.yaml over PyYAML

Round-trip YAML preservation for doc-mapping.yaml updates. Better Python 3.14 support (explicit classifiers vs experimental).

## Architecture

```
agent-docs-sync/
├── src/agent_docs_sync/
│   ├── cli.py              # Typer CLI (check, update, validate, sync, sync-all)
│   ├── agent.py            # BaseAgent wiring (build_doc_sync_agent)
│   ├── flavors.py          # Flavor definitions (doc_checker, doc_generator, doc_full_sync)
│   ├── hooks.py            # Hook implementations (validate_write_path, audit_doc_writes)
│   ├── tools/
│   │   ├── git_diff.py     # GitDiffTool (git diff analysis)
│   │   ├── read_doc.py     # ReadDocTool (markdown parsing)
│   │   ├── write_doc.py    # WriteDocTool (with approval gate)
│   │   ├── check_links.py  # CheckLinksTool (link validation)
│   │   ├── parse_source.py # ParseSourceTool (AST extraction)
│   │   └── sync_spec.py    # SyncSpecTool (delta spec merging)
│   ├── workflows/
│   │   └── sync_pipeline.py  # WorkflowBuilder DAG
│   ├── durable.py          # SchedulerEngine workflow
│   ├── multi_repo.py       # Multi-repo orchestrator
│   └── config.py           # doc-mapping.yaml loader
├── tests/
│   ├── test_tools/         # Unit tests for all 6 tools
│   ├── test_hooks.py       # Unit tests for hooks
│   ├── test_workflows/     # Integration tests for WorkflowBuilder
│   └── test_cli/           # CLI command tests
├── docs/
│   ├── architecture.md     # System diagrams and data flow
│   ├── configuration.md    # doc-mapping.yaml schema
│   ├── tools.md            # Tool documentation
│   ├── hooks.md            # Hook documentation
│   └── cli.md              # CLI command reference
├── pyproject.toml
└── README.md
```

## agent-core Integration Map

| agent-core Feature | Usage in agent-docs-sync |
|-------------------|-------------------------|
| BaseAgent | Core agent with LLM integration, tool execution |
| ToolRegistry | Register/unregister 6 doc tools, enforce tool policies |
| HookRegistry | 3 hooks: before-write, after-write, error recovery |
| Flavor | 3 modes: check, generate, full_sync |
| FlavorPrompt | System prompts per mode |
| FlavorToolPolicy | allow/deny/require_approval per mode |
| FlavorDefaults | max_iterations, timeout_seconds, budget_usd |
| WorkflowBuilder | 5-step DAG pipeline |
| SchedulerEngine | @workflow/@step for durable execution |
| otel_metrics | Built-in OpenTelemetry hook |
| structured_audit | Built-in audit trail hook |
| ApprovalGate | pydantic-ai capability for write approval |

## Data Flow

```
CLI command
    ↓
build_doc_sync_agent(mode) → BaseAgent(gateway, tools, hooks, flavor)
    ↓
BaseAgent.run(prompt, context)
    ↓
┌─────────────────────────────────────────────────────────┐
│ WorkflowBuilder DAG (or SchedulerEngine if --durable)   │
│                                                         │
│ detect_changes → analyze_impact → generate_updates      │
│                                      ↓                  │
│                              validate → report          │
└─────────────────────────────────────────────────────────┘
    ↓
ToolRegistry.execute(tool_name, args)
    ↓
HookRegistry.fire_before/after/error
    ↓
LLMGateway.chat(messages, tools)
```

## Security Considerations

- GitPython 3.1.55: Security-hardened (blocks env expansion in URLs)
- WriteDocTool: Requires approval via ApprovalGate
- SyncSpecTool: Requires approval via ApprovalGate
- validate_write_path hook: Restricts write paths to allowed directories
- No remote Git operations — local repo only

## Testing Strategy

| Test Type | Scope | Tools |
|-----------|-------|-------|
| Unit | Individual tools, hooks | pytest, pytest-asyncio |
| Integration | WorkflowBuilder pipeline | pytest, mock LLM |
| Integration | SchedulerEngine durable | pytest, PostgreSQL test DB |
| E2E | Full CLI commands | subprocess, real repos |
| Contract | Tool metadata, flavor composition | pytest |
