# Design: Ecosystem Index Freshness Automation

## Architecture Overview

Three complementary mechanisms ensure indexes stay fresh for coding agents, built on top of the official Graphify and GitNexus patterns already established in `go-microservices/scripts/knowledge-tools.sh`:

```
┌─────────────────┬──────────────────┬────────────────────────┐
│  Layer 1        │  Layer 2         │  Layer 3               │
│  Post-Merge     │  Worktree-Aware  │  Nightly Bulk          │
│  Trigger        │  Refresh         │  Refresh               │
├─────────────────┼──────────────────┼────────────────────────┤
│  After local    │  On worktree     │  02:30 AM daily        │
│  merge/pull     │  creation        │                        │
├─────────────────┼──────────────────┼────────────────────────┤
│  Main checkout  │  Each worktree   │  All repos + all       │
│  of merged repo │  independently   │  worktrees             │
├─────────────────┼──────────────────┼────────────────────────┤
│  Official       │  Official owner  │  Official              │
│  post-merge     │  lock pattern    │  analyze --index-only  │
│  hook pattern   │  + COMMONDIR     │  + extract --code-only │
└─────────────────┴──────────────────┴────────────────────────┘
```

## Official Patterns (from knowledge-tools.sh)

This design reuses the established patterns from `go-microservices/scripts/knowledge-tools.sh` rather than inventing new ones:

### Graphify owner lock mechanism

```bash
# Official pattern: directory-based lock with owner tracking
graphify_lock_dir() {
  local name="$1"
  printf '%s/locks/graphify-%s.lock\n' "$STATE_DIR" "$name"
}

acquire_graphify_owner() {
  local root="$1" name="$2" owner="$3"
  local lock_dir
  lock_dir="$(graphify_lock_dir "$name")"
  mkdir -p "${STATE_DIR}/locks"
  # Check for hook-owned rebuild lock
  if [[ -e "${root}/graphify-out/.rebuild.lock" ]]; then
    warn "Graphify ${name} is already rebuilding under the hook-owned lock"
    return 1
  fi
  if ! mkdir "$lock_dir" 2>/dev/null; then
    # Lock held by another process
    local active_owner="unknown"
    [[ -f "${lock_dir}/owner" ]] && active_owner="$(head -1 "${lock_dir}/owner")"
    warn "Graphify ${name} refresh owner is ${active_owner}; ${owner} cannot start"
    return 1
  fi
  printf '%s\n' "$owner" >"${lock_dir}/owner"
}
```

### GitNexus workspace lock

```bash
# Official pattern: directory-based lock with PID tracking
gitnexus_lock_dir() {
  printf '%s/locks/gitnexus-workspace.lock\n' "$STATE_DIR"
}

acquire_gitnexus_owner() {
  local owner="$1"
  local lock_dir
  lock_dir="$(gitnexus_lock_dir)"
  mkdir -p "${STATE_DIR}/locks"
  if mkdir "$lock_dir" 2>/dev/null; then
    printf '%s\t%s\n' "$$" "$owner" >"${lock_dir}/owner"
    return 0
  fi
  # Stale lock detection: check if owner PID is still alive
  local active_pid="" active_owner="unknown"
  [[ -f "${lock_dir}/owner" ]] && read -r active_pid active_owner <"${lock_dir}/owner"
  if [[ "$active_pid" =~ ^[0-9]+$ ]] && ! kill -0 "$active_pid" 2>/dev/null; then
    rm -f "${lock_dir}/owner" && rmdir "$lock_dir" 2>/dev/null
    if mkdir "$lock_dir" 2>/dev/null; then
      printf '%s\t%s\n' "$$" "$owner" >"${lock_dir}/owner"
      return 0
    fi
  fi
  warn "GitNexus workspace owner is ${active_owner}; ${owner} cannot start"
  return 1
}
```

### Graphify hook coordination

The existing Graphify post-commit hook checks for the owner lock and yields:

```bash
# From .git/hooks/post-commit
_KNOWLEDGE_GRAPHIFY_OWNER=/Users/androidteam/Developer/go-microservices/.knowledge-state/locks/graphify-microservices.lock
[ -d "$_KNOWLEDGE_GRAPHIFY_OWNER" ] && exit 0  # yield to explicit refresh
```

### GitNexus authorized recovery pattern

From `gitnexus-stable-contract`:

> **WHEN** an index is stale and the user has contemporaneously authorized recovery
> **THEN** an operator MAY run `analyze --index-only --default-branch main`
> **AND** the operation SHALL reject `--force`, embeddings, PDG, skills/context injection

## Part 1: Extend Existing Post-Merge Hook for GitNexus

### Problem

When a PR merges to main, agents working on subsequent tasks get stale GitNexus index results. Graphify is already handled by the existing post-merge hook, but GitNexus has no post-merge trigger.

### Critical Finding

**The Graphify post-merge hook already exists in all 18 repos.** It:
- Skips during rebase/merge/cherry-pick (advisory, doesn't block)
- Checks for graphify state (`.graphify/graph.json` or `graphify-out/graph.json`)
- Marks graph as stale (writes `.graphify/needs_update`)
- Rebuilds code-only graph in background (`graphify hook-rebuild`)

**We don't need to create a new post-merge hook.** We extend the existing one.

### Design

Extend the existing `graphify-post-merge-hook-start` / `graphify-post-merge-hook-end` block to also trigger GitNexus refresh:

```bash
# After graphify_rebuild_code
# Add GitNexus refresh
gitnexus_refresh_after_merge() {
  # Check if GitNexus index exists
  [ -d ".gitnexus" ] || return 0
  
  # Acquire workspace lock (yields if another refresh is running)
  local lock_dir="$HOME/Developer/go-microservices/.knowledge-state/locks/gitnexus-workspace.lock"
  mkdir -p "$(dirname "$lock_dir")"
  if ! mkdir "$lock_dir" 2>/dev/null; then
    # Another refresh is running — yield
    return 0
  fi
  printf '%s\t%s\n' "$$" "post-merge" >"${lock_dir}/owner"
  
  # Run refresh in background (non-blocking)
  nohup gitnexus analyze . --index-only --default-branch main \
    >>"$HOME/.cache/gitnexus-postmerge.log" 2>&1 &
  
  # Release lock after a delay (let the background process start)
  (sleep 5 && rm -f "${lock_dir}/owner" && rmdir "$lock_dir" 2>/dev/null) &
}
```

### Hook installation

The existing hook is installed by `graphify hook install` and uses the marked block pattern. We extend the block content rather than adding a new block:

```bash
# graphify-post-merge-hook-start
# ... existing Graphify content ...
# NEW: gitnexus_refresh_after_merge
# graphify-post-merge-hook-end
```

The extension is idempotent — re-running `graphify hook install` preserves the entire block.

### Debounce

The existing hook doesn't have debounce because Graphify handles it via the `.rebuild.lock` mechanism. For GitNexus, the workspace lock provides debounce — if a previous refresh is running, the new one yields.

### SLA clarification

The post-merge hook fires on **local merges and pulls**, not on remote PR merges. When a developer runs `git merge` or `git pull`, the hook fires immediately. The "30s after PR merge" framing is incorrect — there is no remote trigger mechanism in this design.

## Part 2: Worktree-Aware Refresh

### Problem

Git worktrees are used extensively (7 active across 5 repos). Each worktree may have its own `.gitnexus/` and potentially its own `graphify-out/`.

### Critical Finding: Worktree Graphify State

Worktrees do NOT always share the main checkout's graphify-out:

| Repo | Worktree | Has graphify-out? | Has graph.json? |
|---|---|---|---|
| go-microservices | centralize-mcp-knowledge-servers | NO | NO |
| tdt-core | tdt-core-completion-goose-luna | YES (dir exists) | NO (empty) |
| agent-docs-sync | agent-docs-sync-completion-goose-luna | YES (dir exists) | NO (empty) |

**The assumption that worktrees always share the main checkout's graph is WRONG.** Worktrees CAN have their own graphify-out directories, but they may be empty or stale.

### Design

#### GitNexus worktree indexing

Each worktree already has its own `.gitnexus/` with a separate index. The nightly refresh discovers worktrees and refreshes each one using the official `analyze --index-only` pattern:

```bash
discover_worktrees() {
  local repo_root="$1"
  git -C "$repo_root" worktree list --porcelain | \
    awk '/^worktree / { print $2 }' | \
    grep -v "^${repo_root}$"  # exclude main checkout
}

# For each worktree with .gitnexus/
for wt in $(discover_worktrees "$repo_root"); do
  if [[ -d "$wt/.gitnexus" ]]; then
    (cd "$wt" && gitnexus analyze . --index-only --default-branch main)
  fi
done
```

GitNexus handles worktree isolation natively — each worktree's index is independent.

#### Graphify worktree awareness

Worktrees may or may not have their own graphify state. The strategy:

1. **If worktree has `graphify-out/` or `.graphify/`**: Refresh it independently
2. **If worktree has NO graphify state**: Use main checkout's graph (shared)
3. **Main checkout always gets refreshed** (ensures fresh graph for all worktrees)

```bash
for wt in $(discover_worktrees "$repo_root"); do
  if [[ -d "$wt/graphify-out" ]] || [[ -d "$wt/.graphify" ]]; then
    # Worktree has its own graph — refresh independently
    (cd "$wt" && GRAPHIFY_VIZ_NODE_LIMIT=0 graphify extract . --code-only)
  fi
  # else: worktree uses main checkout's graph (already refreshed)
done
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

LaunchAgent at 02:30 AM running the refresh script. Uses the official owner lock mechanism to coordinate with any running watch sessions or hooks.

```
~/Library/LaunchAgents/com.developer.index-refresh.plist
  └── runs: ~/Developer/scripts/refresh-knowledge-indexes.sh
        ├── discovers repos with .gitnexus/ or graphify-out/
        ├── validates each is a git repository (.git marker)
        ├── discovers worktrees for each repo
        ├── for each repo + worktree:
        │   ├── acquire_gitnexus_owner (yields if workspace lock held)
        │   ├── gitnexus analyze . --index-only --default-branch main
        │   ├── release_gitnexus_owner
        │   ├── acquire_graphify_owner (yields if watch/hook running)
        │   ├── graphify extract . --code-only (official foreground pattern)
        │   ├── release_graphify_owner
        │   └── (worktrees: same pattern independently)
        └── writes: ~/Developer/.knowledge-refresh/refresh.log
```

## Part 4: Status Command

### Problem

No visibility into index freshness across the workspace.

### Design

A status command that reports freshness for all repos and worktrees:

```
~/Developer/scripts/knowledge-status.sh
  ├── discovers repos with .gitnexus/ or graphify-out/
  ├── for each repo:
  │   ├── GitNexus: compare meta.json lastCommit with current HEAD
  │   ├── Graphify: compare graph.json mtime with last commit mtime
  │   └── Report: FRESH / STALE / UNKNOWN
  ├── discovers worktrees for each repo
  ├── for each worktree:
  │   ├── Same freshness checks
  │   └── Report status
  └── outputs formatted table
```

### Output format

```
Repository              Tool      Status    Last Refresh    HEAD
────────────────────── ───────── ───────── ─────────────── ────────
agent-core             GitNexus  STALE     2026-08-13      24d0280
agent-core             Graphify  FRESH     2026-08-14      24d0280
agent-core (worktree)  GitNexus  UNKNOWN   never           -
go-microservices       GitNexus  STALE     2026-08-10      d44b677
go-microservices       Graphify  STALE     2026-08-10      d44b677
mcp-router             GitNexus  FRESH     2026-08-10      bad6ff5
mcp-router             Graphify  FRESH     2026-08-10      bad6ff5
```

## Key Design Decisions

### 1. Three layers, not one

| Layer | Latency | Coverage | Cost |
|---|---|---|---|
| Post-merge trigger | Immediate (after local merge/pull) | Merged repos | Low (incremental) |
| Worktree-aware | On worktree creation | New worktrees | Low (one-shot) |
| Nightly bulk | Hours (02:30 AM) | Everything | Low (incremental) |

### 2. Official commands, not custom ones

| Tool | Official Command | Why |
|---|---|---|
| GitNexus refresh | `gitnexus analyze . --index-only --default-branch main` | Authorized in `gitnexus-stable-contract` for stale-index recovery |
| Graphify foreground refresh | `graphify extract . --code-only` | Official pattern from `knowledge-tools.sh` line 404 |
| Graphify hook refresh | `graphify update .` | Official pattern from post-commit hook |

**NOT** `graphify update .` for foreground refresh — the official `knowledge-tools.sh` uses `graphify extract . --code-only` for foreground operations (line 404) and reserves `graphify update .` for the hook (line 892).

### 3. Official owner lock mechanism

Reuses the established directory-based lock pattern from `knowledge-tools.sh`:
- `acquire_graphify_owner` / `release_graphify_owner`
- `acquire_gitnexus_owner` / `release_gitnexus_owner`
- Checks for `.rebuild.lock` (hook-owned rebuild)
- Stale lock detection via PID liveness check

### 4. Watcher lock starvation mitigation

The Graphify watcher (`graphify watch`) can hold the owner lock indefinitely. To prevent starvation:

- **Lock age check**: If lock is older than 30 minutes, log warning and proceed with bounded refresh
- **Bounded refresh**: Complete within 5 minutes and release lock
- **Freshness policy**: Nightly refresh is the safety net — if watcher starves the lock, the next nightly refresh catches up

### 5. Valid repository marker

The discovery process requires a valid git repository marker (`.git` directory or file) to prevent:
- Accidental indexing of workspace root (`~/Developer/`)
- Indexing of non-repository directories that happen to have `.gitnexus/` or `graphify-out/`

### 6. Hook coordination, not hook replacement

The post-merge hook coordinates with existing hooks:
- Checks `_KNOWLEDGE_GRAPHIFY_OWNER` lock before running
- Uses the same marked block pattern for installation
- Yields to running `graphify watch` sessions
- Doesn't duplicate the Graphify post-commit hook's work

### 7. `--index-only` for GitNexus (no embeddings/PDG)

Embeddings and PDG are expensive and should remain on-demand. The refresh uses `--index-only` which:
- Updates the symbol graph and FTS index
- Preserves existing embeddings (no re-embedding)
- Skips PDG analysis
- Matches the bounded recovery authorized in `gitnexus-stable-contract`

### 8. LaunchAgent over crontab

- LaunchAgent survives macOS restarts (crontab doesn't on modern macOS)
- Integrates with `launchd` logging
- Consistent with AgentMemory's proven pattern

## Files to Create/Modify

| File | Action | Purpose |
|---|---|---|
| `~/Developer/scripts/refresh-knowledge-indexes.sh` | CREATE | Main nightly refresh script (uses official owner lock) |
| `~/Developer/scripts/knowledge-status.sh` | CREATE | Status check across all repos + worktrees |
| `go-microservices/scripts/knowledge-tools.sh` | MODIFY | Extend post-merge hook to include GitNexus refresh |
| `~/Library/LaunchAgents/com.developer.index-refresh.plist` | CREATE | Nightly LaunchAgent |
| `~/Developer/AGENTS.md` | MODIFY | Fix stale cron claims |
| `~/Developer/CLAUDE.md` | MODIFY | Update staleness warnings |
| `openspec/specs/refresh-gitnexus-index-groups/spec.md` | EXTEND | Add automation requirements (extend, not replace) |

## Error Handling

- Individual repo failures don't abort the script
- Owner lock contention yields gracefully (no forced override)
- Missing tools (gitnexus/graphify not installed) skip repos with a warning
- Stale worktrees (detached HEAD, old feature branches) are skipped
- Watcher lock starvation mitigated with 30-minute age check
- Graphify output preservation: backup `graph.json` before refresh, restore on failure
- Logs capture both stdout and stderr per repo
