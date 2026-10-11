# Design

## Context

The workspace root at `~/Developer/data/` serves as a shared runtime state store (`state_store.db`, stream stores, capture spools, tenant quarantine). However, recent automated testing and exploration cycles left 61 duplicate skill directories in `data/skills/` (identical to canonical skills under `.agents/skills/`), obsolete test harness reproduction scratchpads (`data/harness-prod-repro-*`), and loose review/patch dumps.

## Goals / Non-Goals

**Goals:**
- Eliminate redundant skill trees in `data/skills/` to prevent discovery ambiguity and ensure `.agents/skills/` remains the single canonical source of truth.
- Prune empty and obsolete test reproduction directories (`harness-prod-repro-*`) from `data/`.
- Remove unmanaged task review artifacts from `data/` while preserving core state databases (`state_store.db`, `stream_store`, `quarantine`).
- Author, validate, review via Orca, and archive OpenSpec change `reconcile-data-root-and-scrap-hygiene`.
- Persist memory to AgentMemory and Notion (`ntn` CLI).

**Non-Goals:**
- Modifying operational databases (`state_store.db`, `stream_store`) or quarantined secrets (`data/quarantine/`).

## Decisions

- **Decision 1: Direct removal of data/skills**: Audit confirmed 61/61 skills in `data/skills` exist in `.agents/skills`. Deletion eliminates shadowing with zero data loss.
- **Decision 2: Remove ephemeral reproduction folders**: Empty folder `harness-prod-repro-qb71_yqg` and obsolete repro cache `harness-prod-repro-to792iqu` are ephemeral test artifacts that can be safely purged.
- **Decision 3: Retain state databases and quarantine**: Keep `state_store.db`, `stream_store`, `capture-spool`, and `quarantine` completely untouched.

## Risks / Trade-offs

- **Risk**: Deleting active runtime data.
  - **Mitigation**: Strictly target only `skills/`, `harness-prod-repro-*`, and loose `.patch`/`.md` review files. Verify database checksums before and after.
