# Design: TDT_HOME Provider Release and Rollout

## Context

`tdt-core` is the shared provider for TDT_HOME path resolution, configuration
diagnostics, packaged governance contracts, and common runtime behavior. A
provider change can pass its source-tree tests while still fail after packaging:
package data can be omitted, distribution and runtime versions can disagree,
the console entry point can be missing, or a dependency can be satisfied only
by an ambient checkout or cache. It can also be correct in isolation while
breaking a particular consumer's dependency resolution, startup path, or
runtime assumptions.

This change defines the operational boundary between an approved `tdt-core`
source revision and controlled consumer availability. It qualifies one immutable
wheel and its dependency closure, publishes that exact artifact to the approved
internal Python registry, proves the registry copy in clean environments, and
then rolls it out to one consumer at a time. Every transition has an explicit
verification gate and retains the exact pre-change artifact needed to reverse
the transition.

The provider package contains `source-registry.json`. The registry currently has
15 participants with these roles:

- one provider: `tdt-core`;
- twelve consumers: `agent-core`, `agent-docs-sync`, `agent-harness`,
  `ai-harness-skills`, `browser-cli`, `code-daily-scan`, `jira-daily-reports`,
  `jira-kanban-from-spreadsheet`, `jira-skill`, `tdt-observability`,
  `tdt-sheets`, and `webhook-receiver`; and
- two verification participants: `ai-review` and `jira-epic-report`.

The participant snapshot is evidence about expected ecosystem membership, not a
deployment plan. A repository with role `verification` is not silently treated
as a deployable consumer, and a `consumer` entry is not proof that a live
deployment exists. Repository-owned governance manifests and rollout records
supply those facts.

This design defines publication and rollout procedures, but authoring this
OpenSpec change does not itself upload to Nexus or another registry, change
credentials, update consumer source, restart a service, or touch the operator's
real `~/.tdt`. Those effects occur only when an authorized release operator
executes the approved procedure.

## Goals / Non-Goals

### Goals

- Build a complete, locked wheelhouse from one clean `tdt-core` source revision.
- Bind the release candidate to its source revision, distribution version,
  wheel hash, lockfile identity, build-tool identity, supported runtime, and
  value-free artifact inventory.
- Prove the candidate from a fresh, checkout-free environment with no
  `PYTHONPATH`, editable install, package index, or ambient wheel cache.
- Verify version identity, the base CLI, `tdt config doctor`, packaged resources,
  and provider contracts from the installed artifact.
- Publish the exact qualified wheel to the approved internal registry without
  rebuilding it, then repeat clean installation and qualification from the
  registry copy.
- Roll out the pinned provider to one consumer at a time, with consumer-owned
  compatibility, health, observation, and approval gates before advancing.
- Rehearse reverse rollback by restoring the exact pre-change provider artifact
  and proving that the consumer returns to its recorded baseline behavior.
- Define fail-closed release criteria, monitoring signals, rollback triggers,
  ownership, and redacted evidence retention.
- Keep provider, publication, consumer, deployment, and live-root readiness as
  distinct claims.

### Non-Goals

- Migrating consumer source from legacy path construction to provider APIs.
- Cutting over, repairing, or mutating the live `~/.tdt` tree.
- Changing databases, application schemas, credentials, service configuration,
  launch definitions, or runtime principals as part of the provider release.
- Choosing or configuring the internal registry product, creating credentials,
  rotating tokens, or changing repository retention policy.
- Treating local source tests, a successful upload, or a passing provider doctor
  as proof that every consumer is ready.
- Rolling out multiple consumers concurrently.
- Automatically promoting a failed or unknown gate through an operator override.
- Deleting the pre-change artifact or release evidence immediately after a
  successful rollout.

## Architecture and Promotion Flow

The release is an immutable promotion pipeline:

```text
clean source revision
        |
        v
locked wheelhouse build
        |
        v
checkout-free qualification
        |
        v
internal registry publication of the same wheel bytes
        |
        v
registry-download qualification
        |
        v
consumer 1 -> verify -> soak -> reverse rollback rehearsal -> approve
        |
        v
consumer 2 -> verify -> soak -> reverse rollback rehearsal -> approve
        |
       ...
        |
        v
consumer N -> verify -> soak -> reverse rollback rehearsal -> approve
        |
        v
ecosystem rollout record
```

The system has five logical components:

1. **Builder** — creates the provider wheel and complete dependency wheelhouse
   from an immutable source revision and locked dependency graph.
2. **Qualifier** — installs the wheelhouse into disposable environments and runs
   the clean-environment verification matrix.
3. **Publisher** — uploads only the qualified provider wheel and records the
   internal registry coordinate and returned digest. It does not rebuild.
4. **Consumer rollout controller** — serializes consumer changes, evaluates each
   repository's rollout manifest, and blocks advancement until all gates for the
   current consumer pass.
5. **Evidence store** — retains value-free build, publication, verification,
   approval, monitoring, and rollback records keyed by a release ID.

These may be CI jobs rather than new application services. Their separation is
logical: a principal allowed to upload a package need not be able to deploy a
consumer, and a consumer operator need not receive package-publishing
credentials.

## Release Identity and Evidence Envelope

A release ID identifies one candidate and is never reused. The canonical release
envelope records at least:

- package name (`tdt-core`) and expected normalized distribution name;
- source repository URL or stable repository identity;
- full source commit and whether the build tree was clean;
- annotated release tag when policy requires one;
- public distribution version;
- wheel filename, wheel tags, size, and SHA-256 digest;
- wheel `METADATA` name/version and `RECORD` digest;
- `uv.lock` or equivalent lockfile SHA-256 and the selected runtime subset;
- SHA-256 digest for every wheel in the wheelhouse;
- Python implementation and exact version (currently Python `>=3.14,<3.15`);
- operating system and architecture for every qualification lane;
- builder, build backend, `uv`, and installer identities and versions;
- source-registry schema version and SHA-256 digest;
- contract-test bundle identity and digest;
- build and qualification timestamps in UTC;
- CI run identity, release operator, and approval references;
- internal registry repository, immutable package coordinate, and registry-copy
  digest after publication; and
- the exact pre-change artifact coordinate, digest, and dependency closure used
  for rollback.

The envelope contains no registry token, environment value, credential, raw
configuration, DSN, secret-bearing doctor output, or consumer payload. Command
output is redacted before retention. Evidence files are written atomically and
considered complete only after their schema and referenced hashes validate.

## Decision 1: Build One Immutable Candidate from a Locked Wheelhouse

### Source and version preconditions

The builder operates on an immutable checkout of the approved revision. Before
building, it verifies:

1. the checkout revision equals the revision in the release request;
2. the tracked tree is clean and has no generated wheel, `dist/`, stale evidence,
   or untracked package data that could enter the build;
3. the release version is valid, not a mutable development version unless the
   target repository explicitly permits prereleases, and has not already been
   published;
4. project metadata, the importable runtime version, and the release request
   agree; and
5. the lockfile is current for `pyproject.toml` and covers the supported Python
   runtime and required provider extras selected for release.

A dirty source tree or version mismatch blocks the build. The pipeline does not
repair metadata, regenerate the lock silently, or infer which source value is
authoritative during a release run.

### Wheelhouse construction

The wheelhouse is a release unit, not merely a directory containing the provider
wheel. It contains:

- exactly one candidate `tdt-core` wheel;
- all transitive wheels required by the base provider contract for each supported
  target lane;
- any separately declared extra closure used by a rollout lane, kept distinct
  from the base closure;
- a fully hashed, machine-readable install manifest mapping normalized package
  names and versions to wheel filenames and SHA-256 digests; and
- a value-free inventory and build log.

The build resolves only from the approved lock and approved upstream package
source. Dependencies are downloaded as wheels for the declared runtime/platform
lane; an unexpected source distribution is a release-gate failure unless an
approved reproducible source-build lane builds and qualifies its resulting wheel
separately. Duplicate candidates for one normalized name/version, an unresolved
dependency, an unhashed file, or a wheel not referenced by the closure fails the
wheelhouse check.

The provider wheel is built once. Qualification, publication, registry
verification, and consumer rollout all use those same bytes. A code, metadata,
lock, build-tool, or package-data fix invalidates the candidate; the pipeline
assigns a new candidate execution, rebuilds the wheelhouse, and reruns every
artifact gate.

### Reproducibility

Where the build backend and wheel metadata permit byte-for-byte reproducibility,
an independent rebuild from the same revision and declared build environment
must produce the same provider wheel hash. If unavoidable build metadata prevents
byte identity, the pipeline must at minimum prove an equivalent normalized wheel
inventory and document the differing fields. This weaker result requires an
explicit release-policy approval and never permits the publisher to substitute
the independently rebuilt wheel for the originally qualified bytes.

**Alternatives rejected:**

- *Build during publication:* it creates unqualified bytes after the gate.
- *Install dependencies from the network during qualification:* it makes the
  result depend on changing indexes and cannot prove closure completeness.
- *Use an editable install for smoke tests:* it can hide missing entry points and
  package resources.
- *Treat the lockfile alone as the artifact:* a lock does not prove that every
  required wheel is downloadable or installable for the target runtime.

## Decision 2: Qualification Runs in a Checkout-Free Clean Environment

Each qualification lane starts with a newly created virtual environment or
container/VM that has only the supported Python runtime and the approved
installer. The source checkout is not mounted or present in the working
directory. The runner clears `PYTHONPATH`, `PYTHONHOME`, virtual-environment
inheritance, editable-install state, and package caches. Offline qualification
installs with index access disabled and with the wheelhouse as the only package
source. `pip check` or the installer-equivalent dependency consistency check must
pass after installation.

Doctor tests use a test-owned, absolute temporary TDT_HOME fixture supplied
through the supported explicit-root interface or sanitized `TDT_HOME`. They do
not rely on the runner's real home and must prove, using an outside-root canary or
equivalent audit, that the operator's real `~/.tdt` was neither opened for
mutation nor changed.

### Verification matrix

Every supported release lane executes the following checks against the installed
candidate. A skipped, unavailable, contradictory, or indeterminate result is not
a pass.

| Area | Verification | Required result |
|---|---|---|
| Install | Install the fully hashed base closure with no index, cache, source checkout, or editable path; run dependency consistency check. | Installation and dependency check pass using only inventoried wheelhouse files. |
| Distribution version | Read `importlib.metadata.version("tdt-core")`, wheel filename, and wheel `METADATA`. | All equal the release-envelope version. |
| Runtime version | Import `tdt_core` and read its public runtime version. | Equals the distribution version exactly. |
| CLI version | Run `tdt --version` and compare its machine-normalized version with metadata. If an older supported CLI also exposes `tdt version`, that alias may be checked, but it cannot replace the canonical probe. | Command exits zero and reports only the installed candidate version. |
| CLI discovery | Run `tdt --help` and `tdt config doctor --help` from a working directory with no checkout. | Commands exit zero; base CLI and doctor are reachable without scheduler extras. |
| Doctor, conforming root | Run `tdt config doctor --root <isolated-valid-root> --strict --json` (or the equivalent supported option ordering). | Exit zero; result is schema-valid, value-free, and contains no false finding. |
| Doctor, negative fixtures | Run doctor against isolated fixtures with representative missing root, unsafe mode, broken link, ambiguous configuration, and secret-placement findings. | Stable finding classes and strict nonzero status match the contract; output remains redacted. |
| Package resources | Load package data through `importlib.resources`, not source-relative paths. Parse `source-registry.json` and any packaged schemas/contracts. | Resources exist in the wheel, parse strictly, and their digests equal the release envelope. |
| Registry contract | Validate the packaged participant registry. | Schema version is supported; all repository IDs are unique; there are exactly 15 participants: one provider, twelve consumers, and two verification participants. |
| Provider contracts | Run the versioned, immutable provider contract suite against only the installed distribution. | CLI, path-resolution, resource, diagnostic schema, and redaction contracts pass. |
| Import isolation | Record imported module origins and search installed metadata for editable/direct-url leakage. | Every `tdt_core` module resolves under the disposable environment's installation root; no sibling checkout or developer path appears. |
| Secret/redaction | Use synthetic canary values in negative diagnostics and scan stdout, stderr, exceptions, JSON, and retained logs. | No canary value, credential, raw environment value, or unapproved absolute home path is emitted. |
| Uninstall/reinstall | Remove the candidate, verify its commands/imports disappear, then reinstall from the same wheelhouse. | Reinstallation is deterministic and the same matrix subset passes. |

The supported lane set is derived from package metadata and release policy. At
minimum, every operating-system/architecture combination on which the provider
is approved for consumer rollout must be represented with a Python version in
`>=3.14,<3.15`. A lane absent from the matrix is unsupported for this release;
it is not implicitly covered by a different host.

Source-level tests, lint, type checking, security review, build configuration
validation, and secret scanning run before artifact qualification. They remain
required release evidence, but they do not substitute for any installed-wheel
matrix row.

### Contract-test isolation

The contract suite used after installation is versioned independently from the
source checkout and included in the evidence envelope by digest. It may be
provided as a release-test bundle or installed test package, but must not import
fixtures, helpers, or modules from the candidate's source tree. A test that
passes only when executed from the `tdt-core` checkout fails isolation.

## Decision 3: Publish by Promotion, Then Re-qualify the Registry Copy

Publication is allowed only after all source and offline clean-environment gates
pass. The publisher uploads the exact qualified provider wheel to the approved
internal Python registry under its immutable name and version. The dependency
closure may already exist in approved internal repositories; whether dependency
wheels are mirrored is registry-policy specific, but every coordinate and digest
used to reinstall must remain recorded.

Publication follows these rules:

1. package upload and consumer deployment use separate least-privilege
   principals;
2. credentials are injected by the CI secret mechanism and never written to the
   wheelhouse, command transcript, configuration artifact, or release envelope;
3. an existing name/version with a different digest is a hard failure;
4. overwrite, delete-and-reupload, mutable snapshot, and unpinned "latest"
   semantics are prohibited for release coordinates;
5. the registry response, immutable coordinate, and digest are recorded;
6. the published artifact is downloaded into a new empty directory;
7. its SHA-256 must equal the qualified wheel hash before installation; and
8. a new disposable environment installs by exact version from the internal
   registry and reruns the entire clean-environment matrix.

A successful upload is not release readiness. The registry-download matrix proves
that index metadata, package naming, permissions, dependency visibility, and
downloaded bytes are usable by a consumer-like principal. Authentication or
network failure is classified as a publication failure or unknown result, never
as a package pass.

If the approved internal registry is Nexus, this procedure applies to its hosted
Python repository; the OpenSpec change does not create that repository or rotate
Nexus credentials. An equivalent internal registry may be used when the release
record identifies it and it satisfies immutability, digest, access-control, and
audit requirements.

**Alternative rejected:** consume directly from CI artifacts. A CI artifact can
support investigation or rollback retention, but it does not verify the package
index and permission path consumers will use.

## Decision 4: Roll Out to One Consumer at a Time

### Rollout inventory and ordering

Before the first consumer change, the rollout controller snapshots the exact
packaged `source-registry.json` and joins each `consumer` participant to its
repository-owned governance manifest. The join determines whether the repository
is a library, CI-only tool, scheduled job, service, or other deployable unit;
its owner; launch mechanism; deployment targets; provider dependency mechanism;
health command/endpoint; and runtime principal.

The 12 registry participants with role `consumer` form the required rollout
inventory. The two `verification` participants supply the separately declared
ecosystem checks assigned to them; they are not added to the install queue unless
their own manifest declares a provider-consuming deployable surface. A missing,
duplicate, stale, contradictory, or unowned participant record blocks rollout
planning.

Consumer order is explicit and approved before rollout. It normally progresses
from the smallest reversible/non-deployed surface through stateless services to
stateful or scheduler-coupled workloads, but risk—not alphabetical order—selects
the sequence. Changing the order requires a new approval record. There is one
active consumer transaction at a time; queued consumers retain their current
provider artifact.

### Per-consumer preflight

For consumer `C`, preflight records:

- immutable consumer source/deployment revision;
- accountable repository owner and deployment operator;
- current provider version, wheel hash, dependency closure, and package source;
- candidate version, exact internal-registry coordinate, and expected hash;
- supported Python, OS, and architecture lane;
- dependency/lock resolution showing the candidate satisfies the consumer's
  declared bounds without unrelated upgrades;
- source-conformance and provider-contract result required by that consumer;
- target, launch mechanism, runtime principal, configuration profile, and health
  endpoint or smoke command;
- current redacted health, error-rate, startup, and business-check baseline;
- observation/soak period and metric thresholds;
- retained pre-change wheelhouse or immutable registry coordinates;
- exact upgrade, verification, and rollback procedures; and
- approvals for the candidate, target, and maintenance/deployment window.

Unknown current artifact identity, unresolved dependencies, a dirty or mutable
consumer revision, missing ownership, missing health checks, unavailable
rollback bytes, or inability to separate provider upgrade from unrelated package
changes blocks the consumer.

### Per-consumer transaction

Each consumer passes through these states:

```text
pending
  -> preflight_passed
  -> candidate_installed
  -> startup_verified
  -> behavior_verified
  -> observing
  -> rollback_rehearsed
  -> approved
```

Failure or approval withdrawal from any nonterminal state transitions to
`rolling_back`, then either `rolled_back` after verification or
`rollback_failed`. A consumer in `rollback_failed` stops the ecosystem rollout
and triggers operator escalation. The next consumer cannot enter
`candidate_installed` until the current consumer reaches `approved` and the
release operator records the advance decision.

The consumer deployment must pin both version and accepted wheel digest. It must
not resolve an unbounded latest version or perform unrelated dependency upgrades.
After install and restart/reload where applicable, its verification gate checks:

1. runtime package metadata and imported `tdt_core` version/hash equal the
   candidate;
2. `tdt --version`, `tdt --help`, and the consumer-relevant provider diagnostics
   are reachable in the same runtime environment/principal as the consumer;
3. `tdt config doctor` runs only against the approved isolated or explicitly
   authorized target root and produces the expected redacted result;
4. consumer contract tests and startup/import smoke tests pass;
5. the declared health endpoint, scheduled dry run, or bounded business smoke
   test matches its preflight expectations;
6. logs contain no new provider import, path, permission, configuration,
   deprecation, or dependency errors and no secret canaries;
7. databases, credentials, consumer source, and live TDT_HOME data have not been
   migrated or rewritten by the package install; and
8. monitoring remains within the consumer's approved thresholds for the complete
   observation period, including at least one representative workload cycle for
   scheduled consumers.

A library/non-deployable consumer performs the same transaction in its clean CI
or integration-test environment and uses its contract suite in place of a
service restart. A provider-only pass cannot satisfy a consumer behavior check.

### Advancement gate

The release operator may advance to the next consumer only when:

- every per-consumer preflight and behavior check is `PASS`;
- the observation period completed without a rollback trigger;
- reverse rollback rehearsal completed and re-upgrade, if required to leave the
  candidate staged, used the same candidate bytes;
- the consumer and deployment owners approved the evidence;
- no unresolved severity-one or severity-two release finding exists; and
- monitoring and rollback ownership for the next consumer are staffed.

`SKIPPED`, `UNKNOWN`, `NOT_APPLICABLE` without a reviewed rationale, and
`PASS_WITH_WARNINGS` are not silently promoted to `PASS`. An approved exception
must identify its exact bounded condition, owner, expiry, and why it cannot mask
a version, resource, contract, health, or rollback failure.

## Decision 5: Rehearse Reverse Rollback with the Real Artifacts

Rollback capability is proven before ecosystem advancement rather than inferred
from the existence of an older version number. The rehearsal runs in the
consumer's disposable/staging target using the same package source, install
mechanism, runtime principal, launch mechanism, and verification commands planned
for rollout.

The sequence is deliberately forward and reverse:

1. install the retained pre-change provider wheel and locked closure;
2. verify its package hash/version and record the consumer's redacted baseline;
3. install the candidate by exact coordinate and hash;
4. verify candidate startup, contracts, health, and representative behavior;
5. stop or quiesce the consumer using its approved deployment procedure;
6. uninstall/replace the candidate and restore the exact pre-change provider
   wheel and its compatible locked closure, without rebuilding;
7. restart/reload through the normal deployment path;
8. prove metadata, imported version, `tdt --version`, module origins, and installed
   file inventory correspond to the pre-change artifact;
9. rerun the same consumer smoke, health, contract, and monitoring probes captured
   in step 2; and
10. compare approved configuration/data canaries and show that consumer source,
    credentials, databases, and TDT_HOME contents were not changed by rollback.

A passing rehearsal requires the restored artifact to match the exact retained
SHA-256, not merely the same public version. It also requires consumer behavior
to return to the pre-change acceptance range; command success alone is
insufficient. Installer caches are cleared or bypassed so the evidence cannot
accidentally reuse candidate files.

Where the rollout target must finish on the candidate, the operator may reapply
the same candidate bytes after the reverse proof and rerun the candidate health
and observation gates. This second forward transition is recorded; it is not
assumed safe because the first one passed.

If a candidate introduces an irreversible database, configuration, or live-root
change, artifact rollback is not sufficient and this change's release gate must
remain closed. Such a transition requires a separate migration/cutover design
with its own snapshot and recovery procedure.

A rehearsal deferral is permitted only when the target is demonstrably
non-deployable and an equivalent clean integration target proves install,
behavior, restore, and re-verification. The release record names the bounded
rationale and approver. A deployable consumer cannot waive rollback rehearsal
merely because the provider passed elsewhere.

## Release and Rollout Gate Criteria

Readiness is reported as separate scopes. No aggregate green status may hide a
failed or unverified lower-level scope.

### Gate A: Source and build readiness

Pass only when:

- the approved revision and release metadata are immutable and agree;
- source tests, lint, strict type checks, security/review gates, and redaction
  scans pass;
- the lock is current and the supported runtime/platform lane set is explicit;
- the wheelhouse closure is complete, unique, and fully hashed; and
- the candidate wheel and release envelope are complete and internally
  consistent.

### Gate B: Artifact readiness

Pass only when every clean-environment matrix lane passes from the offline
wheelhouse and imported modules, CLI entry points, doctor behavior, resources,
participant counts, versions, and contract tests agree. Failure leaves the
candidate unpublished.

### Gate C: Publication readiness

Pass only when the internal registry contains the exact qualified wheel bytes,
the registry coordinate is immutable, a consumer-like principal can download by
exact version, the downloaded hash matches, and the full registry-install matrix
passes. Upload success alone is insufficient.

### Gate D: Consumer readiness

Evaluated independently for each consumer. Pass only when preflight, exact
install, version/hash verification, provider diagnostics, consumer contracts,
startup/health/business smoke, observation, monitoring, reverse rollback, and
owner approvals pass. One consumer's result cannot be copied to another.

### Gate E: Ecosystem rollout completion

Pass only when:

- all 12 participants with registry role `consumer` have one current approved
  rollout record or a reviewed non-deployable integration record;
- the two verification participants have produced their assigned compatible
  verification evidence or are explicitly outside the release's approved scope;
- records bind the same provider version and SHA-256;
- no consumer remains pending, observing, rolling back, failed, unknown, or on an
  unauthorized artifact;
- monitoring is healthy through the ecosystem observation window; and
- the retained rollback artifacts and responsible operators remain available.

Gate E proves provider distribution and bounded consumer rollout. It does not
prove live-root migration or authorize `~/.tdt` cutover.

## Monitoring and Operational Response

### Signals

Monitoring starts before each consumer upgrade to establish a baseline and
continues through the per-consumer observation period and the ecosystem window.
The release dashboard or evidence record tracks, per target:

- expected versus observed `tdt-core` version and wheel SHA-256;
- startup/restart success, readiness/liveness, and process crash/restart count;
- provider import, missing-resource, entry-point, dependency, and version errors;
- `tdt config doctor` finding counts by stable class and severity, with paths and
  values redacted;
- TDT_HOME path-resolution, permission, broken-link, configuration ambiguity, and
  secret-placement failures;
- consumer contract-test and smoke-test status;
- request/job success rate, error rate, latency, queue depth, schedule completion,
  or other consumer-owned service-level indicators;
- scheduler/database connectivity where the consumer contract requires it,
  without logging DSNs or credentials;
- package-resolution drift or an unexpected provider/dependency replacement;
- log redaction canary results; and
- rollback artifact availability and last successful rehearsal time.

Each signal has a named owner, data source, baseline window, observation window,
and approved threshold in the consumer rollout record. Lack of telemetry needed
to evaluate a required threshold is `UNKNOWN` and blocks advancement.

### Rollback triggers

The current consumer rolls back and the serialized rollout stops when any of the
following occurs:

- installed version or hash differs from the approved candidate;
- startup, health, provider contract, consumer contract, or required doctor gate
  fails;
- a packaged resource or console entry point is missing;
- a new path, permission, configuration, dependency, or secret-redaction failure
  appears;
- consumer error/latency/job metrics cross an approved threshold;
- an unexplained database, credential, source, deployment, or TDT_HOME mutation is
  observed;
- monitoring becomes unavailable before the observation gate completes;
- consumer or release approval is withdrawn; or
- the pre-change artifact can no longer be retrieved and hash-verified.

Rollback is initiated for the current consumer only. Already approved consumers
remain on the candidate unless evidence indicates a shared artifact defect; a
shared defect triggers coordinated rollback in reverse rollout order, one
consumer at a time, using each consumer's recorded procedure. Queued consumers
remain unchanged.

### Incident and escalation behavior

The operator freezes promotion, preserves artifacts and redacted evidence,
records the last completed transaction state, and notifies the provider release
owner plus the current consumer owner. A failed rollback escalates immediately
to the deployment owner and incident process; it never causes speculative
consumer-source edits, credential changes, database repairs, or live-root
mutation. Resumption requires disposition of the finding and fresh approval.
Any candidate rebuild or digest change restarts Gate A rather than resuming the
old rollout ledger.

## Evidence Retention and Security

The internal registry and independent release storage retain both candidate and
pre-change provider artifacts for at least the organization-defined rollback and
incident-analysis period. Retention covers wheel bytes, hashed dependency
manifests, release envelopes, clean-environment results, publication receipts,
consumer approvals, monitoring summaries, and rollback rehearsal records.

Evidence follows these controls:

- package and report digests are SHA-256 or the stronger organization-approved
  replacement;
- immutable object/version retention is preferred over mutable job workspaces;
- access is least privilege and reads/uploads are auditable;
- logs and structured reports use stable finding classes and relative/logical
  target identities rather than raw secret-bearing values;
- registry URLs are stripped of embedded credentials;
- synthetic secret canaries are scanned across stdout, stderr, JSON, exception,
  and retained report surfaces; and
- deletion after expiry follows registry/evidence policy and cannot remove the
  active rollback artifact during rollout.

## Transaction Boundaries

1. **Build transaction:** validate source/lock/version, build once, inventory and
   hash all artifacts, then publish the completed release envelope. An interrupted
   build creates no candidate eligible for qualification.
2. **Qualification transaction:** create a clean lane, install from one immutable
   source, execute the complete matrix, and atomically publish the lane result.
   Partial rows cannot produce a passing lane.
3. **Publication transaction:** upload the qualified bytes, record the immutable
   coordinate, download, hash-compare, and requalify. Publication is not complete
   at upload acknowledgement.
4. **Consumer transaction:** bind preflight and baseline, install one candidate,
   verify, observe, rehearse rollback, and receive owner approval before changing
   the queue head.
5. **Rollback transaction:** select the recorded pre-change artifact, restore it,
   reopen and verify identity, rerun consumer behavior checks, and only then mark
   rollback complete.
6. **Ecosystem completion transaction:** aggregate one compatible record for each
   participant role, verify a common artifact digest and terminal state, then
   publish the scoped completion claim.

No transaction in this design authorizes live TDT_HOME data migration.

## Failure Semantics

- **Build failure:** no publishable candidate exists; correct the source/build
  input and start a new build execution.
- **Offline qualification failure:** candidate remains quarantined and is not
  uploaded to the release repository.
- **Publication failure:** no rollout occurs. If upload state is ambiguous, query
  by immutable coordinate and digest; never blindly retry an overwrite.
- **Registry qualification failure:** artifact remains unavailable for rollout
  even if upload succeeded.
- **Consumer preflight failure:** that consumer and all later consumers remain on
  their current artifacts.
- **Consumer verification/monitoring failure:** roll back the current consumer and
  stop advancement.
- **Rollback failure:** preserve both artifact sets and target evidence, mark
  `rollback_failed`, and escalate; do not continue rollout.
- **Evidence/version disagreement:** fail closed at the earliest affected gate and
  invalidate downstream claims that depend on it.
- **Monitoring unknown:** treat as a blocked observation gate, not a pass.

## Risks / Trade-offs

- **Serial rollout is slower.** It limits blast radius and makes the first failing
  consumer attributable, which is more valuable than parallel speed for a shared
  provider.
- **A complete wheelhouse can be platform-specific.** Build and identify separate
  closures per supported lane rather than claiming one host proves all hosts.
- **Internal indexes may not expose a trusted digest API.** Download the bytes and
  compute SHA-256 independently; do not rely only on index metadata.
- **Dependency solvers can introduce unrelated upgrades.** Compare pre/post lock
  plans and require the consumer deployment to pin the intended provider and
  approved closure.
- **Doctor output may expose sensitive paths or values.** Use isolated fixtures,
  stable finding classes, JSON schema checks, canaries, and redaction scans before
  retaining output.
- **The participant registry can drift during a long rollout.** Bind the rollout
  to one registry digest. A membership/role change requires explicit
  reconciliation and a revised rollout plan, not silent queue mutation.
- **A rollback can restore package identity but not behavior.** Require the same
  consumer probes and metric range used for the pre-change baseline.
- **Verification participants do not map cleanly to deployable units.** Keep role
  handling explicit and require repository-owned deployment facts instead of
  inferring them from the central registry.
- **Artifact retention can conflict with cleanup policy.** Protect the active
  candidate and pre-change artifact until rollout and incident windows close.
- **Reproducible wheel bytes may be difficult with some build tooling.** Prefer
  deterministic builds; when byte identity cannot be proven, record normalized
  differences and require an explicit risk decision while still promoting only
  the exact qualified artifact.

## Implementation and Rollout Plan

1. Define the release-envelope, wheelhouse-manifest, qualification-result,
   publication-result, consumer-rollout, and rollback-result schemas.
2. Pin the builder and supported Python/platform lanes; add clean-tree, metadata,
   lock-currentness, package-data, and artifact-inventory checks.
3. Build the complete hashed wheelhouse and qualify it offline in fresh,
   checkout-free environments.
4. Add or externalize the installed-distribution contract bundle and execute the
   full clean-environment matrix, including `tdt --version`,
   `tdt config doctor`, package resources, 15-participant registry validation,
   import isolation, and redaction checks.
5. Configure the approved release CI publisher with a least-privilege registry
   principal. This is an operator prerequisite, not credential material stored in
   OpenSpec.
6. Upload the exact qualified provider wheel, download it by immutable coordinate,
   verify its digest, and repeat the matrix from the registry source.
7. Snapshot the participant registry and join its 12 consumers and two
   verification participants to their current governance manifests and owners.
8. Approve a risk-ordered serialized rollout queue and complete each consumer's
   baseline, preflight, candidate install, behavior verification, monitoring,
   reverse rollback rehearsal, and advance decision.
9. Aggregate terminal participant records, verify one common candidate digest,
   and publish the scoped ecosystem rollout report.
10. Continue monitoring through the approved ecosystem window, retain both
    artifact sets, and hand any live-root or source-migration work to its separate
    successor change.
11. Run strict OpenSpec validation and final repository/worktree review before
    archive; keep runtime publication/deployment evidence separate from planning
    artifacts and redact it before linkage.

## Open Questions

1. Which internal Python repository is the approved immutable release target, and
   does it provide server-side digest and overwrite-prevention guarantees?
2. What CI principal is allowed to upload, and what consumer-like principal will
   perform registry-download qualification?
3. Which Python 3.14 OS/architecture lanes are mandatory for the first release,
   based on the current deployment inventory?
4. What external/package contract bundle is authoritative for checkout-free
   installed-wheel tests, and how is its compatibility with the candidate
   version expressed?
5. What risk order, observation duration, representative workload cycle, and
   metric thresholds apply to each of the 12 consumers?
6. Which checks are owned by `ai-review` and `jira-epic-report`, and do either
   have an independently deployable provider-consuming surface?
7. What retention period protects both candidate and pre-change artifacts after
   ecosystem rollout completion?
8. Does release policy require byte-for-byte independent rebuild reproducibility,
   or is normalized wheel equivalence with explicit approval sufficient?
