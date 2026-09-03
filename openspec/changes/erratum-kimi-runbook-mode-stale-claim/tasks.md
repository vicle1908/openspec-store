## 1. Evidence collection

- [x] 1.1 Write `evidence/erratum-mode-state.json`: authoritative state record with complete line citations and archive-supported wording. **Done:** hash `d9140b57…` (2,130 bytes), cites archived `2.1-kimi-pm-sh-runbook.json` lines 7/11/12/13/16/17 (derived_from/mode/size/sha256/drift) vs archived `2.0-hardening-evidence.json` lines 5-14/16 (backup/modes/sha256/byte-identity/sizes/mutation/verification/zero-credential); `archived_mode_observation` and `root_cause` use archive-supported wording only.

## 2. Validation

- [x] 2.1 Run strict validation. **Done:** `{"valid": true, "issues": []}`.

## 3. Closure

- [x] 3.1 Commit only this change directory; no push. Verify: the resulting commit file list is confined to this change directory. **Done (verified):** pathspec-limited commit verified; files confined to this change directory.
- [x] 3.2 Leave ACTIVE permanently. **Decision:** leave ACTIVE; erratum for audit reference.
