## 1. Evidence collection

- [ ] 1.1 Write `evidence/archive-closure-defects.json`: value-blind record of the defects in the archived `invalidate-archive-gaps-premature-archive` — (a) 2.1 void tick (authorization genuine, cited live path absent, only quarantined planted record exists; cited line 12920 vs genuine line 12921), (b) 2.2 citation defect (unsupported phrase in ledger, real ratification artifact exists in sibling archive), (c) 2.3 model mismatch (evidence: `sh/gpt-5.6-sol`, ledger: `sh/Claude-Fable`), (d) line 16 self-contradiction ("archive" vs "verification pending"). Verify: every claim cites archived file + line; zero credential values.

## 2. Gates (owner decisions; never agent-cleared)

- [ ] 2.1 (carry-forward) Kimi/Cline live-sentinel verification: genuine authorization verified (Prime line 12921); no independently verified PM+SH execution result exists (cited live path absent; quarantined planted record only). Run only on explicit owner order, recorded as evidence in this change if run.

## 3. Validation and closure

- [ ] 3.1 Run `openspec validate remediate-invalid-premature-archive-closure --strict --store openspec-store` and record the exact result. Verify: valid with zero issues.
- [ ] 3.2 Commit only this change directory (`git add -- openspec/changes/remediate-invalid-premature-archive-closure`; use `git commit --only` if foreign index entries must be preserved), no push. Verify: the resulting commit's file list is confined to this change directory.
- [ ] 3.3 Leave this change ACTIVE until 2.1 is resolved; any archive executed while 2.1 is unchecked is void by this change's own spec delta. Verify: the closure decision cites the state of every gate.
