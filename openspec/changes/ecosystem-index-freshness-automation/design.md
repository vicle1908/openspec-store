# Design: Ecosystem Index Freshness Automation

## Architecture Overview

Three complementary mechanisms ensure indexes stay fresh for coding agents:

```
┌─────────────────────────────────────────────────────────┐
│                    FRESHNESS LAYERS                      │
├─────────────┬──────────────────┬────────────────────────┤
│  Layer 1    │  Layer 2         │  Layer 3               │
│  Post-Merge │  Worktree-Aware  │  Nightly Bulk          │
│  Trigger    │  Refresh         │  Refresh               │
├─────────────┼──────────────────┼────────────────────────┤
│ Fires:      │ Fires:           │ Fires:                 │
│ 30s after   │ On worktree      │ 02:30 AM daily         │
│ merge to    │ creation/switch  │                        │
│ main        │                  │                        │
├─────────────┼──────────────────┼────────────────────────┤
│ Scope:      │ Scope:           │ Scope:                 │
│ Main checkout│ Main checkout   │ All repos + all        │
│ of merged   │ + new worktree   │ worktrees              │
│ repo only   │                  │                        │
├─────────────┼──────────────────┼────────────────────────┤
│ Tools:      │ Tools:           │ Tools:                 │
│ gitnexus    │ graphify update  │ gitnexus analyze       │
│ analyze     │ (main checkout)  │ --index-only           │
│ --index-only│                  │ graphify update .      │
│ graphify    │                  │                        │
│ update .    │                  │                        │
└─────────────┴──────────────────┴────────────────────────┘
```

## Part 1: Post-Merge Trigger

### Problem

When a PR merges to main, agents working on subsequent tasks get stale index results. The 30-60s delay lets git operations settle (pack files, ref updates) before indexing.

### Design

A **post-merge hook** installed in each indexed repo's `.git/hooks/post-merge`. Unlike the existing Graphify post-commit hook (which runs on every commit), this only fires on actual merges to main.

```
.git/hooks/post-merge
  ├── Detect if merge target is main branch
  ├── Debounce: write timestamp to /tmp/knowledge-postmerge-<repo>.ts
  ├── Sleep 30s (lets git operations settle)
  ├── Check if timestamp still matches (no newer merge happened)
  ├── If match: run refresh in background (detached process)
  └── If mismatch: skip (newer merge will handle it)
```

### Key decisions

**Why post-merge, not post-commit?**
- Post-commit fires on every commit including local WIP commits
- Post-merge only fires when code actually lands on a branch
- The existing Graphify post-commit hook already handles local commits (in go-microservices)

**Why 30s delay?**
- Git operations (pack files, ref updates) take a few seconds after merge
- GitHub/GitLab push events may trigger additional operations
- 30s is enough for settling but fast enough for agent freshness
- The debounce check prevents redundant work if multiple merges land quickly

**Why not use `at` or `launchctl` for the delay?**
- `at` is deprecated on macOS
- LaunchAgent scheduling is too coarse (minute-level)
- A simple `sleep 30` in the hook is reliable and self-contained
- The hook already runs detached (background), so it doesn't block the merge

### Hook installation

The hook is installed alongside the existing Graphify post-commit hook:
- `knowledge-tools.sh install-hooks` extends to include post-merge
- The hook is marked with `# knowledge-postmerge-start` / `# knowledge-postmerge-end` blocks
- Idempotent: re-running install-hooks doesn't duplicate the block

## Part 2: Worktree-Aware Refresh

### Problem

Git worktrees are used extensively (4 active). Each worktree:
- Has its own `.gitnexus/` directory (GitNexus indexes per-worktree correctly)
- Shares the main checkout's `graphify-out/` (Graphify graph is shared)
- The existing Graphify hook explicitly skips worktrees (COMMONDIR check)

When agents work in worktrees, they need:
1. Their own GitNexus index to be current
2. The shared Graphify graph to be current (refreshed from main checkout)

### Design

#### GitNexus worktree indexing

Each worktree already has its own `.gitnexus/` with a separate index. The nightly refresh discovers worktrees and refreshes each one:

```
For each repo with .gitnexus/:
  1. git worktree list --porcelain
  2. For each worktree path:
     a. If worktree has .gitnexus/ → run gitnexus analyze --index-only
     b. Skip bare repos and detached HEAD worktrees
```

GitNexus handles worktree isolation natively — each worktree's index is independent.

#### Graphify worktree awareness

Worktrees share the main checkout's `graphify-out/`. The strategy:

1. **Post-merge hook** runs from main checkout → refreshes shared graph
2. **Worktree creation** triggers post-checkout hook → refreshes main checkout's graph
3. **Nightly refresh** scans main checkouts only for Graphify (not worktrees)
4. **Worktree status** reports whether the shared graph is fresh

#### Worktree discovery

```bash
discover_worktrees() {
  local repo_root="$1"
  git -C "$repo_root" worktree list --porcelain | \
    awk '/^worktree / { print $2 }' | \
    grep -v "^${repo_root}$"  # exclude main checkout
}
```

#### Worktree filtering

Not all worktrees need indexing:
- Skip detached HEAD worktrees (no branch to index against)
- Skip worktrees on feature branches older than 30 days (stale)
- Skip worktrees under `.claude/worktrees/` (ephemeral Claude Code worktrees)

## Part 3: Nightly Bulk Refresh

### Problem

Catches anything the post-merge trigger missed (manual `git pull`, force pushes, etc.).

### Design

Same as original proposal — LaunchAgent at 02:30 AM running the refresh script across all repos and worktrees.

```
~/Library/LaunchAgents/com.developer.index-refresh.plist
  └── runs: ~/Developer/scripts/refresh-knowledge-indexes.sh
        ├── discovers repos with .gitnexus/ or graphify-out/
        ├── discovers worktrees for each repo
        ├── for each repo + worktree:
        │   ├── gitnexus analyze . --index-only --default-branch main
        │   └── graphify update .  (main checkout only)
        └── writes: ~/Developer/.knowledge-refresh/refresh.log
```

## Key Design Decisions

### 1. Three layers, not one

| Layer | Latency | Coverage | Cost |
|---|---|---|---|
| Post-merge trigger | 30s after merge | Merged repos | Low (incremental) |
| Worktree-aware | On worktree creation | New worktrees | Low (one-shot) |
| Nightly bulk | Hours (02:30 AM) | Everything | Low (incremental) |

Each layer catches what the others miss. The post-merge trigger gives agents fresh indexes within minutes of a merge. The nightly refresh is the safety net.

### 2. `--index-only` for GitNexus (no embeddings/PDG)

Embeddings and PDG are expensive and should remain on-demand. The refresh uses `--index-only` which:
- Updates the symbol graph and FTS index
- Preserves existing embeddings (no re-embedding)
- Skips PDG analysis
- Matches the bounded recovery authorized in `gitnexus-stable-contract`

### 3. `graphify update .` for Graphify (AST-only)

`graphify update .` runs incremental AST extraction:
- No LLM/API cost
- Fast (typically 5-15s per repo)
- Only processes new/changed files
- Matches the existing post-commit hook behavior

### 4. Debounce over dedup

The post-merge hook uses timestamp-based debounce rather than lockfile-based dedup:
- Simpler (no lockfile management needed)
- Handles rapid merge sequences (merge queue)
- The 30s sleep naturally coalesces rapid merges
- No risk of abandoned locks

### 5. LaunchAgent over crontab

- LaunchAgent survives macOS restarts (crontab doesn't on modern macOS)
- Integrates with `launchd` logging
- Consistent with AgentMemory's proven pattern

### 6. Concurrency guard

The nightly refresh script uses a lockfile (`/tmp/knowledge-refresh.lock`). The post-merge hook uses debounce (no lockfile needed since it's per-repo).

## Script Flow: Nightly Refresh

```
1. Acquire lockfile (non-blocking, exit if held)
2. Start logging with timestamp
3. Discover repos:
   a. Find all dirs under ~/Developer with .gitnexus/ → GitNexus repos
   b. Find all dirs under ~/Developer with graphify-out/ → Graphify repos
4. For each repo:
   a. Check if git operations are safe (not in merge/rebase)
   b. Run gitnexus analyze --index-only (if GitNexus repo)
   c. Run graphify update . (if Graphify repo, main checkout only)
   d. Discover worktrees:
      - git worktree list --porcelain
      - For each worktree with .gitnexus/: run gitnexus analyze --index-only
   e. Record success/failure
5. Write summary to log
6. Release lockfile
```

## Script Flow: Post-Merge Hook

```
1. Check if merge target is main branch (exit if not)
2. Write current timestamp to /tmp/knowledge-postmerge-<repo-slug>.ts
3. Sleep 30 seconds (background, detached)
4. Read timestamp back — if changed, exit (newer merge will handle it)
5. Acquire per-repo lockfile (non-blocking)
6. Run gitnexus analyze . --index-only --default-branch main
7. Run graphify update . (from main checkout)
8. Log result
9. Release lockfile
```

## Files to Create/Modify

| File | Action | Purpose |
|---|---|---|
| `~/Developer/scripts/refresh-knowledge-indexes.sh` | CREATE | Main nightly refresh script |
| `~/Developer/scripts/knowledge-status.sh` | CREATE | Status check across all repos + worktrees |
| `~/Developer/scripts/install-post-merge-hook.sh` | CREATE | Install post-merge hook in indexed repos |
| `~/Library/LaunchAgents/com.developer.index-refresh.plist` | CREATE | Nightly LaunchAgent |
| `go-microservices/scripts/knowledge-tools.sh` | MODIFY | Extend install-hooks to include post-merge |
| `~/Developer/AGENTS.md` | MODIFY | Fix stale cron claims |
| `~/Developer/.claude/CLAUDE.md` | MODIFY | Update staleness warnings |
| `openspec/specs/refresh-gitnexus-index-groups/spec.md` | MODIFY | Add automation requirements |

## Logging

- Log directory: `~/Developer/.knowledge-refresh/`
- Log files:
  - `refresh.log` — nightly bulk refresh (rotated weekly, max 52)
  - `post-merge.log` — post-merge triggers (rotated weekly)
  - `worktree-refresh.log` — worktree-specific refreshes
- Format: `[ISO timestamp] [repo-name] [worktree|main] [tool] [status] [duration]`
- Example: `[2026-08-14T02:30:01Z] [agent-core] [main] [gitnexus] [success] [8.2s]`
- Example: `[2026-08-14T14:22:31Z] [go-microservices] [main] [gitnexus] [success] [12.3s]` (post-merge)

## Error Handling

- Individual repo failures don't abort the script
- Lockfile contention exits cleanly (no retry)
- Missing tools (gitnexus/graphify not installed) skip repos with a warning
- Stale worktrees (detached HEAD, old feature branches) are skipped
- Post-merge debounce prevents redundant refreshes during rapid merges
- Logs capture both stdout and stderr per repo
