# Tasks

## 1. Pre-State Capture and Diagnosis Record

- [ ] 1.1 Capture the exact pre-change text of `/Users/androidteam/package.json` for the evidence record
- [ ] 1.2 Confirm the broken state: `newman` and `newman-reporter-htmlextra` absent from `node_modules` while present in `package-lock.json`
- [ ] 1.3 Verify `npm prefix` resolves to `/Users/androidteam` from `~/Developer`

## 2. Coordinated Newman Chain Upgrade

- [ ] 2.1 Set `newman` to `^6.2.2` and `newman-reporter-htmlextra` to `^1.23.1` in `/Users/androidteam/package.json` in a single edit
- [ ] 2.2 Reconcile the `csv-parse` override against `newman@6.2.2`'s pinned `4.16.3` so the tree is internally consistent
- [ ] 2.3 Run `npm install` **without** `--force` or `--legacy-peer-deps` and confirm exit code 0

## 3. Restored Binary Verification

- [ ] 3.1 Verify `node_modules/newman/package.json` and `node_modules/newman-reporter-htmlextra/package.json` exist and report versions satisfying the manifest ranges
- [ ] 3.2 Run `npx newman --version` and confirm exit code 0
- [ ] 3.3 Confirm the installed htmlextra version declares a `newman` peer range satisfied by the installed newman version

## 4. Audit and Residual Identity Recording

- [ ] 4.1 Run `npm audit` in `/Users/androidteam` and capture the full advisory identity output
- [ ] 4.2 Reconcile the post-remediation count against the pre-remediation 12 (3 moderate, 9 high), classifying each residual as fixed, unpatched-upstream, or newly published
- [ ] 4.3 Record that a non-zero `npm audit` exit caused by unpatched-upstream residuals is not a recovery failure

## 5. Evidence and Spec Sync

- [ ] 5.1 Author `evidence.md` in the change directory from output read back from disk, including the `$HOME` manifest footgun record
- [ ] 5.2 Run `openspec validate --all` and confirm the delta spec validates
- [ ] 5.3 Sync the delta spec into the main `npm-audit-remediation` spec at archive time
