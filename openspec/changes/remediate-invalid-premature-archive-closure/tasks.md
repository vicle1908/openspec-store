## 1. Evidence collection

- [ ] 1.1 Write `evidence/archive-closure-defects.json`: value-blind record of the three defects in the archived `invalidate-archive-gaps-premature-archive` — (a) 2.1 void tick (authorization genuine, no verifiable executed sentinel; cited evidence file missing), (b) 2.3 model mismatch (evidence: `sh/gpt-5.6-sol`, ledger: `sh/Claude-Fable`), (c) line 16 self-contradiction ("archive" vs "verification pending"). Verify: every claim cites archived file + line; zero credential values.

## 2. Gates (owner decisions; never agent-cleared)

- [ ] 2.1 (carry-forward) Kimi/Cline live-sentinel verification: genuine authorization verified (Prime line 12921); valid sentinel evidence for `sh/gpt-5.6-sol` exists in `archive/2026-09-02-invalidate-archive-gaps-closure-fabrications/evidence/cline-live-sentinel-20260901.json`; run only on explicit owner order, recorded as evidence in this change if run.

## 3. Validation and closure

- [ ] 3.1 Run `openspec validate remediate-invalid-premature-archive-closure --strict --store openspec-store` and record the exact result. Verify: valid with zero issues.
- [ ] 3.2 Commit only this change directory (`git add -- openspec/changes/remediate-invalid-premature-archive-closure`; use `git commit --only` if foreign index entries must be preserved), no push. Verify: the resulting commit's file list is confined to this change directory.
- [ ] 3.3 Leave this change ACTIVE until 2.1 is resolved; any archive executed while 2.1 is unchecked is void by this change's own spec delta. Verify: the closure decision cites the state of every gate.
