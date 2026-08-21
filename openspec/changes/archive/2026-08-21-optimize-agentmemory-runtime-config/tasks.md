## 1. Freeze ownership and baseline

- [x] 1.1 Confirm the sole maintenance owner for the user-owned AgentMemory launchd service and `~/.agentmemory/.env`; verify the unrelated active OpenSpec change `align-jti-skill-runtime-contract` remains out of scope and record the decision in the evidence ledger.
- [x] 1.2 Capture a redacted baseline containing AgentMemory version, launchd/iii PIDs, non-secret provider/model/endpoint shape, timeout values, feature flags including current `AGENTMEMORY_REFLECT=true` and `AGENTMEMORY_SLOTS=memory`, store path/size, `AGENTMEMORY_AGENT_SCOPE=shared`, viewer port, both base URLs, the presence-only two-key LLM-versus-local-embedding boundary, and exact current configuration-line fingerprints; fingerprint the pre-existing `.env.bak` without overwriting it and verify no credential value appears in the artifact.
- [x] 1.3 Run the current baseline matrix (`agentmemory doctor --dry-run`, liveness, health, flags, exact PostToolUse hook, observation readback, embedding, summarize, graph extract, smart search, sessions, graph stats) and record commands, bounds, exits/statuses, provider-error delta, active-invocation measurements, the doctor/status graph metric discrepancy, and iii `default_timeout=180000` evidence.

## 2. Apply the bounded default configuration

- [x] 2.1 Update only the allowlisted AgentMemory environment entries: set `OPENAI_TIMEOUT_MS=90000`, `AGENTMEMORY_LLM_TIMEOUT_MS=90000`, make `AGENTMEMORY_AUTO_COMPRESS=false`, `AGENTMEMORY_ALLOW_AGENT_SDK=false`, `AGENTMEMORY_SLOTS=false`, and `AGENTMEMORY_REFLECT=false` explicit, and preserve the tested default `shopapikey`/`fable-5`, local embedding, graph, consolidation, context-injection, snapshot, decay, all-tool settings, `AGENTMEMORY_AGENT_SCOPE=shared`, viewer port, both base URLs, and the separate embedding credential line; verify the redacted diff contains no credential, `.env.bak` change, or unrelated key.
- [x] 2.2 Restart only the launchd-managed AgentMemory worker and its owning iii engine during a declared maintenance window; verify the new process identity, pinned package/iii versions, liveness, health, KV connectivity, and closed circuit before continuing.
- [x] 2.3 Confirm that the configuration does not enable GiaoDuc, Anthropic Messages, provider fallbacks, image embeddings, Claude/Obsidian bridges, or any credential-store copy; verify the effective provider/model/embedding route, two-key boundary, `.env.bak` identity, and `AGENTMEMORY_SLOTS=false`/`AGENTMEMORY_REFLECT=false` semantics through non-secret diagnostics.

## 3. Verify behavior and load containment

- [x] 3.1 Rerun the complete default feature matrix from task 1.3 and require successful hook capture, observation readback, embedding dimension match, default-provider summarization, LLM graph extraction, smart search, session listing, graph statistics, and healthy service status.
- [x] 3.2 Exercise controlled provider-failure/timeout behavior in a disposable or mocked probe and verify a failed LLM request releases within the selected AgentMemory timeout, record whether iii `default_timeout=180000` is binding, and verify the failure does not hold the service unhealthy or block observation capture.
- [x] 3.3 Compare baseline and candidate evidence for summary/graph p50/p95 latency, hook-to-observation latency, active invocations, heap pressure, KV latency, provider/index error deltas, and doctor-versus-status graph metrics; keep the candidate incomplete if any required gate regresses or the metric discrepancy is unexplained.

## 4. Rollback and handoff evidence

- [x] 4.1 Rehearse rollback from the frozen baseline lines: restore only the prior allowlisted values, restart the same service boundary, and rerun liveness, health, hook, summary, graph, search, and session checks; verify the persistent store is unchanged.
- [x] 4.2 Write the final redacted evidence ledger under the change root with pre/post configuration fingerprints, exact commands and results, service identities, latency/load comparison, rollback result, `.env.bak` preservation, provider-key boundary, review report paths, and unresolved follow-up for the separate pinned-slots semantic mismatch.
- [x] 4.3 Recheck OpenSpec status, confirm `skip_specs: true` remains explicit with no delta-spec files, and leave implementation/archive decisions for a separate user-authorized workflow.
