# Tasks: Cut Over Live TDT Home

This is an operator runbook, not a code change. Each task requires explicit
operator approval. Depends on ALL prior changes being complete and archived.

## 1. Pre-migration

- [ ] 1.1 Operator reviews and approves the migration plan for the specific ~/.tdt tree.
- [ ] 1.2 Run `tdt config doctor` against live ~/.tdt and record baseline findings.
- [ ] 1.3 Back up entire ~/.tdt tree to a timestamped location using `BackupMetadata` schema.
- [ ] 1.4 Verify backup integrity: hash every backed-up file, compare to original.
- [ ] 1.5 Document current state: which consumers are using which paths, active credentials, running services.

## 2. Service window

- [ ] 2.1 Schedule maintenance window and notify affected consumers/operators.
- [ ] 2.2 Stop all services that read/write ~/.tdt during migration.
- [ ] 2.3 Verify no processes hold open file handles to ~/.tdt.

## 3. Apply migration

- [ ] 3.1 Run migration engine against live ~/.tdt with journal logging.
- [ ] 3.2 Monitor migration progress and journal state transitions.
- [ ] 3.3 Verify each migration phase completes before proceeding.

## 4. Post-migration verification

- [ ] 4.1 Run `tdt config doctor` against migrated ~/.tdt — expect clean result.
- [ ] 4.2 Run provider contract tests against migrated tree.
- [ ] 4.3 Start each consumer service and verify it loads credentials and config correctly.
- [ ] 4.4 Run consumer smoke tests for each affected repository.
- [ ] 4.5 Monitor for 24 hours for any anomaly.

## 5. Rollback (if needed)

- [ ] 5.1 Stop all services.
- [ ] 5.2 Restore ~/.tdt from backup.
- [ ] 5.3 Verify restore integrity.
- [ ] 5.4 Restart services and verify they function correctly.
- [ ] 5.5 Document rollback reason and schedule retry.

## 6. Sign-off

- [ ] 6.1 Operator confirms all services operational post-migration.
- [ ] 6.2 Archive backup location documented for reference.
- [ ] 6.3 Update consumer dependency floors if applicable.
- [ ] 6.4 Run `openspec validate --all --strict` and `openspec store doctor`.

## Archive gate

Do not archive until operator sign-off is recorded, all services verified,
and 24-hour monitoring period passes without anomalies.
