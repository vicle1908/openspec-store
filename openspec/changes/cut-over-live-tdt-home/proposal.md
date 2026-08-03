# Cut Over Live TDT_HOME

## Why

The operator-owned `~/.tdt` tree is the final migration target for the TDT_HOME program. It can contain configuration, credentials, symlinks, permissions, schedules, databases, logs, and other runtime state used by multiple consumers. Migrating it changes a live shared filesystem boundary: an incorrect mapping, an active writer, an unverified backup, or an incomplete rollback path could cause data loss, secret exposure, service interruption, or a split view in which consumers use different roots.

Source conformance, a crash-recoverable migration engine, and a qualified provider rollout reduce those risks, but none of them authorizes mutation of the real tree. The live cutover therefore needs its own operator-approved runbook and verification protocol. The runbook must bind approval to one current inventory, one migration plan, one root identity, one maintenance window, named principals, and one rehearsed rollback decision; it must fail closed if any of those inputs drift.

This is the final change in the sequence. It may proceed only after `govern-tdt-home-source-conformance`, `build-tdt-home-synthetic-migration-engine`, and `release-and-roll-out-tdt-home-provider` are complete and their required evidence remains current. OpenSpec acceptance of this proposal does not itself approve a maintenance window or authorize live execution.

## What Changes

- Establish a version-controlled, operator-owned cutover runbook for the real `~/.tdt` tree. The runbook records the target root identity, complete value-free inventory, approved source-to-destination mapping, participating consumers and deployment surfaces, authorized principals, maintenance window, approvers, checkpoints, stop conditions, and evidence locations.
- Add a hard preflight gate that verifies all three predecessor changes are complete, all declared consumers and writers are accounted for, no prerequisite evidence is stale or contradictory, the live root still matches the approved inventory, and the migration plan passes the released engine's dry-run and precondition checks.
- Require an operator-controlled backup of the live tree before mutation. Backup evidence records scope, timestamp, root and plan identity, protected storage location, representable metadata, verification result, retention owner, and restore procedure without copying file contents or secret values into OpenSpec artifacts or logs.
- Require a rollback rehearsal before cutover. The approved backup and restore procedure are exercised against an isolated target, compared with the captured pre-migration state, and repeated to demonstrate idempotence. The real root is not destructively rehearsed.
- Define maintenance-mode entry and quiescence verification for every declared reader, writer, service, scheduler, and database-owning process. A caller assertion such as `--quiesced` is not evidence; each owner must verify that its write path is stopped or participates in the approved exclusion mechanism.
- Apply the reviewed migration plan to the live tree only through the released `tdt-home-migration-engine`. Execution is bound to the approved root identity, plan digest, generation, journal, backup metadata, and principal; ad hoc copy, move, recursive cleanup, permission repair, or pathname-based fallback commands are outside the runbook.
- Verify each journal checkpoint and stop before further mutation on identity drift, capability drift, unexpected objects, backup failure, journal inconsistency, approval withdrawal, or an unmet operation postcondition. Recovery or rollback—not improvisation—is the default failure path.
- Define post-apply verification by evidence scope: migration-engine terminal state, filesystem object and metadata checks, provider diagnostics, consumer smoke tests, deployment health, scheduler/database checks, and absence of unexpected readers or writers. Passing one scope does not imply that another scope passed.
- Define an owner-attributed monitoring period after services resume, with concrete health signals, thresholds, observation duration, escalation contacts, and rollback deadlines. The cutover is not complete merely because apply returned successfully.
- Retain a redacted cutover report containing approvals, timestamps, plan and root identities, journal terminal state, backup and rollback references, verification results, exceptions, monitoring outcome, and final operator decision. Evidence may include bounded relative paths and cryptographic digests but must not contain credential values, file contents, literal connection strings, or unrestricted absolute-path listings.

### Execution and Verification Protocol

1. **Freeze and approve:** capture the current value-free inventory, compile the concrete migration plan, bind it to the live root and backup strategy, and obtain separate eligibility and execution approvals from the named operator and affected deployment owners.
2. **Back up and rehearse:** create and verify the protected live-tree backup, restore it to an isolated target, compare all supported content and metadata, repeat rollback to prove idempotence, and record the result.
3. **Enter maintenance mode:** stop or exclude every declared writer and verify reader/writer quiescence using observable process, lock, or deployment evidence. Recheck the root identity and plan immediately before apply.
4. **Apply:** invoke the approved migration engine with the approved plan, generation, root, journal, and principal. Verify durable checkpoints and do not bypass any failed precondition or recovery decision.
5. **Verify before restart:** confirm the committed journal state, destination object digests and types, required permissions and ownership policy, permitted symlink targets, expected absence states, backup integrity, and provider diagnostics while consumers remain quiesced.
6. **Restart and smoke test:** resume consumers in the approved order. Each owner records direct evidence for its service, configuration resolution, schedules, database access, and read/write behavior.
7. **Monitor and close:** observe the declared signals for the approved period. The operator declares success only when every required scope is green; otherwise maintenance mode remains active or rollback begins according to the recorded decision matrix.

## Capabilities

### New Capabilities

- `tdt-home-live-cutover`: operator-approved planning, backup, rollback rehearsal, journaled execution, scoped verification, monitoring, and deterministic recovery/rollback for the real `~/.tdt` root.

### Modified Capabilities

- None. `tdt-env-loader-tdt-home`, `tdt-home-migration-engine`, source-conformance governance, and provider-rollout contracts are prerequisites consumed by this change; their behavior is not redefined here.

## Ownership Boundaries

- The authorized operator owns the live `~/.tdt` tree, selection of the maintenance window, approval of the concrete mapping and backup location, execution and rollback authorization, evidence retention, and the final success decision. No repository or automated check may grant that authority implicitly.
- `tdt-core` owns the released provider, migration engine, plan validation, journal/recovery behavior, backup metadata validation, and provider diagnostics. It does not choose the operator's mappings, resolve ambiguous live data, or declare consumer health.
- Each consumer and deployment owner owns the accuracy of its reader/writer inventory, maintenance-mode procedure, principal and access requirements, restart order, smoke tests, monitoring signals, and approval to resume service.
- Scheduler and database owners own checks for paused work, duplicate or missed executions, database integrity/access, and safe resumption. A filesystem-level pass does not substitute for those checks.
- Security or secret owners retain control of credentials, backup access, retention, and incident handling. Cutover evidence records classifications and references, never secret material.
- `openspec-store` owns the normative runbook, requirements, task tracking, and redacted evidence references. It neither owns the runtime data nor executes, approves, or silently retries live mutations.
- The migration engine is the only approved mutation mechanism for plan operations. Manual intervention may stop execution or preserve evidence, but any broadened mapping, unplanned repair, or changed root/principal requires a new plan and renewed approval.

## Explicit Non-Goals

- Implementing or modifying the TDT_HOME provider, migration engine, journal schemas, backup schemas, source-conformance auditor, or provider release process.
- Migrating consumer source code, changing dependency metadata, publishing packages, or introducing new deployment mechanisms as part of the maintenance window.
- Discovering or guessing ownership, destination mappings, precedence among duplicate configuration sources, meanings of broken links, or treatment of unknown runtime state. Unresolved items block approval.
- Using the cutover to perform broad home-directory cleanup, unrelated permission repair, credential or key rotation, database schema/data conversion, log retention changes, or schedule redesign.
- Embedding secrets, file contents, literal DSNs, tokens, private keys, or credential-bearing command output in the plan, journal evidence, monitoring report, or OpenSpec store.
- Supporting ad hoc `cp`, `mv`, `rsync`, recursive `mkdir`, pathname `rename`, shell hooks, best-effort journal repair, or unsafe fallback behavior when required descriptor-relative or durability primitives are unavailable.
- Treating a successful dry run, backup creation, provider doctor, engine commit, or single consumer smoke test as sufficient proof of complete cutover success.
- Performing an unattended or automatically scheduled cutover. A named operator must explicitly approve execution for the current plan and maintenance window and remain able to stop or roll back it.
- Deleting unknown files or rewriting credentials during rollback. Unexpected post-snapshot changes are drift requiring operator review, not permission to force restoration.

## Prerequisites

All of the following are hard gates. Each predecessor change must be marked complete, strictly validated, and represented by current, reviewable evidence. A bounded exception must identify an owner, scope, expiry or review point, and explicit acceptance by the live-cutover operator; an exception that weakens recoverability, root containment, secret protection, or complete reader/writer ownership is not eligible for acceptance.

1. **`govern-tdt-home-source-conformance` is complete.** Every participating consumer has a valid governance manifest, its deployment and launch surfaces have accountable owners, the deterministic source audit is green or has explicitly accepted bounded exceptions, and no undeclared hard-coded `~/.tdt` construction or ownerless writer remains. The repository set is frozen for the cutover window; newly discovered consumers block execution.
2. **`build-tdt-home-synthetic-migration-engine` is complete.** The exact released engine intended for live use has passed plan validation, root-containment, journal integrity, backup/restore, interruption recovery, tamper rejection, redaction, and idempotence tests on isolated roots. Synthetic migration and rollback have passed twice, including fresh-process recovery at supported interruption boundaries, and the plan/journal/backup schema versions match the live runbook.
3. **`release-and-roll-out-tdt-home-provider` is complete.** The provider artifact is reproducibly built and installed from the qualified release artifact, provider-only installed-artifact checks pass in target runtimes, staged rollout and compatibility evidence are green, affected owners have accepted the release, and the retained provider rollback artifact and procedure are available. No live cutover may be used to compensate for an incomplete provider rollout.

The live plan additionally requires:

- a current, value-free inventory and stable identity for the exact operator-owned root;
- a complete, engine-validated migration plan with no unresolved objects, conflicting destinations, unsafe paths, or stale preconditions;
- a verified, access-controlled backup with sufficient capacity, retention, integrity evidence, and a successful isolated restore/rollback rehearsal;
- named execution and rollback operators, affected consumer/deployment owners, authorized principals, escalation contacts, and evidence owners;
- an approved maintenance window long enough for backup verification, apply, scoped verification, monitoring, and rollback before its deadline;
- verified quiescence procedures and restart ordering for all declared readers, writers, services, schedulers, and databases;
- documented go/no-go, stop, recovery, rollback, and abort criteria, including what happens if the monitoring window cannot finish before the rollback deadline; and
- sufficient host capabilities and free space for the approved engine's descriptor-relative operations, durable journal, backup, staging, and recovery behavior.

Any missing, expired, inconsistent, secret-bearing, or drifted prerequisite returns the change to planning. It does not authorize a reduced-scope live attempt.

## Impact

- The approved execution can mutate the real `~/.tdt` tree, including the location or representation of approved files and links and their supported metadata. This is the first change in the sequence permitted to affect operator data.
- Consumers of TDT_HOME will experience a planned maintenance period and controlled restart. Their source and dependency changes belong to predecessor adoption work, but their runtime health and configuration resolution are directly affected by this cutover.
- The operator must reserve protected storage for a full verified backup, journal, staging data, and retained evidence, and must retain the pre-cutover recovery material through at least the monitoring and rollback decision period.
- Schedulers, databases, long-running agents, launch surfaces, and concurrent shells may require quiescence and post-restart validation even when their underlying data is not moved. Missed, duplicate, or stale work is an operational risk that must be observed explicitly.
- Cutover records introduce sensitive operational metadata. They must be access-controlled and redacted; only bounded path identifiers, object classifications, hashes, timestamps, owner references, and pass/fail outcomes should enter shared evidence.
- The primary safety risks are incomplete inventory, a still-active writer, backup or journal corruption, root/principal drift, divergent consumer behavior, and late health regression. Hard gates, fail-closed execution, independent evidence scopes, and a rehearsed rollback limit those risks.
- No application database schema, credential value, consumer source file, package artifact, or deployment definition is intentionally changed by this proposal. Discovery that one must change blocks cutover and requires separately reviewed work.

## Rollback

Rollback is a first-class phase of the runbook, not a best-effort cleanup step. Before execution, the operator records which journal states permit forward recovery, which conditions require rollback, who may decide, and the latest safe rollback time. Automatic stop conditions include root or principal mismatch, journal or backup validation failure, unexpected filesystem objects, unmet operation postconditions, failed provider/filesystem verification, failed critical consumer or scheduler/database checks, approval withdrawal, or a monitoring threshold breach.

When rollback is selected:

1. Keep or re-enter the same verified maintenance mode; do not resume writers to make the system appear healthy.
2. Preserve the journal, diagnostics, and current root identity as redacted incident evidence.
3. Revalidate the approved plan digest, generation, root descriptor identity, journal chain, backup metadata, backup payloads, operator principal, and required platform capabilities.
4. Invoke only the migration engine's tested idempotent recovery/rollback path or the approved snapshot restore procedure for the state identified by the runbook. Do not mix both mechanisms without an explicitly rehearsed decision point.
5. Restore the supported pre-migration content, object kind, permissions, ownership policy, link text, and prior-absence state. Stop for operator review rather than deleting an unknown object, overwriting post-snapshot data, broadening the plan, or rewriting a credential.
6. Verify the restored tree against the pre-cutover inventory and backup identities, run provider and filesystem diagnostics, restart consumers in the approved order, and repeat all required consumer, deployment, scheduler/database, and monitoring checks.
7. Record the rollback terminal state, any data that could not be restored, service impact, retained evidence and backup references, and the operator's final disposition. A successful rollback is reported as rollback, never as a successful cutover.

Rollback remains available until the operator closes the observation period and explicitly accepts the new tree. Backups and journals are retained according to the approved retention policy after closure. If rollback cannot be validated or completed, the root remains quiesced where operationally possible, the incident is escalated to the named owners, evidence is preserved, and no ad hoc forward migration or destructive cleanup is authorized by this change.
