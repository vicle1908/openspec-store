## Context

`agent-harness` owns a typed 12-stage LangGraph graph with gate and durability mechanics. Its GitNexus and Graphify classes currently return empty placeholder structures, the stage-agent factory is exercised only in tests, and `build_graph` directly wraps pure handlers. Jira is not injected into intake, evidence is absent from context/impact, review passes through a constant, validation sees only artifact content, and the artifact store is not part of production composition.

The change modifies `agent-harness` and consumes `agent-core` plus factory-owned `tdt_core` Jira access. `build_graph` is CRITICAL, so production composition must be introduced behind characterization tests without altering gate/checkpoint semantics. The harness remains a local/manual CLI and read-only planning system.

## Goals / Non-Goals

**Goals:**

- Execute production stages through explicit services and official agent/toolset composition.
- Replace placeholder code intelligence with bounded read-only evidence adapters.
- Fail closed on missing/stale required evidence.
- Review plans through traceability rather than constants.
- Persist immutable artifact revisions outside checkpoint payloads.
- Preserve existing graph/gate/durable lifecycle behavior.

**Non-Goals:**

- Grant shell, source-write, Jira-write, GitLab-write, or deployment authority.
- Store live clients in LangGraph state.
- Replace LangGraph or move stage topology to `agent-core`.
- Require external live services in deterministic PR CI.

## Decisions

### 1. Gate implementation on a read-only transport spike

The first implementation slice proves a narrow `CodeIntelligencePort` using a read-only GitNexus MCP adapter with fixture transport and a bounded Graphify artifact reader. The port exposes only query/context/impact/status and validated graph query/path/freshness operations. General subprocess execution is not the default fallback.

Alternative: invoke `npx gitnexus` from stage code. Rejected because the harness explicitly denies shell/code-execution authority and a CLI fallback would expand it.

If no approved transport can meet the contract without a new dependency, implementation pauses for dependency approval; it does not retain placeholders.

### 2. Introduce immutable service composition

`HarnessServices` contains factories/configuration for Jira reader, code intelligence, bounded files, gateway/stage agents, artifact store, clock, and observability. A stage receives a narrowed immutable `StageServices` view. The runner reconstructs services for each process and closes operation-scoped resources.

Alternative: place services in checkpoint state. Rejected because clients are not serializable, trusted checkpoint types would broaden, and credentials could leak.

### 3. Close graph nodes over services

`build_graph` accepts or is created by a composition root that closes each stage node over its stage definition and narrowed services. Pure deterministic handlers remain pure, while evidence/model stages use official agents/toolsets. Gate nodes and topology remain unchanged.

Alternative: introduce a parallel workflow engine. Rejected because native LangGraph ownership and current durability are sound.

### 4. Resolve Jira through `tdt_core` only

Intake uses a read-only port backed by `tdt_core.clients` Jira Cloud API v3 factories. The stage receives bounded ticket fields and evidence metadata, never a raw SDK client or credentials. Jira unavailable/auth failures produce `needs_input` or configuration failure according to the stage contract.

### 5. Encode evidence requirements in stage definitions

Each stage declares required and optional evidence types plus freshness policy. Empty, placeholder, malformed, or mismatched required evidence blocks completion. Optional omissions lower confidence and remain visible. Provider-authored freshness is not authoritative.

### 6. Make local validation authoritative

Validation receives requirements, accepted evidence, input/output artifact references, repository examples, stage policy, and source identity. Plan review derives missing obligations and cannot be overridden by model output. Agent output is a proposal to local validation.

### 7. Persist artifacts in an immutable ledger

Artifact content is stored by stable identity/revision with digest, inputs, evidence, validation, and source identity. Checkpoints store identifiers and minimal typed workflow state. Resume verifies stored digests and does not rerun completed producers.

### 8. Keep adapters and logs bounded

Adapters validate response schemas, result counts, paths, repository identity, index commit/graph freshness, timeouts, and diagnostic size. Traces contain IDs, counts, freshness, validation, and durations—not credentials or full ticket/artifact bodies. Agentmemory may receive summary observations but is not evidence or artifact authority.

## Risks / Trade-offs

- **CRITICAL graph regression** → Freeze topology/gate characterization, inject one stage at a time, and run full lifecycle/change detection after each slice.
- **MCP transport availability varies by host** → Use an interface and deterministic fixture; report `needs_input` rather than synthesizing evidence.
- **New dependency may be needed** → Stop for approval after the transport spike; do not silently add one.
- **Artifact and checkpoint state diverge** → Persist artifact first, checkpoint only the verified identity/digest, and reconcile on resume.
- **Stricter evidence blocks previously completed runs** → Report legacy results as historical and require a new run/revision for grounded completion.

## Migration Plan

1. Capture current graph/gate/checkpoint and hollow-run fixtures.
2. Complete the GitNexus MCP/Graphify transport spike and authority review.
3. Add service/port models and artifact-store integration without changing topology.
4. Wire intake/context/impact first; require non-empty current evidence.
5. Wire remaining agent stages and local validation/traceability review.
6. Move checkpoint payloads to artifact references while preserving compatibility.
7. Remove placeholder providers and test-only production branches.
8. Run deterministic CLI fixture, optional authorized read-only smoke, PostgreSQL lifecycle, and cross-repository verification.

Rollback selects the last known service adapter version but must never fall back to empty successful providers. The runner may disable evidence-dependent execution and return `needs_input`; immutable artifacts remain readable. Deployment is the normal CLI/library installation path, not Docker or launchd.

## Open Questions

- The transport spike must confirm whether an existing approved MCP client is reusable; adding one requires explicit approval.
