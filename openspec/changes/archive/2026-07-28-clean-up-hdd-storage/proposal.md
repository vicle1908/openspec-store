## Why

The development Mac is operating with approximately 25 GiB available on its
Data volume, below the 30 GiB preflight required by the repository's canonical
local Compose readiness run. The shortage is currently blocking end-to-end
verification, while disposable caches, retained Trash, obsolete developer
toolchains, local models, application backups, and operator-declared unused
projects and media are competing with active source and evidence.

## What Changes

- Establish a workstation storage-hygiene capability for this repository's
  macOS development workflow.
- Define a measured, staged cleanup procedure with a 120 GiB aggressive
  high-water target and a hard 30 GiB minimum for local readiness preflight.
- Prioritize recoverable data first: reviewed Trash, Go build cache, npm npx
  cache, pnpm orphaned packages, and Docker build cache.
- Add a retention-allowlist-driven verified-unused decommission phase that may
  continue after the 120 GiB capacity target is reached because its purpose is
  to retire explicitly unwanted state, not maximize opportunistic deletion.
- Preauthorize the discovered unused Android, Apple Simulator, local-AI, old
  IDE/profile, application-backup, and obsolete Docker categories for
  eligibility assessment while retaining an exact action gate for each item.
- Inventory and retire confirmed obsolete IDE profiles, unused application
  bundles and backups, Android SDK/NDK/CMake/build-tool packages, Android
  virtual devices, Ollama models, AI editor indexes/models, simulator runtimes,
  Docker images/volumes/clusters, Downloads project trees, and the local Photos
  library through exact owner-supported actions.
- Add explicit confirmation gates and protected-resource rules for personal
  files, Photos, Downloads projects, Docker volumes/images, active kind
  clusters, Google Drive/FileProvider state, IDE settings, and simulator
  runtimes.
- Require nested Git cleanliness, upstream or archive evidence, settings/model
  export where applicable, verified cloud or external backup for personal
  data, and active-process shutdown before an unused item becomes eligible.
- Add before/after measurement and post-cleanup verification requirements so
  disk recovery is evidenced rather than inferred.
- Document exact decommission and recovery paths for simulator caches and
  runtimes, old IDE generations, Android packages and AVDs, local AI models,
  application backups, Docker state, and archived project/media data.
- Keep the procedure operator-controlled and reversible where practical;
  **BREAKING**: emptying Trash or deleting user data remains irreversible after
  the confirmation gate and is never automatic.

## Capabilities

### New Capabilities

- `workstation-storage-hygiene`: Measured, staged, safety-gated HDD cleanup
  and verification for the macOS development workstation.

### Modified Capabilities

- None.

## Impact

- Affects the macOS workstation's local caches, Trash, Docker Desktop storage,
  Android SDK and emulator state, simulator runtimes, IDE generations, local AI
  models/indexes, application backups, and personal-data archival workflow.
- Provides preconditions and evidence for `make preflight` and
  `make local-operational-readiness`; it does not change service APIs,
  production deployment behavior, or application data contracts.
- Requires operator review for destructive steps and coordination with active
  Docker, Xcode/Simulator, IDE, cloud-sync, and repository verification
  processes.
- Requires exact recovery proof for project and media deletion; the current
  discovery found nested dirty or upstream-less repositories and an active
  Android emulator. No external physical storage is currently mounted, so
  project and Photos retirement remains blocked until a verified remote archive
  or suitable external destination exists.
- Adds no runtime dependency and does not alter the nested `mcp-router` Git
  repository.
