# Design: Ecosystem Index Freshness Automation

## Official Tool Identity

| Tool | Source | Package | CLI | Pinned Version | Python | License |
|---|---|---|---|---|---|---|
| Graphify | [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | `graphifyy` (PyPI) | `graphify` | 0.9.42 | 3.12.13 | Apache-2.0 |
| GitNexus | npm | `gitnexus` | `gitnexus` | 1.6.9 | Node.js | PolyForm NC |

**No other provider is referenced.** The obsolete alternate-provider statement in `developer-code-intelligence` is corrected by a delta spec in this change.

## Architecture Overview

```
+-------------------+------------------+------------------------+
|  Layer 1          |  Layer 2         |  Layer 3               |
|  Post-Merge       |  Worktree-Aware  |  Nightly Bulk          |
|  Dispatcher       |  Refresh         |  Refresh               |
+-------------------+------------------+------------------------+
|  After local      |  Only indexed    |  02:30 AM daily        |
|  merge/pull       |  worktrees       |                        |
+-------------------+------------------+------------------------+
|  Main checkout    |  Per-worktree    |  All inventoried       |
|  of merged repo   |  (skip missing)  |  repos + worktrees     |
+-------------------+------------------+------------------------+
|  Workspace-       |  Official owner  |  Official              |
|  managed block    |  lock pattern    |  analyze --index-only  |
|  (dispatch only)  |                  |  + update .            |
+-------------------+------------------+------------------------+
```

## Official Graphify Commands

| Use Case | Command | Source |
|---|---|---|
| Routine incremental code refresh | `graphify update .` | `knowledge-tools.sh` line 892 |
| Bounded full code-only extraction | `graphify extract . --code-only` | `knowledge-tools.sh` line 404 |
| Real-time file watching | `graphify watch <path>` | Watch mode |
| Hook installation | `graphify hook install` | Installs post-commit + post-checkout |
| Status/diagnosis | `graphify hook status` | Check hook state |

**Key distinction:** `graphify update .` is the routine incremental command (re-extracts changed files, rebuilds graph). `graphify extract . --code-only` is the full bounded repair. Both use code-only AST parsing — no LLM, no network.

## Graphify 0.9.42 Features Integrated

- **Non-regular file resilience**: FIFOs, device files, and other non-regular files are skipped during extraction.
- **Same-length rewrite detection**: `graphify update` catches files rewritten to the same length within one mtime tick.
- **Deterministic provenance**: `built_at_commit` is stamped from the analyzed repository, not the shell cwd.
- **POSIX path canonicalization**: `source_file` paths are canonicalized to POSIX separators.
- **Cache corruption detection**: Corrupt semantic-cache entries are surfaced and re-extracted.

## Lock Design

### Semantics

```
acquire():
  1. mkdir $LOCK_DIR                    # atomic — fails if exists
  2. write PID, owner, timestamp        # metadata for diagnostics
  3. return success

release() via trap:
  1. rm -f $LOCK_DIR/owner
  2. rmdir $LOCK_DIR                    # best-effort

reclaim():
  1. read PID from lock
  2. kill -0 $PID 2>/dev/null           # PID alive?
  3. if alive: SKIP (never steal)
  4. if dead: reclaim the lock
```

**Never steal a live lock based on age.** A live process holding a lock is doing legitimate work. Reclaim only after PID liveness check proves the owner is dead.

### Lock identifier

Derived from canonical repository path, not basename. Prevents collisions between repos with the same name in different parents.

```bash
lock_id() {
  local canonical_root="$1"
  printf '%s' "$canonical_root" | shasum -a 256 | awk '{print $1}'
}
```

## Path Layout Convention

All tracked source lives under `openspec-store/scripts/knowledge-refresh/`. The installer copies/symlinks into `~/Developer/scripts/knowledge-refresh/`. All hooks, LaunchAgent, and documentation reference the installed paths.

```
openspec-store/scripts/knowledge-refresh/
  refresh-knowledge-indexes.sh
  knowledge-status.sh
  install-hooks.sh
  install-launchagent.sh
  knowledge-refresh-inventory.tsv
  knowledge-refresh-approval.sha256
  com.developer.index-refresh.plist.template

~/Developer/scripts/knowledge-refresh/          (installed copies)
~/Developer/.knowledge-refresh/                 (runtime state: logs, locks)
~/Library/LaunchAgents/com.developer.index-refresh.plist  (rendered)
```

## Part 1: Reviewed Repository Inventory

### File: `scripts/knowledge-refresh/knowledge-refresh-inventory.tsv`

```text
canonical_root<TAB>default_branch<TAB>gitnexus_enabled<TAB>graphify_enabled
```

Example:

```text
/Users/androidteam/Developer/agent-core	main	yes	yes
/Users/androidteam/Developer/go-microservices	main	yes	yes
```

### Requirements

- Canonical absolute paths only, resolved symlinks
- Under approved workspace roots (`~/Developer/`)
- One entry per Git common directory (deduplicates linked worktrees)
- Explicit default branch per repository

### Approval mechanism

The inventory file and a companion approval manifest (`knowledge-refresh-approval.sha256`) are both tracked. The approval manifest contains the SHA-256 of the normalized inventory that was explicitly approved.

```bash
# On explicit approval:
sha256sum "$INVENTORY_FILE" > "$APPROVAL_FILE"

# On every refresh run:
expected_digest=$(sha256sum "$INVENTORY_FILE" | awk '{print $1}')
approved_digest=$(cat "$APPROVAL_FILE" 2>/dev/null)
[ "$expected_digest" = "$approved_digest" ] || { echo "INVENTORY NOT APPROVED"; exit 1; }
```

The refresh script **fails closed** if:
- The approval manifest is missing
- The inventory digest differs from the approved digest
- Any inventory entry fails validation

Discovery may report candidates but must not refresh unlisted repositories.

### Path containment validation

```bash
validate_inventory_path() {
  local path="$1"
  local canonical
  canonical="$(realpath "$path" 2>/dev/null)" || return 1
  case "$canonical" in
    "$HOME/Developer/"*) ;;
    *) return 1 ;;  # outside approved root
  esac
  [ -d "$canonical/.git" ] || [ -f "$canonical/.git" ] || return 1
}
```

## Part 2: Central Refresh Script

### File: `scripts/knowledge-refresh/refresh-knowledge-indexes.sh`

Entry-point script. Reads inventory + approval, validates entries, checks dirty/merge state, coordinates locks, runs official refresh commands, verifies post-run revision equality.

### macOS-compatible timeout

macOS does not ship GNU `timeout`. Use a PID watchdog instead:

```bash
run_with_timeout() {
  local timeout_secs="$1"; shift
  "$@" &
  local child_pid=$!
  (
    sleep "$timeout_secs"
    kill -TERM "$child_pid" 2>/dev/null
    sleep 2
    kill -KILL "$child_pid" 2>/dev/null
  ) &
  local watchdog_pid=$!
  wait "$child_pid" 2>/dev/null
  local rc=$?
  kill "$watchdog_pid" 2>/dev/null
  wait "$watchdog_pid" 2>/dev/null
  return $rc
}
```

This terminates the full child process group. Lock release is handled by `trap` on exit.

### Dirty-tree guard

```bash
is_repo_dirty() {
  local repo_root="$1"
  local dirty
  dirty="$(git -C "$repo_root" status --porcelain --untracked-files=normal 2>/dev/null)"
  [ -n "$dirty" ]
}
```

### Merge/rebase-state guard

```bash
is_repo_in_merge_state() {
  local repo_root="$1"
  local git_dir
  git_dir="$(git -C "$repo_root" rev-parse --git-dir 2>/dev/null)"
  [ -d "$git_dir/rebase-merge" ] || [ -d "$git_dir/rebase-apply" ] || \
  [ -f "$git_dir/MERGE_HEAD" ] || [ -f "$git_dir/CHERRY_PICK_HEAD" ]
}
```

### Per-repository timeout

Each repository refresh is bounded to 300 seconds (5 minutes) via the PID watchdog above.

### Overall run timeout

The entire nightly run is bounded to 7200 seconds (2 hours):

```bash
OVERALL_TIMEOUT=7200
start_time=$(date +%s)
# ... in loop:
elapsed=$(( $(date +%s) - start_time ))
[ "$elapsed" -ge "$OVERALL_TIMEOUT" ] && { log "overall timeout reached"; break; }
```

### Post-run revision verification

After GitNexus completes, verify the indexed revision equals the target. If HEAD changed during execution, report `superseded`.

### Watcher detection

The active watcher resolves its authoritative graph root from:

1. The explicit CLI argument (`graphify watch <path>`), or
2. The process CWD when no path argument is present.

```bash
is_watcher_active() {
  local canonical_root="$1"
  # Find the watcher PID
  local watcher_pid
  watcher_pid="$(pgrep -f 'graphify watch' | head -1)" || return 1
  # Check if the watcher has a path argument matching this root
  local ps_args
  ps_args="$(ps -p "$watcher_pid" -o args= 2>/dev/null)" || return 1
  # Extract the last argument after 'watch'
  local watch_target
  watch_target="$(echo "$ps_args" | sed -n 's/.*graphify watch \([^ ]*\).*/\1/p')"
  if [ -n "$watch_target" ]; then
    # Explicit argument: match exactly
    [ "$(realpath "$watch_target" 2>/dev/null)" = "$canonical_root" ]
  else
    # No argument: resolve CWD
    local watcher_cwd
    watcher_cwd="$(lsof -a -p "$watcher_pid" -d cwd 2>/dev/null | awk 'NR==2{print $NF}')"
    [ -n "$watcher_cwd" ] && [ "$(realpath "$watcher_cwd" 2>/dev/null)" = "$canonical_root" ]
  fi
}
```

Skip scheduled Graphify only when the watcher's resolved graph root **exactly matches** the target repository's canonical root — not merely when it is an ancestor.

### Refresh commands

```bash
# GitNexus: official bounded recovery
gitnexus analyze . --index-only --default-branch "$expected_branch"

# Graphify: official incremental
graphify update .

# Graphify: bounded full code-only repair (when update fails)
graphify extract . --code-only
```

### Transactional Graphify recovery

Before running `graphify extract . --code-only`, snapshot the complete usable output set:

```bash
snapshot_graph_outputs() {
  local repo_root="$1"
  local snapshot_dir="$2"
  mkdir -p "$snapshot_dir"
  for f in graph.json manifest.json .graphify_analysis.json GRAPH_REPORT.md; do
    [ -f "$repo_root/graphify-out/$f" ] && \
      cp "$repo_root/graphify-out/$f" "$snapshot_dir/$f"
  done
}

restore_graph_snapshot() {
  local repo_root="$1"
  local snapshot_dir="$2"
  for f in "$snapshot_dir"/*; do
    [ -f "$f" ] && cp "$f" "$repo_root/graphify-out/$(basename "$f")"
  done
}
```

After extraction, validate the new `graph.json` parses. If invalid or missing, restore from snapshot. Use temporary-directory generation plus atomic replacement where the CLI permits it.

### Status values

`success`, `fresh_noop`, `skipped_dirty`, `skipped_merge_state`, `skipped_uninitialized`, `provider_missing`, `lock_busy`, `watcher_active`, `timeout`, `failed`, `superseded`

## Part 3: Post-Merge Dispatcher

### Design

A workspace-managed block in each repo's `.git/hooks/post-merge` dispatches asynchronously to the central script. The hook itself never acquires a lock.

**Critical hook finding:** Official Graphify 0.9.42's `graphify hook install` installs `post-commit` and `post-checkout`, but NOT `post-merge`. The existing 18 `post-merge` hooks were installed by a previous workspace procedure. The workspace dispatcher adds a separate managed block that preserves Graphify-owned marker blocks byte-for-byte.

### Hook structure

The hook is a pure dispatcher. It does not load the inventory or validate branches — that responsibility belongs to the central script.

```bash
# knowledge-gitnexus-post-merge-start
# Managed by workspace refresh system — do not edit between markers.
knowledge_gitnexus_dispatch() {
  nohup "$HOME/Developer/scripts/knowledge-refresh/refresh-knowledge-indexes.sh" \
    --repo "$(git rev-parse --show-toplevel)" \
    --trigger post-merge \
    >>"$HOME/Developer/.knowledge-refresh/post-merge.log" 2>&1 </dev/null &
}
knowledge_gitnexus_dispatch
# knowledge-gitnexus-post-merge-end
```

The central script loads the inventory, validates the configured branch, checks dirty state, acquires locks, and decides whether to refresh. The hook only dispatches.

### SLA clarification

The `post-merge` hook fires on **local merges and merge-based pulls**, not on remote PR merges. When a developer runs `git pull --rebase`, the hook does NOT fire. There is no remote trigger mechanism.

## Part 4: Worktree-Aware Refresh

### Critical finding

Most worktrees do NOT have `.gitnexus/` or `graphify-out/` state. The system refreshes only worktrees that already have the relevant index state. Others are reported as `UNINITIALIZED`.

### Worktree filtering

- Skip detached HEAD worktrees
- Skip worktrees under `.claude/worktrees/` (ephemeral)
- Skip worktrees older than 30 days on feature branches
- Deduplicate by canonical path and Git common directory

## Part 5: LaunchAgent

### Template: `scripts/knowledge-refresh/com.developer.index-refresh.plist.template`

Uses `@HOME@` placeholders, expanded by `install-launchagent.sh`.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.developer.index-refresh</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>@HOME@/Developer/scripts/knowledge-refresh/refresh-knowledge-indexes.sh</string>
    </array>
    <key>WorkingDirectory</key>
    <string>@HOME@/Developer</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>2</integer>
        <key>Minute</key>
        <integer>30</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>@HOME@/Developer/.knowledge-refresh/launchd-stdout.log</string>
    <key>StandardErrorPath</key>
    <string>@HOME@/Developer/.knowledge-refresh/launchd-stderr.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>@HOME@/.npm-global/bin:@HOME@/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
        <key>HOME</key>
        <string>@HOME@</string>
    </dict>
</dict>
</plist>
```

The installer renders `@HOME@` to the actual home directory and validates with `plutil -lint`.

### Installation

```bash
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.developer.index-refresh.plist
```

## Part 6: Status Command

### File: `scripts/knowledge-refresh/knowledge-status.sh`

### Output format

```
Repository              Tool      Status       Last Refresh    HEAD
agent-core             GitNexus  STALE        2026-08-13      b9dde69
agent-core             Graphify  FRESH        2026-08-14      b9dde69
agent-core             Dirty     2 files      -               -
go-microservices       GitNexus  STALE        2026-08-10      d44b677
go-microservices       Graphify  WATCHER      -               d44b677
mcp-router             GitNexus  FRESH        2026-08-10      bad6ff5
mcp-router             Graphify  FRESH        2026-08-10      bad6ff5
go-microservices (wt)  GitNexus  UNINITIALIZED -              -
```

### Machine-readable output

`knowledge-status.sh --json` outputs structured JSON.

## Files Created/Modified

| File | Action | Purpose |
|---|---|---|
| `openspec-store/scripts/knowledge-refresh/*` | CREATE | Tracked source scripts |
| `~/Developer/scripts/knowledge-refresh/*` | INSTALL | Installed copies |
| `~/Library/LaunchAgents/com.developer.index-refresh.plist` | CREATE | Rendered LaunchAgent |
| `~/Developer/AGENTS.md` | MODIFY | Fix stale cron claims |
| `~/Developer/.claude/CLAUDE.md` | MODIFY | Update staleness warnings |
| `openspec/specs/workspace-index-freshness/spec.md` | CREATE | New capability |
| `openspec/specs/developer-code-intelligence/spec.md` | MODIFY | Correct Graphify identity |
| `openspec/specs/gitnexus-stable-contract/spec.md` | MODIFY | Authorize scheduled refresh |

## Error Handling

- Individual repo failures don't abort the script
- Owner lock contention yields gracefully (no forced override, no age-based steal)
- Missing tools skip repos with `provider_missing` status
- Dirty repos skipped with `skipped_dirty`
- Merge/rebase state repos skipped with `skipped_merge_state`
- Uninitialized worktrees reported as `skipped_uninitialized`
- Watcher-active repos skipped for Graphify refresh (exact root match only)
- Post-run revision verification catches concurrent modifications (`superseded`)
- Per-repository timeout (5 min) via PID watchdog prevents hung CLI
- Overall run timeout (2 hours) ensures completion before next day
- `trap`-based cleanup for lock files and temporary state
- Transactional Graphify recovery: snapshot → extract → validate → restore on failure
- Bounded log rotation (last 1000 lines per log file)
- Inventory approval enforcement: fails closed on digest mismatch or missing approval
- All status values are explicit and machine-readable
