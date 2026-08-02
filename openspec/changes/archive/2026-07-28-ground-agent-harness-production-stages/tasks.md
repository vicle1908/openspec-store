## 1. Dependencies and CRITICAL-Root Baseline

- [x] 1.1 Confirm harden-agent-core-consumer-contract is complete and install its verified core version into agent-harness.
- [x] 1.2 Refresh the harness GitNexus index and rerun impact for build_graph, run_validation, GitNexusTool, and GraphifyTool; obtain confirmation before editing the CRITICAL graph root.
- [x] 1.3 Freeze characterization fixtures for topology, gate identities/routing, run/status/resume/history/report, PostgreSQL checkpoints, and the current hollow completed run.

## 2. Read-Only Transport Spike

- [x] 2.1 Define a bounded CodeIntelligencePort and deterministic fixture responses for GitNexus query/context/impact/status and Graphify query/path/freshness.
- [x] 2.2 Prove a read-only GitNexus MCP adapter can operate without shell/code-execution authority and records repository/index source identity.
- [x] 2.3 Implement bounded Graphify artifact parsing with approved-root, schema, freshness, result-count, and diagnostic-size validation.
- [x] 2.4 If the spike requires a new external dependency, stop and obtain explicit approval before adding it; otherwise record the reused dependency/API.
- [x] 2.5 Add failure tests proving unavailable/malformed adapters return needs_input or configuration failure rather than current-fresh empty evidence.

## 3. Service and Artifact Composition

- [x] 3.1 Add immutable HarnessServices and narrowed StageServices models/factories covering Jira, code intelligence, bounded files, gateway/agents, artifact store, clock, and observability.
- [x] 3.2 Back the Jira read port with tdt_core.clients Jira Cloud API v3 factories and add auth/unavailable/bounded-field tests without raw SDK clients.
- [x] 3.3 Reconstruct and close live services per runner process; add checkpoint tests proving no client, gateway, transport, or store handle is serialized.
- [x] 3.4 Wire the artifact store to append immutable revisions with digests, input/evidence references, validation, and source identity.
- [x] 3.5 Update checkpoint state to reference verified artifact identities while preserving strict type and legacy checkpoint compatibility.

## 4. Production Graph Wiring

- [x] 4.1 Incrementally update build_graph/stage-node construction to close nodes over stage definitions and narrowed services without changing topology or gate nodes.
- [x] 4.2 Wire intake to factory-owned Jira data and context/impact to non-empty current code-intelligence evidence.
- [x] 4.3 Wire model/evidence stages through the official agent_core.sdk stage-agent/toolset factory and remove the fabricated no-tools sentinel.
- [x] 4.4 Preserve pure deterministic handlers where valid, but require every artifact-producing stage to persist and validate a revision.
- [x] 4.5 Remove placeholder providers and ensure test-only factories cannot be selected by public production CLI composition.

## 5. Grounded Validation and Review

- [x] 5.1 Extend stage definitions with required/optional evidence types and freshness policies owned by local code.
- [x] 5.2 Expand validation inputs to requirements, evidence, repository examples, input/output artifact references, stage policy, and source identity.
- [x] 5.3 Replace hard-coded plan review with deterministic traceability obligations and explicit missing-evidence/mapping results.
- [x] 5.4 Add negative tests for empty/stale/wrong-repository evidence, provider-authored pass booleans, artifact digest mismatch, and unavailable artifact store.

## 6. Lifecycle, Verification, and Rollback

- [x] 6.1 Add a public-CLI production-composition fixture that yields non-empty requirements/evidence, persists artifacts, and fails when wiring is replaced by placeholders or test-only composition.
- [x] 6.2 Run the separate-process PostgreSQL run/status/decision/resume/report lifecycle with strict MessagePack types and confirm completed artifact stages do not rerun.
- [x] 6.3 Run frozen Ruff, format, strict source-plus-test mypy, full pytest/coverage, secret scan, and CLI tests in agent-harness.
- [x] 6.4 Run fresh GitNexus change detection and confirm only intended graph/stage/service processes changed.
- [x] 6.5 Exercise rollback by disabling evidence-dependent execution to needs_input while preserving readable immutable artifacts; never restore empty successful providers.
- [x] 6.6 Validate ground-agent-harness-production-stages with strict OpenSpec validation.
