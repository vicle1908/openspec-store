## Why

TDT needs a planning agent that can turn an engineering ticket into grounded requirements, design, API, implementation, test, and verification artifacts across multiple repositories. The workflow must preserve human authority at consequential decisions and must never claim that an API, symbol, file, or dependency exists without code-intelligence evidence.

The earlier design depended on custom `WorkflowBuilder`, dict-only state, `CommandResult`, `ApprovalGate` workflow gates, and private memory adapters. Research in `stabilize-agent-framework-integration` and `converge-agent-framework-upstream` shows that Pydantic AI, Harness, and LangGraph now provide the generic composition, lifecycle, continuation, memory, typed-state, routing, interrupt, and persistence mechanisms directly.

## What Changes

- Make completion of `stabilize-agent-framework-integration` and `converge-agent-framework-upstream` a hard implementation prerequisite.
- Create a new `agent-harness` repository as the first typed consumer of the converged `agent_core.sdk`.
- Implement one exact 12-stage planning workflow: intake, context, clarify, spec, impact, design, API contract, implementation plan, coding plan, plan review, test plan, and verification.
- Use native typed LangGraph state, reducers, `Command`, `interrupt`, async execution, and caller-owned checkpointer contexts.
- Compose official Pydantic AI capabilities/toolsets and Harness memory/step persistence through the public agent-core SDK.
- Use GitNexus MCP tools as the primary symbol/impact evidence source and Graphify as the structural traversal source; stale or missing indexes reduce confidence and block unsupported claims.
- Use native LangGraph interrupts for stage approvals and native Pydantic deferred tool calls only for individual tool authorization.
- Store artifacts only under a bounded `$TDT_HOME/agent-harness/` root.
- Keep the initial release planning-only and read-only with respect to target repositories, Jira, GitLab, and OpenSpec stores.

## Capabilities

### New Capabilities

- `workflow-dag`: Typed 12-stage planning workflow with native LangGraph routing and durability.
- `approval-gates`: Authorized human stage decisions using native interrupts and resume commands.
- `anti-hallucination`: Evidence-backed existence, semantic, and cross-artifact validation.
- `data-model`: Typed artifacts, workflow state, decisions, and trace entries.
- `multi-repo-workspace`: Bounded multi-repository discovery and code-intelligence aggregation.
- `memory-system`: Explicit ownership for workflow checkpoints, agent steps, semantic memory, and artifact files.
- `traceability`: Requirement-to-verification lineage and evidence reporting.
- `configuration`: TDT_HOME-based typed configuration and authority profiles.
- `cli-interface`: Run, status, report, approve, and reject operations.
- `integration-guide`: Supported dependency, index, persistence, and observability setup.

### Modified Capabilities

None.

## Impact

- **New repository**: `agent-harness/`.
- **Dependencies**: workspace `agent-core`/`tdt-core` plus the reviewed Pydantic AI 2.18.0, Harness 0.11.0, Monty 0.0.19, and LangGraph 1.2.9 family. Adding dependencies requires explicit approval before repository setup.
- **Framework dependency**: implementation SHALL not begin until both framework changes are complete and verified.
- **Authority**: the initial release reads tickets and repositories and writes only bounded harness artifacts. Source edits, OpenSpec promotion, branches, commits, merge requests, shell/code execution, and external mutation are out of scope.
- **GitNexus/Graphify**: every symbol or execution-flow claim carries repository, index commit, query/tool, and confidence evidence.
- **Existing services**: no runtime or deployment change.

## Success Criteria

- All 12 stages produce schema-valid artifacts or an explicit blocked/needs-human outcome.
- Every codebase reference is tied to verifiable GitNexus, Graphify, or file evidence.
- Stage approvals survive restart when durable mode is enabled and reject unauthorized/stale decisions.
- Workflow state is typed; no generic `results` dictionary or custom command semantic is required.
- Target repository files remain unchanged in end-to-end tests.
- Full traceability is available from ticket inputs through the verification report.

## Non-Goals

- Generating or applying source-code changes.
- Creating or modifying Jira issues, OpenSpec changes, Git branches, commits, merge requests, or deployments.
- Enabling shell, code execution, filesystem access outside the artifact root, runtime authoring, or unrestricted network access.
- Replacing TDT gateway/auth, budget, audit, or authorization policy.
- Supporting webhook approval transport in the initial release; the first transport is the authenticated local CLI.
