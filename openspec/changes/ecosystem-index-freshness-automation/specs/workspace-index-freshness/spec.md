# workspace-index-freshness Specification

## Purpose

Define automated, non-destructive GitNexus and Graphify index freshness for all workspace repositories, including post-merge triggers for agent freshness, worktree-aware refresh, and scheduled bulk refresh.

## ADDED Requirements

### Requirement: Scheduled automated index refresh

The workspace SHALL provide a scheduled refresh mechanism that keeps GitNexus and Graphify indexes current with each repository's latest committed HEAD.

#### Scenario: Nightly refresh runs automatically

- **WHEN** the scheduled LaunchAgent fires (nightly at 02:30 local time)
- **THEN** the refresh script SHALL discover all repositories under `~/Developer/` with existing `.gitnexus/` or `graphify-out/` state
- **AND** for each discovered repository, it SHALL run `gitnexus analyze . --index-only --default-branch main` (if GitNexus state exists) and `graphify update .` (if Graphify state exists)
- **AND** the operation SHALL complete without user interaction

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

When code merges to any repository's main branch, the workspace SHALL trigger a delayed index refresh so that coding agents get fresh indexes within minutes.

#### Scenario: Merge lands on main branch

- **WHEN** a merge completes to a repository's main branch
- **THEN** a post-merge hook SHALL detect the merge and schedule a delayed refresh (30 seconds)
- **AND** after the delay, it SHALL run `gitnexus analyze . --index-only --default-branch main` and `graphify update .` from the main checkout
- **AND** the refresh SHALL run in the background without blocking the merge

#### Scenario: Multiple merges land rapidly

- **WHEN** multiple merges to main occur within the 30-second debounce window
- **THEN** only the last merge SHALL trigger a refresh
- **AND** earlier scheduled refreshes SHALL be cancelled by the debounce check

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

#### Scenario: Worktree shares Graphify graph

- **WHEN** a worktree exists for a repository with `graphify-out/`
- **THEN** the worktree shares the main checkout's Graphify graph
- **AND** the refresh SHALL only run `graphify update .` from the main checkout
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

The refresh mechanism SHALL prevent overlapping runs through appropriate locking.

#### Scenario: Nightly refresh overlap is prevented

- **WHEN** the scheduled nightly refresh fires and a previous run holds the lockfile
- **THEN** the new run SHALL exit cleanly without waiting or killing the previous run
- **AND** the exit SHALL be logged as "skipped: previous run active"

#### Scenario: Post-merge debounce prevents redundant work

- **WHEN** the post-merge hook fires and a newer merge timestamp is detected after the delay
- **THEN** the hook SHALL exit without running a refresh
- **AND** the newer merge's hook SHALL handle the refresh

#### Scenario: Post-merge and nightly refresh overlap

- **WHEN** a post-merge refresh is running when the nightly refresh starts
- **THEN** the nightly refresh SHALL wait for the post-merge to complete (or skip the affected repo)
- **AND** no index corruption SHALL occur from concurrent writes

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
- **THEN** it SHALL modify only `.gitnexus/` and `graphify-out/` directories
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

- **WHEN** a developer reads CLAUDE.md for knowledge graph guidance
- **THEN** it SHALL reference the automated refresh mechanism
- **AND** the staleness warning SHALL be updated to reflect that automation is in place
