## Why

The current AgentMemory installation is functionally healthy, but its LLM timeout budget and optional-feature configuration can amplify provider or engine load into iii invocation pressure. Recent live verification showed the default `shopapikey`/`fable-5` summarization and graph paths working, while earlier 300-second LLM timeouts, concurrent background work, and ambiguous slot configuration created avoidable saturation risk; this change establishes a bounded, reversible runtime configuration baseline now that the latest package is installed.

This is a configuration and operational-verification change only. It keeps the tested default provider and local embedding route, avoids moving credentials, and does not introduce a new product capability or API contract.

## What Changes

- Bound the default LLM request timeout to a measured 60–90 second operating range instead of the current 300-second failure hold time, with one selected value recorded in the implementation evidence.
- Make the intended optional-feature posture explicit: keep automatic per-observation compression, Agent SDK fallback, pinned slots/reflection, image embeddings, Claude/Obsidian bridges, and provider fallback chains disabled unless separately authorized.
- Preserve the currently validated graph extraction, consolidation, context injection, snapshots, lesson decay, all-tool visibility, default `shopapikey`/`fable-5` LLM route, and local `nomic-embed-text` embedding route.
- Resolve the `AGENTMEMORY_SLOTS=memory` versus runtime `AGENTMEMORY_SLOTS=true` semantic mismatch as a documented decision; enable pinned slots only if a separate acceptance probe confirms the intended scope and write behavior.
- Add rollback instructions and a post-change acceptance matrix covering liveness, health, flags, exact PostToolUse capture, observation readback, embedding, summarization, graph extraction, smart search, session listing, graph statistics, latency, invocation pressure, and provider-error deltas.

## Capabilities

### New Capabilities

None. This is a configuration, operational-baseline, and verification change with no new product capability.

### Modified Capabilities

None. Existing OpenSpec requirements are unchanged; `.openspec.yaml` declares `skip_specs: true`.

## Impact

- User-owned AgentMemory runtime configuration under `~/.agentmemory/.env` and its launchd-managed service restart boundary.
- AgentMemory's default LLM and embedding provider behavior, iii invocation occupancy, and background consolidation/graph workload.
- Operational evidence and rollback documentation in the shared OpenSpec store.
- The configuration has two separate provider routes and credential boundaries: external LLM routing through `OPENAI_BASE_URL`/`OPENAI_API_KEY`, and local embedding routing through `OPENAI_EMBEDDING_BASE_URL`/`OPENAI_EMBEDDING_API_KEY`; both are preserved byte-for-byte except for the selected timeout/explicit-flag entries.
- No repository source code, public API, credential value, TDT provider registry, or unrelated active OpenSpec change is in scope.
