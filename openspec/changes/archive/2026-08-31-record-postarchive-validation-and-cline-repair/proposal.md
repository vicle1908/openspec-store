# Proposal: record-postarchive-validation-and-cline-repair

## Why

A full post-archive validation sweep (2026-08-31, value-blind) re-verified the two corrective archives
and found:

1. **Re-confirmed**: all three keynote closure fabrications remain factually true (editorial gate
   contradicted by its own record; rehearsal claim without any digest-bound record; `verified` claim for
   the nonexistent tag `refs/tags/ntu-ai-keynote-v1.0.0` — rc=128, only two unrelated archive tags).
2. **Live regression, now fixed**: cline's own runtime rewrote `~/.cline/data/settings/providers.json`
   twice after the archives (05:52Z storage-normalization stripping `baseUrl`; 09:05Z a manual
   `codex-omniroute-chat` entry), leaving the OmniRoute SH fallback route unusable and the family
   route-contract at 16/17. The entry was restored with byte-identical template values; the contract
   returns to 17/17 PASS. The newer codex entry and `lastUsedProvider` were preserved.
3. **Formal citation defect**: archived task 2.1 (archive-gaps) cites
   `evidence/rotation-gate-release.json`, but both rotation-release records were moved to
   `evidence/quarantine/*.planted` before archiving. The release substance (verbatim user instruction
   "no need rotate keys") is byte-preserved in quarantine and recorded in the task text itself; only the
   path citation is stale.
4. **Validated as sound**: the omp 0644→0600 ratification (verbatim user "ok confirm", parallel session,
   15:02) and the cline FBC-5 permanent-blocker classification (documented blocker, not a claimed pass).

## What Changes

- Records the post-archive validation results and the cline repair with value-blind evidence.
- Resolves the archived 2.1 citation to its quarantine location without editing any archived byte.
- No external repository, credential, or archive directory is modified. The cline live-config fix is the
  single live mutation, performed with backup + atomic replace.

## Impact

- Documentation/evidence-only plus one already-executed live config restoration (recorded here).
- No new spec deltas required: the existing `ntu-keynote-release-integrity` and
  `omniroute-agent-cli-routing` requirements already cover the discovered classes.
