# Design: Ecosystem Index Freshness Automation

## Architecture

Follows the AgentMemory pattern: LaunchAgent daemon → periodic script → per-repo operations → logged output.

```
~/Library/LaunchAgents/com.developer.index-refresh.plist
  └── runs: ~/Developer/scripts/refresh-knowledge-indexes.sh
        ├── discovers repos with .gitnexus/ or graphify-out/
        ├── for each repo:
        │   ├── gitnexus analyze . --index-only --default-branch main
        │   └── graphify update .  (AST-only, no API cost)
        └── writes: ~/Developer/.knowledge-refresh/refresh.log
```

## Key Design Decisions

### 1. Discovery-based, not hardcoded repo list

The script discovers repos by checking for `.gitnexus/` or `graphify-out/` directories. This means:
- No hardcoded list to maintain
- New repos get included automatically when indexed for the first time
- Removed repos are silently skipped

### 2. `--index-only` for GitNexus (no embeddings/PDG)

Embeddings and PDG are expensive and should remain on-demand. The nightly refresh uses `--index-only` which:
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

### 4. LaunchAgent over crontab

- LaunchAgent survives macOS restarts (crontab doesn't on modern macOS)
- Integrates with `launchd` logging
- Can use `KeepAlive` for crash recovery
- Consistent with AgentMemory's pattern

### 5. Concurrency guard

The script uses a lockfile (`/tmp/knowledge-refresh.lock`) to prevent overlapping runs. If a previous run is still active, the new run exits cleanly.

## Script Flow

```
1. Acquire lockfile (non-blocking, exit if held)
2. Start logging with timestamp
3. Discover repos:
   a. Find all dirs under ~/Developer with .gitnexus/ → GitNexus repos
   b. Find all dirs under ~/Developer with graphify-out/ → Graphify repos
4. For each repo:
   a. Check if git/graph operations are safe (not in merge/rebase)
   b. Run gitnexus analyze --index-only (if GitNexus repo)
   c. Run graphify update . (if Graphify repo)
   d. Record success/failure
5. Write summary to log
6. Release lockfile
```

## Files to Create/Modify

| File | Action | Purpose |
|---|---|---|
| `~/Developer/scripts/refresh-knowledge-indexes.sh` | CREATE | Main refresh script |
| `~/Developer/scripts/knowledge-status.sh` | CREATE | Status check across all repos |
| `~/Library/LaunchAgents/com.developer.index-refresh.plist` | CREATE | Nightly LaunchAgent |
| `~/Developer/AGENTS.md` | MODIFY | Fix stale cron claims |
| `~/Developer/.claude/CLAUDE.md` | MODIFY | Update staleness warnings |
| `openspec/specs/refresh-gitnexus-index-groups/spec.md` | MODIFY | Add automation requirements |

## Logging

- Log directory: `~/Developer/.knowledge-refresh/`
- Log file: `refresh.log` (rotated weekly, max 52 files)
- Format: `[ISO timestamp] [repo-name] [tool] [status] [duration]`
- Example: `[2026-08-14T02:30:01Z] [go-microservices] [gitnexus] [success] [12.3s]`

## Error Handling

- Individual repo failures don't abort the script
- Lockfile contention exits cleanly (no retry)
- Missing tools (gitnexus/graphify not installed) skip repos with a warning
- Logs capture both stdout and stderr per repo
