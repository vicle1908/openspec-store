# Proposal: invalidate-ntu-keynote-closure-fabrications

## Why

The change `add-ntu-ai-keynote-deck` was archived on 2026-08-31 (archive
`2026-08-31-add-ntu-ai-keynote-deck`) with `decision: accepted`, but verifiable checks show its
release decision contains fabricated gate closures:

1. **Section 4 (editorial/copy) marked `accepted`** while the same archive's
   `acceptance/verification.json` task-4.1 record lists `human-vietnamese-editorial-review-not-submitted`
   as an open blocker, and the only editorial artifact is `editorial-review-simulation.json` whose
   own status reads `simulation-only-not-human-approval`.
2. **Section 5 (rehearsal/release identity) marked `accepted`** with "Presentation session and venue
   delivery successfully concluded" — no venue-rehearsal record for the submitted digest exists in the
   archive, and the archived external-repo rehearsal record predates the registered candidate.
3. **`release_ref` marked `status: verified`** for `refs/tags/ntu-ai-keynote-v1.0.0`, but that tag does
   not exist in the external repository (verified read-only 2026-08-31: `git rev-parse` fails; only two
   unrelated archive tags exist). Task 5.2 required a verified annotated tag at that exact ref.

The archive's own task 6.1 contract says `decision: accepted` may be emitted only when every mapped
requirement is accepted with no blocker remaining, and task 6.2 required re-verification of the
cited hashes and the fixed ref. Both were falsified. The store forbids editing archived artifacts in
place; this corrective change records the invalidity read-only and supersedes the fabricated closure.

## What Changes

- Records a value-blind invalidity report for the archived closure with file+line citations.
- Marks the archived `decision: accepted` and `closure.json` as void evidence for any downstream
  consumer (the keynote remains un-released; no tag, no human editorial record, no venue rehearsal).
- Adds a durable spec requirement that release decisions SHALL cite verifiable evidence for every
  accepted gate (hash-bound record references), and that tag/ref claims SHALL be re-verified against
  the live repository at decision time.
- Does NOT edit the archive, the external repository, any credential, or the applied keynote files.

## Impact

- New capability: `ntu-keynote-release-integrity` (supersedes the archived closure record read-only).
- The `add-ntu-ai-keynote-deck` archive stays byte-identical; consumers must treat its acceptance as
  void until the real external gates (human editorial review, venue rehearsal, annotated tag) are
  performed and a new closure is recorded under a fresh change.
