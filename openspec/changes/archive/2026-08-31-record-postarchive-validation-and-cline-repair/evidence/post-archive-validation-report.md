# Post-Archive Validation Report — 2026-08-31 (2026-08-31T09:50:50Z)

Scope: archived changes `2026-08-31-reconcile-omniroute-dialects-archive-gaps`,
`2026-08-31-invalidate-ntu-keynote-closure-fabrications`, and their subjects. Value-blind throughout.

## 1. Keynote closure fabrications (re-confirmed)

| ID | Claim in archive | Fresh verification | Verdict |
|---|---|---|---|
| F-1 | `release-decision.json` section_4 = accepted | same archive `verification.json` 4.1 records `human-vietnamese-editorial-review-not-submitted`; only editorial artifact is `editorial-review-simulation.json` (`simulation-only-not-human-approval`) | TRUE |
| F-2 | rehearsal_and_presentation.session_status = completed | no file in the archive's acceptance set or the external repo's evidence names the registered digest `3f299c876…` except the claim files themselves | TRUE |
| F-3 | release_ref status = verified | `git -C ~/Developer/ntu-keynote rev-parse refs/tags/ntu-ai-keynote-v1.0.0` → rc=128; repository has only `archive/ntu-brand-theme-candidate-4fb4c86` and `archive/visual-contract-review-986be2f` | TRUE |

## 2. Applied-surface integrity (omniroute family)

- 31 surfaces compared against the archived current-state freeze: 10/11 applied surfaces hash-identical.
- Sole drift: `~/.cline/data/settings/providers.json` (freeze sha `3f18e12f…`, 749 bytes → current 806+ bytes), mtime 16:05 local — after both archives. Cause: cline runtime provider normalization at 05:52Z stripped `baseUrl`; a manual `codex-omniroute-chat` entry appeared at 09:05Z.

## 3. Cline repair (live, executed)

- Backup written: `~/.hermes/backups/reconcile-omniroute-native-dialects/ac101948ae736bd5-providers.json` (mode 0600).
- The `Claude-Fable-omniroute-chat` provider settings were restored BYTE-IDENTICAL to the archived template (`provider: Claude-Fable-compatible`, `model: sh/Claude-Fable`, `baseUrl: http://localhost:20128`, placeholder key), preserving the newer `codex-omniroute-chat` entry and `lastUsedProvider`.
- Post-fix route-contract: **SUMMARY PASS checks=17** (was 16/17 with cline FAIL).
- Note: two earlier display-corrupted repair attempts wrote the wrong `provider`/`model` strings; each was detected by the contract check and corrected; the final state is byte-verified against the template.

## 4. Citation integrity (archive-gaps task 2.1)

- Archived 2.1 cites `evidence/rotation-gate-release.json`; both rotation records (v1, v2) live under
  `evidence/quarantine/*.planted`, byte-preserved with sha256 recorded in the archive's own annex.
- Resolution recorded here (archives are read-only): the release substance — verbatim user instruction
  "no need rotate keys" — is preserved in the quarantine bytes and in the 2.1 task text itself; the
  citation path is stale by the quarantine move, not by any retraction.

## 5. Validated-sound closures (no action)

- omp 0644→0600 ratification: verbatim user "ok confirm", recorded 2026-08-31T15:02:14+07:00 in
  `evidence/omp-mode-ratification.json` (archived). VALID.
- cline FBC-5: honest permanent-blocker classification; config-level evidence stands. VALID.

## 6. Parallel-session artifact note

- A change dir `invalidate-archive-gaps-closure-fabrications` was created and deleted during the sweep by
  a concurrent session; never committed; no store residue.

## Integrity statement

No archived byte was modified. The single live mutation (cline providers.json restoration) is recorded
above with its backup hash. All comparisons were programmatic to defeat hyphenated-token display corruption.


## 7. Residual sweep item (documented, no action)

`openspec validate --all --strict` (1.11.0) reports one remaining failure:
`change/invalidate-ntu-keynote-closure-fabrications` — the ARCHIVED copy of that change. The identical
delta validates cleanly as an active change (verified with a disposable copy, since removed); the
archived main spec `ntu-keynote-release-integrity` is valid and synced. This is an openspec 1.11.0
archived-change validation quirk, not a content defect. Archived bytes are left untouched per the
immutability rule; the item is recorded here as a known tooling exception.
