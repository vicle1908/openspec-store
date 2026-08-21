## Context

The current default AgentMemory 0.9.29 service uses the tested `shopapikey`/`fable-5` OpenAI-compatible LLM route and local `nomic-embed-text` embeddings. Live acceptance passed capture, embedding, summarization, graph extraction, smart search, session listing, and health. Earlier load evidence showed that 300-second LLM timeouts and ambiguous optional flags can retain iii invocations during provider failures; the runtime also treats `AGENTMEMORY_SLOTS` as enabled only when its value is the literal `true`, while the current environment uses `memory`. The live configuration has separate external-LLM and localhost-embedding routes/keys, a pre-existing `.env.bak`, and an iii `default_timeout` of 180000 ms that must be compared with the AgentMemory timeout rather than silently assumed equivalent.

## Goals / Non-Goals

**Goals:**

- Bound LLM provider failure occupancy at a selected 90-second budget while retaining enough headroom for the proven default provider.
- Make the conservative optional-feature posture explicit and restart-safe.
- Preserve the validated default provider, local embedding model, graph extraction, consolidation, context injection, snapshots, lesson decay, and all MCP tools.
- Capture pre-change configuration shape, service identity, and feature-matrix evidence; provide a reversible rollback.

**Non-Goals:**

- Switching AgentMemory to GiaoDuc, Anthropic Messages, a fallback provider, or a new model.
- Copying credentials between TDT, Hermes, AgentMemory, or shell environment stores.
- Enabling automatic per-observation compression, Agent SDK fallback, image embeddings, Claude/Obsidian bridges, or pinned slots in this change.
- Editing AgentMemory source, the npm package, OpenSpec main specs, or unrelated active changes.

## Decisions

1. **Use a 90-second LLM timeout.** Set the provider-specific and shared AgentMemory LLM timeout knobs to `90000` ms. Ninety seconds preserves materially more headroom than 60 seconds for the observed 7–11 second successful calls while preventing a five-minute failed request from holding an iii invocation slot. A 60-second value remains a follow-up tuning option if provider latency evidence supports it.

2. **Make disabled optional paths explicit.** Declare `AGENTMEMORY_AUTO_COMPRESS=false`, `AGENTMEMORY_ALLOW_AGENT_SDK=false`, `AGENTMEMORY_SLOTS=false`, and `AGENTMEMORY_REFLECT=false`. Reflection is currently `true`; disabling it is an intentional load-containment decision because the selected scope does not include pinned-slot behavior, and the baseline/acceptance matrix must record that behavior change explicitly. This resolves the current `AGENTMEMORY_SLOTS=memory` value mismatch without enabling new write or nested-agent behavior.

3. **Preserve proven active paths and routing topology.** Leave `GRAPH_EXTRACTION_ENABLED`, `CONSOLIDATION_ENABLED`, `AGENTMEMORY_INJECT_CONTEXT`, `SNAPSHOT_ENABLED`, `LESSON_DECAY_ENABLED`, and `AGENTMEMORY_TOOLS=all` enabled as currently tested. Preserve `AGENTMEMORY_AGENT_SCOPE=shared`, `AGENTMEMORY_VIEWER_PORT`, `OPENAI_BASE_URL`, `OPENAI_EMBEDDING_BASE_URL`, and `OPENAI_EMBEDDING_API_KEY` unchanged. The external LLM key and localhost Ollama embedding key are distinct credential boundaries; neither value may be copied, normalized, or included in evidence. Leave the default `shopapikey`/`fable-5` and local embedding configuration untouched.

4. **Keep recovery controls separate.** Do not change `AGENTMEMORY_DROP_STALE_INDEX` in this change. Its recovery behavior can discard persisted vectors on startup and requires a separate dimension/rollback rehearsal. Treat the existing `.env.bak` as a pre-existing snapshot and do not overwrite or rotate it during this maintenance transaction.

5. **Use one maintenance transaction.** Freeze or disclose active AgentMemory clients, capture the non-secret configuration and service/store identity, edit only the owned AgentMemory environment, restart the launchd-managed worker and iii engine, then run the complete acceptance matrix. Rollback restores the exact pre-change lines and repeats the same matrix.

6. **Treat evidence as independent gates.** A healthy endpoint or green doctor result is insufficient. Acceptance must separately prove provider reachability, hook capture, observation readback, embedding dimensions, summary success, graph success, search, sessions, graph stats, bounded latency, invocation pressure, and absence of new provider/index failures. Record the iii `default_timeout=180000` binding and explain whether the 90000 ms AgentMemory timeout or iii timeout governs each path. Reconcile the known doctor “graph empty” versus status/graph-stats populated discrepancy as a pre-existing metric-definition distinction or fail the change.

## Risks / Trade-offs

- **[Timeout too short]** A legitimate slow summary may fail at 90 seconds → retain the prior values in the frozen rollback record and compare p95/p99 latency before considering 60 seconds.
- **[Timeout too long]** Provider outages can still consume slots for 90 seconds → monitor active invocations and provider error deltas during the acceptance window.
- **[Explicit disabled flags]** Existing users may have intended slots/reflection or compression → record the opt-in commands as a follow-up rather than silently enabling them.
- **[Concurrent clients]** Restarting the service can interrupt hooks and MCP clients → use a maintenance window, preserve the store, and verify hook recovery immediately after restart.
- **[Credential boundary]** Provider fallback or GiaoDuc experiments could mix credential stores → keep provider selection unchanged and perform any alternate-provider work in a separately authorized disposable process.
- **[Snapshot overwrite]** A restart or helper may rotate `.env.bak` → fingerprint it before the change and verify its metadata/content identity is unchanged afterward.
- **[Metric discrepancy]** Doctor and graph stats may report different graph definitions → capture both, document the semantics, and require persistence plus graph-extract success rather than treating either single count as sufficient.
