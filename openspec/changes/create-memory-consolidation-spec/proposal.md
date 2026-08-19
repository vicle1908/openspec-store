# Proposal: Create Memory Consolidation Spec

## Why

Six memory specs exist (`memory-framework`, `memory-system`, `vector-memory-search`, `agent-core-memory-enhancement`, `agent-core-memory-lifecycle`, `developer-memory`) but none cover automatic consolidation — the process of promoting frequently-accessed scratch items to long_term, demoting stale long_term items, and merging duplicate keys. The `Memory` facade in `facade.py` routes operations across 4 layers (context, scratch, long_term, vector) but has no logic for data movement between layers. Without consolidation, scratch data is lost on cleanup and long_term accumulates stale entries indefinitely.

Modern memory systems (MemGPT/Letta, Zep) handle this automatically. Our spec gap means consumers must manually manage cross-layer data flow.

## What Changes

1. Create a `memory-consolidation` spec defining:
   - Consolidation trigger (after N recall operations or on explicit call)
   - Promotion policy (scratch → long_term when access_count > threshold)
   - Demotion policy (long_term → deleted when TTL expired and access_count == 0)
   - Conflict resolution (recency wins for duplicate keys)
   - Consolidation metrics (promoted, demoted, merged, expired counts)
2. Add a `ConsolidationEngine` design to `design.md`
3. No code implementation in this change — spec-only

## Scope

- `openspec/specs/memory-consolidation/spec.md` — NEW: consolidation spec
- Delta specs within the change directory

## Out of Scope

- Implementation of ConsolidationEngine (separate follow-up change)
- Changes to existing 6 memory specs (they remain valid)
- Changes to facade.py or any backend

## Overlap Note

The `align-jti-skill-runtime-contract` active change touches the skill system but does not overlap with memory consolidation. These are independent.
