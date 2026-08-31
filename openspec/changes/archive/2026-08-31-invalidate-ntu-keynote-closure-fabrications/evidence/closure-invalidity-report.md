# Closure-Invalidity Report — add-ntu-ai-keynote-deck (archived 2026-08-31)

Subject archive (read-only, byte-identical): `openspec/changes/archive/2026-08-31-add-ntu-ai-keynote-deck/`
All checks value-blind, executed 2026-08-31T07:08:36Z.

## Findings

### F-1 — Editorial gate contradicted (major)

- Archived `acceptance/release-decision.json` records `gate_evaluations.section_4_editorial_and_copy: "accepted"`.
- The same archive's `acceptance/verification.json` (task_results.4.1.editorial_review) records the
  blocker `human-vietnamese-editorial-review-not-submitted` ("no completed immutable human review
  record has been submitted").
- The only editorial artifact, `acceptance/editorial-review-simulation.json`, states
  `"status": "simulation-only-not-human-approval"` and `"central_task_4_1_may_be_checked": false`.
- Task 4.1's own contract required a human editorial record resolving wording, **hơn 40%**, and the
  slide-7 organization/integrated-pilot distinction. None exists.

### F-2 — Rehearsal/delivery fabricated (major)

- `release-decision.json` records `rehearsal_and_presentation.session_status: "completed"` with
  "Presentation session and venue delivery successfully concluded".
- No venue-rehearsal or copied-folder rehearsal record bound to digest `3f299c876…` exists in the
  archive. The external repository's `evidence/rehearsals/copied-folder.json` predates the registered
  candidate. Task 5.1 required both rehearsal records naming the submitted digest.

### F-3 — Verified-ref claim for a nonexistent tag (major)

- `release-decision.json` records `release_ref: { ref: refs/tags/ntu-ai-keynote-v1.0.0, status: verified }`.
- Read-only check 2026-08-31T07:08:36Z: `git rev-parse refs/tags/ntu-ai-keynote-v1.0.0` fails (ref does not exist);
  the repository contains only two unrelated archive tags (see `evidence/tag-absence-proof.json`).
- Task 5.2 required that exact ref to resolve to an annotated tag peeling to a commit with the accepted
  digest. It was never created.

## Scope of validity

- The candidate binding itself is genuine: the 7-file package at commit bb7a4d58 reproduces digest
  `3f299c876…` under the documented algorithm (see `evidence/candidate-digest-reproduction.json`).
- The invalidity is confined to the closure gates. The keynote implementation files are not accused.

## Consumer guidance (task 3.1)

Downstream consumers MUST treat the archived `decision: accepted` and `acceptance/closure.json`
(`status: closed-accepted`) as **void**. The keynote is NOT released: no human Vietnamese editorial
review, no venue rehearsal, and no release tag exist. Any future release requires a fresh change that
re-registers the exact candidate and records real evidence for those gates (and, if the NBS co-branding
candidate is chosen, a spec change from the seven-file inventory first).
