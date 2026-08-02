## Context

`agent-docs-sync` has deterministic discovery/audit components and a nominal canonical pipeline, but configuration and CLI behavior diverge from that path. The loader reads only one section, some commands resolve configuration from `src/`, multiple options are discarded, default write roots include source, and dry-run still carries write-capable composition. Approval requests are not exposed as a resumable lifecycle, mappings use inconsistent field names, and newly written files are not guaranteed to be rediscovered before validation.

The change modifies only `agent-docs-sync` after the core allowlist/persistence contract is available. `run_canonical_pipeline` is CRITICAL and must be changed incrementally. The service remains a manually invoked CLI/library; no Docker or launchd service is introduced.

## Goals / Non-Goals

**Goals:**

- Make one config schema and one pipeline authoritative.
- Make command options and reports truthful.
- Remove write authority from dry-run and bound approved writes.
- Resume approvals across process restart with exactly-once mutation.
- Rediscover and validate post-write state.
- Remove independent legacy behavior.

**Non-Goals:**

- General source editing or automatic OpenSpec promotion.
- Using LangGraph checkpoints as agent-step continuation.
- Requiring an LLM for deterministic discovery/audit.
- Running as a daemon or adding distributed coordination.

## Decisions

### 1. Resolve a strict repository-root configuration

Every public command resolves the target repository first, then loads one schema from the documented root plus centralized TDT environment overrides. Unknown/legacy sections fail before gateway or write-tool construction. Migration diagnostics name supported fields but redact protected values.

Alternative: continue permissively ignoring unknown keys. Rejected because ignored configuration created false operational confidence.

### 2. Compile options into an immutable execution plan

CLI parsing produces a typed plan containing mode, repository, base reference, discovery boundary, LLM policy, durability, authority, and output policy. The canonical pipeline consumes the plan, and reports echo effective non-secret choices. Unsupported options are removed rather than reserved indefinitely.

Alternative: pass unstructured keyword arguments through stages. Rejected because unused options remain undetectable.

### 3. Express dry-run as absent authority

Read-only modes never construct or expose `WriteDocTool`, `SyncSpecTool`, or mutation equivalents. Generation uses a separate bounded toolset whose roots default to documentation only. Source/OpenSpec promotion requires another OpenSpec change and explicit authority review.

Alternative: pass `dry_run=True` into write tools. Rejected because the mutation capability still exists and can be bypassed by another call path.

### 4. Separate upstream snapshots from application lifecycle indexing

Use upstream `SqliteStepStore` plus `StepPersistence` for continuable snapshots under `$TDT_HOME/state/agent-docs-sync/steps.sqlite3`. Maintain a consumer-owned SQLite lifecycle/write ledger in a separate database in the same state directory. The application ledger indexes pending requests, actors/decisions, repository identity, normalized operation digest, and exactly-once write result without modifying upstream store tables.

Alternative: add application tables to the upstream database or use LangGraph checkpoints. Rejected because ownership/schema lifecycles differ.

### 5. Reconstruct the same composition on resume

`pending`, `list`, `approve`, `deny`, and `resume` load config, authenticate/resolve the actor through trusted local policy, reopen both stores, rebuild the same agent/toolset policy, validate request identity/expiry/path/content digest, and call the public upstream continuation API. Decisions are transactionally single-use.

### 6. Make writes idempotent before touching the filesystem

The ledger claims a key derived from run, continuation/tool call, normalized path, operation, and content digest in a transaction. A completed key returns the prior result; an in-progress/recovered key revalidates filesystem digest before deciding whether to finish or report conflict. No ledger success is recorded before atomic file replacement completes.

### 7. Validate post-write source identity

After any mutation, the pipeline rediscovers files/mappings and validates the resulting state. Execution success, compliance, approval, and write outcome are separate report fields. Discovery failure cannot appear as empty compliance.

### 8. Converge legacy paths through caller census

Legacy modules either delegate to typed canonical stages or raise migration errors, then are removed only after GitNexus/Graphify and import/CLI tests show no production callers. No placeholder `generate_updates()` path remains.

### 9. Keep observability secret-safe

Trace events carry run/pending IDs, stages, path digests, decisions, and durations, not prompts, credentials, or full generated bodies. Agentmemory may receive high-level run summaries but is not approval or write authority.

## Risks / Trade-offs

- **CRITICAL pipeline regression** → Characterize every CLI mode first and land stage-by-stage changes with detect-changes evidence.
- **SQLite crash between write and ledger completion** → Atomic replacement plus digest reconciliation makes recovery explicit and idempotent.
- **Approval replay or actor spoofing** → Resolve actors at the trusted CLI boundary and transactionally bind decisions to request identity and expiry.
- **Strict config breaks current files** → Provide deterministic migration guidance and a one-time config conversion example without secret values.
- **Pending runs outlive a rollback** → Preserve both databases; rollback disables generation but keeps inspection/export available.

## Migration Plan

1. Add current-path characterization and negative authority tests.
2. Introduce strict config and typed execution plans; migrate repository config.
3. Split read-only and write-capable composition and enforce root policy.
4. Add upstream SQLite snapshots plus the application lifecycle/write ledger.
5. Add lifecycle commands and separate-process continuation tests.
6. Add idempotent atomic writes, rediscovery, and truthful reports.
7. Delegate/remove legacy paths after caller census.
8. Run full compatibility, security, typing, and fixture verification.

Rollback disables generation and resume while preserving deterministic audit and both SQLite databases for later recovery. No destructive downgrade runs automatically.

## Open Questions

- During implementation, confirm which upstream store query APIs can support listing; the consumer index remains authoritative for CLI listing even if upstream listing is available.
