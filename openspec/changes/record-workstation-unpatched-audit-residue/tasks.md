# Tasks

## 1. Diagnosis and Ownership Preflight

- [x] 1.1 Confirm `npm prefix` resolves to `/Users/androidteam` when invoked from `~/Developer`
- [x] 1.2 Confirm `~/Developer` has no `package.json`, so the command resolved to the `$HOME` manifest
- [x] 1.3 Resolve ownership of the 09:01:18 manifest mutation by interrogating each live session in `~/Developer`
- [x] 1.4 Identify the archived change that performed the mutation and confirm no write to the manifest is warranted

## 2. Residual Advisory Identity Recording

- [x] 2.1 Capture `npm audit --json` and enumerate every advisory by package, severity, range, and dependency chain
- [x] 2.2 Confirm the offered remedy for each residual is a downgrade, not an upgrade
- [x] 2.3 Confirm each direct dependency is installed at its latest published version
- [x] 2.4 Separate the residuals into their contributing chains (`newman` family, `@usebruno/cli` family, `newman-reporter-htmlextra` family)
- [x] 2.5 Confirm `npm install --dry-run` resolves cleanly with no `ERESOLVE`

## 3. Verification of Non-Convergence

- [x] 3.1 Verify `newman@6.2.2`, `newman-reporter-htmlextra@1.23.1`, and `@usebruno/cli@4.2.0` equal their `npm view` latest versions
- [x] 3.2 Verify the audit's offered fixes are downgrades to `5.3.2`, `1.22.11`, and `4.1.0` respectively
- [x] 3.3 Record `npm audit fix --force` as non-convergent on this manifest and therefore not re-runnable

## 4. Evidence and Spec Sync

- [x] 4.1 Author `evidence.md` in the change directory from output read back from disk
- [x] 4.2 Record the `$HOME` manifest footgun and the correct invocation discipline
- [x] 4.3 Run `openspec validate --all` and confirm the delta spec validates
- [ ] 4.4 Sync the delta spec into the main `npm-audit-remediation` spec at archive time
- [ ] 4.5 Archive the change and commit the store
