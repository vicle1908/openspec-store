# Design: TDT_HOME Synthetic Migration Engine

## Context

The TDT_HOME provider foundation establishes a dynamic root contract, strict
control-plane schemas, descriptor-relative filesystem operations, packaged
contract data, and an installed-wheel verification boundary. It intentionally
does not move live consumer data. The next required layer is a migration engine
that can prove the mechanics of a future cutover without touching the operator's
real `~/.tdt` tree.

A filesystem migration is not safe merely because each individual replacement
is atomic. A process can terminate after one object is replaced but before the
next object starts, after a replacement but before its completion is recorded,
or while rollback is restoring prior state. Recovery therefore needs a durable,
root-bound account of the plan and each transaction boundary, plus complete
pre-migration snapshots.

This change builds that engine and validates it only against synthetic source
and destination trees. Consumer adoption, process quiescence, service rollout,
and live operator cutover remain separate approval gates.

The engine is divided into five components with narrow responsibilities:

1. **Inventory reader** — reads only explicitly declared source roots, anchors
   them by identity, and emits typed, value-free object facts.
2. **Plan compiler** — combines the source inventory with governed migration
   rules and emits a canonical immutable plan plus a SHA-256 plan digest.
3. **Generation store** — owns one root-contained generation directory with the
   plan, journal header, hash-chained records, staging payloads, backups, and
   metadata.
4. **Apply/recovery engine** — acquires the root migration lock, validates all
   bindings, and advances or resumes the journal state machine.
5. **Synthetic harness** — creates isolated roots, controls child processes,
   injects real `SIGTERM` at durable boundaries, and verifies terminal state.

A generation uses a canonical nonzero UUID and is stored under a provider-owned
migration-state directory beneath the explicit target root. Conceptually:

```text
<TDT_HOME>/state/migrations/<generation-id>/
├── plan.json                 # canonical immutable typed plan
├── journal/
│   ├── header.json           # JournalHeader
│   └── records/
│       ├── 00000000.json     # JournalRecord("prepared")
│       ├── 00000001.json     # JournalRecord("staged")
│       └── ...
├── stage/                    # verified desired payloads, keyed by plan step
└── backup/
    ├── metadata.json         # ordered BackupMetadata entries
    └── objects/              # payloads for prior regular/symlink objects
```

Names are illustrative; the implementation may use equivalent provider-owned
relative components. It may not store generation artifacts outside the anchored
target root or accept an arbitrary journal path from the caller.

## Goals / Non-Goals

### Goals

- Compile an explicit source inventory and governed migration rules into one
  immutable, typed, deterministic migration plan.
- Bind each apply generation to the target root identity and canonical plan
  digest.
- Snapshot every destination object that the plan may mutate before the first
  destination mutation, using `BackupMetadata` and verified backup payloads.
- Apply the plan through the durable state sequence
  `prepared → staged → switching → intent → completed → switched → committed`.
- Resume safely and idempotently from every valid journal state, including a
  crash after a mutation but before its `completed` record.
- Roll back by reversing the journaled plan and restoring exact prior object
  state, including explicit prior absence.
- Exercise real `SIGTERM` interruption at every journal boundary in child
  processes, then prove recovery or rollback in a new process.
- Prove that all tests operate beneath an isolated temporary TDT_HOME root and
  do not inspect or mutate the operator's real root.

### Non-Goals

- Migrating the real `~/.tdt` tree or any production-selected `TDT_HOME`.
- Discovering consumer paths by convention, source grep, or a guessed map.
- Changing consumers, launchd jobs, Compose services, credentials, or scheduler
  deployment configuration.
- Treating a caller-provided Boolean as proof that writers are quiesced.
- Coordinating concurrent writers that do not participate in the migration
  lock. Writer discovery and quiescence are future rollout responsibilities.
- Supporting arbitrary directory replacement, hard-linked objects, devices,
  sockets, FIFOs, or unregistered filesystem metadata formats.
- Automatically deleting committed generation evidence or backups. Retention
  policy is a later operational concern.

## Decisions

### Decision 1: Compile inventory into a typed canonical plan

#### Source inventory

The compiler does not crawl arbitrary home directories. It accepts a validated
set of source roots and governed mapping rules. Inventory entries capture only
facts required to plan and later verify an operation:

- source-root identifier and anchored device/inode identity;
- safe source-relative and destination-relative object paths;
- object kind (`regular`, `symlink`, or explicit absence where allowed);
- mode, owner/group facts that policy permits the engine to preserve;
- size, link count, and content or link-text digest;
- presence of ACLs, xattrs, or flags and the registered metadata adapter needed
  to preserve them;
- the governing participant/rule identifier and schema version.

Inventory uses descriptor-relative, no-follow reads. A source object that changes
identity or digest between inventory and staging invalidates the plan rather than
silently changing its meaning.

#### Typed plan

The plan compiler validates the whole inventory before publishing a plan. Each
plan step contains a stable sequence number, operation kind, typed source and
destination relative paths, expected source facts, desired destination facts,
metadata strategy, and conflict policy. Payload values are not embedded.

Compilation rejects:

- duplicate or overlapping destination ownership;
- an undeclared source or destination;
- conflicting mappings for the same destination;
- replacement of an unsupported destination kind;
- source facts that require an unavailable metadata adapter;
- hard-linked regular files (`link_count > 1`) or any object whose exact restore
  semantics are not supported;
- a destination path that escapes or aliases the anchored target root;
- a secret-shaped scalar in control-plane metadata; and
- nondeterministic input such as unordered rules without a canonical key.

The compiler canonicalizes schema versions, normalized relative components,
operation order, and JSON serialization. It computes the plan digest over the
canonical bytes. The immutable `plan.json` written for apply must round-trip to
the same typed plan and digest. Recovery never recompiles from current source
state; it uses the exact plan bound into the generation header.

**Alternatives rejected:**

- *Discover destinations at apply time:* changes the transaction after review
  and makes recovery dependent on mutable external state.
- *Store an executable shell script as the plan:* provides no typed validation,
  deterministic postconditions, or safe recovery mapping.
- *Embed source contents in plan JSON:* increases secret exposure and makes
  diagnostics/control-plane data unsafe to retain.

### Decision 2: Use a root-bound, hash-chained journal

A generation is created while holding the target migration lock. The engine
anchors the target root, writes the canonical plan, and writes a `JournalHeader`
containing the generation UUID, target `RootIdentity`, plan digest, and creation
time. It then appends canonical `JournalRecord` objects.

Each record has a contiguous sequence number, state, previous-record hash, and
recomputable record hash. A record is published through a private temporary
file, complete write, file sync, descriptor-relative rename, and journal
directory sync. A temporary file that was never renamed is not a journal record.
A published record that fails schema, sequence, transition, or digest validation
makes the generation corrupt and non-actionable.

One file per record is preferred over in-place JSONL append because recovery can
unambiguously distinguish a published record from an interrupted temporary
write. The engine accepts only the longest fully valid contiguous chain and only
when any higher-numbered entries are recognized unpublished temporary artifacts;
a gap, duplicate, or malformed published record fails closed.

Only one apply/recover/rollback process may own the provider migration lock for a
target root. Lock acquisition is rooted in the same verified filesystem object;
a path-only lock in `/tmp` is not sufficient.

**Alternatives rejected:**

- *Use a mutable in-place journal:* an interrupted append or rewrite makes the
  publication boundary ambiguous and weakens chain verification.
- *Bind only to a caller-supplied path or external lock:* path rebinding can target
  a different filesystem object and an unrelated lock cannot serialize work for
  the anchored root.

### Decision 3: Make journal states explicit durability boundaries

The forward state machine is:

```text
prepared → staged → switching → intent ⇄ completed → switched → committed
                                      (one pair per ordered plan step)
```

The existing legal transition `completed → intent` represents advancement to the
next deterministic plan step. State meanings are:

| State | Durable facts and permitted next action |
|---|---|
| `prepared` | Header, canonical plan, and an initialized generation exist and validate. No destination object has been changed. Build and verify backups and staging. |
| `staged` | The complete backup set and every desired staged payload are durable and match typed metadata/digests. No destination object has been changed. Enter switching. |
| `switching` | The engine has durably committed to forward apply. Resolve the first not-completed step and append its intent. |
| `intent` | The next step is durably authorized. Its destination may be unchanged, partially acted on, or already at the desired postcondition. Reconcile that step only. |
| `completed` | The current step's destination postcondition has been reopened and verified. Append the next intent, or verify the entire plan and mark switched. |
| `switched` | Every plan postcondition and required metadata fact has been verified against the target root. Perform final generation verification and commit. |
| `committed` | The generation is terminal successful. Resume is an idempotent success and performs no mutation. |

The implementation invokes a test observer only after each state record and its
parent directory are durable. No success state is logged or reported before that
boundary.

#### Per-step switching protocol

For each deterministic plan step, the engine:

1. derives the step index from the validated journal history;
2. appends and synchronizes `intent`;
3. reopens the destination without following links;
4. if the exact desired postcondition already exists, treats the effect as done;
5. otherwise verifies that the destination is either the expected pre-state or a
   recognized interrupted state, then applies from the verified staged payload;
6. synchronizes the replacement and parent directory;
7. reopens and verifies kind, identity policy, size, digest, mode, ownership, and
   registered metadata facts; and
8. appends and synchronizes `completed`.

A destination that matches neither the expected precondition nor the desired
postcondition is ambiguous external interference. Recovery stops fail closed and
requires operator disposition; it never overwrites the object speculatively.

**Alternatives rejected:**

- *Record only a final success marker:* recovery could not distinguish which
  operation was authorized or durably verified before interruption.
- *Perform effects before durable intent:* a crash could leave an unaccounted
  mutation that neither forward recovery nor rollback can identify safely.

### Decision 4: Snapshot the complete pre-migration state

Before `staged` is recorded, the engine snapshots every destination object that
any plan step may change. Each snapshot has a strict `BackupMetadata` record:

- `regular` stores the protected payload plus mode, owner/group, size, SHA-256,
  link count, root/source identity, and supported metadata flags;
- `symlink` stores exact link text and its digest without following the link;
- `absent` records `prior_absent=true` and contains no invented payload or source
  identity.

If ACLs, xattrs, or flags are present, the snapshot names a registered metadata
adapter. Unregistered or unavailable adapters stop preparation. Hard links and
unsupported special objects are rejected instead of being flattened.

Backups are copied and verified through descriptors. Regular backup content is
synchronized before its metadata entry is published. The complete ordered
metadata manifest and backup directory are synchronized before `staged`.
`BackupMetadata` is validated again before any restore, and restored objects are
reopened and compared against that metadata before rollback can finish.

A pre-existing directory is never replaced by a leaf plan step. Required parent
directory creation is delegated to the provider's verified bootstrap primitive
and is permitted only where the typed plan declares it. Rollback removes a
migration-created directory only when it is still empty and its identity proves
it is the directory created by this generation; otherwise rollback fails closed
and preserves evidence.

**Alternative rejected:** a coarse archive of the whole root. It obscures which
objects are authorized, captures unrelated secrets, cannot represent prior
absence precisely, and makes exact reverse verification difficult.

### Decision 5: Recover by replaying state, not by guessing intent

Recovery requires the caller to select a canonical generation UUID. It acquires
the root migration lock, anchors the explicit root, validates the header against
that root and the stored plan digest, validates the complete journal chain, then
uses the terminal record as follows:

| Last state | Recovery action |
|---|---|
| `prepared` | Revalidate source facts, complete backup and staging, and append `staged`; or allow explicit rollback, which has no destination payload to restore. |
| `staged` | Revalidate the complete backup/stage set, append `switching`, and continue. |
| `switching` | Begin the first incomplete deterministic step by appending `intent`. |
| `intent` | Identify the current step from prior `completed` records. If the exact postcondition exists, append `completed`; otherwise safely reapply the same staged payload and verify it before appending `completed`. |
| `completed` | Continue with the next step, or verify all plan postconditions and append `switched`. |
| `switched` | Reverify the full final state, append `committed`, and return success. |
| `committed` | Return the existing committed result without changing files or adding records. |
| `rolling_back` | Resume idempotent reverse restoration and append `rolled_back` only after all prior states verify. |
| `rolled_back` | Return the existing rolled-back result without changing files or adding records. |

Recovery does not read current consumer manifests, recalculate operation order,
or trust a caller-supplied plan. A missing stage payload after `switching`, a
missing backup needed for rollback, or a plan/root binding mismatch is a hard
error. Diagnostics identify the generation, relative object path, expected fact
class, and state without rendering payload values.

**Alternatives rejected:**

- *Recompile from current inventory during recovery:* mutable source state could
  change the reviewed transaction and its deterministic operation order.
- *Retry the whole plan blindly:* already-completed steps and external interference
  would be indistinguishable from work that is safe to repeat.

### Decision 6: Roll back by reversing journaled effects

Rollback is explicit; a failed forward recovery does not silently choose
rollback. Once requested, the engine appends `rolling_back` at the first legal
rollback boundary and will only converge toward `rolled_back`.

The engine derives the possibly affected prefix from the validated journal:

- each `completed` record proves its corresponding plan step took effect;
- a terminal `intent` means the current step is uncertain and must also be
  restored because the mutation may have completed before interruption;
- `switched` means every plan step is in the affected prefix;
- `prepared` or `staged` has no destination effects, though generation artifacts
  still require terminal rollback recording.

Affected steps are visited in reverse plan order. For every step, rollback
revalidates `BackupMetadata` and backup payload, then:

- restores a prior regular file and supported metadata exactly;
- recreates a prior symlink with exact link text and no-follow replacement; or
- removes an object only when metadata proves it was previously absent and the
  current object matches this generation's desired postcondition.

Each reverse action is idempotent. Recovery from `rolling_back` scans the entire
affected prefix in reverse again: an object already matching its backup is
verified and skipped; an object matching the generation's applied postcondition
is restored; any third state is external interference and stops rollback. This
allows interruption after any reverse operation even though the value-free
journal does not expose object values or require a per-object rollback state.

After all destination objects and generation-created empty parents match the
pre-migration snapshot, the engine performs a full reverse verification and
appends `rolled_back`. Backups and journal evidence are retained.

Rollback from `committed` is not implicit. If a future operator workflow permits
post-commit rollback, it must be a separately approved generation with a new
plan using the retained snapshots; this synthetic engine treats `committed` as
terminal.

**Alternatives rejected:**

- *Choose rollback automatically after any failure:* some journal states can safely
  recover forward, and policy—not a low-level error—must select the outcome.
- *Generate inverse shell commands:* untyped inverse operations cannot prove exact
  prior absence, metadata restoration, or safe handling of interrupted effects.

### Decision 7: Test real process interruption at every boundary

The interruption harness runs migration commands in child processes. A private
test-only boundary observer reports `(generation, state, occurrence, sequence)`
to the parent only after the journal record is durable, then blocks. The parent
sends the child an actual `SIGTERM`, waits for signal termination, and starts a
fresh process for recovery or rollback.

The engine does not catch `SIGTERM` in these tests, translate it into a graceful
checkpoint, or call an in-process cleanup hook. The purpose is to prove that
already-durable evidence is sufficient when memory and open process state are
lost.

The forward matrix interrupts after every occurrence of:

- `prepared`;
- `staged`;
- `switching`;
- every per-step `intent`;
- every per-step `completed`;
- `switched`; and
- `committed`.

For every interruption point, a fresh recovery process must converge to the same
canonical destination state and `committed` journal as an uninterrupted run.
Recovery is then invoked again to prove terminal idempotence.

A complementary rollback matrix interrupts forward apply at each nonterminal
boundary, requests rollback in a fresh process, and verifies exact restoration.
It also interrupts after `rolling_back` and during each reverse operation, then
starts another process to resume to `rolled_back`. Because reverse operations do
not create a new journal state per object, the harness exposes test-only reverse
operation boundaries without changing the production journal schema.

The harness additionally corrupts one fact at a time—root identity binding, plan
digest, record hash/link, record sequence, stage digest, backup digest, and
unexpected destination state—and proves that recovery fails before any new
mutation.

**Alternatives rejected:**

- *Simulate interruption with exceptions or cleanup hooks:* those tests preserve
  process memory and do not exercise actual signal termination between durable
  filesystem boundaries.
- *Sample only one interruption point:* it leaves untested ambiguity at other
  journal occurrences and during reverse restoration.

### Decision 8: Enforce Cross-Cutting Migration Invariants

The following invariants apply to compilation, apply, recovery, and rollback:

1. **Explicit scope:** every source and destination object is declared by typed
   relative components. Absolute paths, `..`, globbing, empty components, and
   unregistered object kinds are rejected.
2. **Stable binding:** the `JournalHeader` binds a generation UUID, anchored
   target `RootIdentity`, canonical plan digest, and aware creation timestamp.
   The root identity and digest are revalidated before recovery or mutation.
3. **Deterministic order:** plan steps have a canonical total order. The nth
   `intent`/`completed` pair always refers to the nth plan step, so journal
   records contain no values or secret material.
4. **Durable-before-effect:** a state or intent record is atomically written and
   synchronized before the side effect it authorizes begins.
5. **Verified-after-effect:** `completed`, `switched`, or `committed` is recorded
   only after the corresponding postcondition is reopened and verified.
6. **Backup-before-mutation:** all `BackupMetadata` entries and required backup
   payloads are complete, synchronized, and verified before `switching`.
7. **Descriptor-relative mutation:** destination traversal and replacement use
   the provider security kernel with retained directory descriptors,
   no-follow checks, identity validation, file synchronization, rename, and
   parent-directory synchronization.
8. **Fail closed:** malformed schemas, a broken hash chain, an illegal state
   transition, root or plan mismatch, missing backup data, an unsupported object
   kind, or ambiguous destination state stops recovery without further mutation.
9. **Idempotent convergence:** retrying an authorized operation either verifies
   the already-achieved postcondition or recreates the same postcondition. It
   does not infer success merely from a file's presence.
10. **Value-free control plane:** journals, diagnostics, and plan metadata store
    object identities, relative paths, operation kinds, sizes, and digests—not
    file contents, resolved secret values, raw DSNs, or credentials. Payloads
    remain confined to protected staging and backup files.

**Alternatives rejected:**

- *Treat these invariants as implementation guidance:* optional interpretation
  would allow compile, apply, recovery, and rollback paths to enforce different
  containment or durability rules.
- *Validate binding and scope only at generation creation:* root replacement,
  plan drift, or journal corruption after creation could otherwise authorize a
  mutation against unreviewed state.

## Isolated Test Root Verification

All migration tests construct their source, target, process home, temporary
directory, and generation storage under a test-owned temporary directory. Child
processes receive both an explicit target-root argument and a sanitized
environment with `TDT_HOME`, `HOME`, and temporary-directory variables pointed at
that fixture. Repository-local dotenv loading is disabled by the selected test
profile.

Isolation is verified rather than assumed:

1. The child reports the anchored root identity; the parent compares it with the
   fixture target's device/inode.
2. Every plan, journal, stage, backup, and changed destination path is enumerated
   and proven descriptor-relative to that identity.
3. Source fixtures are made read-only where practical and compared before/after.
4. Canaries outside the source and target roots are hashed and statted before and
   after every interrupted run.
5. The test records the operator-root pathname before sanitizing the child
   environment and rejects any event or diagnostic that names it.
6. Filesystem event tracing or a provider-kernel mutation audit records every
   opened mutation anchor; the test asserts the set contains only the fixture
   target and test-owned IPC/temporary artifacts.
7. Tests use synthetic payloads and secret canaries, then assert that stdout,
   stderr, exceptions, plan JSON, and journal JSON do not contain payload or
   secret values.

No test obtains success credit solely because the final synthetic files look
correct. It must also validate the journal chain, header bindings, backup
metadata/payloads, absence of unrecognized staging temporaries, and unchanged
outside-root canaries.

## Durability Ordering

Each boundary follows the same ordering discipline:

1. write a private file through a retained directory descriptor;
2. write complete bytes and synchronize the file;
3. reopen and verify schema, identity, size, and digest as applicable;
4. rename descriptor-relative into its published name;
5. synchronize the containing directory;
6. only then expose the boundary to logs, IPC, or the next side effect.

For destination replacement, the staged payload is already durable before
`intent`; the replacement is synchronized and its parent directory is
synchronized before postcondition verification and `completed`. `switched`
requires full-plan verification. `committed` requires the journal and all final
verification evidence to be durable.

The implementation will use the provider security kernel rather than duplicating
pathname-based filesystem logic. If the supported macOS/Python runtime lacks a
required no-follow, descriptor-relative, identity, rename, or synchronization
primitive, mutating commands fail closed while read-only inspection remains
available.

## Concurrency and Invocation Contract

Public entry points separate compile, apply, recover, inspect, and rollback.
Apply accepts a reviewed typed plan and an explicit root; recover and rollback
accept an explicit root plus canonical generation UUID. They do not accept a
replacement journal location, an unchecked absolute object path, or a
`--quiesced` bypass.

The root migration lock serializes engine processes. This lock is necessary but
not sufficient for a future live cutover because current consumers may not
participate. Synthetic tests have no undeclared writers. Live writer inventory,
principal verification, shared-lock adoption, rollout approvals, and quiescence
proof are deferred to successor changes.

## Failure Semantics and Diagnostics

Failures are classified so callers can decide whether retry is safe:

- **Compilation failure:** no generation and no destination mutation.
- **Preparation failure:** generation may remain at `prepared`; destination is
  unchanged and recovery may retry after the underlying issue is corrected.
- **Switch failure:** journal remains at `switching`, `intent`, or `completed`;
  recovery or explicit rollback is required.
- **Verification failure:** no later success record is appended.
- **Corruption/binding failure:** generation is quarantined from automatic
  mutation; manual evidence review is required.
- **Rollback failure:** journal remains `rolling_back`; backup and generation
  evidence are retained for retry or inspection.

Diagnostics are structured and redacted. They may include generation UUID,
journal state and sequence, operation index, relative object path, expected and
actual digest labels, error category, and adapter identifier. They must not
include file contents, symlink targets classified as sensitive, resolved secret
values, raw environment values, or arbitrary journal bytes.

## Verification Strategy

Implementation evidence is organized into progressive gates:

1. **Compiler unit tests:** schema rejection, explicit inventory scope,
   deterministic ordering, canonical serialization/digest, duplicate/conflict
   detection, and source-change detection.
2. **Backup unit tests:** regular/symlink/absent snapshots, exact metadata,
   unsupported kinds and hard links, adapter enforcement, digest failure, and
   restore verification.
3. **Journal unit tests:** header bindings, canonical generation selection,
   contiguous hash chains, legal transitions, atomic publication, and corruption
   rejection.
4. **Apply/recovery integration tests:** multi-step uninterrupted apply and a
   recovery case for every state, including the post-effect/pre-`completed`
   ambiguity.
5. **Rollback integration tests:** reverse ordering, exact regular and symlink
   restore, removal for prior absence, interruption during rollback, terminal
   idempotence, and external-interference refusal.
6. **SIGTERM matrix:** separate-process termination after every state occurrence
   and reverse-operation boundary, followed by fresh-process convergence.
7. **Isolation/redaction tests:** root identity, mutation-anchor audit, outside
   canaries, sanitized environment, and payload/secret absence from control-plane
   output.
8. **Installed-wheel test:** build and clean-install the provider from the local
   wheelhouse without checkout or `PYTHONPATH`, then run a representative
   compile/apply/interrupt/recover/rollback cycle against an isolated root.
9. **Static and security gates:** project tests, lint, formatting, strict typing,
   dependency checks, and independent review focused on containment, durability
   ordering, recovery, rollback, and redaction.

Synthetic migration and rollback must pass twice from clean fixture roots before
the engine can be considered ready for a later consumer or live-cutover change.
Passing this change does not authorize live apply.

## Risks / Trade-offs

| Risk / trade-off | Mitigation |
|---|---|
| A journal claims more durability than the filesystem provides | Publish each record by synchronized file replacement plus parent-directory sync; expose test boundaries only afterward. |
| Crash occurs after mutation but before `completed` | Durable `intent`, deterministic step mapping, exact pre/postcondition checks, and idempotent reapply resolve the ambiguity. |
| Source changes after compilation | Bind inventory identity/digests into the plan and revalidate before staging; recovery uses staged payloads rather than mutable sources after switching. |
| Backup is incomplete or itself corrupted | Verify the complete `BackupMetadata` set and payload digests before `staged`, and revalidate before restore. |
| An external writer changes a destination during recovery | Accept only exact expected pre-state, desired post-state, or backup state for the current phase; otherwise fail closed. |
| State-only journal makes rollback progress less visible | Reverse operations are idempotent and inspect exact backup/applied postconditions; the durable `rolling_back` state forces future processes to continue rollback. |
| Keeping backups consumes space and retains sensitive payloads | Use protected provider-owned storage, minimal per-object snapshots, restrictive access, redacted metadata, and defer deletion to an explicit retention policy. |
| Synthetic fixtures miss production filesystem behavior | Use the same provider kernel and real subprocess/SIGTERM/fsync path; require a separate future live-readiness and principal/quiescence gate. |
| Test configuration accidentally resolves real TDT_HOME | Require explicit root plus sanitized `HOME`/`TDT_HOME`, compare root identity, audit mutation anchors, and verify outside canaries. |
| Unsupported ACL/xattr/flag semantics make restore lossy | Require a registered adapter and fail preparation when exact snapshot/restore cannot be proven. |

## Implementation Sequence

1. Define typed inventory and canonical migration-plan schemas with deterministic
   serialization and digest tests.
2. Implement root-contained generation storage, header creation, atomic journal
   record publication, and complete chain validation using the existing strict
   control-plane schemas.
3. Implement backup snapshot/verification for regular, symlink, and absent
   objects using `BackupMetadata`.
4. Implement staging and uninterrupted journaled apply through `committed`.
5. Implement state-specific recovery and post-effect/pre-completion
   reconciliation.
6. Implement explicit reverse-journal rollback through `rolling_back` and
   `rolled_back`.
7. Add the child-process boundary observer and exhaustive SIGTERM recovery and
   rollback matrices.
8. Add root-isolation, mutation-audit, corruption, redaction, and installed-wheel
   verification gates.
9. Run the complete synthetic suite twice from new fixture roots and retain the
   evidence for OpenSpec verification.
10. Leave the real operator root, consumers, services, and deployment metadata
    unchanged.

## Rollout and Rollback of This Change

Rollout publishes only the migration-engine code, schemas, tests, and synthetic
verification evidence in the provider artifact. No consumer invokes the engine
implicitly, and no installation hook starts migration. Mutating commands require
an explicit target root and plan/generation selection.

Code rollback restores the prior provider artifact. Synthetic generation roots
are test-owned and can be deleted by the test harness only after their assertions
complete. Any retained non-test generation evidence is not automatically removed
by package rollback. Because this change performs no live migration, reverting it
must not rewrite the operator's TDT_HOME.

## Open Questions

None for the synthetic engine boundary. Live source inventories, consumer-owned
mapping manifests, participating writers, runtime principals, quiescence proof,
backup retention duration, and post-commit live rollback policy belong to the
consumer-adoption and cutover changes and require separate review and approval.
