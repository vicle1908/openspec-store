# Design: Ecosystem Index Freshness Automation

## Architecture Overview

Three complementary mechanisms ensure indexes stay fresh for coding agents, built on top of the official Graphify and GitNexus patterns already established in `go-microservices/scripts/knowledge-tools.sh`:

```
┌─────────────────┬──────────────────┬────────────────────────┐
│  Layer 1        │  Layer 2         │  Layer 3               │
│  Post-Merge     │  Worktree-Aware  │  Nightly Bulk          │
│  Trigger        │  Refresh         │  Refresh               │
├─────────────────┼──────────────────┼────────────────────────┤
│  30s after      │  On worktree     │  02:30 AM daily        │
│  merge to main  │  creation        │                        │
├─────────────────┼──────────────────┼────────────────────────┤
│  Main checkout  │  Main + new      │  All repos + all       │
│  of merged repo │  worktree        │  worktrees             │
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
# Official pattern: directory-based lock
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

## Part 1: Post-Merge Trigger

### Problem

When a PR merges to main, agents working on subsequent tasks get stale index results.

### Design

A **post-merge hook** installed in each indexed repo's `.git/hooks/post-merge`. Uses the official owner lock mechanism to coordinate with the existing Graphify post-commit hook and any running `graphify watch` sessions.

```
.git/hooks/post-merge
  ├── Detect if merge target is main branch
  ├── Acquire graphify owner lock (yields if watch/refresh running)
  ├── Debounce: write timestamp to /tmp/knowledge-postmerge-<repo>.ts
  ├── Sleep 30s (detached background)
  ├── Check if timestamp still matches (no newer merge)
  ├── Run: gitnexus analyze . --index-only --default-branch main
  ├── Run: graphify extract . --code-only (official foreground pattern)
  ├── Release owner lock
  └── Log result
```

### Hook installation

Extend `knowledge-tools.sh install-hooks` to include post-merge alongside the existing Graphify post-commit and post-checkout hooks. Uses the same marked block pattern:

```bash
# knowledge-postmerge-start
# ... hook content ...
# knowledge-postmerge-end
```

### Debounce logic

```bash
_REPO_SLUG=$(echo "$REPO_ROOT" | tr '/' '_' | tr '.' '_')
_TS_FILE="/tmp/knowledge-postmerge-${_REPO_SLUG}.ts"
echo "$(date +%s)" > "$_TS_FILE"
sleep 30
# Check if a newer merge happened during the sleep
_CURRENT_TS=$(cat "$_TS_FILE" 2>/dev/null || echo 0)
_STORED_TS=$(echo "$_CURRENT_TS" | head -1)
if [ "$(cat "$_TS_FILE")" != "$_STORED_TS" ]; then
  exit 0  # newer merge will handle it
fi
```

## Part 2: Worktree-Aware Refresh

### Problem

Git worktrees are used extensively. Each worktree:
- Has its own `.gitnexus/` directory (GitNexus indexes per-worktree correctly)
- Shares the main checkout's `graphify-out/` (Graphify graph is shared)
- The existing Graphify hook explicitly skips worktrees (COMMONDIR check)

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

Worktrees share the main checkout's `graphify-out/`. The official pattern (from the Graphify post-commit hook) is:

1. **Hook-owned refresh** runs from main checkout → refreshes shared graph
2. **Worktree creation** triggers post-checkout hook → refreshes main checkout's graph
3. **Nightly refresh** uses owner lock mechanism to coordinate with hooks

The COMMONDIR check in the existing hook ensures worktrees don't run Graphify refreshes:

```bash
_GFY_GITDIR=$(cd "$(git rev-parse --git-dir 2>/dev/null)" 2>/dev/null && pwd)
_GFY_COMMONDIR=$(cd "$(git rev-parse --git-common-dir 2>/dev/null)" 2>/dev/null && pwd)
if [ -n "$_GFY_COMMONDIR" ] && [ "$_GFY_GITDIR" != "$_GFY_COMMONDIR" ]; then
    exit 0  # skip worktrees
fi
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
        ├── discovers worktrees for each repo
        ├── for each repo + worktree:
        │   ├── acquire_gitnexus_owner (yields if workspace lock held)
        │   ├── gitnexus analyze . --index-only --default-branch main
        │   ├── release_gitnexus_owner
        │   ├── acquire_graphify_owner (yields if watch/hook running)
        │   ├── graphify extract . --code-only (official foreground pattern)
        │   ├── release_graphify_owner
        │   └── (worktrees: gitnexus analyze --index-only only)
        └── writes: ~/Developer/.knowledge-refresh/refresh.log
```

## Key Design Decisions

### 1. Three layers, not one

| Layer | Latency | Coverage | Cost |
|---|---|---|---|
| Post-merge trigger | 30s after merge | Merged repos | Low (incremental) |
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

### 4. Hook coordination, not hook replacement

The post-merge hook coordinates with existing hooks:
- Checks `_KNOWLEDGE_GRAPHIFY_OWNER` lock before running
- Uses the same marked block pattern for installation
- Yields to running `graphify watch` sessions
- Doesn't duplicate the Graphify post-commit hook's work

### 5. `--index-only` for GitNexus (no embeddings/PDG)

Embeddings and PDG are expensive and should remain on-demand. The refresh uses `--index-only` which:
- Updates the symbol graph and FTS index
- Preserves existing embeddings (no re-embedding)
- Skips PDG analysis
- Matches the bounded recovery authorized in `gitnexus-stable-contract`

### 6. LaunchAgent over crontab

- LaunchAgent survives macOS restarts (crontab doesn't on modern macOS)
- Integrates with `launchd` logging
- Consistent with AgentMemory's proven pattern

## Files to Create/Modify

| File | Action | Purpose |
|---|---|---|
| `~/Developer/scripts/refresh-knowledge-indexes.sh` | CREATE | Main nightly refresh script (uses official owner lock) |
| `~/Developer/scripts/knowledge-status.sh` | CREATE | Status check across all repos + worktrees |
| `~/Developer/scripts/install-post-merge-hook.sh` | CREATE | Install post-merge hook in indexed repos |
| `~/Library/LaunchAgents/com.developer.index-refresh.plist` | CREATE | Nightly LaunchAgent |
| `go-microservices/scripts/knowledge-tools.sh` | MODIFY | Extend install-hooks to include post-merge |
| `~/Developer/AGENTS.md` | MODIFY | Fix stale cron claims |
| `~/Developer/.claude/CLAUDE.md` | MODIFY | Update staleness warnings |
| `openspec/specs/refresh-gitnexus-index-groups/spec.md` | MODIFY | Add automation requirements |

## Error Handling

- Individual repo failures don't abort the script
- Owner lock contention yields gracefully (no forced override)
- Missing tools (gitnexus/graphify not installed) skip repos with a warning
- Stale worktrees (detached HEAD, old feature branches) are skipped
- Post-merge debounce prevents redundant refreshes during rapid merges
- Graphify output preservation: backup `graph.json` before refresh, restore on failure
- Logs capture both stdout and stderr per repo
