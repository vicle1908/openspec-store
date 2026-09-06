## Purpose
Defines safety policies, classification rules, approval gates, and verification criteria for purging transient build, package cache, and sync conflict artifacts from iCloud Drive project folders while guaranteeing zero loss of source and documentation files.

## ADDED Requirements

### Requirement: Transient Artifact Classification and Detection
The cleanup tooling SHALL classify and locate transient build outputs, package manager caches, temporary test/compiler artifacts, and sync conflict copies across `com~apple~CloudDocs/project/microservices` and `com~apple~CloudDocs/project/vds`.

#### Scenario: Detection of transient build and dependency directories
- **WHEN** the cleanup scanner inspects project directories
- **THEN** it identifies transient directory roots by exact-basename match — `node_modules`, `.gradle`, `build`, `dist`, `target`, `out`, `__pycache__`, `.pytest_cache`, `.ruff_cache`, `.mypy_cache`, `.hypothesis` — and transient file patterns — `.DS_Store`, `.coverage`, `*.tmp`, `*.log` (suffix-matched), `*.corrupted.*` (mid-name marker) — as eligible targets for removal, with the same candidate set used across proposal, tasks, and scanner.

#### Scenario: Detection of iCloud sync conflict copies
- **WHEN** the cleanup scanner encounters duplicate paths matching `*.corrupted.*` or similar conflict naming created during iCloud synchronization
- **THEN** it flags them for removal subject to pathname-based verification that canonical counterparts (same parent directory and stem with the conflict marker stripped) exist; content comparison MUST NOT be performed because reading dataless files can block on FileProvider hydration.

#### Scenario: Preservation of lookalike source directories
- **WHEN** a directory shares only a name prefix or suffix with a removal target (for example `buildSrc` beside `build`, or the `gradle/` wrapper beside a `.gradle` cache)
- **THEN** it is preserved, because a removal candidate MUST match the removal-target name exactly on its basename.

### Requirement: Strict Source and Documentation Preservation
The cleanup process SHALL strictly preserve all source code files, project manifests, configuration definitions, documentation, and repository tracking structures.

#### Scenario: Preservation of source and configuration files
- **WHEN** files with code extensions (`.go`, `.py`, `.kt`, `.java`, `.ts`, `.tsx`, `.js`, `.proto`, `.sql`) or configuration/manifest and lockfile names (`package.json`, `build.gradle.kts`, `pom.xml`, `go.mod`, `Dockerfile`, `.gitignore`, `compose.yml`, `.env`, `.env.*`, `bun.lock`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `go.sum`, `gradle.lockfile`) are scanned
- **THEN** the cleanup process excludes them from deletion candidates regardless of directory location.

#### Scenario: Preservation of documentation and design assets
- **WHEN** documentation files (`*.md`, `*.rst`, `*.adoc`, `*.pdf`) or documentation directories (`docs/`, `design-artifacts/`, `Documents/`) are encountered
- **THEN** they are preserved intact and excluded from removal.

### Requirement: Dry-Run Manifest and Approval Gate
Prior to executing any destructive mutation or directory deletion, the cleanup process SHALL generate an exact manifest of targeted paths with item counts and SHALL require explicit approval.

#### Scenario: Unapproved deletion attempt fails closed
- **WHEN** a removal command is invoked without prior manifest generation and explicit confirmation
- **THEN** the system refuses to delete any file and halts with an authorization requirement.

#### Scenario: Approved deletion execution
- **WHEN** target paths are verified and explicit confirmation is provided
- **THEN** removals execute only against the explicitly approved paths using absolute paths.

### Requirement: Post-Cleanup Verification and Inode Reduction
Following approved removals, the cleanup process SHALL verify that target inode counts have decreased substantially and verify the metadata-level presence of remaining source and documentation trees without reading file contents of dataless files.

#### Scenario: Verification of source preservation and inode reduction
- **WHEN** post-cleanup verification runs
- **THEN** it measures the new inode count, proves significant reduction, and verifies that key source entrypoints, build manifests, lockfiles, and documentation paths are present via filesystem metadata only (`lstat`/directory entries), recording dataless files as present-but-content-unverified; content reads SHALL be limited to files already materialized.
