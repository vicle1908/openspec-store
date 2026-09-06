## Context

See `proposal.md` for background and motivation.

The source directories in iCloud Drive:
- `/Users/androidteam/Library/Mobile Documents/com~apple~CloudDocs/project/microservices` (89 top-level service modules, Gradle multi-module architecture)
- `/Users/androidteam/Library/Mobile Documents/com~apple~CloudDocs/project/vds` (104 top-level entries, enterprise microservice subprojects)

Together, these trees contain $2,030,747$ inodes. A significant portion are marked `dataless` (`SF_DATALESS`) — observed sampling: ~9% of files in `microservices` and ~35–50% in `vds` source/ignored splits. Hydration is **functional but queue-delayed**, not broken: unified-log evidence (2026-09-06 12:01:35) shows 27 materialization jobs completing at `userRequest` priority in ~78s each, while ~9,171 background eviction jobs (`clean-remote-versions`) churn the same queue; pending fetches observed behind that backlog exceeded 31 minutes. Consequently, opening file contents blocks unpredictably (seconds to hours), APFS directory deletion (`rmdir` / directory unlinking) operates on directory metadata without hydrating child file contents, and all scan/verify steps below are metadata-only.

## Goals / Non-Goals

**Goals:**
- Catalogue and categorize transient/cache directory hierarchies across both iCloud project trees without triggering file body hydration.
- Generate an explicit dry-run manifest detailing target directory paths, category (package cache, build output, compiler cache, conflict duplicate), and item counts.
- Gate all removals behind explicit user approval of exact target paths and commands.
- Execute verified removals to eliminate non-source inodes.
- Measure post-cleanup inode count and verify the metadata-level presence of source code, configuration manifests, lockfiles, and documentation trees (no content reads of dataless files).

**Non-Goals:**
- Does NOT perform any copy, migration, or git cloning to `~/Developer` (deferred per user directive).
- Does NOT delete or alter any source code, project manifests, documentation, or git repositories.
- Does NOT stop or disable `fileproviderd` or `bird`.

## Decisions

### Decision 1: Directory-Root Matching Over Deep File Walks
- **Rationale**: Searching for well-known directory roots (`node_modules`, `.gradle`, `build`, `dist`, `target`, `out`, `__pycache__`, `.pytest_cache`, `.ruff_cache`, `.mypy_cache`) and pruning the walk at those roots avoids reading millions of child inodes individually; matching basenames exactly protects lookalike source directories (`gradle/` wrapper, `buildSrc/`).
- **Alternative considered**: Deep per-file inspection. Rejected: massive I/O overhead and risks hanging on dataless files.
- **Alternative considered**: Gitignore-driven cleanup (`git clean -Xdn`). Rejected: it requires reading `.gitignore` contents, which may themselves be dataless and block on hydration.

### Decision 2: Strict Keep-List Filter
- **Rationale**: Before adding any directory to the removal manifest, test against a strict keep-list:
  - Keep: all files matching code extensions (`.go`, `.py`, `.kt`, `.java`, `.ts`, `.tsx`, `.js`, `.proto`, `.sql`, `.yaml`, `.yml`, `.json`, `.xml`, `.env*`).
  - Keep: all manifest and lockfile names (`package.json`, `build.gradle.kts`, `pom.xml`, `go.mod`, `Dockerfile`, `bun.lock`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `go.sum`, `gradle.lockfile`, `.env`, `.env.*`).
  - Keep: all documentation directories and files (`docs/`, `design-artifacts/`, `Documents/`, `*.md`); keep lookalike source directories by exact-basename matching — `.gradle` (cache) is removed but `gradle/` (wrapper) and `buildSrc/` (build-logic source) are preserved because candidate matching is basename-exact, never prefix-based.
  - Keep: `.git` directories and repository metadata.
- **Alternative considered**: Whitelisting only specific subdirectories. Rejected because enterprise projects have varied subproject structures.

### Decision 3: Value-Blind Manifest and Mandatory Approval Gate
- **Rationale**: Follow system safety rules: never run `rm -rf` without user confirmation of the exact target paths and commands. The dry-run script prints the full list of candidate directories and item counts, pausing for explicit interactive authorization before proceeding.

### Decision 4: Two-Phase Execution
- **Phase A (Audit & Manifest)**: Run a non-destructive inventory script that writes the target list and count to an evidence file.
- **Phase B (Approved Removal & Verification)**: Upon receiving explicit approval for the manifest, delete approved directories and run verification: inode counts plus metadata-only presence checks of key source entrypoints, manifests, lockfiles, and docs — recording dataless files as present-but-content-unverified; content reads only for files already materialized (e.g., `st_blocks > 0` or `SF_DATALESS` unset).

## Risks / Trade-offs

- **Risk**: Collateral deletion of custom code or assets placed inside a build directory.
  - **Mitigation**: Scanner inspects target directories for non-standard file extensions before confirming candidacy; standard source directories (`src/`, `lib/`, `pkg/`) are strictly protected.
- **Risk**: iCloud Drive daemon sync surge while processing deletions.
  - **Mitigation**: Deleting top-level directory roots issues directory-level unlinks rather than individual file deletions, minimizing FileProvider tombstone churn.
- **Risk**: Verification blocking on dataless hydration — content reads of kept files (e.g. `microservices/.env`, ~700 dataless source files in `vds`) hang for the hydration-queue delay above.
  - **Mitigation**: All verification is metadata-only (`lstat`, `readdir`, `st_flags`); dataless files are recorded present-but-content-unverified; materialized-file reads gated on `SF_DATALESS` being unset.
