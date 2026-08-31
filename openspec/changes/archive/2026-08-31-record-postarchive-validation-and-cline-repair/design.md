# Design: record-postarchive-validation-and-cline-repair

## Validation method

- Byte-level comparisons via programmatic extraction (no hand-typed identifiers; the workstation has a
  documented hyphenated-token display corruption and every comparison was done in code).
- Read-only git checks against the external `ntu-keynote` repository for the tag claim.
- Value-blind sha256/mode comparisons against the archived current-state freeze for all 31 surfaces.

## Findings matrix

| Check | Result |
|---|---|
| Keynote F-1 editorial contradiction | CONFIRMED TRUE (decision accepted vs recorded not-submitted blocker; only simulation artifact) |
| Keynote F-2 rehearsal fabrication | CONFIRMED TRUE (no record names digest 3f299c876…) |
| Keynote F-3 nonexistent tag | CONFIRMED TRUE (`git rev-parse` rc=128; two unrelated archive tags only) |
| Applied-surface integrity | 10/11 intact at freeze hashes; cline drifted post-archive (mtime 16:05 local, after all archives) |
| cline drift cause | cline runtime normalization (05:52Z) + manual codex entry (09:05Z); baseUrl stripped |
| cline repair | omniroute-chat settings restored byte-identical to the archived template; backup ac101948…-providers.json; contract 17/17 PASS |
| omp ratification provenance | VALID (verbatim "ok confirm", user, 15:02, recorded in archived ratification record) |
| cline FBC-5 classification | HONEST (documented permanent blocker; config-level evidence; no mutation claimed as pass) |
| rotation-release citation | SUBSTANCE INTACT, PATH STALE (record byte-preserved in quarantine; task text carries the verbatim instruction) |

## Decisions

- Live cline fix: minimal-entry restoration only; the post-archive manual codex provider entry and
  `lastUsedProvider` were preserved (they are the user's/other sessions' surface, not ours to prune).
- No new spec delta: the existing canon covers citation integrity and gate-claim honesty; this change
  is the recorded evidence application of those rules.
- The empty `invalidate-archive-gaps-closure-fabrications` change (created and deleted by a parallel
  session mid-sweep) is noted; the store's git tree shows it was never committed.

## Risks

- cline's runtime may rewrite its providers file again on its next run; the recorded template values and
  backup make any future restoration a one-command operation.
