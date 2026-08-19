# Design: Memory Consolidation Spec

## Problem

The memory facade routes operations across context/scratch/long_term/vector but has no cross-layer data movement. Scratches accumulate without cleanup. Long_term entries with expired TTLs are only removed by `cleanup_expired()` which must be called manually. There's no promotion of frequently-accessed scratch data to durable storage.

## Architecture

```
┌─────────────────────────────────────────────────┐
│              Memory Facade (current)             │
│                                                 │
│  context ◄── in-process buffer (bounded)        │
│  scratch ◄── filesystem (per-task)              │
│  long_term ◄── Postgres JSONB (TTL)            │
│  vector ◄── pgvector (semantic search)          │
│                                                 │
│  NO cross-layer movement currently              │
└─────────────────────────────────────────────────┘

                    │
                    ▼  (this spec defines)

┌─────────────────────────────────────────────────┐
│          ConsolidationEngine (future)            │
│                                                 │
│  Trigger: after N recalls or explicit call       │
│                                                 │
│  Promote: scratch → long_term                   │
│    WHEN access_count > promotion_threshold       │
│    AND key not already in long_term              │
│                                                 │
│  Demote: long_term → deleted                    │
│    WHEN expires_at < NOW                         │
│    AND access_count == 0                         │
│                                                 │
│  Merge: long_term ← long_term                   │
│    WHEN duplicate keys across sessions           │
│    AND recency wins                              │
│                                                 │
│  Metrics: promoted/demoted/merged/expired counts │
└─────────────────────────────────────────────────┘
```

## Key Design Decisions

1. **Consolidation is opt-in** — existing consumers are unaffected
2. **Consolidation runs in-process** — no separate daemon required
3. **Metrics are returned, not stored** — consumers decide how to record them
4. **Conflict resolution: recency wins** — most recently written value overrides
5. **Scratch access tracking** — add `access_count` to scratch entries (new field)
