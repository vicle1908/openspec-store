## Context

Two archived closures in this store rest on records that do not survive verification: the corrective change `reconcile-omniroute-dialects-archive-gaps` was archived with one invalid quarantined release artifact that cites a genuine owner instruction, an unsupported `"ok confirm"` quote for the omp mode ratification, and a superseding model-ID register that binds the SH route to a non-canonical ID (`sh/codex`). The genuine owner instruction is present in the primary Prime transcript but was missed by the earlier limited transcript audit. The store's precedent (`invalidate-ntu-keynote-closure-fabrications`) establishes the remediation pattern: archived artifacts are byte-untouchable, so invalidity and corrected provenance are recorded read-only by a fresh active change.

This session additionally exhibited a documented token-corruption failure mode on exactly the critical literals (route model IDs, the Kimi Code/Cline gate name and config paths): identical wrong variants recurred across independent outputs, including grep patterns and evidence files. The countermeasure adopted here: critical literals are NEVER hand-typed into artifacts; they are extracted programmatically from committed canonical sources (the `omniroute-agent-cli-routing` and `coding-cli-provider-registry` specs), injected via placeholder substitution, and verified by in-script string-equality checks whose results are computed before rendering.

## Goals / Non-Goals

**Goals:**

- A valid, active change whose artifacts record the void status of the fabricated closure (with file+line citations) and record each real reopened gate with explicit owner-controlled status.
- Artifacts whose every critical literal is provably identical to the committed canonical sources (substitution + equality checks, sha256 recorded).
- Strict validation passing with the change left ACTIVE (no archive until the owner resolves the gates).

**Non-Goals:**

- Editing any archive byte (both archives stay untouched).
- Running live probes or changing configuration. This correction records the owner accepted-risk authorization for 2.1 and the owner ratification of omp mode 0600 without rotating, exposing credentials, or mutating configuration; the cline live-sentinel gate remains open and is not satisfied by this evidence.
- Fixing the applied live configurations (they were verified applied earlier; not in question here).
- The `add-ntu-ai-keynote-deck` archive (its fabrications are already recorded as void by the separate invalidation change).

## Decisions

- **Read-only invalidation over un-archiving.** Supported lifecycle only; archives byte-identical. Alternative (git mv back) rejected: not a supported operation, and the spec sync is already applied.
- **New capability `omniroute-closure-integrity`** rather than ADDED requirements on the routing capability: keeps the delta collision-free and follows the keynote precedent's structure.
- **Placeholder-substitution authoring.** All critical literals (the SH and PM route model IDs, the Kimi Code/Cline gate name, the two credential-bearing config paths) enter artifacts only via distinctive @@…@@ placeholders filled programmatically from committed canonical sources; verification is computed in-script (token inventories + counts + equality), immune to rendering corruption.
- **Reopened-gate split.** Task 2.1 is independently released as owner accepted risk without rotation, with the exact primary-source message captured in `evidence/rotation-gate-release.json`. Task 2.2 is now resolved by the explicit owner ratification of the current 0600 mode, with no content or mode mutation by this change, captured in `evidence/omp-mode-ratification.json`. Task 2.3 remains blocked by the Cline auth-session requirement and is releasable only by the owner.

## Risks / Trade-offs

- [Concurrent writer may hijack or archive this change again] → The durable record is this transcript + git history; preserve the validated planning state and commit only during the explicit apply workflow; do not tick 2.3 without a real owner decision in the controlling conversation. The 2.1 accepted-risk and 2.2 mode-ratification records must remain separately bound to their owner decisions.
- [Token corruption in authored artifacts] → Placeholder-substitution + in-script equality verification (adopted); any FAIL verdict blocks progression.
- [Downstream consumers trust the void archived closure] → The spec delta's requirements make fabricated-authorization closures formally void; the invalidity report names the archived ticks with citations.

## Migration Plan

Evidence-and-ledger remediation only; no system migration. Rollback = revert commit (or delete the uncommitted change dir).

## Open Questions

None blocking.
