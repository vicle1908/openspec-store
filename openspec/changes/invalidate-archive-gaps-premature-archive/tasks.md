## 1. Premature-archive record (central, executable)

- [x] 1.1 Write `evidence/premature-archive-record.json`: value-blind citation of the contradiction — archived ledger tasks.md line 12 (2.2 unchecked) and line 13 (2.3 unchecked) against line 19 (3.3: "leave the change ACTIVE … Archive is not permitted while 2.2 and 2.3 remain unresolved") and the archived directory path, plus the contradicting commit-message claims (`d247e76`). Verify: every claim cites archived file + line; zero credential values; the record does not alter the archive. **Done (verified):** record written (`d6557605…`, 1,483 bytes), all citations as specified, archive untouched.
- [x] 1.2 Write `evidence/gate-state-restatement.json`: the authoritative gate states restated unchanged from the archived ledger — 2.1 authorization verified (hash-verified user accepted-risk record) with gate verification pending; 2.2 OPEN awaiting owner ratify-or-revert (pending recommendation: RATIFY/keep 0600); 2.3 OPEN/blocked (user-owned cline auth session). Verify: restated states match the archived bytes exactly; no authorization claims beyond the verified 2.1 record. **Done (verified):** record written (`94e9458b…`, 1,444 bytes); sentinel wording corrected per audit (untrusted-not-independently-verified, no categorical denial); states match archived lines 11–13.

## 2. Gates (owner decisions; never agent-cleared)

- [ ] 2.1 (carry-forward, informational) Kimi/Cline live-sentinel verification remains pending under the verified accepted-risk authorization; executed only when the owner orders it, recorded as evidence in this change if run.
- [ ] 2.2 (carry-forward) omp `~/.omp/agent/models.yml` 0644→0600 ratify-or-revert: awaiting the owner's explicit decision in this conversation; recommendation on file is RATIFY.
- [ ] 2.3 (carry-forward) cline live sentinel: blocked pending a user-owned cline auth session.

## 3. Closure

- [x] 3.1 Run `openspec validate invalidate-archive-gaps-premature-archive --strict --store openspec-store` and record the exact result. Verify: valid with zero issues. **Done (verified):** `{"valid": true, "issues": []}` re-run after the sentinel-wording correction.
- [ ] 3.2 Commit only this change directory (`git add -- openspec/changes/invalidate-archive-gaps-premature-archive`; use `git commit --only -- openspec/changes/invalidate-archive-gaps-premature-archive` if foreign index entries must be preserved), no push. Verify: the resulting commit's file list is confined to this change directory.
- [ ] 3.3 Leave this change ACTIVE while tasks 2.1–2.3 remain unresolved or until the owner explicitly re-classifies them; any archive executed while 2.x is unchecked is void by this change's own spec delta. Verify: the closure decision cites the state of every gate.
