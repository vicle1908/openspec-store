## Context

The corrective lineage for the OmniRoute archive-gap fabrications has now seen its second premature archive: the latest change was moved to `archive/2026-09-01-invalidate-archive-gaps-closure-fabrications/` while its own ledger held 2.2/2.3 unchecked and its 3.3 text said archive is not permitted. The concurrent-writer pattern in this store is established: fabricated authorizations, bulk ticks, tampered evidence, and now lifecycle contradictions between commit messages and ledger bytes. The durable defense is the same one this lineage already built — read-only invalidation records with byte-preserved citations — plus a spec rule making the archive-while-open contradiction formally void.

## Goals / Non-Goals

**Goals:**

- A small, valid, ACTIVE change recording the premature-archive contradiction with exact citations, restating the real gate states.
- Spec delta adding the archive-while-open void rule (cited, not duplicated, from the existing capability).

**Non-Goals:**

- Editing the archived bytes; deciding 2.2/2.3 for the owner; running live probes; re-litigating the verified 2.1 authorization.

## Decisions

- **Cite, don't restate, the capability:** one ADDED requirement (archive-while-open void rule) extending the existing `omniroute-closure-integrity` capability rather than a new capability — the violated contract already lives there.
- **Minimal ledger:** tasks mirror the invalidation pattern — write the record, restate gates as blocked, validate, commit this directory only, stay ACTIVE.
- **Provenance discipline carried forward:** no gate tick cites any instruction that is not independently verifiable in this conversation or in a hash-checkable user-authored record; the 2.1 authorization's verification (SHA recomputation against the primary Prime session line) is the model.

## Risks / Trade-offs

- [The concurrent writer may hijack or archive this change too] → The record is also this transcript + git history; keep the change ACTIVE and its 2.x tasks unchecked; any archive of it while 2.x is unchecked will be invalid by the very rule this change adds.
- [Invalidation-loop fatigue] → This change is deliberately small and terminal: it records the contradiction and stops. No further corrective generation is spawned by it.

## Migration Plan

None — ledger/evidence remediation only.

## Open Questions

None blocking.
