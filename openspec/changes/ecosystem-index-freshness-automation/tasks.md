# Tasks: Ecosystem Index Freshness Automation

## 1. Create workspace refresh script

Create `~/Developer/scripts/refresh-knowledge-indexes.sh` using official patterns from `go-microservices/scripts/knowledge-tools.sh`.

### 1.1 Create log directory

Create `~/Developer/.knowledge-refresh/` directory.

### 1.2 Implement owner lock mechanism

Reuse the official directory-based lock pattern:
- `acquire_gitnexus_owner` / `release_gitnexus_owner` (from knowledge-tools.sh)
- `acquire_graphify_owner` / `release_graphify_owner` (from knowledge-tools.sh)
- Check for `.rebuild.lock` before acquiring Graphify lock
- Stale lock detection via PID liveness check

### 1.3 Implement repo discovery

Find repos by checking for `.gitnexus/` and `graphify-out/` directories.

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

### 1.7 Implement logging

Timestamped entries with repo name, worktree/main, tool, status, duration.

## 2. Create post-merge hook

Create a post-merge hook that triggers delayed refresh when code lands on main.

### 2.1 Write the post-merge hook

Hook logic (uses official patterns):
- Detect if merge target is main branch (check `MERGE_HEAD` or branch name)
- Acquire graphify owner lock (yields if watch/refresh running)
- Write timestamp to `/tmp/knowledge-postmerge-<repo-slug>.ts`
- Sleep 30 seconds (detached background)
- Check timestamp — if changed, exit (newer merge will handle it)
- Run: `gitnexus analyze . --index-only --default-branch main`
- Run: `GRAPHIFY_VIZ_NODE_LIMIT=0 graphify extract . --code-only`
- Release owner lock
- Log result to `~/Developer/.knowledge-refresh/post-merge.log`

### 2.2 Create hook installer

Create `~/Developer/scripts/install-post-merge-hook.sh` that:
- Finds all repos with `.gitnexus/` or `graphify-out/`
- Installs the post-merge hook in each (idempotent, marked block)
- Uses `# knowledge-postmerge-start` / `# knowledge-postmerge-end` markers
- Preserves existing hook content
- Reports which repos were updated

### 2.3 Extend knowledge-tools.sh

Add `install-post-merge-hooks` target to `go-microservices/scripts/knowledge-tools.sh` so it runs alongside the existing Graphify hook installation.

## 3. Create status command

Create `~/Developer/scripts/knowledge-status.sh` that reports freshness across all repos and worktrees.

### 3.1 Implement status discovery

Same discovery as refresh script (repos + worktrees).

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

Remove stale "Weekly crons: graphify freshness (Mon 8AM), wiki lint (Mon 9AM)" claim. Add actual LaunchAgent + post-merge hook description.

### 5.2 Update CLAUDE.md

Update staleness warnings to reference the automated refresh mechanism.

## 6. Extend existing spec

Add automation requirements to `openspec/specs/refresh-gitnexus-index-groups/spec.md`.

## Verification

- [ ] `~/Developer/scripts/refresh-knowledge-indexes.sh` runs successfully on all repos
- [ ] `~/Developer/scripts/refresh-knowledge-indexes.sh` discovers and refreshes worktrees
- [ ] `~/Developer/scripts/knowledge-status.sh` reports freshness correctly for repos + worktrees
- [ ] Post-merge hook triggers delayed refresh on merge to main
- [ ] Post-merge debounce prevents redundant refreshes during rapid merges
- [ ] Owner lock mechanism coordinates with existing `graphify watch` sessions
- [ ] LaunchAgent loads with `launchctl load ~/Library/LaunchAgents/com.developer.index-refresh.plist`
- [ ] Manual trigger works: `launchctl start com.developer.index-refresh`
- [ ] Log files are created and contain timestamped entries
- [ ] Owner lock contention yields gracefully (no forced override)
- [ ] Missing CLI (gitnexus/graphify) doesn't crash the script
- [ ] Detached HEAD worktrees are skipped
- [ ] Stale worktrees (>30 days) are skipped
- [ ] AGENTS.md no longer contains stale cron claims
