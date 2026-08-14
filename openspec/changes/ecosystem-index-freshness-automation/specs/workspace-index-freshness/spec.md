# workspace-index-freshness Specification

## Purpose

Define automated, non-destructive GitNexus and Graphify index freshness for all workspace repositories, including post-merge triggers for agent freshness, worktree-aware refresh, and scheduled bulk refresh.

## ADDED Requirements

### Requirement: Scheduled automated index refresh

The workspace SHALL provide a scheduled refresh mechanism that keeps GitNexus and Graphify indexes current with each repository's latest committed HEAD.

#### Scenario: Nightly refresh runs automatically

- **WHEN** the scheduled LaunchAgent fires (nightly at 02:30 local time)
- **THEN** the refresh script SHALL discover all repositories under `~/Developer/` with existing `.gitnexus/` or `graphify-out/` state AND a valid git repository marker (`.git` directory or file)
- **AND** for each discovered repository, it SHALL run `gitnexus analyze . --index-only --default-branch main` (if GitNexus state exists) and `graphify extract . --code-only` (if Graphify state exists)
- **AND** the operation SHALL complete without user interaction

#### Scenario: Directory is not a valid repository

- **WHEN** a directory under `~/Developer/` has `.gitnexus/` or `graphify-out/` but no `.git` marker
- **THEN** the refresh script SHALL skip it
- **AND** the skip SHALL be logged with the reason "not a git repository"

#### Scenario: Repository has no index state

- **WHEN** a repository under `~/Developer/` has neither `.gitnexus/` nor `graphify-out/`
- **THEN** the refresh script SHALL skip it silently without error

#### Scenario: GitNexus CLI is not installed

- **WHEN** the refresh script runs and `gitnexus` is not on PATH
- **THEN** the script SHALL skip GitNexus operations for all repos and log a warning
- **AND** it SHALL still run Graphify operations for repos with Graphify state

#### Scenario: Graphify CLI is not installed

- **WHEN** the refresh script runs and `graphify` is not on PATH
- **THEN** the script SHALL skip Graphify operations for all repos and log a warning
- **AND** it SHALL still run GitNexus operations for repos with GitNexus state

### Requirement: Post-merge freshness trigger

When code merges or pulls to a repository's main branch locally, the workspace SHALL trigger an index refresh so that coding agents get fresh indexes promptly.

#### Scenario: Local merge or pull lands on main branch

- **WHEN** a local merge or `git pull` completes to a repository's main branch
- **THEN** the existing post-merge hook SHALL trigger a Graphify refresh (already implemented) and a GitNexus refresh
- **AND** the GitNexus refresh SHALL run `gitnexus analyze . --index-only --default-branch main` in the background
- **AND** the refresh SHALL not block the merge or pull operation

#### Scenario: Multiple merges land rapidly

- **WHEN** multiple merges to main occur in rapid succession
- **THEN** the workspace lock SHALL prevent concurrent refreshes
- **AND** only one refresh SHALL run at a time per repository

#### Scenario: Merge is not to main branch

- **WHEN** a merge completes to a non-main branch (e.g., feature branch)
- **THEN** the post-merge hook SHALL exit silently without triggering a refresh

#### Scenario: Post-merge hook is not installed

- **WHEN** a repository has not had the post-merge hook installed
- **THEN** merges SHALL complete normally without triggering a refresh
- **AND** the nightly bulk refresh SHALL still cover the repository

### Requirement: Worktree-aware index refresh

The refresh mechanism SHALL discover and handle git worktrees, ensuring indexes are available for agents working in any worktree.

#### Scenario: Worktree has its own GitNexus index

- **WHEN** a worktree has a `.gitnexus/` directory
- **THEN** the nightly refresh SHALL run `gitnexus analyze . --index-only` for that worktree independently
- **AND** the worktree's index SHALL NOT affect the main checkout's index

#### Scenario: Worktree has its own Graphify state

- **WHEN** a worktree has its own `graphify-out/` or `.graphify/` directory
- **THEN** the nightly refresh SHALL run `graphify extract . --code-only` for that worktree independently
- **AND** the worktree's graph SHALL NOT affect the main checkout's graph

#### Scenario: Worktree shares main checkout's Graphify graph

- **WHEN** a worktree has NO `graphify-out/` or `.graphify/` directory
- **THEN** the worktree uses the main checkout's Graphify graph
- **AND** the refresh SHALL only run `graphify extract . --code-only` from the main checkout
- **AND** worktree status SHALL report whether the shared graph is fresh

#### Scenario: Worktree creation triggers graph refresh

- **WHEN** `git worktree add` creates a new worktree
- **THEN** the post-checkout hook (already installed by Graphify) SHALL trigger a Graphify refresh in the main checkout
- **AND** the new worktree's GitNexus index SHALL be initialized on first use

#### Scenario: Detached HEAD worktree is skipped

- **WHEN** a worktree is in detached HEAD state
- **THEN** the refresh script SHALL skip it
- **AND** the skip SHALL be logged with the reason "detached HEAD"

#### Scenario: Stale worktree is skipped

- **WHEN** a worktree's branch has not been updated in more than 30 days
- **THEN** the refresh script SHALL skip it
- **AND** the skip SHALL be logged with the reason "stale worktree (>30 days)"

### Requirement: Concurrency safety

The refresh mechanism SHALL prevent overlapping runs through appropriate locking and SHALL not starve operations when a long-running watcher holds the lock.

#### Scenario: Nightly refresh overlap is prevented

- **WHEN** the scheduled nightly refresh fires and a previous run holds the lockfile
- **THEN** the new run SHALL exit cleanly without waiting or killing the previous run
- **AND** the exit SHALL be logged as "skipped: previous run active"

#### Scenario: Post-merge debounce prevents redundant work

- **WHEN** the post-merge hook fires and a refresh is already running
- **THEN** the hook SHALL yield to the running refresh
- **AND** no concurrent refresh SHALL start

#### Scenario: Graphify watcher holds lock indefinitely

- **WHEN** the Graphify watcher (`graphify watch`) holds the owner lock for an extended period
- **THEN** the refresh script SHALL check the lock's age
- **AND** if the lock is older than 30 minutes, the refresh script SHALL log a warning and proceed with a bounded refresh
- **AND** the bounded refresh SHALL complete within 5 minutes and release the lock

#### Scenario: Lock staleness detection

- **WHEN** a lock file exists but its owning process is no longer running
- **THEN** the refresh script SHALL detect the stale lock via PID liveness check
- **AND** it SHALL remove the stale lock and acquire it
- **AND** the stale lock removal SHALL be logged

### Requirement: Observable refresh status

The workspace SHALL provide a status command that reports index freshness across all repositories and worktrees.

#### Scenario: Status is checked manually

- **WHEN** a developer runs `~/Developer/scripts/knowledge-status.sh`
- **THEN** it SHALL list every repository with existing index state
- **AND** for each, it SHALL report: tool (GitNexus/Graphify), last refresh time, current HEAD revision, indexed revision, freshness status (current/stale/unknown)
- **AND** it SHALL list worktrees for each repository with their index status

#### Scenario: Refresh log is available

- **WHEN** a developer inspects `~/Developer/.knowledge-refresh/refresh.log`
- **THEN** it SHALL contain timestamped entries for each repo refresh attempt
- **AND** entries SHALL include: timestamp, repo name, worktree/main, tool, status (success/failure/skipped), duration

#### Scenario: Post-merge trigger log is available

- **WHEN** a developer inspects `~/Developer/.knowledge-refresh/post-merge.log`
- **THEN** it SHALL contain timestamped entries for each post-merge trigger
- **AND** entries SHALL include: timestamp, repo name, merge commit, refresh result

### Requirement: Non-destructive operations

The refresh mechanism SHALL not modify application code, credentials, or configuration.

#### Scenario: Refresh affects only index state

- **WHEN** the refresh runs
- **THEN** it SHALL modify only `.gitnexus/`, `graphify-out/`, `.graphify/`, and `.graphify/needs_update` directories/files
- **AND** it SHALL NOT modify source code, `.env` files, `pyproject.toml`, `go.mod`, or other application files

#### Scenario: Repository is in merge or rebase state

- **WHEN** a repository is in the middle of a merge, rebase, or cherry-pick
- **THEN** the refresh script SHALL skip that repository
- **AND** the skip SHALL be logged with the reason "repo in merge state"

### Requirement: Documentation accuracy

Workspace documentation SHALL accurately describe the refresh mechanism without stale claims.

#### Scenario: AGENTS.md describes refresh automation

- **WHEN** a developer reads AGENTS.md for refresh information
- **THEN** it SHALL describe the actual LaunchAgent-based automation and post-merge triggers
- **AND** it SHALL NOT contain stale claims about weekly crons that don't exist

#### Scenario: CLAUDE.md reflects current staleness policy

- **WHEN** a developer reads the workspace root `~/Developer/CLAUDE.md` for knowledge graph guidance
- **THEN** it SHALL reference the automated refresh mechanism
- **AND** the staleness warning SHALL be updated to reflect that automation is in place
