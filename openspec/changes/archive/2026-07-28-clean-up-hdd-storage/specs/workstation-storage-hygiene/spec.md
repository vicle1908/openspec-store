## ADDED Requirements

### Requirement: Read-only workstation storage audit

The workstation storage-hygiene workflow SHALL provide a read-only audit that
records the macOS Data-volume capacity, available storage, relevant APFS or
Time Machine snapshot state, candidate cleanup categories and sizes, and
active-resource warnings without deleting or modifying data.

#### Scenario: Audit captures a complete baseline

- **WHEN** the operator starts a storage-hygiene run
- **THEN** the audit records a timestamped baseline with filesystem capacity,
  available space, candidate sizes, reclaimable estimates, and relevant active
  processes or containers
- **AND** the audit labels time-specific measurements as estimates rather than
  durable guarantees

#### Scenario: A measurement tool is unavailable

- **WHEN** a candidate cannot be measured because its owning tool is missing,
  unavailable, or returns an error
- **THEN** the audit records that category as unknown with the redacted error
- **AND** the workflow MUST NOT infer that the category is safe or reclaimable

### Requirement: Cleanup candidates have explicit safety classifications

Every cleanup candidate SHALL be classified as read-only evidence,
rebuildable cache, operator-reviewed irreversible data, or protected stateful
data before an action is proposed.

#### Scenario: Rebuildable cache is classified

- **WHEN** the audit identifies Go build cache, npm npx cache, pnpm orphaned
  packages, Docker build cache, or simulator dyld cache
- **THEN** the plan identifies its owning tool, estimated recovery,
  regeneration cost, prerequisites, and supported cleanup command

#### Scenario: Stateful or personal data is classified

- **WHEN** the audit identifies Photos, Downloads projects, source,
  verification evidence, Docker volumes or images, active kind clusters, IDE
  settings, cloud-provider state, Android packages or AVDs, local models, or
  simulator runtimes
- **THEN** the plan marks the item protected until a complete verified-unused
  eligibility record exists
- **AND** it MUST NOT include the item in a bulk cleanup action

### Requirement: Irreversible actions require exact operator confirmation

The workflow MUST require a separate, explicit confirmation for each
irreversible or stateful cleanup category and SHALL allow the operator to
cancel without side effects.

#### Scenario: Trash is reviewed before emptying

- **WHEN** the plan proposes reclaiming space from Trash
- **THEN** the operator is directed to review the Trash contents and measured
  size
- **AND** Trash MUST NOT be emptied until the operator confirms that exact
  action

#### Scenario: Operator declines a cleanup category

- **WHEN** the operator declines or does not confirm a proposed category
- **THEN** the workflow skips it without modifying the category
- **AND** the evidence records a skipped-by-operator outcome

### Requirement: Rebuildable cleanup uses the owning tool

The workflow SHALL use the supported owner command for rebuildable caches and
MUST NOT replace owner commands with broad recursive deletion of system,
developer-tool, Docker, or cloud-provider directories.

#### Scenario: Supported cache cleanup succeeds

- **WHEN** the operator approves a rebuildable cache category and its
  prerequisites are satisfied
- **THEN** the workflow runs only that category's owner command
- **AND** it records the redacted outcome and remeasures Data-volume
  availability before proposing another category

#### Scenario: Cleanup command fails

- **WHEN** an owner command fails or reports partial cleanup
- **THEN** the workflow stops that category, preserves diagnostics, and MUST
  NOT fall back to direct filesystem deletion
- **AND** subsequent categories require a new operator decision

### Requirement: Active and stateful resources are protected

The workflow MUST protect active developer processes and stateful local
resources unless their exact ownership, backup or regeneration path, and
operator authorization are established.

#### Scenario: Docker resources are active

- **WHEN** Docker reports running containers, active kind clusters, attached
  volumes, or images used by active containers
- **THEN** the first-pass cleanup excludes those resources
- **AND** Docker build-cache cleanup remains distinct from image and volume
  pruning

#### Scenario: Xcode or Simulator is active

- **WHEN** Xcode, Simulator, CoreSimulator work, or a simulator device is active
- **THEN** simulator cache cleanup is deferred until the affected processes are
  quiescent
- **AND** simulator runtime deletion remains prohibited without a separate
  exact-runtime confirmation

#### Scenario: Android Studio or an AVD is active

- **WHEN** Android Studio, the Android emulator, or an Android virtual device is
  active
- **THEN** Android SDK, NDK, CMake, system-image, IDE-profile, and AVD
  decommissioning is deferred until the affected processes are quiescent
- **AND** the workflow MUST retain the active package and device identifiers in
  the evidence

### Requirement: Aggressive cleanup is target-driven and allowlist-bounded

The workflow SHALL use 120 GiB available storage as the default aggressive
high-water target for routine capacity cleanup and MUST treat 30 GiB as the
minimum for the repository's canonical local readiness preflight. The workflow
SHALL classify every discovered candidate as retain, archive-then-remove,
remove, or blocked and SHALL permit an approved verified-unused manifest to
continue after the capacity target only for already named items.

#### Scenario: Recommended target is reached

- **WHEN** post-category measurement reports at least 120 GiB available
- **THEN** routine capacity cleanup stops and MUST NOT discover or propose
  additional opportunistic deletion
- **AND** only already named, separately approved verified-unused items remain
  eligible in the current run

#### Scenario: Target remains unmet

- **WHEN** approved first-pass categories complete and less than 120 GiB remains
  available
- **THEN** the workflow presents remaining preclassified manifest categories
  individually in increasing risk order
- **AND** each category requires its own evidence and authorization

#### Scenario: Candidate is absent from retention allowlist

- **WHEN** an exact discovered item is not retained, is inactive, has a proven
  owner-supported removal or recovery path, and has passed its action gate
- **THEN** the workflow SHALL classify it as remove or archive-then-remove
- **AND** the presence of a newer version in the same otherwise-unused
  ecosystem MUST NOT force retention

#### Scenario: Hard minimum remains unmet

- **WHEN** final measurement reports less than 30 GiB available
- **THEN** the workflow marks the workstation ineligible for canonical local
  readiness
- **AND** it MUST NOT claim success or start readiness implicitly

### Requirement: Verified-unused decommissioning is manifest-driven

The workflow MUST create an exact eligibility record before decommissioning an
operator-declared unused item. The record SHALL contain the item path or owner
identifier, measured size, active-use signals, dependency references, owner
tool, backup or regeneration proof, reversibility, proposed action, separate
authorization, and outcome.

#### Scenario: Candidate passes every eligibility gate

- **WHEN** an exact item is inactive, absent from retained dependencies, backed
  up or reproducible, supported by an owner removal path, and separately
  confirmed
- **THEN** the workflow marks only that exact item eligible
- **AND** the eligibility MUST NOT extend to sibling paths, versions, models,
  repositories, volumes, devices, or runtimes

#### Scenario: Eligibility evidence is incomplete

- **WHEN** identity, inactivity, dependency, ownership, recovery, or approval
  evidence is missing or stale
- **THEN** the workflow keeps the item protected
- **AND** it records the unresolved gate without attempting removal

#### Scenario: Capacity target is already reached

- **WHEN** routine cleanup has reached 120 GiB and an exact verified-unused item
  remains approved in the manifest
- **THEN** the workflow SHALL permit decommissioning of that named item
- **AND** it MUST NOT add a new deletion candidate merely because more space
  could be reclaimed

### Requirement: Unused applications, developer packages, and models use owner retirement paths

The workflow SHALL retire unused application bundles, application backups, IDE
profiles, Android packages and AVDs, Ollama models, and editor-owned
indexes/models through exact owner-supported uninstall, remove, reset, or
profile operations whenever such an operation exists.

#### Scenario: Obsolete IDE generation or application backup is eligible

- **WHEN** the current application is identified and tested, required settings
  are exported or migrated, the obsolete generation or backup bundle is
  inactive, and its exact path is confirmed
- **THEN** the workflow SHALL permit retirement of only the confirmed obsolete
  generation or backup
- **AND** the current application, current profile, and independent
  `mcp-router` source repository MUST remain protected

#### Scenario: Android package remains referenced

- **WHEN** a retained Gradle build, version catalog, native build, system image,
  or AVD references an SDK, build-tools, NDK, CMake, source, platform, or
  emulator package
- **THEN** that exact package remains protected
- **AND** age or the presence of a newer installed version MUST NOT make it
  eligible

#### Scenario: Android package or AVD is unused

- **WHEN** an exact Android package or AVD is inactive, absent from retained
  project requirements, reproducible, and separately confirmed
- **THEN** the workflow uses the current Android owner CLI, AVD manager, or IDE
  SDK manager to remove it
- **AND** it MUST NOT delete the Android SDK or AVD directory recursively

#### Scenario: Entire Android ecosystem is unused

- **WHEN** no retained project or workflow requires Android Studio, the Android
  SDK, NDK, CMake, system images, or AVDs and every Android process is stopped
- **THEN** the workflow SHALL permit exact owner-tool removal of every installed
  Android package and AVD followed by application uninstall and exact residual
  profile cleanup
- **AND** it MUST verify the owner inventories are empty before residual
  directories become eligible

#### Scenario: Local model is unused

- **WHEN** the operator confirms an exact Ollama model or application-owned
  model/index is unused and desired sessions, settings, and authentication are
  preserved
- **THEN** the workflow uses the model name or application-supported reset
  scope to retire it
- **AND** it MUST NOT delete a shared blob, global-storage directory, or profile
  solely from its age or size

#### Scenario: Entire local model ecosystem is unused

- **WHEN** every listed Ollama model and the Ollama application are absent from
  the retention allowlist and the service is stopped
- **THEN** the workflow SHALL remove each model by exact name, verify the model
  inventory is empty, and permit the documented macOS application uninstall
- **AND** application files MUST remain protected until model removal outcomes
  are recorded

### Requirement: Project and media retirement requires verified recovery

The workflow MUST prove recoverability for every source repository, project
tree, Photos library, or media collection before local deletion.

#### Scenario: Downloads tree contains nested repositories

- **WHEN** a Downloads project tree contains nested Git repositories
- **THEN** the workflow inventories each nested repository's dirty, ahead,
  detached, upstream, and readability state
- **AND** the containing tree MUST remain protected while any nested repository
  is dirty, ahead, detached, upstream-less without an archive, or unreadable

#### Scenario: Project tree is recoverable

- **WHEN** every nested repository is clean and reproducible from a reachable
  upstream or verified bundle/archive and non-repository files have a verified
  destination
- **THEN** the workflow SHALL permit the exact containing tree to become
  eligible after separate confirmation
- **AND** the evidence retains the recovery method without recording
  credentials or private remote URLs

#### Scenario: Photos or media is recoverable

- **WHEN** the local Photos library or media collection has a complete,
  accessible iCloud or external copy and representative items reopen
  successfully from that destination
- **THEN** the workflow SHALL permit the operator to approve local retirement
  or optimized local storage
- **AND** the workflow MUST preserve the local library when backup completeness
  or reopen verification is uncertain

#### Scenario: No independent archive destination exists

- **WHEN** no suitable external physical volume is mounted and remote or iCloud
  recovery completeness has not been verified
- **THEN** project trees and the Photos library remain blocked
- **AND** an archive stored only on the same Data volume MUST NOT count as
  recovery proof or recovered capacity

### Requirement: Docker and simulator retirement requires exact ownership

The workflow MUST establish exact project, container, image, volume, device,
and runtime ownership before retiring Docker or Apple Simulator state.

#### Scenario: Docker object appears dangling

- **WHEN** Docker reports an image or volume as dangling or reclaimable
- **THEN** the workflow still verifies labels, mounts, owning Compose or kind
  project, backup requirements, and rebuild or pull path
- **AND** dangling status alone MUST NOT authorize deletion

#### Scenario: Aggressive Docker prune set is proven unowned

- **WHEN** all stopped containers, unused images, networks, build cache, and
  unused named or anonymous volumes outside the retention allowlist have exact
  rebuild, pull, or backup proof and no active container references them
- **THEN** the workflow SHALL permit Docker's supported all-unused prune
  operations with their native confirmation prompts
- **AND** it MUST remeasure host-allocated sparse-disk usage without modifying
  `Docker.raw` directly

#### Scenario: Kind cluster is inactive and owned

- **WHEN** an exact kind cluster is inactive, no retained run or evidence
  depends on it, its ownership labels are known, and the operator confirms it
- **THEN** the workflow removes only that named cluster through the owning kind
  lifecycle
- **AND** other running clusters and their attached volumes remain protected

#### Scenario: Simulator runtime is unused

- **WHEN** an exact runtime has no required device or compatibility consumer,
  Xcode and Simulator are quiescent, the runtime can be re-downloaded, and the
  operator confirms its identifier
- **THEN** the workflow uses the simulator owner command to remove that exact
  runtime
- **AND** dyld shared-cache removal remains a separate action and MUST NOT imply
  runtime deletion

#### Scenario: Entire Apple simulator ecosystem is unused

- **WHEN** no retained project or workflow requires Xcode or Apple Simulator
  runtimes and Xcode, Simulator, and CoreSimulator work are quiescent
- **THEN** the workflow SHALL permit removal of all exact downloadable
  simulator runtimes and Xcode
- **AND** it MUST retain the Command Line Tools needed by repository workflows

### Requirement: Cleanup evidence is run-scoped and redacted

Each storage-hygiene run SHALL retain a run-scoped, redacted report containing
the baseline, approved and skipped categories, command outcomes, actual
recovery, final capacity, and unresolved warnings.

#### Scenario: Cleanup run completes

- **WHEN** the operator stops the workflow or the target is reached
- **THEN** the report records before and after measurements plus the outcome of
  every proposed category
- **AND** it excludes file contents, credentials, environment secrets, Docker
  authentication, and cloud tokens

#### Scenario: Cleanup is interrupted

- **WHEN** the workflow is interrupted between categories
- **THEN** the report remains readable and identifies the last completed
  category
- **AND** a retry MUST start with a fresh audit rather than trusting stale
  measurements

### Requirement: Readiness handoff remains a separate verification

The storage-hygiene workflow SHALL hand off to repository preflight only after
recording final capacity and MUST NOT represent disk cleanup as service,
deployment, or cloud readiness.

#### Scenario: Workstation has sufficient headroom

- **WHEN** cleanup completes with at least 120 GiB available
- **THEN** the workflow SHALL permit the operator to run `make preflight`
  followed by the separately authorized canonical local readiness workflow
- **AND** readiness evidence remains separate from cleanup evidence

#### Scenario: Preflight consumes or detects insufficient space

- **WHEN** repository preflight fails its disk requirement after cleanup
- **THEN** the readiness run stops with its own failure evidence
- **AND** the cleanup workflow MUST NOT silently delete additional categories
