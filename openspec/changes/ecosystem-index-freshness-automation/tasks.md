# Tasks: Ecosystem Index Freshness Automation

## 1. Create workspace refresh script

Create `~/Developer/scripts/refresh-knowledge-indexes.sh` using official patterns from `go-microservices/scripts/knowledge-tools.sh`.

### 1.1 Create log directory

Create `~/Developer/.knowledge-refresh/` directory.

### 1.2 Implement owner lock mechanism

Reuse the official directory-based lock pattern from `knowledge-tools.sh`:
- `acquire_gitnexus_owner` / `release_gitnexus_owner`
- `acquire_graphify_owner` / `release_graphify_owner`
- Check for `.rebuild.lock` before acquiring Graphify lock
- Stale lock detection via PID liveness check

### 1.3 Implement repo discovery

Find repos by checking for `.gitnexus/` and `graphify-out/` directories. **Require valid git repository marker** (`.git` directory or file) to prevent indexing workspace root or non-repo directories.

### 1.4 Implement worktree discovery

For each repo, run `git worktree list --porcelain` and filter:
- Skip main checkout (handled separately)
- Skip detached HEAD worktrees
- Skip worktrees with no branch activity in 30+ days
- Skip `.claude/worktrees/` (ephemeral)

### 1.5 Implement GitNexus refresh

Use the official command: `gitnexus analyze . --index-only --default-branch main`
- Acquire workspace lock before refresh
- Release after refresh
- For worktrees: run from worktree directory (each has own `.gitnexus/`)

### 1.6 Implement Graphify refresh

Use the official foreground command: `graphify extract . --code-only`
- Acquire repo owner lock before refresh
- Release after refresh
- Only run from main checkouts (not worktrees)
- Set `GRAPHIFY_VIZ_NODE_LIMIT=0` (official pattern)
- Backup `graph.json` before refresh, restore on failure
- **Worktree handling**: Check if worktree has its own `graphify-out/` or `.graphify/` — if yes, refresh independently; if no, use main checkout's graph

### 1.7 Implement watcher lock starvation mitigation

Check lock age before proceeding:
- If lock is older than 30 minutes, log warning and proceed with bounded refresh
- Bounded refresh completes within 5 minutes and releases lock
- Log the starvation detection and recovery

### 1.8 Implement logging

Timestamped entries with repo name, worktree/main, tool, status, duration.

## 2. Extend existing post-merge hook for GitNexus

**Critical finding:** Graphify post-merge hooks already exist in all 18 repos. We only need to add GitNexus refresh.

### 2.1 Read existing hook

The existing hook at `.git/hooks/post-merge` has:
- `graphify-post-merge-hook-start` / `graphify-post-merge-hook-end` markers
- `graphify_should_skip` — skips during rebase/merge/cherry-pick
- `graphify_has_state` — checks for graphify state
- `graphify_mark_stale` — marks graph as stale
- `graphify_rebuild_code` — rebuilds code-only graph in background

### 2.2 Add GitNexus refresh function

Add `gitnexus_refresh_after_merge()` to the existing hook:
- Check if `.gitnexus/` exists
- Acquire workspace lock (yields if another refresh is running)
- Run `gitnexus analyze . --index-only --default-branch main` in background
- Release lock after delay

### 2.3 Test extension

Verify the extended hook:
- Doesn't break existing Graphify behavior
- GitNexus refresh runs after merge to main
- Workspace lock coordinates with running operations
- Yields gracefully when lock is held

## 3. Create status command

Create `~/Developer/scripts/knowledge-status.sh` that reports freshness across all repos and worktrees.

### 3.1 Implement status discovery

Same discovery as refresh script (repos + worktrees), with valid git marker check.

### 3.2 Implement freshness check

For each repo/worktree:
- GitNexus: compare `meta.json` `lastCommit` with current HEAD
- Graphify: compare `graph.json` timestamp with last commit time

### 3.3 Implement formatted output

Table output with repo, worktree, tool, last refresh, freshness status.

## 4. Create LaunchAgent

Create `~/Library/LaunchAgents/com.developer.index-refresh.plist` for nightly execution.

### 4.1 Write plist file

Nightly schedule at 02:30 local time with KeepAlive on crash.

### 4.2 Load and verify LaunchAgent

Load the agent and verify it fires correctly.

## 5. Update documentation

### 5.1 Fix AGENTS.md

Remove stale "Weekly crons: graphify freshness (Mon 8AM), wiki lint (Mon 9AM)" claim. Add actual LaunchAgent + hook system description.

### 5.2 Update CLAUDE.md

Update staleness warnings in `~/Developer/CLAUDE.md` (workspace root) to reference the automated refresh mechanism.

## 6. Extend existing spec

**Extend, not replace** the existing `openspec/specs/refresh-gitnexus-index-groups/spec.md` with automation requirements. The existing spec has 33 lines covering bounded index maintenance and group synchronization. We add requirements for scheduled refresh, post-merge triggers, and worktree awareness.

## Verification

- [ ] `~/Developer/scripts/refresh-knowledge-indexes.sh` runs successfully on all repos
- [ ] `~/Developer/scripts/refresh-knowledge-indexes.sh` discovers and refreshes worktrees
- [ ] `~/Developer/scripts/refresh-knowledge-indexes.sh` requires valid git marker (skips ~/Developer/)
- [ ] `~/Developer/scripts/knowledge-status.sh` reports freshness correctly for repos + worktrees
- [ ] Extended post-merge hook triggers GitNexus refresh after local merge/pull
- [ ] Extended post-merge hook doesn't break existing Graphify behavior
- [ ] Workspace lock coordinates with running operations
- [ ] Watcher lock starvation is detected and mitigated (30min age check)
- [ ] LaunchAgent loads with `launchctl load ~/Library/LaunchAgents/com.developer.index-refresh.plist`
- [ ] Manual trigger works: `launchctl start com.developer.index-refresh`
- [ ] Log files are created and contain timestamped entries
- [ ] Owner lock contention yields gracefully (no forced override)
- [ ] Missing CLI (gitnexus/graphify) doesn't crash the script
- [ ] Detached HEAD worktrees are skipped
- [ ] Stale worktrees (>30 days) are skipped
- [ ] Worktrees with own graphify-out are refreshed independently
- [ ] AGENTS.md no longer contains stale cron claims
- [ ] CLAUDE.md (workspace root) staleness warning is updated
