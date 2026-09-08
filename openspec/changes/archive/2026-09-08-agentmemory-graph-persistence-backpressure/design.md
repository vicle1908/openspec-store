## Context

See proposal.md for motivation. The installed AgentMemory runtime triggers `mem::graph-extract` asynchronously from `event::session::stopped`; graph persistence writes nodes, edges, degree counters, and snapshots through iii state operations. The launchd-managed iii process uses `/Users/androidteam/Library/Application Support/agentmemory/iii-config.yaml`, while `~/.agentmemory/iii-config.yaml` is a legacy reference. Current logs show graph extraction failures at `state::set` after large queued workloads, while observation capture and session summarization continue.

## Goals / Non-Goals

**Goals:**

- Bound graph extraction batch size, queue capacity, and persistence concurrency.
- Keep graph work asynchronous and isolated from session-end acknowledgement.
- Make timeout, retry, defer, and recovery behavior observable without sensitive payloads.
- Provide an operationally safe rollout and rollback path for the active launchd configuration.
- Provide disposable provider-failure fixtures for the related provider-stability verification.

**Non-Goals:**

- Do not rewrite the persistent state database or migrate existing graph data.
- Do not disable graph extraction as the permanent solution.
- Do not change client ownership boundaries or provider selection.
- Do not emit transcript contents, observation bodies, credentials, or raw provider responses in diagnostics.

## Decisions

### 1. Use bounded asynchronous graph work

Graph extraction SHALL remain fire-and-forget from session stop, but the scheduler SHALL impose a fixed batch size, queue capacity, and concurrency limit. A bounded queue is preferred over unbounded Promise fan-out because the current failure pattern is resource pressure in state writes, not lack of provider connectivity.

Alternative rejected: synchronously waiting for graph extraction during session end, because it would reintroduce the original hook-cancellation failure mode.

### 2. Prefer coalescing/defer over aggressive retries

When queue capacity or state writes are saturated, work SHALL be deferred or coalesced and retried with bounded backoff. Retries SHALL have a maximum attempt count and SHALL not duplicate nodes or edges. This avoids amplifying `state::set` contention.

Alternative rejected: immediate unbounded retries, because they increase pressure and obscure recovery status.

### 3. Keep the active iii timeout as an outer bound

The active launchd config remains the source of truth for `workers[iii-http].config.default_timeout`; graph persistence settings must not rely on the legacy config path. Graph operation deadlines SHALL be shorter than the engine deadline where supported, allowing failed batches to return before iii forcibly terminates them.

### 4. Instrument outcomes, not payloads

Diagnostics SHALL record queue depth, batch size, batch duration, attempt number, timeout category, and recovery status. Identifiers may be opaque batch/session IDs, but logs SHALL not include observation text, prompts, transcripts, API keys, or raw provider responses.

### 5. Validate failures in disposable fixtures

Provider 502, provider timeout, and invalid model alias behavior SHALL be tested against a local disposable provider/configuration or mock boundary. The live provider and persistent production-like state SHALL not be deliberately poisoned for testing.

## Risks / Trade-offs

- [Deferred graph work increases staleness] -> expose queue depth and oldest deferred age; retry after recovery.
- [Coalescing can hide per-observation granularity] -> retain opaque batch counters and idempotent graph keys.
- [Lower concurrency reduces throughput] -> measure batch latency and recovery time before tuning upward.
- [Runtime config path drift] -> verify launchd `--config` argument and keep active/legacy references aligned.
- [Rollback interrupts graph work] -> backup configs first and verify session-end/observation health after restart.

## Migration Plan

1. Capture redacted active/legacy config, launchd arguments, graph metrics, and log baseline.
2. Create timestamped backups of both iii config paths and any graph scheduler settings.
3. Apply bounded batch, queue, concurrency, retry, and diagnostic settings to the active config/source supported by the installed runtime.
4. Validate config syntax and restart only `com.agentmemory.server` through launchd.
5. Verify `/agentmemory/health`, synthetic observation capture, and synthetic session-end response.
6. Run a controlled graph workload and confirm no unbounded queue growth, bounded failures, and recovery after state availability returns.
7. Run disposable provider-failure and invalid-model fixtures.
8. If a gate fails, restore active and legacy backups, restart, and re-run health/session probes.

## Research Findings

- The installed AgentMemory build exposes `REBUILD_EMBED_BATCH_SIZE` for embedding index rebuilds and `SUMMARIZE_CHUNK_CONCURRENCY` for summarization, but no graph-specific queue, batch, concurrency, retry, or backoff environment setting.
- `mem::graph-snapshot-rebuild` has a local `BATCH_SIZE=100`, but that applies only to snapshot rebuild index writes and does not bound `mem::graph-extract` persistence.
- `event::session::stopped` invokes `mem::graph-extract` asynchronously with a void action; graph extraction persists nodes, edges, degree counters, and snapshots through multiple `state::set` calls.
- The active launchd iii process uses `/Users/androidteam/Library/Application Support/agentmemory/iii-config.yaml`; its configured `default_timeout` is now 75000 ms. Existing 180000 ms messages are associated with queued graph work and/or an internal iii invocation path, not a supported graph-specific AgentMemory setting.

These findings mean the implementation cannot safely be expressed as an environment-only configuration change. The installed version is 0.9.29, npm exposes no newer release, and neither the package README nor installed source documents graph-specific queue, batch, concurrency, retry, or backoff controls. No supported package upgrade boundary is available in this rollout.

### Selected implementation boundary

This change will use only the official `@agentmemory/agentmemory@0.9.29` release and supported runtime configuration. No AgentMemory source patch, fork, rebuild, or unofficial package is allowed. The operational mitigation is to disable `GRAPH_EXTRACTION_ENABLED` while preserving observation capture, summarization, consolidation, embeddings, and session-end behavior. This is explicitly temporary, backup-first, and reversible; it prevents new graph work from adding to the existing state-store backlog. A future source/package change must re-enable graph extraction only after bounded graph scheduling exists.

No unsupported variable names SHALL be introduced, and no graph reset or persistent state rewrite SHALL be performed.

## Open Questions

None blocking execution. A future source-level backpressure change may define supported graph scheduler settings after upstream or a maintained fork provides them.