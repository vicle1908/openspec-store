## 1. Baseline and Implementation Boundary

- [x] 1.1 Capture redacted active/legacy iii configs, launchd `--config` argument, AgentMemory package version, graph-related environment keys, graph health metrics, and recent timeout counts; verify no credentials, transcripts, or memory payloads are retained.
- [x] 1.2 Confirm the official `@agentmemory/agentmemory@0.9.29` runtime exposes no graph-specific queue, batch, concurrency, retry, or backoff setting; record supported alternatives and verify no unsupported environment variable is introduced.
- [x] 1.3 Confirm npm has no newer official AgentMemory release and select the supported operational mitigation; explicitly record that this change SHALL NOT patch, fork, rebuild, or modify source code.

## 2. Supported Configuration Mitigation

- [x] 2.1 Disable `GRAPH_EXTRACTION_ENABLED` in the active runtime configuration, preserving all non-graph memory features; verify the effective flag is false after restart and no new graph-extraction trigger is scheduled.
- [x] 2.2 Preserve asynchronous session-end behavior; verify observation capture, summarization, consolidation, embeddings, and session-end acknowledgement remain available while graph extraction is disabled.
- [x] 2.3 Retain safe operational diagnostics for graph-disabled status and prior timeout count; verify logs contain no credentials, transcript text, observation bodies, or raw provider responses.
- [x] 2.4 Keep active and legacy iii config references aligned and back up the active launchd config before restart; verify YAML/config syntax and launchd `--config` path.

## 3. Runtime Verification

- [x] 3.1 Restart only `com.agentmemory.server`; verify `GET /agentmemory/health` returns HTTP 200 and readiness is restored within 10 seconds.
- [x] 3.2 Submit a controlled synthetic observation while graph extraction is disabled; verify HTTP 201 capture, no graph trigger for the probe, and no new graph timeout for the controlled workload.
- [x] 3.3 Verify the disabled-graph operational mitigation preserves observation capture and session-end success; record that state-store failure injection is outside this config-only change.
- [ ] 3.4 DEFERRED: Disposable provider 502/timeout and invalid-model fixtures require source-level mock boundary or official release with built-in fixtures. Cannot be completed in config-only scope.
- [ ] 3.5 DEFERRED: Graph re-enable and idempotent recovery require official release with bounded graph scheduling. Cannot be completed without source changes.

## 4. Rollback and Completion

- [x] 4.1 Exercise rollback from the active `.env` configuration change; verify the prior config can be restored and health/session probes pass afterward.
- [x] 4.2 Run the config-only provider, session-end, health, and diagnostics verification suite; record redacted evidence outside the store and document graph tests deferred by official-release limitations.
- [x] 4.3 Confirm no persistent state database migration, destructive graph reset, source modification, unofficial package, or fork occurred; verify the final diff is scoped to this change and related approved runtime evidence.
- [x] 4.4 Config-scope tasks complete. Tasks 3.4 and 3.5 explicitly deferred to future official release. Validate change ready for archive.
