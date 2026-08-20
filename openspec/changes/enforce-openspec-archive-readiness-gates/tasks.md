## 1. Freeze Store Ownership and Define Evidence

- [ ] 1.1 Publish the sole openspec-store writer, dedicated worktree, 40-character base SHA, raw dirty inventory, content fingerprint, and preserved active/untracked paths; verify observability and JTI changes are not selected.
- [ ] 1.2 Define a redacted machine-readable archive-readiness evidence schema covering repository identity, dirty inventory, content hash, dependency origins, commands/exits, gate classification, spec paths/sync, rollback, and owner; verify valid/invalid fixtures parse deterministically.
- [ ] 1.3 Create a corrective ledger for the four reviewed archives with exact archived paths, incomplete or unsupported claims, owning corrective tasks, and closure gates; verify the archives themselves remain unchanged.

## 2. Implement Active-Change Preflight

- [ ] 2.1 Implement task parsing that rejects any unchecked tracked task before archive readiness and verify fixtures for complete, incomplete, missing, and malformed task files.
- [ ] 2.2 Resolve required artifacts and authoritative delta specs from OpenSpec status/instruction JSON, including `artifactPaths.specs.existingOutputPaths`, and verify `skip_specs: true` is an explicit no-delta success while missing required deltas fail.
- [ ] 2.3 Validate the evidence manifest against current source identities and required gate outcomes, and verify source drift, failed/skipped/unavailable gates, missing dependency origins, and missing rollback each fail closed.
- [ ] 2.4 Emit stable redacted JSON and human-readable diagnostics with no credential values, and verify every failure identifies the owning task and remediation.

## 3. Detect Post-Archive Integrity Violations

- [ ] 3.1 Implement a base-ref-scoped audit for newly moved archive paths and verify it detects an archive move performed with incomplete tasks.
- [ ] 3.2 Detect completion-only task edits made after the archive move and verify the validator reports a corrective-ledger incident without rewriting history.
- [ ] 3.3 Scope legacy debt to the corrective baseline so unrelated pre-existing archives do not block all store validation, and verify any newly introduced violation still fails CI.

## 4. Integrate Store and Agent Workflow Enforcement

- [ ] 4.1 Add the readiness validator to the store’s reviewed verification/CI entry point and verify a bypassed raw CLI archive is caught by the post-archive audit.
- [ ] 4.2 Update the canonical archive workflow guidance to run the validator before single and bulk archive mutation, then run the workspace skill sync script and `--check` to verify managed mirrors match.
- [ ] 4.3 Verify single/bulk archive guidance preserves inline spec synchronization, user confirmation, store selection, and unrelated dirty-state boundaries.

## 5. Validate, Roll Back, and Hand Off

- [ ] 5.1 Run focused validator tests covering clean success, incomplete tasks, missing evidence, drift, failed gates, unavailable gates, `skip_specs`, missing deltas, sync failure, and post-archive edits; record exact results.
- [ ] 5.2 Run strict selected/full-store OpenSpec validation, store doctor, managed-skill checks, and `git diff --check`; verify no unrelated active/archived artifact changed.
- [ ] 5.3 Rehearse rollback by removing only the validator integration in a disposable worktree and verify the prior store behavior and all unrelated histories remain intact.
- [ ] 5.4 Freeze final HEAD, raw dirty inventory, content fingerprint, validator evidence, and corrective ledger; commit the scoped store result and leave its own archive task incomplete until the validator passes against itself.
