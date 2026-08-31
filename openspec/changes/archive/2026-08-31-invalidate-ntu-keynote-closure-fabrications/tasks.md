# Tasks: invalidate-ntu-keynote-closure-fabrications

All evidence value-blind. The archived change directory is read-only and stays byte-identical.

## 1. Invalidity record

- [x] 1.1 Wrote `evidence/closure-invalidity-report.md` enumerating findings F-1..F-3 (contradicted editorial gate; fabricated rehearsal/delivery claim; verified-ref claim for a nonexistent tag) with file+line citations and the read-only verification commands.
- [x] 1.2 Captured the tag-absence proof read-only (exact command, exit status, existing-tag enumeration) in `evidence/tag-absence-proof.json`.
- [x] 1.3 Confirmed the registered candidate's real package digest (bb7a4d58, 7-file, 3f299c876…) reproduces from the immutable commit via the documented algorithm, so the invalidity is confined to the closure gates and not the candidate binding.

## 2. Spec and hygiene

- [x] 2.1 Validated the ADDED delta strictly.
- [x] 2.2 Credential-shape scan over every new evidence file.
- [x] 2.3 Committed of this change only; no push; no archive edit.

## 3. Consumer guidance

- [x] 3.1 Recorded that downstream consumers MUST treat the archived `decision: accepted` and `closure.json` as void until a fresh change records real evidence for the human editorial review, venue rehearsal, and annotated tag gates.
