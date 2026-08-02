## Why

`agent-harness` has strong typed graph, gate, and checkpoint mechanics, but the production graph bypasses its stage-agent factory and executes handlers without Jira, code-intelligence evidence, artifact persistence, or evidence-grounded review. Placeholder providers can therefore yield a completed planning run with empty evidence and a hard-coded passing review.

## What Changes

- Begin with a transport spike for a read-only GitNexus MCP adapter and bounded Graphify output adapter; shell/code-execution fallback is not the default authority.
- Introduce immutable `HarnessServices`/`StageServices` composition and reconstruct live services per runner process instead of checkpointing clients.
- Inject factory-owned Jira reading, code intelligence, bounded file access, gateway/stage-agent creation, and artifact storage into production graph nodes.
- Make the production graph use the official stage agents/toolsets and preserve deterministic pure handlers where evidence is not required.
- Fail closed or enter `needs_input` when required evidence is absent, stale, malformed, or unavailable; placeholder empty evidence cannot satisfy a stage.
- Replace hard-coded plan review with requirements, evidence, repository-example, and downstream traceability validation.
- Persist immutable artifact revisions, content digests, input/evidence references, and validation results.
- Add a production-composition fixture that yields non-empty requirements and evidence and an optional real read-only smoke test.
- **BREAKING**: Production planning without required service/evidence configuration will no longer report `completed`; it will fail closed or report `needs_input`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `stage-toolset-composition`: Require production service composition, real read-only adapters, and explicit failure semantics.
- `agent-harness-integration`: Require the consumer-owned production graph to invoke composed stage services and official agent/toolset factories.
- `agent-harness-workflow`: Require grounded evidence, traceability-based review, fail-closed completion, and immutable artifact revisions.

## Non-Goals

- Granting shell, source-write, Jira-write, GitLab-write, deployment, or OpenSpec-promotion authority.
- Checkpointing live clients, gateways, MCP sessions, or artifact-store handles.
- Moving the 12-stage topology into `agent-core` or replacing LangGraph.
- Making external live-provider smoke tests mandatory for deterministic pull-request CI.

## Impact

- Repository: `agent-harness`; dependencies on `agent-core` composition and `tdt_core` client factories.
- Primary modules: workflow graph/runner, stage definitions and handlers, agent factory, GitNexus/Graphify tools, Jira intake, validation, evidence models, and artifact storage.
- GitNexus rates `build_graph` CRITICAL: 8 impacted symbols across 9 run/status/approve/reject/stream/resume/history/report paths. `run_validation`, `GitNexusTool`, and `GraphifyTool` are LOW.
- CRITICAL-root implementation must preserve characterization fixtures and gate/checkpoint behavior before service injection.
- The transport spike must prefer existing dependencies; adding an MCP client package requires explicit approval.
- Mobile applications are unaffected.
