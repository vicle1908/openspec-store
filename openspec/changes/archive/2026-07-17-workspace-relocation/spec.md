# Workspace Relocation - Specification

**Change ID:** workspace-relocation
**Status:** Ready
**Version:** 0.2.0
**Date:** 2026-05-23
**Modifies:** `specs/uv-runtime-management/spec.md`

---

## Overview

This change defines a complete migration out of legacy cloud workspace. After cutover, all active development happens under `$HOME/Developer/tdt/`. Source code, workspace metadata, docs, OpenSpec artifacts, skills, configs, and utility scripts are versioned in Git. legacy cloud workspace is not a supported development path, synchronization channel, rollback path, or bootstrap dependency.

When archived, this change replaces the legacy cloud-primary and hybrid assumptions in `specs/uv-runtime-management/spec.md` with the canonical non-legacy cloud workspace model.

---

## ADDED Requirement: Canonical workspace location

The TDT workspace SHALL live at `$HOME/Developer/tdt/` on every developer machine. The workspace root is a container, not a Git repository and not a uv workspace. Every source project and the workspace metadata project SHALL be its own Git repository under that root.

### Scenario: Developer machine layout

- **WHEN** inspecting a developer machine after cutover
- **THEN** `$HOME/Developer/tdt/` SHALL exist as a real local APFS directory
- **AND** it SHALL contain source repositories such as `tdt-core/`, `webhook-receiver/`, `poems-mobile3-ios/`, and `poems-mobile3-android/`, each with its own `.git/`
- **AND** it SHALL contain `tdt-meta/`, a Git repository for workspace knowledge, agent config, OpenSpec, shared docs, shared scripts, and root workspace guidance
- **AND** compatibility paths at the workspace root (`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `docs`, `openspec`, `.agents`, `config`, `skills`, `openapi`, `examples`, `tools`, `.github`, `.vscode`, `.gitignore`, `.graphifyignore`) SHALL be symlinks into `tdt-meta/`
- **AND** the legacy path `/Users/lekhanhvinh/Developer/tdt/` SHALL NOT be used for active development.

### Scenario: Path safety

- **WHEN** verifying the workspace path
- **THEN** the path SHALL NOT contain spaces or non-ASCII characters
- **AND** the path SHALL be no longer than 64 characters before the per-repo segment
- **AND** tooling SHALL use `$HOME/Developer/tdt` or an explicit `TDT_WORKSPACE_ROOT` override instead of hard-coding the legacy legacy cloud path.

### Scenario: Platform tooling integration

- **WHEN** opening a repo from `$HOME/Developer/tdt/`
- **THEN** Xcode SHALL open `.xcworkspace` files and show clean Source Control state after the first refresh
- **AND** Android Studio SHALL Gradle-sync after path-bound IDE caches are regenerated
- **AND** Docker Desktop SHALL bind-mount paths under `$HOME/Developer/tdt/` without extra File Sharing configuration because the path is under `/Users`
- **AND** launchd-managed development commands SHALL not depend on File Provider paths.

### Scenario: launchd-managed services source from the new location

- **WHEN** `webhook-receiver/scripts/deploy.sh` runs without `WEBHOOK_RECEIVER_SOURCE`
- **THEN** its default source path SHALL be `$HOME/Developer/tdt/webhook-receiver`
- **AND** the deployed runtime location SHALL remain `$HOME/.tdt-webhook-receiver/`
- **AND** deploy verification SHALL fail if the source path resolves under legacy cloud workspace.

---

## ADDED Requirement: Git-backed workspace metadata

The shared workspace knowledge base SHALL be moved from legacy cloud workspace into a Git repository named `tdt-meta` hosted on `git.ecomedic.vn/tdt/tdt-meta`.

### Scenario: Metadata repository contents

- **WHEN** `tdt-meta` is inspected
- **THEN** it SHALL contain all cross-repo workspace assets: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `README.md`, `INDEX.md`, `docs/`, `openspec/`, `.agents/`, `config/`, `skills/`, `openapi/`, `examples/`, `tools/`, `.github/`, `.vscode/`, `.env.example`, `.gitignore`, and `.graphifyignore`
- **AND** it SHALL NOT contain secrets, virtual environments, GitNexus databases, Graphify output, worktrees, IDE runtime state, generated caches, or binary build artifacts.

### Scenario: Metadata symlink compatibility

- **WHEN** an agent or script reads `$HOME/Developer/tdt/AGENTS.md` or `$HOME/Developer/tdt/openspec`
- **THEN** the read SHALL resolve through a symlink to `$HOME/Developer/tdt/tdt-meta/AGENTS.md` or `$HOME/Developer/tdt/tdt-meta/openspec`
- **AND** writes through those symlinks SHALL modify the Git-tracked files in `tdt-meta/`
- **AND** metadata changes SHALL propagate only through `git commit`, `git push`, `git fetch`, and `git pull`.

### Scenario: No legacy cloud metadata dependency

- **WHEN** the machine is signed out of legacy cloud workspace or legacy cloud workspace is unavailable
- **THEN** the workspace SHALL remain usable for development, documentation reads, OpenSpec work, skills lookup, and script execution
- **AND** no supported workflow SHALL require `$HOME/Library/legacy-workspace/legacy-cloud-workspace/tdt-knowledge/`.

---

## MODIFIED Requirement: Development venvs outside legacy cloud workspace

Development virtual environments SHALL live outside legacy cloud workspace. The canonical layout keeps source outside legacy cloud and still permits relocated venvs for consistency across repos.

### Scenario: Workspace lives at the canonical location

- **WHEN** a Python repository is under `$HOME/Developer/tdt/`
- **THEN** `UV_PROJECT_ENVIRONMENT` SHALL resolve to a unique per-repo path, preferably `$HOME/.tdt/venvs/<repo-name>`
- **AND** `PYTHONPYCACHEPREFIX` SHALL resolve to `$HOME/.tdt/pycache/<repo-name>` unless a repo explicitly opts into local source-tree bytecode
- **AND** `<repo>/.venv` MAY be a symlink to the relocated venv for IDE/tool discovery
- **AND** no two repos SHALL share the same absolute `UV_PROJECT_ENVIRONMENT` path.

### Scenario: Workspace accidentally lives under legacy cloud

- **WHEN** `uv sync`, `uv run`, tests, deploy, or migration validation runs from a path under `legacy workspace` or `legacy-cloud-workspace`
- **THEN** the command SHALL fail fast or warn as a policy violation unless it is the one-time migration script reading the legacy source
- **AND** agents SHALL not continue feature development from that path.

### Scenario: Cross-repo path-dependency installs

- **WHEN** repo A declares a path dependency on repo B
- **THEN** `uv sync` in repo A SHALL install B into A's unique relocated venv
- **AND** `_editable_impl_<pkg>.pth` files SHALL contain exactly one path per line
- **AND** the paths SHALL reference `$HOME/Developer/tdt/...`, not legacy cloud workspace.

---

## ADDED Requirement: Complete migration script idempotence

A migration script SHALL exist at `tdt-meta/tools/migrate-out-of-legacy cloud.sh` and be exposed as `$HOME/Developer/tdt/tools/migrate-out-of-legacy cloud.sh`. It SHALL perform a complete cutover from legacy cloud workspace to Git-backed local development.

### Scenario: First-time migration

- **WHEN** the migration script runs on a machine where source still exists in legacy cloud
- **THEN** it SHALL preflight-check git working-tree cleanliness, pushed remotes, `$HOME/Developer` writability, free disk space of at least 4 GB, required CLIs (`git`, `uv`, `glab`, `npx`), and legacy legacy cloud path readability
- **AND** it SHALL create or reuse `git.ecomedic.vn/tdt/tdt-meta`
- **AND** it SHALL commit workspace metadata into `tdt-meta` with generated/runtime/secrets excluded
- **AND** it SHALL clone every source repo from its `origin` into `$HOME/Developer/tdt/<repo>`
- **AND** it SHALL convert source-like top-level entries without `.git/` into GitLab repos before cloning them into the new workspace
- **AND** it SHALL create root symlinks into `tdt-meta/`
- **AND** it SHALL run or instruct `tools/relocate-venvs.sh` from the new workspace.

### Scenario: Re-running after partial completion

- **WHEN** the migration script runs after a prior interrupted run
- **THEN** it SHALL detect existing repos, existing remotes, existing metadata commits, existing symlinks, and existing relocated venvs
- **AND** it SHALL skip completed steps without overwriting uncommitted changes
- **AND** it SHALL exit 0 when the target state is already satisfied.

### Scenario: Legacy path is decommissioned

- **WHEN** cutover verification passes
- **THEN** the script SHALL remove active references to the legacy legacy cloud workspace from shell hooks, deploy defaults, docs, scripts, and agent instructions
- **AND** the legacy legacy cloud directory MAY be deleted or renamed as an inert operator backup
- **AND** no rollback workflow SHALL be specified, tested, or supported by this change.

---

## ADDED Requirement: Comprehensive content categorization

Every top-level entry in the legacy workspace SHALL have an explicit destination. No entry SHALL be copied implicitly.

### Scenario: Source repos with own `.git` (Category A)

- **WHEN** a top-level entry has its own `.git/`
- **THEN** the migration SHALL clone it from `origin` into `$HOME/Developer/tdt/<name>`
- **AND** the cloned HEAD SHALL match the legacy working tree HEAD
- **AND** dirty or unpushed commits SHALL block migration.

### Scenario: Source-like directories without `.git` (Category B)

- **WHEN** a top-level entry contains code, infrastructure, or buildable artifacts but no `.git/` (`bootstrap-nexus-for-mobile/`, `qi-bridge/`)
- **THEN** the migration SHALL create a GitLab repo at `git.ecomedic.vn/tdt/<name>`
- **AND** it SHALL commit source/config only, excluding generated binaries and caches
- **AND** it SHALL clone the new repo into `$HOME/Developer/tdt/<name>`.

### Scenario: Workspace metadata (Category C)

- **WHEN** a top-level entry is docs, OpenSpec, agent config, workspace config, examples, OpenAPI contracts, root guidance, workspace ignore files, workspace editor config, or shared tools
- **THEN** it SHALL move into `tdt-meta/`
- **AND** the workspace root SHALL expose compatibility symlinks to that content where existing tools expect root-level paths.

### Scenario: Hidden AI-tool runtime dotdirs (Category D)

- **WHEN** a workspace-root entry is a hidden AI-tool runtime/state dotdir such as `.claude/`, `.continue/`, `.augment/`, `.qwen/`, `.roo/`, or similar
- **THEN** it SHALL NOT be migrated to Git, legacy cloud, or `tdt-meta`
- **AND** it SHALL be allowed to recreate locally under `$HOME/Developer/tdt/.<tool>/`
- **AND** `tdt-meta/.gitignore` SHALL ignore these runtime directories.

### Scenario: Secrets (Category E)

- **WHEN** the migration encounters workspace-root `.env`
- **THEN** it SHALL compare keys against `$HOME/.tdt/.env`
- **AND** any missing keys SHALL be merged into `$HOME/.tdt/.env` only after operator review
- **AND** workspace-root `.env` SHALL NOT be copied to Git, legacy cloud, `tdt-meta`, or any synced location
- **AND** `.env.example` in `tdt-meta/` SHALL document non-secret schema only.

### Scenario: Runtime and generated content (Category F)

- **WHEN** a workspace entry is generated/cache/runtime data (`data/`, `nexus-test-data/`, `graphify-out/`, worktree dirs, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `.gitnexus/`, `DerivedData/`, build outputs, venvs)
- **THEN** it SHALL be skipped
- **AND** the new workspace SHALL recreate it from documented commands
- **AND** ignore rules SHALL prevent it from entering source repos or `tdt-meta/`.

### Scenario: New top-level entry encountered

- **WHEN** migration sees an uncategorized top-level entry
- **THEN** it SHALL stop and require an explicit operator category decision
- **AND** the decision SHALL be recorded in `tdt-meta/tools/migration-decisions.log` or an equivalent reviewed file.

---

## ADDED Requirement: Path-bound cache and index invalidation

The migration SHALL treat all absolute-path-bound caches and indexes as invalid after relocation.

### Scenario: Code intelligence indexes

- **WHEN** migration completes source relocation
- **THEN** GitNexus indexes SHALL be rebuilt or re-pointed for every active repo
- **AND** Graphify output SHALL be regenerated from `$HOME/Developer/tdt/`
- **AND** old indexes containing legacy legacy cloud paths SHALL not be used for impact analysis or architecture answers.

### Scenario: IDE caches

- **WHEN** Xcode or Android Studio is opened from the new path
- **THEN** absolute-path caches such as Android Studio `.idea/workspace.xml`, Gradle local references, Xcode derived data, or Source Control bookmarks SHALL be regenerated or cleared as needed
- **AND** generated IDE state SHALL not be committed unless it is intentional shared configuration.

### Scenario: Agent and automation references

- **WHEN** migration verifies cutover
- **THEN** launchd plists, cron/automation prompts, shell hooks, skill docs, AGENTS guidance, MCP configs, and local scripts SHALL be scanned for the legacy legacy cloud path
- **AND** every active reference SHALL be replaced with `$HOME/Developer/tdt` or a configurable env var.

---

## ADDED Requirement: Multi-machine consistency without legacy cloud

Every developer machine SHALL converge via Git remotes, not legacy cloud workspace.

### Scenario: Source propagation between machines

- **WHEN** developer A changes source code
- **THEN** developer A SHALL commit and push to the corresponding source repo remote
- **AND** developer B SHALL fetch or pull that repo to receive the change
- **AND** legacy cloud SHALL NOT be involved.

### Scenario: Metadata propagation between machines

- **WHEN** developer A changes `AGENTS.md`, OpenSpec artifacts, docs, skills, or shared scripts
- **THEN** developer A SHALL commit and push in `tdt-meta`
- **AND** developer B SHALL pull `tdt-meta` before relying on those changes
- **AND** legacy cloud SHALL NOT be involved.

### Scenario: New machine bootstrap

- **WHEN** a developer adds a new machine
- **THEN** they SHALL create `$HOME/Developer/tdt/`
- **AND** they SHALL clone `tdt-meta` plus each source repo from GitLab
- **AND** they SHALL create root symlinks to `tdt-meta/`
- **AND** they SHALL run `tools/relocate-venvs.sh`, install hooks, rebuild indexes, and run the verification harness
- **AND** the machine SHALL pass verification with no legacy cloud account configured.

---

## ADDED Requirement: Final cutover verification

The migration SHALL not be considered complete until automated and manual verification passes from the new location.

### Scenario: Verification harness

- **WHEN** cutover verification runs
- **THEN** `tools/legacy cloud-audit.sh` SHALL report no active legacy cloud workspace violations
- **AND** Python repo tests SHALL pass from relocated venvs
- **AND** Jira and GitLab live SDK smoke checks SHALL pass through `tdt_core` factories
- **AND** `webhook-receiver` deploy and `/health` SHALL pass from `$HOME/Developer/tdt/webhook-receiver`
- **AND** Xcode, Android Studio, Docker bind mounts, GitNexus, and Graphify SHALL be validated from the new path.

### Scenario: Legacy path guard

- **WHEN** cutover is complete
- **THEN** shell hooks and scripts SHALL no longer match `/Users/lekhanhvinh/Developer/tdt/`
- **AND** agents SHALL treat edits under the legacy path as policy violations
- **AND** future development SHALL happen only in `$HOME/Developer/tdt/`.

---

## Non-functional requirements

- **No rollback contract:** The migration is one-way for supported workflows; legacy legacy cloud content may be kept only as an inert backup outside the active toolchain.
- **No legacy cloud dependency:** Development must work when legacy cloud workspace is disabled or unavailable.
- **Git auditability:** Every source or metadata change must have Git history.
- **Operational continuity:** The production daemon remains at `$HOME/.tdt-webhook-receiver/`; only its source checkout moves.
- **Path configurability:** Scripts should default to `$HOME/Developer/tdt` but accept explicit env overrides for tests.
- **Documentation currency:** `AGENTS.md`, OpenSpec, and tool docs must describe the new layout before cutover is declared complete.
