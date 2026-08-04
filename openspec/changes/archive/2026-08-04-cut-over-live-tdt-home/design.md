# Design: Live TDT_HOME Cutover Runbook

## Context

The operator-owned live `TDT_HOME` (normally `~/.tdt`) contains configuration,
links, credentials, runtime state, schedules, databases, and logs used by more
than one consumer. Provider qualification, source conformance, synthetic
migration testing, and provider rollout reduce risk, but none of them authorizes
or proves a mutation of this live tree.

This design is the operational contract for one future, explicitly approved
cutover. It binds a concrete migration plan to one live root identity, one
maintenance window, one set of principals, one verified pre-migration backup,
and one rollback decision. It is a runbook, not an implementation: this change
must remain dormant until an authorized operator supplies the per-run record and
separately approves execution.

The cutover uses the migration engine designed by
`build-tdt-home-synthetic-migration-engine`. That engine owns typed plans,
root-contained generation storage, descriptor-relative mutation, durable
journaling, recovery, and `BackupMetadata` validation. This runbook owns the
human approval, live writer quiescence, communication, health gates, rollback
decision, monitoring, and final sign-off around that engine.

## Goals / Non-Goals

### Goals

- Require two explicit operator decisions: eligibility approval after preflight
  and execution approval at the start of the maintenance window.
- Bind approval to an immutable plan digest, root identity, provider artifact,
  generation, backup set, named principals, and time-bounded window.
- Capture and verify the pre-migration state of every live object the plan can
  mutate using the existing strict `BackupMetadata` schema before any such
  object changes.
- Quiesce all declared readers and writers and apply only the approved plan
  through the migration engine.
- Verify provider, filesystem, consumer, deployment, scheduler, and database
  outcomes as separate evidence scopes.
- Restore the verified backup deterministically if apply, recovery, or a health
  gate fails, then prove the restored state before readers and writers resume.
- Define a heightened monitoring period, communication cadence, escalation path,
  and final operator sign-off.
- Keep plans, journals, diagnostics, and retained reports value-free and
  redacted; protected backup payloads are not copied into OpenSpec artifacts.

### Non-Goals

- Discovering or guessing consumer mappings, owners, principals, duplicate
  configuration precedence, broken-link intent, or credential values during the
  window.
- Repairing an object, permission, link, schedule, database, or secret that is
  not an explicit step in the approved plan.
- Rotating credentials, changing database schemas, triggering schedules, or
  rewriting consumer source or deployment definitions as an incidental part of
  cutover.
- Using a clean provider doctor result as proof of consumer, deployment,
  scheduler, or database health.
- Using ad-hoc `cp`, `mv`, recursive `mkdir`, pathname-based `rename`, broad
  deletion, shell-generated inverse scripts, or an unreviewed manual repair as
  an alternative to the migration engine.
- Treating approval of this design, the proposal, or task list as approval to
  touch the live tree.
- Automatically deleting backup, journal, or incident evidence after success or
  rollback.

## Core Safety Invariants

1. **No approval by implication.** Passing prerequisites makes a plan eligible;
   only a separate in-window execution approval authorizes live mutation.
2. **One root, plan, and generation.** Every action is bound to the approved
   root identity, canonical plan digest, and generation UUID. A mismatch stops
   execution.
3. **Complete backup before mutation.** Every object the plan may change has
   valid `BackupMetadata` and any required verified payload before the journal
   enters `switching`.
4. **Quiescence is observed, not asserted.** A caller-provided Boolean or a
   successful lock acquisition does not prove undeclared writers are stopped.
5. **Only descriptor-relative engine operations mutate the root.** There is no
   unsafe pathname fallback and no opportunistic cleanup.
6. **Durable intent precedes effect.** The engine's journal remains the authority
   for apply, recovery, and rollback state.
7. **Unknown is failure.** Missing, stale, contradictory, unsupported, or
   unowned evidence cannot be treated as pass.
8. **Scope-specific evidence.** Provider, filesystem, consumer, deployment,
   scheduler, and database checks do not substitute for one another.
9. **Rollback does not guess.** Restore accepts only the exact backed-up state,
   the exact approved applied state, or explicit prior absence. A third state is
   external interference and stops automated mutation.
10. **Evidence is redacted and retained.** Control-plane records may contain
    bounded relative identifiers and digests; protected payloads remain in the
    backup store and are never attached to tickets, chat, or OpenSpec.

## Decisions

### Decision 1: Assign Explicit Roles and Decision Authority

One person may hold more than one role only when the execution record states
that fact and policy permits it. The operator and rollback authority must be
reachable for the whole window.

| Role | Responsibility and authority |
|---|---|
| **Change owner** | Assembles the per-run record, resolves missing evidence, and keeps the plan and stakeholder list current. Cannot infer execution approval. |
| **Authorizing operator** | Owns the live root and records eligibility, execution, maintenance-release, and final sign-off decisions. May withdraw approval at any time. |
| **Migration operator** | Runs the approved commands, records generation/journal states, and stops on drift. Has no authority to broaden scope. |
| **Rollback authority / incident commander** | Makes the forward-recover-versus-rollback decision after a fault or failed gate. During an incident, this role has final operational authority. |
| **Provider owner** | Attests the installed provider artifact, migration-engine version, provider contract tests, doctor interpretation, and provider escalation. |
| **Consumer/deployment owners** | Quiesce and restart their declared surfaces and own the success criteria and evidence for their smoke and service-health checks. |
| **Scheduler/database owner** | Owns read-only scheduler/database verification and confirms that no unapproved job or schema mutation occurred. |
| **Communications lead** | Sends announcements and status updates without exposing paths, payloads, credentials, or unredacted diagnostics. |
| **Security/on-call owner** | Receives suspected credential exposure, permission broadening, unexpected principal access, or backup confidentiality incidents. |

The per-run record names the primary and backup contact for every required role,
the communication channel, the incident channel, and the decision deadline. An
unreachable required authority is a no-go, not implicit delegation.

**Alternatives rejected:**

- *Let the migration operator approve and execute the run alone:* this collapses
  ownership, execution, and incident authority and permits unsafe scope expansion
  under outage pressure.
- *Allow implicit delegation when an authority is unreachable:* no-go conditions
  would become unreviewed approvals without an accountable decision maker.

### Decision 2: Bind Each Cutover to an Immutable Per-Run Control Record

The live cutover is represented by one immutable, reviewable control record. It
contains references and digests, not secret values or backup contents:

- change/run identifier and control-record version;
- target root's approved canonical location and anchored `RootIdentity`;
- provider artifact version, source revision, wheel digest, and migration-engine
  contract version;
- canonical migration plan location and SHA-256 digest;
- planned generation UUID and expected operation count;
- value-free inventory digest and the approved disposition for duplicates,
  broken links, permissions, runtime state, and prior absence;
- complete participant, reader/writer, launch surface, and logical principal
  inventory;
- `BackupMetadata` manifest reference and digest, protected payload-store
  reference, capacity check, restore-plan digest, and retention deadline;
- owner-attributed prerequisite evidence references and freshness timestamps;
- exact quiesce, apply, recover, rollback, verification, restart, and smoke-test
  command identifiers from the reviewed runbook;
- maintenance-window start/end in an aware timestamp, maximum outage budget,
  latest safe rollback start, and timeout for every phase;
- required health thresholds, monitoring duration, and non-waivable gates;
- eligibility, execution, rollback, maintenance-release, and final sign-off
  entries with operator identity, aware timestamp, decision, and approval
  reference; and
- primary/incident channels, update cadence, escalation contacts, and fallback
  authority.

Changing the root, plan digest, provider artifact, mappings, required principals,
backup/restore plan, health thresholds, or maintenance window creates a new
control-record revision and invalidates prior execution approval. Editorial
changes that do not affect execution still receive a recorded review. Runtime
payloads, raw environment values, DSNs, tokens, file contents, or sensitive
symlink text must never appear in this record.

**Alternatives rejected:**

- *Use a mutable checklist or chat transcript as the execution record:* edits and
  partial context cannot reliably bind approval to one root, plan, artifact,
  backup, principal set, and window.
- *Record runtime payloads to make the run self-contained:* that unnecessarily
  exposes secrets and live data outside the protected backup boundary.

### Decision 3: Require a Four-Gate Approval Workflow

#### Gate A: Eligibility review

The change owner assembles the complete evidence packet before the maintenance
window. The authorizing operator reviews the packet and records `ELIGIBLE` or
`BLOCKED`. Eligibility expires at the earliest freshness deadline among its
inputs and does not permit mutation.

| Required evidence | Owner | Acceptance rule |
|---|---|---|
| Provider release and rollout | Provider/release owner | Exact installed artifact and rollback artifact are identified; staging and provider-only checks passed. |
| Source conformance | Each consumer owner | Every participating revision and launch surface is accounted for; exceptions are explicit, valid, and accepted for this run. |
| Synthetic recovery | Provider owner | The same engine/schema family passed apply, interruption recovery, and rollback twice from clean isolated roots. |
| Live mapping and inventory | Change owner + operator | Root identity, typed source/destination mapping, duplicate/broken-link decisions, permission policy, and non-target inventory are complete and value-free. |
| Principals and quiescence plan | Consumer/deployment owners | Every known reader/writer and launch mechanism has a named stop/check/start procedure and accountable owner. |
| Backup and restore readiness | Migration operator + rollback authority | Capacity is sufficient; backup scope covers every mutable object; `BackupMetadata` and restore generation can be validated; retention is approved. |
| Provider/consumer verification plan | Respective owners | Exact test identity, environment/principal, expected result, timeout, and owner are recorded for each check. |
| Window and communications | Authorizing operator | Outage budget, phase deadlines, channels, update cadence, and escalation contacts are accepted. |
| Rollback decision model | Rollback authority | Immediate rollback triggers, latest rollback start, and non-waivable gates are explicit. |

Eligibility is blocked if any evidence is stale, a mapping conflicts, a principal
is unknown, the plan contains secret-bearing control-plane data, exact restore
cannot be represented, the backup lacks capacity, or a required approver is
unavailable.

#### Gate B: In-window execution approval

At the start of the window, before quiescence or live mutation, the migration
operator reads back the run identifier, root identity, plan digest, provider
artifact, window, and rollback reference. Owners confirm availability. The
communications lead confirms the maintenance-start notice. The authorizing
operator then records exactly one of:

- `GO` — authorizes quiescence, backup, and the approved apply sequence;
- `HOLD` — permits read-only investigation but no live mutation; or
- `NO-GO` — ends the attempt and schedules a new window.

A `GO` expires when the window ends or when any bound fact drifts. Approval
withdrawal stops forward work at the next safe journal boundary; the rollback
authority then chooses tested forward recovery or rollback according to the
journal state and health impact.

#### Gate C: Maintenance-release decision

After apply and every required post-migration gate, the authorizing operator
records `RELEASE`, `CONTINUE_MAINTENANCE`, or `ROLLBACK`. `RELEASE` is forbidden
while a required result is failed or unknown. A bounded exception may be accepted
only if the control record identifies its owner, scope, impact, expiry, monitoring
measure, and approval authority. Backup integrity, root identity, journal
integrity, provider contract, and security/principal gates are non-waivable.

#### Gate D: Final sign-off

Cutover remains provisional throughout heightened monitoring. At the end, the
authorizing operator and each affected service owner confirm monitoring results,
open exceptions/incidents, backup retention, and ownership handoff. Only then is
the run recorded as `SIGNED_OFF`. Absence of sign-off leaves the change open; it
does not silently become successful.

**Alternatives rejected:**

- *Use one approval before the maintenance window:* evidence or bound runtime facts
  can drift before mutation begins, so eligibility cannot substitute for an
  in-window execution decision.
- *Automatically release maintenance after journal commit:* engine success does
  not prove consumer, deployment, scheduler, database, or security health.
- *Treat monitoring completion as implicit sign-off:* unresolved incidents,
  exceptions, or retention ownership would be hidden by the passage of time.

## Pre-Migration Live-Tree Backup

### Scope and representation

Immediately after quiescence and immediately before apply, the engine snapshots
every destination object that any approved plan step may mutate. This is a
complete backup of the migration's live-tree mutation scope, not an opaque
archive of unrelated `TDT_HOME` contents. A value-free full-root inventory and
non-target canaries establish that out-of-scope objects remain unchanged.

Each entry uses the shipped `BackupMetadata` schema version accepted by the
approved provider artifact. For schema version 1 the record includes:

- safe root-relative `object_path`;
- `kind`: `regular`, `symlink`, or `absent`;
- mode, owner UID/GID, size, single-link count, and lowercase SHA-256;
- exact `link_text` for a symlink, held only in protected backup metadata;
- registered `metadata_adapter` when ACLs, xattrs, or flags are present;
- `source_identity` for an existing object;
- explicit `prior_absent` for an object that did not exist; and
- ACL, xattr, and flags presence indicators.

An existing object requires owner identity and a single link. Hard-linked files,
special objects, directories treated as opaque leaf payloads, or metadata that
cannot be preserved by an installed registered adapter block the run. An
`absent` entry must contain no invented payload or source identity and must use
the schema's zero/empty metadata shape. A regular file stores its protected
payload; a symlink records and hashes exact link text without following it.

### Backup procedure and gate

While all declared writers remain quiesced, the migration operator:

1. re-anchors the live root and confirms the approved `RootIdentity`, plan digest,
   generation UUID, effective principal, platform capabilities, and free-space
   threshold;
2. inventories every destination through retained descriptors and no-follow
   checks, rejecting any precondition drift;
3. creates the root-contained generation and copies each required regular-file
   payload through descriptors into protected backup storage;
4. records symlink or prior-absence state using `BackupMetadata` without
   dereferencing links;
5. synchronizes each payload before publishing its metadata entry;
6. validates every metadata entry against the shipped strict schema, verifies
   payload size/digest and supported metadata, then publishes the ordered
   manifest atomically;
7. synchronizes the backup directories and independently reopens and verifies
   the complete set; and
8. records only the generation, manifest digest, entry counts by object kind,
   verification status, protected-store reference, and timestamp in the
   redacted control record.

The journal may record `staged` only after all backup and staged desired payloads
are durable and verified. `staged` is the final no-live-object-mutation boundary.
Any backup, schema, capacity, identity, digest, ownership, or metadata-adapter
failure ends the attempt before `switching`.

Backup payloads and sensitive symlink text receive the same or stricter access
than the live originals. They are retained through final sign-off and the
approved recovery-retention deadline. Package rollback, a successful cutover,
or closure of the maintenance window never deletes them automatically.

## Live Apply Procedure

### Phase 1: Quiesce and freeze

1. Announce maintenance start and freeze deployment, schedule, and configuration
   changes that could affect the root or its consumers.
2. Stop or place every declared reader/writer into its approved maintenance mode
   using its owner-approved procedure. Disable automatic restarts that would
   recreate a writer.
3. Observe quiescence using process/service state, launch-surface status, open
   descriptor or activity evidence where available, and application-specific
   acknowledgements. A migration lock alone is insufficient.
4. Record owner-attributed results. An undeclared process, unexpected principal,
   new filesystem activity, or failed stop acknowledgement is a no-go.
5. Capture baseline service, doctor, scheduler/database, permissions, links, and
   non-target canary evidence for comparison. No check may print resolved secret
   values or raw DSNs.

Readers/writers remain quiesced from this point through backup, apply,
post-migration verification, and any rollback verification.

### Phase 2: Prepare and apply

After the backup gate passes, the migration operator invokes only the reviewed
migration-engine entry point with the explicit root, canonical plan, and
approved generation. The engine:

1. acquires the root-contained migration lock and revalidates the root,
   generation, plan digest, principal, platform capabilities, journal chain,
   backup set, staged payloads, and current preconditions;
2. advances through `prepared → staged → switching`;
3. for each deterministic plan step, durably records `intent`, performs the
   descriptor-relative no-follow operation, synchronizes it and its parent,
   reopens and verifies the exact postcondition, then records `completed`;
4. verifies every plan postcondition before `switched`; and
5. records `committed` only after final generation verification.

The operator captures value-free state transitions and timestamps but does not
edit the journal or inspect secret payloads for convenience. No mapping is
recompiled and no operation is appended after approval. If an operation's live
state matches neither its expected pre-state nor its desired post-state, the
engine stops because external interference is ambiguous.

### Interruption and recovery decision

For a process interruption, the migration operator does not rerun apply blindly.
The rollback authority first freezes the incident, preserves the generation,
and has the engine inspect the root binding, plan, journal chain, backup, stage,
and current postconditions.

- At `prepared` or `staged`, no destination mutation has occurred; the authority
  may abandon the attempt or continue only after the fault and approval remain
  valid.
- At `switching`, `intent`, `completed`, or `switched`, only the engine's tested
  state-specific recovery or rollback path may run. A trailing `intent` is
  treated as possibly applied.
- At `committed`, forward recovery is terminal and idempotent. If health checks
  require restoration, use the separately approved restore generation described
  below; do not attempt to reopen the committed journal.
- At `rolling_back`, only idempotent rollback resumption is permitted.
- At `rolled_back`, repeated rollback is verification-only and must not mutate.

A broken journal chain, plan/root mismatch, missing backup payload, failed digest,
or third-state object is escalated and fails closed. Manual repair requires a
new incident plan and authorization; it is never folded into the original run.

## Post-Migration Verification

All checks run while maintenance mode and the change freeze remain active. Each
result records scope, command/test identity, provider or consumer revision,
principal/environment, start/end timestamps, exit status, bounded redacted
output reference, owner, and disposition. Checks are run from installed artifacts
or owner-approved deployment surfaces, not sibling source checkouts.

| Scope | Required verification | Pass criteria |
|---|---|---|
| **Migration/journal** | Validate root/header binding, plan digest, generation UUID, complete hash chain, final state, backup manifest, and absence of unrecognized published temporaries. | Exact approved generation is `committed`; all structural and digest checks pass. |
| **Filesystem** | Reopen every planned destination and verify object kind, digest, mode, owner policy, supported metadata, and link behavior; compare non-target inventory/canaries. | Every planned postcondition matches and no out-of-scope object changed. |
| **Provider doctor** | Run the installed provider's strict, JSON doctor against the explicit approved root (for example, `tdt config doctor --root <approved-root> --strict --json`). | No required provider, layout, permission, ownership, duplicate-config, link, or redaction finding fails. |
| **Provider contract tests** | Run the approved installed-artifact contract suite without checkout imports or `PYTHONPATH`; verify packaged schemas/resources, dynamic root handling, and filesystem capabilities. | Exact deployed provider artifact passes all required contracts under the target runtime. |
| **Consumer smoke tests** | Each consumer owner runs its predeclared minimal smoke using the deployed artifact, intended principal, and explicit root/environment. Tests avoid destructive writes unless separately approved. | Every required consumer can resolve/read the intended resources and satisfies its owner-defined functional assertion. |
| **Deployment/service health** | Check process startup, logs/metrics, dependency health, and principal access for every declared launch surface. | All surfaces are healthy with no new error threshold breach, crash loop, or access widening. |
| **Scheduler/database** | Verify scheduler registration/state, queued/running work, connection health, and database invariants using approved read-only checks. Do not trigger a schedule or modify schema/data merely to test it. | No lost/duplicated/unexpected job, raw-DSN exposure, connectivity regression, or database invariant failure exists. |
| **Security/redaction** | Review access modes, backup permissions, evidence output, and any authorization change. | No secret value leaked and no principal gained broader access than approved. |

A provider doctor pass cannot waive a consumer failure. A consumer smoke pass
cannot waive journal, filesystem, scheduler, or database uncertainty. Any
non-waivable failure or unknown triggers `CONTINUE_MAINTENANCE` and escalation;
the rollback authority decides whether an understood transient check may be
retried within its deadline or rollback must begin.

## Rollback Procedure

### Rollback triggers

Rollback begins immediately, or as soon as the engine can reach a tested safe
boundary, when any of the following occurs:

- root, plan, generation, principal, capability, journal, backup, or payload
  integrity cannot be validated;
- an unapproved writer or external filesystem change is observed;
- exact restoration becomes time-critical under the outage budget;
- provider contract, filesystem, security, or redaction verification fails;
- a required consumer, deployment, scheduler, or database gate fails and cannot
  be resolved by its preapproved retry before the latest rollback start;
- service health exceeds a recorded rollback threshold;
- the authorizing operator withdraws approval; or
- the rollback authority determines continued forward recovery has higher risk.

Only the rollback authority records the decision and selected method. The
communications lead immediately announces that maintenance continues and
rollback is in progress. Readers/writers remain quiesced.

### Select the restore path

- **Before `switching`:** destination objects are unchanged. Validate that fact,
  mark the generation abandoned or rolled back through the engine's legal path,
  and verify the baseline; no payload restore is needed.
- **From a nonterminal forward state:** invoke the engine's rollback for the
  approved generation. The affected prefix includes every `completed` step and
  any trailing `intent`, and is restored in reverse plan order.
- **After `committed`:** the original journal is terminal. Invoke the
  precompiled, separately approved restore generation bound to the same live
  root and the retained backup manifest. Its desired state is exactly the
  pre-migration state represented by `BackupMetadata`; it has its own plan
  digest, journal, approval reference, and generation UUID. It is not an ad-hoc
  copy or mutation of the committed journal.

The post-commit restore plan is compiled and reviewed before Gate B so rollback
is executable under pressure. Activation of that plan is conditional on the
rollback authority's decision and does not grant blanket permission to restore
unrelated objects.

### Restore and verify

For either rollback generation, the engine re-anchors the root, reacquires the
migration lock, validates the relevant plan/journal chain, validates every
`BackupMetadata` entry and payload, and restores affected objects in reverse
order:

- a prior regular file is restored with exact verified content, mode,
  owner/group policy, digest, and registered metadata;
- a prior symlink is recreated from exact protected link text with no-follow
  replacement and verified digest;
- an object recorded as previously absent is removed only if its current state
  exactly matches this generation's approved applied postcondition; and
- a migration-created parent is removed only if still empty and its identity
  proves the generation created it.

An already-restored object is verified and skipped. An exact approved applied
state may be restored. Any third state stops rollback without overwriting it.
Every replacement and containing directory is synchronized and reopened before
rollback can advance. `rolled_back` is recorded only after a full reverse
verification proves that all affected objects match their backup metadata and
out-of-scope canaries remain unchanged.

After restoration, repeat the journal/restore verification, filesystem checks,
provider doctor, provider contract tests, baseline-compatible consumer smoke,
deployment health, scheduler/database checks, and security/redaction check. The
maintenance-release gate remains closed until the restored contract is directly
verified. If rollback itself fails, preserve all artifacts, keep writers
quiesced, declare an incident, and escalate rather than improvising filesystem
commands.

## Timeline and Decision Points

Actual aware timestamps, phase timeouts, and the latest safe rollback start are
required in the control record. The relative timeline below is the default
sequence; the authorizing operator may lengthen preparation but may not collapse
or reorder gates.

| Relative time | Activity and required decision |
|---|---|
| **T-7 days or earlier** | Freeze the candidate plan; collect provider rollout, conformance, synthetic recovery, owner, mapping, backup-capacity, restore-plan, smoke-test, and monitoring evidence. Resolve all unknowns. |
| **T-48 hours** | Run a tabletop review of quiescence, backup, apply, recovery, committed-state restore, communications, and escalation. Confirm contacts and rollback deadline. This is not a live rehearsal. |
| **T-24 hours** | Complete Gate A eligibility review; publish customer/stakeholder maintenance notice; reject stale evidence or reschedule. |
| **T-60 minutes** | Reconfirm installed artifact, runbook revision, root/plan identifiers, staffing, channels, outage budget, and absence of conflicting changes. |
| **T-15 minutes** | Open incident/status bridge, send start reminder, pause deployments/schedules as approved, and take read-only baseline evidence. |
| **T0** | Record Gate B `GO`, `HOLD`, or `NO-GO`. Only `GO` starts quiescence. |
| **T+0 to phase deadline** | Quiesce/freeze; prove all declared readers and writers stopped. A missed deadline is `HOLD` or rollback/no-go according to whether mutation began. |
| **After quiescence** | Capture and independently verify the complete `BackupMetadata` set and staged payloads. No mutation begins until `staged` is durable. |
| **Apply phase** | Apply the immutable plan and report durable phase transitions. Stop and escalate on drift or deadline breach. |
| **Verification phase** | Run every post-migration scope while maintenance remains active. Record Gate C decision before restarting consumers. |
| **Maintenance release** | Restart/re-enable only the approved readers/writers in the recorded order, then repeat immediate service/scheduler health checks. |
| **T+1 hour** | First heightened-monitoring review; confirm thresholds, incidents, and backup availability. |
| **T+24 hours minimum** | Complete the initial monitoring review. Monitoring remains open until each required scheduled/consumer observation in the control record has occurred or a bounded exception is approved. |
| **Monitoring end** | Record Gate D final sign-off, hand off open issues, and set (but do not automatically execute) backup/journal retention disposition. |

If any phase consumes the buffer needed for verified rollback before the window
ends, the default decision is rollback. Extending the outage requires explicit
authorizing-operator and affected-owner approval; silence is not approval.

## Communication Plan

The control record names a stakeholder status channel and a restricted incident
channel. Messages contain the run identifier, current phase, user-visible impact,
status (`ON_TRACK`, `HOLD`, `ROLLING_BACK`, `MONITORING`, or `CLOSED`), next
update time, and decision owner. They omit raw paths where unnecessary, root
identity internals, payloads, environment values, DSNs, credentials, sensitive
link text, and unredacted command output.

Required communications are:

1. **T-24 maintenance notice:** scope, expected impact, window, owner, and next
   notice; no claim that execution is already approved.
2. **T-60 reconfirmation:** final planned timing and contact path.
3. **T0 start/no-go notice:** actual decision and whether consumers are being
   quiesced.
4. **Phase notices:** backup verified, apply started, apply terminal state,
   verification started, maintenance released, and monitoring started.
5. **Cadence update:** at least every 15 minutes during outage/rollback and every
   30 minutes during a hold, even when there is no state change.
6. **Incident/rollback notice:** immediate notice of impact, containment, selected
   rollback path, owner, and next update time.
7. **Provisional completion:** maintenance-release decision, directly verified
   scopes, bounded exceptions, monitoring period, and backup-retention status.
8. **Final closure:** monitoring outcome, sign-off identities, open follow-up
   references, and retained recovery-artifact reference.

Consumer/deployment owners acknowledge quiescence and restart in the restricted
channel. The communications lead is the only default publisher to broad
stakeholders so command output and tentative diagnoses are not leaked or
contradictory.

## Escalation Path

| Level | Trigger | Immediate action | Escalate to |
|---|---|---|---|
| **L1 — execution hold** | Expected command/check failure before mutation, owner late, or evidence near expiry | Stop, preserve output, remain read-only, and resolve before phase deadline. | Change owner, migration operator, affected owner |
| **L2 — migration incident** | Apply interruption, failed health gate, unexpected writer, ambiguous object state, or rollback threshold crossed | Freeze forward work, keep services quiesced, preserve generation, and have rollback authority choose recovery or rollback. | Incident commander, authorizing operator, provider and affected service owners |
| **L3 — integrity/security incident** | Root/plan/journal/backup corruption, secret exposure, permission broadening, unknown principal, or suspected compromise | Stop all automated mutation, restrict evidence, do not post raw output, and preserve forensic state. | Security/on-call owner, incident commander, provider/filesystem owner |
| **L4 — rollback failure or sustained outage** | Restore cannot validate/converge, third-state interference, backup unavailable, or outage will exceed approved limit | Declare major incident, keep change freeze, prevent unapproved restart, and invoke organization incident/continuity procedure. | Executive/service incident authority, security where applicable, all affected owners |

Escalation never authorizes a broader filesystem scope. A decision to perform
manual recovery requires a new bounded incident plan, explicit authority, and
separate evidence. If the primary rollback authority is unavailable, only the
named fallback may decide; otherwise the run remains stopped.

## Heightened Monitoring

Monitoring starts only after maintenance release. Its duration is recorded in
the approved plan and is at least 24 hours for a deployed live cutover unless an
explicit bounded exception is approved. It remains open long enough to observe
each required consumer and scheduled workload identified in the plan.

The monitoring dashboard/checklist separates:

- provider doctor and contract status;
- filesystem permission, ownership, link, and out-of-scope canaries;
- consumer success/error/latency and startup/restart rates;
- deployment crash loops and principal-access denials;
- scheduler queue depth, missed/duplicate/failed executions, and next-run state;
- database connectivity and approved data invariants; and
- security, backup access, and evidence-redaction findings.

Thresholds and baseline comparison windows are fixed before Gate B. Reviews
occur immediately after restart, at approximately one hour, at 24 hours, and at
each required scheduled-workload observation. A threshold breach reopens the
incident and invokes the escalation/rollback decision model; monitoring must not
silently reset the baseline or redefine success after the fact.

## Evidence and Retention

The protected execution evidence contains the canonical plan, journal, complete
backup metadata and payloads, command results, and incident artifacts under the
access policy of the live data. The OpenSpec/store record contains only redacted
references, digests, versions, statuses, timestamps, counts, approvals, and
follow-up identifiers. Runtime data and planning/worktree changes are classified
separately.

Final evidence must make the following discoverable without exposing values:

- live root identity and pre/post inventory references;
- forward and restore plan digests and generation UUIDs;
- `BackupMetadata` manifest digest and verification result;
- complete journal-chain verification and terminal state;
- result/owner/timestamp for every health scope;
- quiesce/restart acknowledgements;
- communication and escalation timeline;
- maintenance-release and final sign-offs; and
- backup/journal retention owner, deadline, and eventual disposition reference.

Retention cleanup is a later explicit operator action. Before deleting a backup,
the owner rechecks that final sign-off is complete, no incident or audit hold is
active, the approved retention period elapsed, and another contractual recovery
need does not exist.

## Risks and Mitigations

| Risk / trade-off | Mitigation |
|---|---|
| Approval is applied to a different live state | Bind it to root identity, plan digest, inventory/preconditions, provider artifact, principals, and window; revalidate at every boundary. |
| A writer restarts during migration | Freeze launch surfaces and deployments, verify observed quiescence, monitor activity, and stop on any unexpected writer. |
| Backup is incomplete or corrupt | Snapshot the complete mutation scope with strict `BackupMetadata`, synchronize and reverify before `staged`, and precompile the restore generation. |
| Backup metadata exposes sensitive link or identity information | Keep full metadata protected with payloads; export only bounded references, counts, and digests to general evidence. |
| `committed` is mistaken for irreversible success | Keep health gates and maintenance release outside journal success; use the separately approved restore generation for post-commit rollback. |
| Provider checks hide consumer failures | Require owner-attributed provider, consumer, deployment, scheduler, and database gates separately. |
| Manual repair under outage pressure widens scope | Fail closed, retain artifacts, escalate, and require a new incident plan rather than ad-hoc filesystem commands. |
| Rollback removes an externally created object | Remove prior-absent objects only when current state exactly matches the approved generation postcondition; stop on a third state. |
| Monitoring declares success before scheduled behavior occurs | Set the required observations and thresholds before execution; keep monitoring/sign-off open until they occur or a bounded exception is approved. |
| Retained backups increase secret exposure | Use least-privilege protected storage, restrict dissemination, audit access, retain only by explicit policy, and delete only through a later approved action. |

## Success and Closure Criteria

The cutover is successful only when:

1. Gate A and Gate B approvals identify the exact live root, plan, provider,
   principals, window, backup, and restore plan;
2. all declared readers/writers were observed quiesced;
3. every mutable object received a verified `BackupMetadata` snapshot before the
   first live mutation;
4. the forward generation reached a valid `committed` state with all planned
   postconditions verified and all non-target canaries unchanged;
5. provider doctor, provider contracts, every required consumer smoke,
   deployment health, scheduler/database, and security checks passed or only a
   permitted bounded exception remains;
6. Gate C released maintenance and restart checks remained green;
7. heightened monitoring met all predeclared thresholds and observations;
8. Gate D final sign-off was recorded by the operator and affected owners; and
9. backup/journal evidence remains protected and discoverable under the approved
   retention policy.

If rollback is selected, the attempt is not reported as a successful cutover.
It is a successfully contained rollback only when the generation is terminal,
the pre-migration state is verified from `BackupMetadata`, non-target objects are
unchanged, baseline-compatible health checks pass, and an operator signs the
rollback report. Any failed or unknown criterion leaves the run open and
unarchived.