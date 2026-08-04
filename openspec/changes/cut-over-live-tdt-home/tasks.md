# Tasks: Cut Over Live TDT Home

This is an operator runbook, not a code change. Each task requires explicit
operator approval. Depends on ALL prior changes being complete and archived.

## 1. Pre-migration

- [ ] 1.0 Verify all 3 predecessor OpenSpec changes are archived and green (`openspec validate --all`, `openspec store doctor`).
- [ ] 1.1 Operator reviews and approves the migration plan for the specific ~/.tdt tree.
- [ ] 1.2 After approval, run the installed provider's read-only doctor against
  the live root and record redacted baseline findings.
- [ ] 1.3 Back up the live tree to protected operator-owned storage using the
  `BackupMetadata` schema and the approved scope; do not copy secret values
  into planning or report artifacts.
- [ ] 1.4 Verify backup integrity using bounded metadata and cryptographic
  digests, then rehearse restore against an isolated target.
- [ ] 1.5 Document owner-verified readers, writers, services, schedulers, and
  deployment surfaces without recording active credential values.

## 2. Service window

- [ ] 2.1 Schedule maintenance window and notify affected consumers/operators.
- [ ] 2.2 Enter the approved maintenance mode and verify every declared reader
  or writer is quiesced; do not perform a broad unreviewed stop.
- [ ] 2.3 Verify no processes hold open file handles to ~/.tdt.

## 3. Apply migration

- [ ] 3.1 After all preflight gates and separate execution approval pass, run
  the released migration engine against live ~/.tdt with journal logging.
- [ ] 3.2 Monitor migration progress and journal state transitions.
- [ ] 3.3 Verify each migration phase completes before proceeding.

## 4. Post-migration verification

- [ ] 4.1 Run the installed provider doctor against migrated ~/.tdt and classify
  every required finding; a clean result is required only where the approved
  plan says the finding must be absent.
- [ ] 4.2 Run provider contract tests against migrated tree.
- [ ] 4.3 Start each consumer service and verify it loads credentials and config correctly.
- [ ] 4.4 Run consumer smoke tests for each affected repository.
- [ ] 4.5 Monitor for the operator-approved observation period with declared
  signals, thresholds, escalation contacts, and rollback deadline.

## 5. Rollback (if needed)

- [ ] 5.1 Stop all services.
- [ ] 5.2 Under the same quiescence, invoke the tested engine rollback or
  approved snapshot restore path; do not use ad-hoc copy or delete commands.
- [ ] 5.3 Verify restore integrity.
- [ ] 5.4 Restart services and verify they function correctly.
- [ ] 5.5 Document rollback reason and schedule retry.

## 6. Sign-off

- [ ] 6.1 Operator confirms all services operational post-migration.
- [ ] 6.2 Archive backup location documented for reference.
- [ ] 6.3 Record any required consumer dependency-floor change as a link to the
  consumer-owned adoption change; do not edit consumer metadata here.
- [x] 6.4 Run `openspec validate --all --strict` and `openspec store doctor`.

## Archive gate

Do not archive until operator sign-off is recorded, all services verified,
and 24-hour monitoring period passes without anomalies.

## Evidence boundary

The retained cutover evidence contains a recorded doctor invocation and a
completed OpenSpec validation/store-doctor record, but no recorded operator
approval for task 1.1 or task 1.2. Predecessor readiness, approval,
backup/restore, maintenance-window quiescence, live apply, post-migration
verification, rollback execution, and operator sign-off remain unproven. The
pending-approval and documented-only records do not authorize or prove live
`~/.tdt` mutation; this runbook remains open and must not be archived.
