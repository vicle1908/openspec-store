# Design: invalidate-ntu-keynote-closure-fabrications

## Verified findings (value-blind, 2026-08-31)

| # | Archived claim | Ground truth (read-only) | Citation |
|---|---|---|---|
| F-1 | `release-decision.json` gate_evaluations.section_4 = `accepted` | `verification.json` task 4.1 lists `human-vietnamese-editorial-review-not-submitted` blocker; only editorial artifact is the simulation (`simulation-only-not-human-approval`) | archive acceptance/verification.json task_results.4.1.editorial_review.external_blockers; acceptance/editorial-review-simulation.json |
| F-2 | section_5 = `accepted`; `rehearsal_and_presentation.session_status: completed` | No venue-rehearsal record for digest 3f299c876… exists in the archive or the external repo; the external `evidence/rehearsals/copied-folder.json` predates the registered candidate | archive release-decision.json rehearsal_and_presentation; external repo read-only listing |
| F-3 | `release_ref.status: verified` for `refs/tags/ntu-ai-keynote-v1.0.0` | `git rev-parse refs/tags/ntu-ai-keynote-v1.0.0` fails; the tag does not exist; only archive/ntu-brand-theme-candidate-4fb4c86 and archive/visual-contract-review-986be2f tags exist | external repo, verified 2026-08-31 |

## Approach

- Corrective-change pattern (same as reconcile-omniroute-dialects-archive-gaps): archive stays
  byte-identical; superseding invalidity record + spec delta live here.
- ADDED-only delta (no MODIFIED blocks): two new requirements for the new capability.
- Evidence is value-blind: hashes, refs, statuses, line citations. No credential or key material.

## Decisions

- Do not attempt un-archiving; the store has no such lifecycle operation and the spec sync at archive
  is already applied. A void-record supersession is auditable and safe.
- The invalidity is closure-record-level: the keynote implementation files themselves are not accused;
  only the acceptance decision and its cited gates.
- Future closure of the keynote (real human review, real rehearsal, real tag) must occur under a NEW
  change that re-registers the exact candidate and records the real evidence.
