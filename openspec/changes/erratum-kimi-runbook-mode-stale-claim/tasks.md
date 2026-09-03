## 1. Evidence collection

- [x] 1.1 Write `evidence/erratum-mode-state.json`: authoritative state record with line citations. **Done:** hash `134be631…` (1,586 bytes), cites archived `2.1-kimi-pm-sh-runbook.json` lines 11/16/17 (0o644/drift) vs archived `2.0-hardening-evidence.json` lines 6/7/13 (0600/no-mutation).

## 2. Validation

- [x] 2.1 Run strict validation. **Done:** `{"valid": true, "issues": []}`.

## 3. Closure

- [x] 3.1 Commit only this change directory; no push. Verify: the resulting commit file list is confined to this change directory. **Done (verified):** pathspec-limited commit verified; files confined to this change directory.
- [x] 3.2 Leave ACTIVE permanently. **Decision:** leave ACTIVE; erratum for audit reference.
