## Context

agent-docs-sync has a fully implemented but disconnected memory module. The pipeline recomputes all classification, link checking, and Diataxis enforcement on every run. The `SyncState` and `MetricsStore` classes exist but are never called from production code.

### Current Pipeline Flow (no memory)

```
discover_handler → audit_handler → generate_handler → validate_handler
     ↓                  ↓                ↓                  ↓
  scan ALL files    check ALL links   LLM generate      check ALL links AGAIN
  classify ALL      enforce Diataxis  per gap            enforce Diataxis AGAIN
  (no caching)      (no caching)      (no caching)       (no caching)
```

### Proposed Pipeline Flow (with memory)

```
discover_handler → audit_handler → generate_handler → validate_handler
     ↓                  ↓                ↓                  ↓
  check staleness   check cache       LLM generate      check cache
  (via SyncState)   (via context)     (uncached)        (via context)
  skip if fresh     skip unchanged    (LLM = expensive)  skip unchanged
```

## Goals / Non-Goals

**Goals:**
- Wire existing SyncState and MetricsStore into pipeline handlers
- Enable incremental discovery (skip re-scanning unchanged repos)
- Cache link/Diataxis validation results per file + content hash
- Track cross-repo metrics (cost, quality scores, run counts)
- Migrate existing YAML state files to Memory on first run

**Non-Goals:**
- Modifying agent-core's Memory module
- Replacing the YAML StateTool used by agent tool-calling
- Adding LLM response caching (generation is intentionally uncached)
- Changing the pipeline's sequential architecture

## Decisions

### D1: Wire SyncState via state dict injection (not global singleton)

**Decision:** Construct `SyncState(memory)` at pipeline entry and pass via `state["sync_state"]`.

**Rationale:** The pipeline handlers already check `state.get("sync_state")` and skip when absent. This is the minimal-change approach — just ensure the entry points (`run_full_pipeline`, `run_full_audit`) construct and inject it.

**Alternatives considered:**
- Global singleton → rejected; breaks testability and multi-repo isolation
- Constructor injection on handlers → rejected; changes handler signatures

### D2: Cache validation results in Memory context layer

**Decision:** After link/Diataxis checks, store results keyed by `{file_path}:{content_hash}` in the context layer.

**Rationale:** The context layer is in-process and session-scoped — perfect for per-run caching. Content-hash invalidation ensures stale results are recomputed. This eliminates the duplicate validation (audit + validate both check the same files).

**Alternatives considered:**
- Disk cache → rejected; adds I/O, context layer is sufficient for per-run dedup
- Skip validate_handler entirely → rejected; validation must run after generate

### D3: MetricsStore with graceful degradation

**Decision:** Construct MetricsStore only when Postgres long_term is available. When unavailable, metrics are no-ops.

**Rationale:** The existing `MetricsStore._has_long_term` guard already handles this. Postgres is optional in agent-docs-sync config. Metrics should not block the pipeline when Postgres is down.

## Risks / Trade-offs

- **[Risk] SyncState staleness check adds latency** → Mitigation: The check is a single `memory.retrieve()` call — sub-millisecond with filesystem backend. Much cheaper than the scan it replaces.

- **[Risk] Content-hash invalidation may miss semantic changes** → Mitigation: Git commit hash covers file-level changes. Content hash covers within-file changes. The combination is sufficient for link/Diataxis validation.

- **[Risk] Migration may fail on corrupt YAML** → Mitigation: `migrate_yaml_to_memory()` already handles missing files and already-migrated state. YAML parsing errors would leave the original file intact.
