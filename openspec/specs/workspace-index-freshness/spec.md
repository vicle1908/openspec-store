# workspace-index-freshness Specification

## Purpose
Define automated, non-destructive GitNexus and official Graphify-Labs Graphify index freshness for inventoried workspace repositories, including local post-merge dispatch, worktree-aware refresh, scheduled bulk refresh, and observable status.

## Requirements

### Requirement: Official provider identity

The workspace refresh mechanism SHALL use GitNexus `1.6.9` and Graphify from `https://github.com/Graphify-Labs/graphify`, package `graphifyy`, CLI `graphify`, pinned at `0.9.42` for this change.

#### Scenario: Provider identity is verified

- **WHEN** the refresh script starts
- **THEN** it SHALL verify the installed GitNexus and Graphify executable versions
- **AND** it SHALL fail closed for a provider version mismatch unless the operation is explicitly diagnostic
- **AND** it SHALL NOT invoke an alternate Graphify package or provider

#### Scenario: Graphify 0.9.42 features are available

- **WHEN** a Graphify refresh runs
- **THEN** non-regular files SHALL be skipped without hanging extraction
- **AND** same-length rewrites SHALL be detected by incremental update
- **AND** graph provenance SHALL be derived from the analyzed repository
- **AND** canonical POSIX source paths SHALL be used

### Requirement: Reviewed inventory authorization

Automated refresh SHALL operate only on an explicit, version-controlled repository inventory containing canonical repository root, default branch, GitNexus enablement, and Graphify enablement.

#### Scenario: Inventory entry is valid

- **WHEN** an inventory entry is loaded
- **THEN** its path SHALL resolve under an approved workspace root
- **AND** it SHALL identify a valid Git repository
- **AND** its default branch SHALL exist
- **AND** its canonical Git common directory SHALL be unique

#### Scenario: Inventory entry is invalid

- **WHEN** an inventory entry is outside the approved root, not a Git repository, or has no valid default branch
- **THEN** the entry SHALL be rejected
- **AND** no refresh SHALL run for that entry
- **AND** the rejection SHALL be logged

#### Scenario: Unlisted repository is discovered

- **WHEN** a repository has index state but is absent from the reviewed inventory
- **THEN** status MAY report it as an unlisted candidate
- **AND** the automated refresh SHALL NOT modify its index

### Requirement: Scheduled automated index refresh

The workspace SHALL provide a LaunchAgent scheduled at 02:30 local time that refreshes eligible inventoried repositories without user interaction.

#### Scenario: Nightly refresh runs automatically

- **WHEN** the LaunchAgent fires
- **THEN** the refresh script SHALL load and validate the reviewed inventory
- **AND** for each clean eligible repository it SHALL run `gitnexus analyze . --index-only --default-branch <inventory-branch>` when GitNexus is enabled
- **AND** it SHALL run the official Graphify incremental command `graphify update .` when Graphify is enabled and no watcher covers the root
- **AND** it SHALL complete without user interaction

#### Scenario: Graphify repair is required

- **WHEN** `graphify update .` fails or the graph is missing/corrupt
- **THEN** the script MAY run the bounded repair command `graphify extract . --code-only`
- **AND** the repair SHALL be bounded by the per-repository timeout
- **AND** the previous usable graph SHALL be preserved on failure

#### Scenario: Provider is missing or mismatched

- **WHEN** GitNexus or Graphify is absent or reports a version other than the approved pin
- **THEN** operations for that provider SHALL be skipped with an explicit `provider_missing` or `provider_mismatch` status
- **AND** the other provider SHALL continue independently

#### Scenario: Repository has no index state

- **WHEN** an inventoried repository has no state directory for an enabled provider
- **THEN** the script SHALL report `skipped_uninitialized`
- **AND** it SHALL NOT implicitly initialize the provider index

### Requirement: Local post-merge freshness dispatch

When code merges or pulls to an inventoried repository's configured default branch locally, the workspace SHALL dispatch a non-blocking GitNexus refresh.

#### Scenario: Local merge or merge-based pull lands on default branch

- **WHEN** a local merge or merge-based `git pull` completes on the configured default branch
- **THEN** the workspace-managed post-merge block SHALL dispatch the central refresh script asynchronously
- **AND** the central script SHALL apply the same inventory, dirty-tree, lock, timeout, and revision checks as a nightly run
- **AND** the hook SHALL not block the merge or pull operation

#### Scenario: Remote pull uses rebase

- **WHEN** `git pull --rebase` completes
- **THEN** the post-merge hook MAY not fire
- **AND** nightly refresh SHALL remain the fallback
- **AND** documentation SHALL not claim that remote PR merges or rebase pulls trigger this hook directly

#### Scenario: Non-default branch

- **WHEN** a merge completes on a non-default branch
- **THEN** the dispatcher SHALL exit without scheduling a refresh

#### Scenario: Hook is not installed

- **WHEN** a repository lacks the workspace-managed post-merge block
- **THEN** its Git operation SHALL complete normally
- **AND** the nightly inventory refresh SHALL remain available

### Requirement: Worktree-aware index refresh

The refresh mechanism SHALL enumerate inventoried repository worktrees and refresh only worktrees that already have the corresponding index state.

#### Scenario: Worktree has GitNexus state

- **WHEN** an eligible non-detached worktree has `.gitnexus/`
- **THEN** the nightly refresh SHALL run `gitnexus analyze . --index-only --default-branch <inventory-branch>` from that worktree
- **AND** it SHALL verify the worktree index independently from the main checkout

#### Scenario: Worktree has Graphify state

- **WHEN** an eligible non-detached worktree has `graphify-out/`
- **THEN** the nightly refresh SHALL run `graphify update .` from that worktree
- **AND** the worktree graph SHALL be evaluated independently

#### Scenario: Worktree is uninitialized

- **WHEN** a worktree has neither `.gitnexus/` nor `graphify-out/`
- **THEN** it SHALL be reported as `skipped_uninitialized`
- **AND** the refresh SHALL not create state implicitly

#### Scenario: Detached or stale worktree

- **WHEN** a worktree is detached, under `.claude/worktrees/`, or its feature branch tip is older than 30 days
- **THEN** the refresh SHALL skip it
- **AND** the skip reason SHALL be logged as `detached_head`, `ephemeral_worktree`, or `stale_worktree`

### Requirement: Dirty and transitional repository safety

The refresh mechanism SHALL preserve committed-HEAD semantics and SHALL not operate during repository transitions.

#### Scenario: Repository is dirty

- **WHEN** tracked, staged, or untracked changes exist in a repository or worktree
- **THEN** the refresh SHALL skip that target with `skipped_dirty`
- **AND** status SHALL expose the dirty condition

#### Scenario: Repository is in merge or rebase state

- **WHEN** a repository is in merge, rebase, or cherry-pick state
- **THEN** the refresh SHALL skip it with `skipped_merge_state`
- **AND** the skip SHALL be logged

### Requirement: Concurrency safety

The refresh mechanism SHALL prevent overlapping writes through PID-aware directory locks and SHALL never steal a live lock based only on age.

#### Scenario: Lock is free

- **WHEN** no live owner holds the target lock
- **THEN** the refresh SHALL create the lock atomically
- **AND** it SHALL record PID, owner, timestamp, and canonical target

#### Scenario: Lock is held by a live process

- **WHEN** the owner PID is alive
- **THEN** the new operation SHALL exit or skip cleanly with `lock_busy`
- **AND** it SHALL not wait indefinitely, kill the owner, or steal the lock

#### Scenario: Lock owner is dead

- **WHEN** the lock exists but its recorded PID is no longer alive
- **THEN** the refresh MAY reclaim the lock
- **AND** the reclaim SHALL be logged

#### Scenario: Graphify watcher covers a root

- **WHEN** `graphify watch` is actively watching an inventoried root
- **THEN** scheduled Graphify refresh for that root SHALL be skipped with `watcher_active`
- **AND** the watcher SHALL remain authoritative for that root

### Requirement: Bounded execution and recovery

Each provider operation SHALL have a five-minute timeout, the whole nightly run SHALL have a two-hour timeout, and failed operations SHALL preserve the last usable index.

#### Scenario: Provider hangs

- **WHEN** a provider operation exceeds five minutes
- **THEN** the operation SHALL be terminated or marked timed out
- **AND** the next repository SHALL still be processed
- **AND** the log SHALL include `timeout`

#### Scenario: HEAD changes during refresh

- **WHEN** the repository HEAD differs from the captured target after refresh
- **THEN** the result SHALL be `superseded`, not success
- **AND** the index SHALL be re-evaluated on a later run

### Requirement: Observable refresh status

The workspace SHALL provide a status command and bounded timestamped logs.

#### Scenario: Human status is requested

- **WHEN** a developer runs `knowledge-status.sh`
- **THEN** it SHALL list every inventoried repository and eligible worktree
- **AND** it SHALL report provider, status, last refresh, current HEAD, indexed revision, dirty state, and watcher state

#### Scenario: Machine status is requested

- **WHEN** a developer runs `knowledge-status.sh --json`
- **THEN** it SHALL emit valid bounded JSON with the same status fields

#### Scenario: Refresh log is inspected

- **WHEN** a developer inspects the refresh log
- **THEN** entries SHALL include timestamp, canonical target, provider, status, duration, target revision, and indexed revision where available
- **AND** logs SHALL be rotated to a bounded size

### Requirement: Non-destructive operations

The refresh mechanism SHALL modify only provider-generated index state, workspace automation state, and logs.

#### Scenario: Refresh succeeds

- **WHEN** a refresh runs
- **THEN** it SHALL modify only `.gitnexus/`, `graphify-out/`, `.graphify/needs_update`, lock state, and automation logs
- **AND** it SHALL NOT modify source files, credentials, environment files, dependency manifests, or application configuration

#### Scenario: Refresh fails

- **WHEN** a provider fails
- **THEN** the last usable graph/index SHALL be preserved
- **AND** temporary files and locks SHALL be cleaned up

### Requirement: Documentation accuracy

Workspace documentation SHALL describe the actual provider versions, commands, automation scope, and limitations.

#### Scenario: AGENTS.md is read

- **WHEN** a developer reads `~/Developer/AGENTS.md`
- **THEN** it SHALL describe the LaunchAgent and local post-merge dispatcher
- **AND** it SHALL NOT claim nonexistent weekly crons

#### Scenario: CLAUDE.md is read

- **WHEN** a developer reads `~/Developer/.claude/CLAUDE.md`
- **THEN** it SHALL reference Graphify-Labs Graphify `graphifyy` 0.9.42 and GitNexus 1.6.9
- **AND** it SHALL describe watcher, dirty-tree, and local-hook limitations accurately
