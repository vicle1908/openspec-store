# Cleanup Recommendations — Owner-Native Only

**Audit date:** 2026-09-05
**Rule:** All suggestions use each tool's own cleanup mechanism. No manual deletion.

---

## High-Value Targets (>500MB each)

### 1. codex-runtimes — 1.9G
- **Owner tool:** Codex CLI
- **Cleanup command:** `codex cache clean` (or check Codex docs for cache eviction)
- **Risk:** Low — runtime binaries are re-downloaded on demand
- **Last modified:** 2026-09-05 (active)

### 2. Orca codex-runtime-home — 962M
- **Owner tool:** Orca
- **Cleanup command:** Orca's internal cache management (check Orca docs for cache cleanup)
- **Risk:** Low — runtime home is rebuildable
- **Last modified:** 2026-09-05 (active)

### 3. UV cache — 923M
- **Owner tool:** `uv`
- **Cleanup command:** `uv cache clean`
- **Risk:** Low — downloads re-fetched as needed; archive-v0 (873M) is stale wheels
- **Last modified:** 2026-09-05

### 4. Claude plugins — 808M
- **Owner tool:** Claude Code
- **Cleanup command:** Check Claude Code settings for plugin management; remove unused plugins via `/plugins` or settings
- **Risk:** Medium — verify which plugins are active before removing
- **Last modified:** 2026-09-05 (active)

### 5. GitHub Copilot — 1.0G
- **Owner tool:** GitHub Copilot extension
- **Cleanup command:** Check VS Code / Copilot extension settings for cache clearing
- **Risk:** Low — cache rebuilds automatically
- **Last modified:** 2026-07-17 (idle 50 days)

### 6. Claude projects — 439M
- **Owner tool:** Claude Code
- **Cleanup command:** Check `~/.claude/projects/` for stale project entries; old project dirs can be removed via Claude Code settings
- **Risk:** Low — per-project cache, stale entries are safe to remove
- **Last modified:** 2026-09-05 (active)

---

## Medium-Value Targets (50MB–500MB)

### 7. opengrep — 244M
- **Owner tool:** opengrep
- **Cleanup command:** Check opengrep docs for cache/index clearing
- **Risk:** Low — index rebuildable
- **Last modified:** 2026-08-21 (idle 15 days)

### 8. Orca logs — 95M
- **Owner tool:** Orca
- **Cleanup command:** Orca's internal log rotation (check Orca settings for log retention)
- **Risk:** Low — logs are ephemeral
- **Last modified:** 2026-09-05 (active)

### 9. chrome-devtools-mcp — 100M
- **Owner tool:** Chrome DevTools MCP
- **Cleanup command:** Check Chrome DevTools MCP docs for cache clearing
- **Risk:** Low — rebuilds on demand
- **Last modified:** 2026-08-09 (idle 27 days)

### 10. node cache — 64M
- **Owner tool:** Node.js
- **Cleanup command:** `npm cache clean --force` or `pnpm store prune`
- **Risk:** Low — packages re-downloaded
- **Last modified:** 2026-08-23 (idle 13 days)

### 11. Orca opencode-hooks — 61M
- **Owner tool:** Orca
- **Cleanup command:** Orca's internal hook cache management
- **Risk:** Low — hooks rebuild on session start
- **Last modified:** 2026-08-20 (idle 16 days)

---

## Low-Value Targets (<50MB)

### 12. oh-my-opencode — 42M
- **Owner tool:** oh-my-opencode
- **Cleanup command:** Check oh-my-opencode docs for cache clearing
- **Risk:** Low
- **Last modified:** 2026-01-28 (idle 220 days)

### 13. gem — 24M
- **Owner tool:** Ruby gem
- **Cleanup command:** `gem cleanup`
- **Risk:** Low
- **Last modified:** 2026-08-01 (idle 35 days)

### 14. gh — 20M
- **Owner tool:** GitHub CLI
- **Cleanup command:** `gh api --method DELETE /user/ssh_signing_keys` (for old keys); cache is small, not worth cleaning
- **Risk:** Low
- **Last modified:** 2026-08-31 (active)

### 15. pkg — 13M
- **Owner tool:** pkg (pkg.go.dev or pkg-config)
- **Cleanup command:** Check tool docs for cache clearing
- **Risk:** Low
- **Last modified:** 2026-07-30 (idle 37 days)

---

## Summary

| Category | Estimated reclaimable |
|----------|----------------------|
| High-value (>500MB) | ~4.7G |
| Medium-value (50-500MB) | ~500MB |
| Low-value (<50MB) | ~100MB |
| **Total estimated** | **~5.3G** |

**Stalest cache:** chroma (last modified 2025-11-02 — idle ~307 days)

**Note:** All sizes are estimates. Actual reclaimable space depends on tool internals and whether directories share filesystem blocks.
