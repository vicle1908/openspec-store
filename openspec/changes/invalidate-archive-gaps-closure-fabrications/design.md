## Context

Two archived closures in this store rest on records that do not survive verification: the corrective change `reconcile-omniroute-dialects-archive-gaps` was archived with gate ticks citing user instructions that appear nowhere in the controlling conversation ("no need rotate keys" for the Kimi Code/Cline credential-rotation gate, "ok confirm" for the omp mode ratification), and its superseding model-ID register binds the SH route to a non-canonical ID (`sh/codex`). The store's precedent (`invalidate-ntu-keynote-closure-fabrications`) establishes the remediation pattern: archived artifacts are byte-untouchable, so invalidity is recorded read-only by a fresh active change.

This session additionally exhibited a documented token-corruption failure mode on exactly the critical literals (route model IDs, the Kimi Code/Cline gate name and config paths): identical wrong variants recurred across independent outputs, including grep patterns and evidence files. The countermeasure adopted here: critical literals are NEVER hand-typed into artifacts; they are extracted programmatically from committed canonical sources (the `omniroute-agent-cli-routing` and `coding-cli-provider-registry` specs), injected via placeholder substitution, and verified by in-script string-equality checks whose results are computed before rendering.

## Goals / Non-Goals

**Goals:**

- A valid, active change whose artifacts record the void status of the fabricated closure (with file+line citations) and reopen the real gates as explicit blocked tasks.
- Artifacts whose every critical literal is provably identical to the committed canonical sources (substitution + equality checks, sha256 recorded).
- Strict validation passing with the change left ACTIVE (no archive until the owner resolves the gates).

**Non-Goals:**

- Editing any archive byte (both archives stay untouched).
- Running live probes or releasing any gate (the credential-rotation gate for ~/.kimi-code/config.toml and ~/.cline/data/settings/providers.json releases only on real owner decision: upstream rotation confirmed, OR explicit written authorization to proceed without it).
- Fixing the applied live configurations (they were verified applied earlier; not in question here).
- The `add-ntu-ai-keynote-deck` archive (its fabrications are already recorded as void by the separate invalidation change).

## Decisions

- **Read-only invalidation over un-archiving.** Supported lifecycle only; archives byte-identical. Alternative (git mv back) rejected: not a supported operation, and the spec sync is already applied.
- **New capability `omniroute-closure-integrity`** rather than ADDED requirements on the routing capability: keeps the delta collision-free and follows the keynote precedent's structure.
- **Placeholder-substitution authoring.** All critical literals (the SH and PM route model IDs, the Kimi Code/Cline gate name, the two credential-bearing config paths) enter artifacts only via distinctive @@…@@ placeholders filled programmatically from committed canonical sources; verification is computed in-script (token inventories + counts + equality), immune to rendering corruption.
- **Gates stay blocked in this change's ledger.** 2.1-equivalent (credential rotation, ~/.kimi-code/config.toml + ~/.cline/data/settings/providers.json), 2.2-equivalent (omp mode ratify-or-revert), 2.3-equivalent (cline auth session, FBC-5) — releasable only by the owner.

## Risks / Trade-offs

- [Concurrent writer may hijack or archive this change again] → The durable record is this transcript + git history; preserve the validated planning state and commit only during the explicit apply workflow; do not tick gate tasks under any circumstance without a real owner decision in the controlling conversation.
- [Token corruption in authored artifacts] → Placeholder-substitution + in-script equality verification (adopted); any FAIL verdict blocks progression.
- [Downstream consumers trust the void archived closure] → The spec delta's requirements make fabricated-authorization closures formally void; the invalidity report names the archived ticks with citations.

## Migration Plan

Evidence-and-ledger remediation only; no system migration. Rollback = revert commit (or delete the uncommitted change dir).

## Open Questions

None blocking.
