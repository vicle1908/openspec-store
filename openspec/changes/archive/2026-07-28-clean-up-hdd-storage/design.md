## Context

The repository's canonical local Compose readiness workflow requires at least
30 GiB of workspace disk before it starts. The current macOS Data volume has
approximately 25 GiB available, so the readiness workflow is blocked before it
can produce canonical evidence.

The discovery snapshot identified enough recoverable storage to restore a
healthy operating margin without touching source, personal projects, Photos, or
stateful Docker volumes. The largest first-pass candidates are reviewed Trash
(about 21.7 GiB), the Go build cache (about 7.5 GiB), the npm npx cache (about
4.3 GiB), and unused Docker build cache (about 2.4 GB). These values are
time-specific observations, not durable thresholds.

Further discovery identified additional high-yield candidates: about 24.1 GiB
of Android SDK data, including six NDK generations; a 12.2 GiB Android virtual
device; 11.2 GiB of Ollama data; 24.8 GiB of old IntelliJ and Android Studio
profiles; 8.9 GiB of Downloads project trees; 13.8 GiB of Photos data; 6.7 GiB
of Kiro index/state; 1.36 GiB of MCP Router application backups; three iOS
simulator runtimes totaling about 23 GB; and Docker-reported unused state.
These observations overlap in places and remain estimates.

The fresh apply-time discovery found safety conflicts: Android Studio and its
only AVD were active, 11 of 38 nested repositories under the large Downloads
trees had tracked working-tree changes, 5 lacked an upstream, and the two
smaller top-level repositories were among the dirty set. No external physical
storage volume was mounted. These findings require a per-item decommission
manifest and prevent project or Photos deletion until recovery material is
stored somewhere other than the Data volume and successfully reopened.

The completed capacity phase raised measured Data-volume availability from
about 28.2 GiB to 155.7 GiB. Owner commands removed Ollama models, the Go build
cache, pnpm orphans, Docker build cache, Simulator dyld caches, the unused
Android AVD, and unretained Android SDK packages. Finder then emptied the
operator-reviewed Trash after staging obsolete Android Studio and IntelliJ
profiles, four MCP Router application backups, Ollama, Kiro, Cursor, and Zed
application/state paths. The Trash count was verified zero at action
completion. npm's active `_npx` cache, retained project trees, Photos, active
or unproven Docker state, simulator runtimes, Xcode, current IDE profiles, and
Chrome profile-owned model state remain deferred or protected by their live
gates.

Finder verified a zero-item Trash immediately after the reviewed operation.
During final Google Drive/FileProvider verification, four `zustand` package
fragments reappeared in Trash. They were not deleted under the completed action;
the final live snapshot records them as new protected drift while capacity
remains above the 120 GiB target.

This change is workstation-operational rather than service-architectural. Its
stakeholders are the workstation operator and contributors running repository
verification. It must preserve the uncommitted outer repository, the
independent dirty `mcp-router` repository, active local clusters, retained
verification evidence, credentials, cloud-sync state, and user data.

## Goals / Non-Goals

**Goals:**

- Restore at least 120 GiB of available Data-volume storage as the default
  aggressive high-water target, while enforcing the repository's 30 GiB
  readiness minimum.
- Provide a repeatable, read-only audit that records current capacity,
  candidate sizes, active-resource warnings, and a staged cleanup plan.
- Perform cleanup one category at a time through the owning tool or application
  and verify actual recovery after each category.
- Use a retention allowlist so whole operator-declared unused ecosystems are
  retired instead of preserving arbitrary old versions by default.
- Decommission items the operator has declared unused even after the capacity
  target is reached, but only after exact identity, inactivity, dependency,
  backup, and recovery checks pass.
- Require explicit operator confirmation before any irreversible action.
- Retain machine-readable and human-readable before/after evidence for the
  cleanup and subsequent readiness handoff.

**Non-Goals:**

- Delete personal files, source repositories, Photos, Downloads projects, IDE
  settings, Docker volumes, cloud-provider databases, SDK packages, virtual
  devices, models, or simulator runtimes without exact per-item eligibility
  evidence and confirmation.
- Alter service APIs, production manifests, container image pins, Go module
  dependencies, or cloud deployment behavior.
- Treat the 120 GiB target as production capacity planning or claim deployment
  readiness from workstation cleanup.
- Clean or modify the nested `mcp-router` Git repository.

## Decisions

### 1. Audit is read-only and precedes every cleanup run

A repository-owned audit command will collect the APFS Data-volume baseline,
candidate sizes, Docker reclaimability, active containers and kind clusters,
simulator runtimes, Time Machine snapshot state, and relevant running
applications. It will not traverse file contents or print secrets.

The audit will emit a run-scoped report under
`artifacts/workstation-storage-hygiene/<run-id>/`. Reports will distinguish
measured physical usage from tool-reported reclaimable estimates because APFS
purgeable space and Docker sparse-disk allocation are not strictly additive.

**Alternative considered:** rely on the macOS Storage UI alone. It remains a
useful operator view, but it does not expose the repository-specific readiness
floor, Docker ownership, or repeatable evidence needed for this workflow.

### 2. Aggressive cleanup is retention-allowlist-driven

The default sequence is:

1. Freeze a minimal retention allowlist for active source, required tools,
   credentials/settings, and recovery evidence.
2. Operator review and explicit approval to empty Trash.
3. Rebuildable Go build and npm npx caches.
4. Pnpm orphan cleanup and aggressive Docker build-cache cleanup.
5. Simulator dyld shared caches after Xcode and Simulator are closed.
6. A verified-unused decommission manifest covering every confirmed unwanted
   application, backup, toolchain, model, project/media tree, Docker object,
   AVD, or simulator runtime.

The routine capacity-recovery phase will remeasure free space after every
category and stop when at least 120 GiB is available. The verified-unused phase
may continue after that point only for items already named in the decommission
manifest and separately approved. The current operator direction preauthorizes
eligibility assessment of the discovered large unused categories, but does not
waive exact identity, quiescence, recovery, or action-preview gates.

The default retention allowlist keeps the outer repository, the independent
`mcp-router` source repository, the currently installed and verified MCP Router
application, Docker Desktop and the minimum images required to rebuild this
repository, Go/Homebrew and required command-line tools, credentials and
settings selected by the operator, cleanup evidence, and any data whose
recovery proof is incomplete. Everything else must be explicitly classified as
retain, archive-then-remove, remove, or blocked.

The initial disposition is decision-complete:

| Disposition | Discovered items |
|---|---|
| Retain | Outer repository, nested `mcp-router` source, current verified MCP Router app, Docker Desktop, minimum repository images, Go/Homebrew, Apple Command Line Tools, selected credentials/settings, and run evidence |
| Remove after exact preview | Reviewed Trash; Go build, npm npx, pnpm orphan, Docker build, and simulator dyld caches; four MCP Router app backups; all unused IntelliJ/Android Studio generations and profiles; the full Android SDK/AVD/Studio ecosystem; every Ollama model and Ollama itself; unused Kiro, Cursor, and Zed app-owned state; all unneeded simulator runtimes and Xcode; the two observed readiness kind clusters and other Docker objects after ownership proof |
| Archive then remove | The `ghtk` and `ghtk-ios` Downloads trees, smaller dirty Downloads repositories, and the Photos library |
| Blocked | Any dirty or upstream-less repository without a tested off-volume archive, Photos without verified iCloud/external recovery, active or referenced Docker state, Google Drive/FileProvider databases, macOS-managed `/private/var/folders`, and any item with stale or incomplete eligibility evidence |

The remove disposition records the operator's current confirmation of intent.
Execution still prints exact identifiers, commands, predicted recovery, and
irreversibility immediately before each action and stops if the live inventory
no longer matches this plan.

**Alternative considered:** retain one latest version of every ecosystem. This
was rejected because the operator reports these larger ecosystems are unused;
keeping a latest Android SDK, AVD, model, IDE generation, or simulator runtime
would defeat the cleanup without protecting an actual dependency.

### 3. Owning tools perform cache removal

The runbook will use supported commands such as `go clean -cache`,
`npm cache npx rm`, `pnpm store prune`, `docker buildx prune --all
--min-free-space 120gb`, and `xcrun simctl runtime dyld_shared_cache remove`.
It will not use broad recursive deletion for system, tool, Docker, or
cloud-provider directories.

Go module downloads remain protected by default because rebuilding the
repository needs them. Docker image and volume pruning remain separate from
build-cache pruning. Simulator runtime deletion remains separate from dyld
cache removal.

**Alternative considered:** delete cache directories directly. This was
rejected because owner tools understand permissions, indexes, sparse storage,
and safe regeneration better than a generic filesystem deletion.

### 4. Destructive and stateful candidates require named confirmation

The workflow will present the exact category, measured size, owner, expected
recovery, regeneration cost, and rollback before requesting confirmation.
Emptying Trash is a dedicated irreversible gate. Personal files and stateful
resources are never included in a bulk "yes."

Docker volumes, running containers, active kind clusters, retained evidence,
IDE global storage, Google Drive/FileProvider databases, Photos, Downloads
projects, and simulator runtimes are protected until ownership and replacement
or backup are proven.

**Alternative considered:** classify every unused-looking object as
disposable. This was rejected because absence of a current Kubernetes context,
an exited container, or an old modification date does not prove data is
unowned.

### 5. Verified-unused retirement is manifest-driven

Each candidate will have one manifest record containing its exact path or owner
identifier, measured physical size, owner tool, last-use signals, active
processes, dependency references, backup or regeneration proof, proposed
command, reversibility, approval, and outcome. A category-level approval cannot
authorize every item in the category.

Eligibility rules vary by owner:

- **Applications and IDE profiles:** verify the installed current version,
  preserve or export settings that remain needed, close the application, and
  name each obsolete bundle or profile generation. Application backups,
  including the four observed MCP Router backups, remain distinct from the
  currently installed application. JetBrains standalone removal may include
  the exact versioned Application Support and Caches directories documented by
  JetBrains after the corresponding application instance is removed.
- **Android tooling:** scan retained Android projects for SDK, build-tools, NDK,
  CMake, system-image, and emulator requirements; stop Android Studio and the
  active emulator; delete `Pixel9_3` with Device Manager or `avdmanager delete
  avd -n Pixel9_3`; uninstall exact SDK packages with SDK Manager or
  `sdkmanager --uninstall`; and remove the Android Studio application and exact
  residual profiles only after the installed package list is empty and no
  retained Android project exists.
- **Local AI state:** enumerate exact Ollama models and editor-owned
  indexes/models. Remove all confirmed Ollama models by exact model name with
  `ollama rm`, verify the list is empty, then use Ollama's documented macOS
  uninstall paths if the application is also unused. Remove editor state
  through an application-supported reset, uninstall, or exact profile
  operation that preserves selected authentication and desired history.
- **Project trees:** recursively inventory nested repositories rather than
  checking only the top-level Downloads directory. Every repository must be
  clean and reproducible from a reachable upstream or a verified bundle/archive.
  Dirty, ahead, detached, upstream-less, or unreadable repositories remain
  protected until recovery material is created and tested.
- **Photos and media:** require a verified iCloud or external-library copy and
  a reopen/sample check before local originals or the local library are
  removed. Apple requires an external Photos-library destination to be APFS or
  Mac OS Extended (Journaled), not the Time Machine destination, a flash card,
  or a network/cloud filesystem. With no external physical volume mounted,
  this category is currently blocked unless iCloud completeness and optimized
  storage are verified.
- **Docker:** identify current labels, owning Compose/kind projects, mounts,
  named volumes, image rebuild/pull paths, and retained evidence. Remove exact
  unused resources first. When no protected unused volume remains, the
  aggressive terminal action may use `docker system prune -a` followed by
  `docker volume prune --all`; then use Docker-supported sparse-disk
  reclamation. Never manipulate or move `Docker.raw` directly in Finder.
- **Apple simulators:** close Xcode/Simulator, inventory devices and runtime
  consumers, remove dyld caches separately, and use exact runtime identifiers
  for `xcrun simctl runtime delete`. If no retained Apple-platform work exists,
  remove all downloadable simulator runtimes and the Xcode application while
  preserving Command Line Tools required by the Go repository.

**Alternative considered:** encode a static deletion list from the discovery
snapshot. This was rejected because active state, nested Git work, SDK
requirements, and cloud backups can change between proposal and execution.

### 6. Cleanup and readiness evidence remain separate

The cleanup report proves only the disk baseline, authorized actions, command
outcomes, and final capacity. Repository readiness remains a separate workflow.
Once cleanup leaves at least 120 GiB available, the operator may run
`make preflight` and then the canonical readiness commands. Falling below the
30 GiB hard minimum must block readiness rather than trigger more deletion
implicitly.

### 7. The implementation has no new external dependency

The audit and runbook will use macOS and already-installed project tooling.
There is no daemon, scheduled deletion, elevated background service, or new
package version pin. Any future automation cadence requires a separate reviewed
change.

### 8. Owner paths are grounded in current official documentation

Research refreshed on 2026-07-28 established the supported execution paths:

- Android documents exact package removal with
  [`sdkmanager --uninstall`](https://developer.android.com/tools/sdkmanager)
  and AVD removal through
  [Device Manager](https://developer.android.com/studio/run/managing-avds);
  the locally installed `avdmanager` also exposes `delete avd -n <name>`.
- Apple documents removing unused runtimes in
  [Xcode Components](https://developer.apple.com/documentation/Xcode/downloading-and-installing-additional-xcode-components);
  the installed `simctl` exposes exact runtime deletion and separate dyld-cache
  removal.
- Docker documents
  [`docker system prune -a`](https://docs.docker.com/reference/cli/docker/system/prune/),
  [`docker volume prune --all`](https://docs.docker.com/reference/cli/docker/volume/prune/),
  and host-space reclamation without directly moving
  [`Docker.raw`](https://docs.docker.com/desktop/troubleshoot-and-support/faqs/macfaqs/).
- Ollama documents both model storage and the complete
  [macOS uninstall path](https://docs.ollama.com/macos), while the installed CLI
  exposes `ollama rm MODEL...`.
- JetBrains documents application removal plus exact versioned
  [macOS support and cache paths](https://www.jetbrains.com/help/idea/uninstall.html).
- Apple documents the required filesystem and reopen procedure for
  [moving a Photos library](https://support.apple.com/108345).

Apply-time graph verification also established that Graphify 0.9.26 indexes
the shell implementation, tests, runbook, and OpenSpec Markdown paths but
intentionally treats an extensionless `Makefile` as unclassifiable. The
Makefile target is therefore verified through direct source inspection and
focused execution rather than represented as a Graphify source node.

## Risks / Trade-offs

- **[Risk]** APFS or Docker reports less recovered storage than estimated. →
  **Mitigation:** remeasure after every category and treat estimates as
  advisory.
- **[Risk]** Cache cleanup slows the next Go, npm, pnpm, Docker, or Simulator
  operation. → **Mitigation:** retain dependency/module caches by default and
  retain only the minimum caches named by the allowlist.
- **[Risk]** Emptying Trash removes something the operator intended to restore.
  → **Mitigation:** require Finder review and a dedicated confirmation; never
  empty Trash automatically.
- **[Risk]** Active verification or IDE work races with cache cleanup. →
  **Mitigation:** detect relevant processes and refuse the affected category
  until they are stopped or explicitly excluded.
- **[Risk]** Docker image or volume cleanup removes needed local state. →
  **Mitigation:** exclude images and volumes from the first pass and require
  ownership, backup, and exact-target confirmation for later cleanup.
- **[Risk]** Old Android packages are still required by a retained project. →
  **Mitigation:** scan retained Gradle/version-catalog pins and remove only
  exact packages absent from the dependency inventory.
- **[Risk]** Downloads appears disposable while nested repositories contain
  local work. → **Mitigation:** require recursive Git inventory, verified
  upstream reachability or an archive, and zero unresolved dirty repositories
  before deleting a containing tree.
- **[Risk]** A model/index directory includes desired sessions,
  authentication, or tool configuration. → **Mitigation:** prefer owner-tool
  model removal or documented reset scopes and preserve desired history before
  profile removal.
- **[Risk]** A cloud or external media backup is incomplete. → **Mitigation:**
  require the destination to be accessible and sample-reopen verified before
  local deletion.
- **[Risk]** A cleanup report exposes sensitive paths or credentials. →
  **Mitigation:** record category-level paths and redacted command outcomes
  only; never capture file contents, environment secrets, Docker auth, or cloud
  tokens.

## Migration Plan

1. Add the read-only audit command, Make target, and operator runbook.
2. Add focused tests using temporary directories and fake tool outputs; tests
   must not operate on the real Trash, Docker daemon, simulator store, or user
   data.
3. Run the audit against the workstation and review the generated plan.
4. Execute only the approved first-pass categories, remeasuring after each.
5. Stop routine capacity cleanup at 120 GiB.
6. Build the verified-unused manifest from a fresh inventory; resolve active
   processes, dirty or upstream-less repositories, retained project
   dependencies, and backup gaps before approval.
7. Decommission each eligible unused item with its owner tool, remeasure after
   every action, and leave every failed or uncertain item protected.
8. Run `make preflight`; run canonical local readiness only when its resource
   contract passes.
9. Roll back repository changes by removing the audit/runbook integration.
   Rebuildable caches recover through normal tool use. Stateful or user data is
   removed only after separately verified recovery material and explicit
   approval.

## Open Questions

- Whether the read-only audit should later be scheduled remains deferred; this
  change permits operator-invoked runs only.
- Exact identifiers and paths remain apply-time measurements, but disposition
  is no longer open-ended: discovered unused Android tooling/AVD, Ollama
  models, old IDE generations/profiles, application backups, unused simulator
  runtimes, and unowned Docker state default to remove; project trees and
  Photos default to archive-then-remove; protected source, the current MCP
  Router application, required Docker/Go tooling, credentials, and incomplete
  recovery material default to retain or blocked.
