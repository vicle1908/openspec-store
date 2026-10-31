# Tasks

All tasks below describe documentation and evaluation work, not permission to alter live services. Runtime checks, downloads, installs, provider calls, cutovers, upstream submissions, and cross-repository writes require separately approved scope. Keep unexercised checks unchecked.

## 1. Establish the operating evidence ledger

- [x] 1.1 Record source revision, deployed image identity, configuration precedence, and local overlays separately; verify each entry against its cited source or read-only runtime result.
- [x] 1.2 Inventory all compatibility modifications (including unasserted rules R1-R8, dual-compiled chunks 87878.js/99834.js, and non-chunk patches) and assertions by target version, purpose, source, and behavioral check; verify that missing or renamed target chunks fail closed rather than skipping marker checks.
- [x] 1.3 Document named-volume persistence, backup verification, single-file bind-mount inode rebinding on container recreation, and operator-driven rollback; verify that no step assumes container restart removes patches, rebinds replaced single-file mounts, or guarantees zero downtime.

## 2. Evaluate feature-preserving memory alternatives

- [x] 2.1 Define a fixed relevance set with exact identifiers, paraphrases, conflicting facts, ownership boundaries, and deleted/expired records; record metrics and pass criteria before running a comparison.
- [x] 2.2 Document supported strategy/backend enums and configuration authority, retain the current Qdrant hybrid baseline, and verify that no instruction uses strategy sqlite or writes raw database settings.
- [x] 2.3 In an approved isolated evaluation, compare local sqlite-vec plus FTS5 with Qdrant-backed retrieval on the same corpus, embedding model, and queries; record relevance, cold/warm end-to-end latency, reranking, resource use, and fallback identity.
- [x] 2.4 Verify ownership, deletion, expiry, vector population, and fallback behavior for each candidate; document migration and rollback prerequisites without scheduling Qdrant removal or data deletion.

## 3. Evaluate compression, cache, and timeout correctness

- [x] 3.1 Define coding, instruction-following, protected-content, and prompt-prefix cases for optional compression; verify quality and latency acceptance criteria against the existing prose-preserving baseline.
- [x] 3.2 Inventory installed ML packages, selected model/revision, asset location, worker readiness, and cold/warm resource needs; use an approved isolated execution to verify load, timeout, and unchanged-input fallback before proposing activation.
- [x] 3.3 Document token-accounting provenance and pricing assumptions; verify zero-reduction and failure cases and label historical cost figures as estimates rather than paid-bill savings.
- [x] 3.4 Trace semantic-cache embedding outer, inner-fetch, and service deadlines; in an approved evaluation record cold, warm, timeout, and unavailable-service outcomes without relying on chat-header flags.
- [x] 3.5 Define and exercise approved cache-isolation cases for owners, system policies, tool schemas/history, and freshness-sensitive responses; record eligibility restrictions for any failing case.
- [x] 3.6 Classify enabled Redis consumers and define an approved memory-pressure evaluation; verify effects on disposable entries and enforcement state before recommending eviction, separation, or a new budget.

## 4. Assess independent optional capabilities

- [x] 4.1 Document the real packs list/install/verify/remove lifecycle, local archive/index requirements, execution target, and persistent paths; verify that Docker package presence is not confused with missing desktop packs.
- [x] 4.2 Evaluate browser-backed providers only for a named use case using the supported browser-ready image/build target; verify executable presence, launch, session persistence/recovery, access limits, and measured resource use in approved isolation.
- [x] 4.3 Document Bifrost's relay-only boundary and mode-specific behavior; in an approved evaluation verify routing attribution, HTTP errors, transport fallback, cancellation, and partial-stream failure without assuming native combos/compression/cache run on the forwarded branch.
- [x] 4.4 Assess Codex app-server independently; document the supported authentication and internal networking contract and verify streaming, cancellation, restart recovery, and the distinct benefit over the existing client before recommending deployment.
- [x] 4.5 Record which native multimodal, MCP/A2A, budget, and telemetry capabilities serve a concrete workload; define endpoint, authorization, provider/model prerequisites, and acceptance cases before any separate activation proposal.

## 5. Reconcile upstream fixes and promotion decisions

- [x] 5.1 Reconcile Gemini turn handling, lockout classification, and attempt-local timing against the target upstream revision and existing behavioral tests; document each fix's scope without presenting minified snippets or unexecuted tests as source-ready patches.
- [x] 5.2 For every proposed patch retirement, identify the released upstream replacement and required clean-image behavioral proof; verify that unrelated cache, memory, transport, and ownership changes remain accounted for.
- [x] 5.3 Record an independent promote/defer decision for each capability with evidence, security limits, resource budget, rollback, and any implementation prerequisite; keep unverified features and external approval gates open.

## 6. Validate the reconciled planning artifacts

- [x] 6.1 Check proposal, design, both deltas, and tasks for consistent scope and compare new requirements with main specs; verify that existing Qdrant and prose-preserving contracts are not silently overridden.
- [x] 6.2 After a permitted save, run store-scoped strict change validation and review parsed deltas; distinguish parser/schema success from runtime acceptance and do not mark runtime tasks complete from syntax validation.
- [x] 6.3 Prepare an approved documentation-sync mapping for the wiki and main specs; verify intended ownership and paths without editing either during this planning update.
