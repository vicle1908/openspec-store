## 1. Preflight and approval

- [ ] 1.1 Record provider release, source-conformance, synthetic-recovery, and
  rollout evidence with current heads and timestamps.
- [ ] 1.2 Capture a value-free live-root inventory, root identity, duplicate
  source decisions, broken-link decisions, permission findings, and mapping.
- [ ] 1.3 Identify readers/writers, principals, maintenance window, backup or
  snapshot, restore procedure, and rollback owner.
- [ ] 1.4 Obtain explicit operator approval for the exact plan and scope.

## 2. Controlled execution

- [ ] 2.1 Quiesce approved readers/writers and record the observed state.
- [ ] 2.2 Prepare the migration journal and verify root/capability identity.
- [ ] 2.3 Execute only approved descriptor-relative operations with a checkpoint
  after every transaction boundary.
- [ ] 2.4 Stop on identity, capability, mapping, or approval drift; do not fall
  back to pathname copying, recursive creation, or broad deletion.

## 3. Recovery and verification

- [ ] 3.1 Exercise the tested recovery/rollback path for any interruption or
  failed health gate.
- [ ] 3.2 Run provider doctor, filesystem, consumer, deployment, and
  scheduler/database checks as separate owner-attributed evidence scopes.
- [ ] 3.3 Release maintenance mode only after every required scope is green or
  an explicit bounded exception is approved.

## 4. Final handoff

- [ ] 4.1 Retain the root snapshot identity, journal, mapping, rollback
  reference, and redacted final report.
- [ ] 4.2 Recheck the OpenSpec/store/worktree state and classify runtime changes
  separately from planning changes.
- [ ] 4.3 Do not execute or archive this change until an authorized operator
  confirms that live actions are in scope for a separate run.
