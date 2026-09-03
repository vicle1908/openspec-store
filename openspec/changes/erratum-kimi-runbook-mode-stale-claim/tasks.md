## 1. Evidence collection

- [x] 1.1 Write `evidence/erratum-mode-state.json`: authoritative state record with complete line citations and archive-supported wording. **Done:** hash `62dbbde5…` (2,950 bytes), cites archived `2.1-kimi-pm-sh-runbook.json` lines 7/11/12/13/16/17 (derived_from/mode/size/sha256/drift) vs archived `2.0-hardening-evidence.json` lines 5-14/16 (backup/modes/sha256/byte-identity/sizes/mutation/verification/zero-credential); `historical_mode_hardening` records the separate 2026-08-29 chmod 0644→0600 (EVIDENCE_MANIFEST.md line 84) for the earlier b251… snapshot — sha-identity scoped to that operation, no causal link to the 2026-09-02 value-blind parse, no byte continuity implied across dates, mode 0600 stated only at verified endpoints (after the 08-29 operation and again at the 09-02 inspection); `archived_mode_observation` and `root_cause` use archive-supported wording only.

## 2. Validation

- [x] 2.1 Run strict validation. **Done (2026-09-03, after semantic correction):** `{"valid": true, "issues": [{"level": "INFO", "message": "skip_specs is set in .openspec.yaml: change declares no spec-level behavior changes, zero deltas accepted"}]}` — valid with one INFO issue, zero errors.

## 3. Closure

- [x] 3.1 Commit only this change directory; no push. Verify: the resulting commit file list is confined to this change directory. **Done (verified):** pathspec-limited commit verified; files confined to this change directory.
- [x] 3.2 Leave ACTIVE permanently. **Decision:** leave ACTIVE; erratum for audit reference.
