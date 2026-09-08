## Why

AgentMemory graph extraction continues to enqueue persistence work after session completion, and graph writes to iii `state::set` repeatedly time out at the old 180-second invocation boundary. This backlog creates noisy failures and resource pressure even though provider requests, observation capture, summarization, and session completion are functioning; the persistence path needs its own bounded, failure-isolated operating contract.

## What Changes

- Add an explicit graph-persistence backpressure capability for graph extraction triggered by stopped sessions.
- Use only the official `@agentmemory/agentmemory@0.9.29` release; do not patch, fork, rebuild, or modify AgentMemory source code in this change.
- Temporarily disable graph extraction in the installed runtime because version 0.9.29 exposes no supported graph backpressure controls and no newer published release is available.
- Preserve observation capture, summarization, consolidation, embeddings, and session-end acknowledgement while graph extraction is disabled.
- Record source-level graph backpressure as a deferred follow-up, not as an implementation task in this change.
- Make the active launchd-managed iii configuration path and graph persistence settings explicit; keep legacy configuration references aligned where applicable.
- Add safe diagnostics for queue depth, batch latency, timeout count, and recovery after restart without logging credentials or memory payloads.
- Define a disposable validation mode for provider failure and invalid-model behavior needed by the related provider-stability change.
- Provide backup-first rollout and rollback procedures for graph-related runtime settings.

## Capabilities

### New Capabilities

- `agentmemory/graph-persistence-backpressure`: bounded graph extraction scheduling, persistence failure isolation, diagnostics, and recovery behavior.

### Modified Capabilities

- `developer-memory`: session-end and observation-capture behavior remains available when graph persistence is delayed or unavailable.
- `agentmemory/provider-stability`: completion of failure-isolation and disposable-provider verification without coupling those tests to live user sessions.

## Impact

- User-managed AgentMemory runtime and launchd-managed iii configuration.
- Installed AgentMemory graph extraction trigger and persistence scheduling behavior.
- iii state-store `state::set` invocation load and timeout telemetry.
- Session-end, observation-capture, summarization, consolidation, and graph APIs.
- Local logs, health/diagnostic probes, redacted evidence, and rollback backups.
- OpenSpec delta specs and task evidence; no credentials, raw memory payloads, or persistent state database migration.
