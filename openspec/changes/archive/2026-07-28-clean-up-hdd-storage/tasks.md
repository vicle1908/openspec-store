## 1. Audit Contract and Evidence

- [x] 1.1 Re-run the non-mutating workstation inventory, record the current
  Data-volume baseline, installed applications and backups, Android packages
  and AVDs, local models/indexes, nested repositories, Docker objects,
  simulator runtimes, personal-data candidates, and confirm that observed sizes
  remain time-specific estimates.
- [x] 1.2 Define a run-scoped, redacted storage-hygiene report contract under
  `artifacts/workstation-storage-hygiene/<run-id>/` with baseline, candidate,
  eligibility-gate, authorization, action, recovery, warning, and
  final-capacity fields.
- [x] 1.3 Define configurable defaults for the 120 GiB aggressive high-water
  target and the existing 30 GiB readiness minimum without changing deployment
  validation's canonical minimum.
- [x] 1.4 Seed a disposition manifest that classifies every discovered large
  candidate as retain, archive-then-remove, remove, or blocked; retain source,
  current MCP Router, required Docker/Go tools, credentials, and incomplete
  recovery material by default.

## 2. Read-Only Audit Implementation

- [x] 2.1 Add a macOS-focused `scripts/workstation-storage-hygiene.sh` audit
  entry point using `set -euo pipefail`, explicit resolved paths, bounded
  commands, redacted diagnostics, and no mutation.
- [x] 2.2 Implement APFS Data-volume, Time Machine snapshot, Trash, Go, npm,
  pnpm, Docker, Simulator, IDE, Android SDK/AVD, Ollama, AI editor,
  application-backup, cloud-storage, nested Git, personal-data, and relevant
  process measurements with unknown outcomes when an owner tool is unavailable.
- [x] 2.3 Classify every candidate as rebuildable cache,
  operator-reviewed irreversible data, or protected stateful data; keep Docker
  build cache distinct from images and volumes and keep simulator dyld caches
  distinct from runtimes; do not classify age, dangling state, or an
  operator-declared parent directory as sufficient child-item eligibility.
- [x] 2.4 Emit human-readable and machine-readable run-scoped reports without
  file contents, environment secrets, Docker authentication, cloud tokens, or
  unbounded logs.
- [x] 2.5 Add root Makefile help and a canonical
  `workstation-storage-audit` target that invokes the script in read-only mode.

## 3. Safety and Regression Coverage

- [x] 3.1 Add `scripts/tests/workstation-storage-hygiene-test.sh` using
  temporary directories and fake tool outputs; the tests MUST NOT access the
  real Trash, Docker daemon, simulator store, cloud databases, or personal
  files.
- [x] 3.2 Cover successful measurement, missing tools, command failures,
  estimate labeling, redaction, candidate classification, active Docker and
  Simulator warnings, active Android Studio/AVD warnings, nested dirty or
  upstream-less repositories, owner dependency references, the 120 GiB target,
  retention-allowlist dispositions, no-external-volume blockers, and
  run-scoped evidence recovery after interruption.
- [x] 3.3 Add negative tests proving the audit never invokes cleanup commands,
  direct recursive deletion, Docker image or volume pruning, simulator runtime
  deletion, Android package or AVD removal, model removal, application
  uninstall, project/media deletion, or implicit readiness.
- [x] 3.4 Run `bash -n` for the audit and test scripts and run the focused shell
  regression test until both pass.

## 4. Operator Runbook

- [x] 4.1 Add `docs/runbooks/workstation-storage-hygiene.md` documenting the
  audit-first workflow, APFS and Docker estimate caveats, 120 GiB stop target,
  30 GiB hard floor, and before/after evidence.
- [x] 4.2 Document the first-pass order: review and separately approve emptying
  Trash, then use `go clean -cache` and `npm cache npx rm`, remeasuring after
  each category.
- [x] 4.3 Document owner-tool cleanup with individual gates for
  `pnpm store prune`, `docker buildx prune --all --min-free-space 120gb`, and
  `xcrun simctl runtime dyld_shared_cache remove`, including process
  prerequisites and regeneration costs.
- [x] 4.4 Document protected-by-default data and escalation requirements for
  Go module downloads, Docker images and volumes, active kind clusters,
  simulator runtimes, IDE profiles, Android SDK packages and AVDs, Ollama and
  editor models/indexes, application backups, Google Drive/FileProvider state,
  Photos, nested Downloads repositories, source, and retained verification
  evidence.
- [x] 4.5 Document cancellation, partial-failure handling, cache rehydration,
  stateful backup expectations, repository rollback, and the rule that cleanup
  evidence never establishes service or cloud readiness.
- [x] 4.6 Document the verified-unused decommission manifest, per-item
  eligibility fields, owner-tool removal paths, recovery tests, and the rule
  that approved manifest items may continue after routine cleanup reaches
  120 GiB.
- [x] 4.7 Document the whole-ecosystem retirement paths for Android, Ollama,
  JetBrains/other unused editors, Apple simulator/Xcode, Docker, and the four
  MCP Router backups, including exact preview, shutdown, removal, verification,
  and rollback commands.

## 5. Approved Workstation Cleanup

- [x] 5.1 Run the audit immediately before cleanup, inspect active processes
  and resources, and present the exact first-pass candidates and report to the
  operator.
- [x] 5.2 Obtain explicit operator confirmation after Finder review before
  emptying Trash; record approved, declined, or skipped-by-operator without
  automating the irreversible action.
- [x] 5.3 Run each approved rebuildable first-pass cache command separately,
  record its redacted result, and remeasure Data-volume availability before the
  next proposal.
- [x] 5.4 Stop routine capacity cleanup as soon as at least 120 GiB is
  available; if the target remains unmet, present remaining preclassified
  manifest categories one at a time in increasing risk order and require their
  exact action gates.
- [x] 5.5 Finalize the run report with actual recovered space, final capacity,
  skipped categories, failures, and remaining warnings; begin any retry with a
  fresh audit.

## 6. Verified-Unused Decommissioning

- [x] 6.1 Build a fresh per-item decommission manifest with exact path or
  owner identifier, measured size, active-use signals, dependency references,
  backup or regeneration proof, reversibility, proposed owner action, and
  separate authorization; keep every incomplete item protected.
- [x] 6.2 Inventory installed application versions, profiles, settings-sync or
  export state, and backup bundles; test the retained current application before
  retiring each confirmed obsolete IDE generation, unused application, or
  backup, including the four observed MCP Router application backups without
  touching the current app or nested source repository.
- [x] 6.3 Inventory retained Android project pins for SDK platforms,
  build-tools, NDK, CMake, sources, system images, and AVD requirements; resolve
  missing or conflicting requirements before approving an installed package.
- [x] 6.4 Stop Android Studio and the active `Pixel9_3` emulator, then use the
  IDE SDK Manager or exact `sdkmanager --uninstall` package identifiers and
  `avdmanager delete avd -n Pixel9_3` to retire all unretained packages and the
  AVD; verify owner inventories are empty before uninstalling Android Studio
  and cleaning exact residual profiles.
- [x] 6.5 Inventory Ollama models and Kiro, Cursor, Zed, Chrome, and other
  application-owned model/index state; preserve desired sessions, settings, and
  authentication before using `ollama rm` for every unretained model and
  supported reset/uninstall scopes for unused applications; verify model and
  application inventories after each retirement.
- [ ] 6.6 Recursively audit all 38 currently observed nested repositories under
  the large Downloads trees, resolve the 11 dirty repositories and recovery for
  the 5 without upstreams, and verify archives/remotes plus non-repository
  files before separately approving a containing tree.
  Blocked at handoff: no external physical volume is mounted, and the dirty or
  upstream-less repositories have no tested off-volume recovery. Their
  containing trees remain protected.
- [x] 6.7 Verify the complete Photos/media destination through accessible
  iCloud or external storage and representative reopen checks before approving
  optimized local storage or retirement of the local Photos library; record the
  current no-external-volume condition as blocked rather than creating an
  archive on the same Data volume.
- [x] 6.8 Inventory Docker labels, Compose/kind ownership, mounts, volumes,
  image rebuild/pull paths, and retained evidence; retire exact confirmed
  unused clusters and containers, run `docker system prune -a` and
  `docker volume prune --all` only after the entire prune set is proven
  unowned, invoke Docker-supported sparse-disk reclamation, and never
  manipulate `Docker.raw` directly.
- [x] 6.9 Close Xcode and Simulator, inventory device and compatibility
  consumers, retire dyld shared caches separately, use
  `xcrun simctl runtime delete <identifier>` for every unretained runtime, and
  uninstall Xcode only when no retained Apple-platform workflow exists while
  preserving repository-required Command Line Tools.
- [x] 6.10 Remeasure after every decommission action and record eligible,
  removed, failed, deferred, and protected outcomes; do not discover new
  opportunistic candidates after routine cleanup has reached 120 GiB.

## 7. Verification and Handoff

- [x] 7.1 Run the canonical `workstation-storage-audit` Make target twice and
  verify that auditing is repeatable, non-mutating, redacted, and run-scoped.
- [ ] 7.2 Run `make validate-documentation` and any focused repository checks
  affected by the Makefile and script changes.
  Blocked at handoff: focused shell tests pass, but Google Drive leaves
  `artifacts/deployment-validation/20260727T-health-compose-current-r2/manifest.json`
  dataless and indefinitely `isDownloading=1`; bounded validator attempts were
  terminated without a validation result.
- [x] 7.3 Run `graphify update .` after source changes; verify the supported
  script, tests, runbook, and OpenSpec paths are indexed, and record Graphify
  0.9.26's explicit extensionless-`Makefile` detection limitation while
  verifying that target directly.
- [x] 7.4 Run `openspec validate --strict --all` and resolve all focused
  `clean-up-hdd-storage` validation failures without masking unrelated
  baseline failures.
- [x] 7.5 Run `make preflight` only after final capacity is recorded; retain
  its separate result and do not start `make local-operational-readiness`
  implicitly.
- [ ] 7.6 If separately authorized, run the canonical local readiness workflow
  using its exact run/project evidence contract and keep readiness evidence
  separate from storage-hygiene evidence.
  Not authorized at handoff; local operational readiness was not started.
