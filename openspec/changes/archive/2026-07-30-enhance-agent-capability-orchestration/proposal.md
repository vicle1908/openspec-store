## Why

The repository has independent GitNexus, Graphify, OpenSpec, agentmemory, and
skill-distribution surfaces, but they do not yet share one health contract or
agent workflow. GitNexus currently has an unreadable outer LadybugDB index,
Graphify hook checks encounter FileProvider stale handles, and agentmemory is
wired but its REST server is stopped; therefore agents can be configured while
still lacking trustworthy context. This change establishes a staged,
evidence-driven orchestration layer before adding more optional features.

## What Changes

- Add an `agent-capability-orchestration` capability covering unified health
  evidence, source-of-truth routing, cross-tool identifiers, and safe fallback
  behavior.
- Add a redacted machine-readable health contract for OpenSpec, GitNexus,
  Graphify, agentmemory, MCP reachability, skill surfaces, versions, freshness,
  and rollback ownership.
- Define quick, exploration, and implementation health profiles with required
  versus optional probes, bounded deadlines, run-scoped evidence, and truthful
  `ready`, `ready-with-warnings`, and `not-ready` outcomes.
- Add a skills-first orchestration workflow that uses OpenSpec for intent and
  verification, GitNexus for code execution and impact, Graphify for documents
  and cross-repository concepts, and agentmemory for prior decisions and
  lessons.
- Repair the current runtime baseline before enabling new integrations:
  agentmemory server health and full MCP visibility, single-writer index
  ownership, and a supported strategy for indexes on FileProvider-backed
  workspaces.
- Add explicit cross-root identity and contract-link conventions for the outer
  repository and the independent `mcp-router/` repository without merging
  their source-of-truth indexes.
- Add fixture and CI checks for health evidence, MCP round trips, index
  freshness, graph integrity, probe timeouts, hook idempotency, secret
  redaction, disposable-memory cleanup, scoped rollback, and explicit
  change-owned versus unrelated dirty-path attribution.
- Keep Git hooks advisory and non-blocking; an unavailable knowledge tool SHALL
  produce evidence and a warning rather than block ordinary commits.
- Keep the first rollout repository-local: expose CLI and retained evidence,
  and defer direct `mcp-router` consumption until the local pilot proves a
  separate nested-repository change is warranted.
- Review (but do not silently apply) the current Graphify `0.9.26` and
  agentmemory `0.9.27` repository pins against the researched stable candidates
  (`0.9.30` and `0.9.28` respectively).

## Capabilities

### New Capabilities

- `agent-capability-orchestration`: Coordinates health evidence, tool selection,
  stable identifiers, safe fallbacks, and the multi-agent exploration,
  implementation, and review workflow.

### Modified Capabilities

- `developer-code-intelligence`: Adds live-health evidence, FileProvider-safe
  index ownership, cross-tool identifiers, and explicit degraded-state
  behavior for GitNexus and Graphify.
- `developer-memory`: Adds server/tool-surface health evidence, durable-memory
  save/search checks, and orchestration rules that keep memory contextual rather
  than authoritative over code or specifications.
- `agent-skill-distribution`: Adds a managed orchestration skill and verifies
  its parity, ownership, client discovery, and rollback across both Git roots.
- `agent-instruction-governance`: Adds deterministic routing and evidence rules
  for the new workflow while preserving generated-surface ownership and
  non-disclosure requirements.

## Impact

- **Repository surfaces:** OpenSpec deltas, `scripts/knowledge-tools.sh`, a
  redacted health/evidence helper, fixture tests, Make targets, runbooks, and
  one hand-authored orchestration skill. Generated OpenSpec and client surfaces
  remain generator-owned.
- **Developer tooling:** GitNexus, Graphify, agentmemory, OpenSpec, MCP
  registrations, project hooks, and the outer/nested skill inventories.
- **Runtime state:** Run-scoped evidence, local index locks and compatibility
  probes, agentmemory's loopback REST/MCP server, and optional local graph
  projections. No production service, database, Kafka, Temporal, Protobuf,
  REST, container image, or deployment contract is changed.
- **Compatibility:** Existing Agentmemory hooks, hand-authored guidance,
  independent Git roots, and unrelated worktree changes remain preserved.
  Version upgrades require separate review and current documentation checks.
- **Rollout:** Recover health first, pass the FileProvider compatibility gate,
  establish schema-validated evidence, pilot the orchestration workflow on
  read-only exploration, then enable pre-change impact and post-change
  verification integrations. Implementation readiness requires all required
  probes for the selected profile to pass for the exact source identity.
- **Rollback:** The orchestration rollback removes only its owned latest-evidence
  pointers and preserves historical runs, skills, hooks, registrations, indexes,
  memories, guidance, and application code. Managed-skill rollback and native
  GitNexus/Graphify uninstall remain separate, explicitly reviewed ownership
  workflows; no aggregate rollback invokes them implicitly.
