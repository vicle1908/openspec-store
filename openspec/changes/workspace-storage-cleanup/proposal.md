# Proposal: Workspace Storage Cleanup

## Why

Disk usage reached 94% (30 GB free on a 494 GB APFS volume). macOS requires ~10-15% free for swap, snapshots, and general operation. Multiple stale caches, build artifacts, and redundant data occupied ~30+ GB across npm, Go, uv, Docker, Chrome, and development worktrees.

## What

Perform a multi-phase disk cleanup across the workspace:

1. **Cache cleanup** — npm, npx, Go build, uv, Homebrew, Chrome, pnpm, bun caches
2. **Docker cleanup** — prune dangling images and unused volumes
3. **Development artifacts** — stale worktrees, OmniRoute `.build/`, `.tdt-backup` archives
4. **Application cleanup** — remove TabNine, Lingma, Chromium snapshots
5. **Media optimization** — enable macOS photo storage optimization, audit Pictures library
6. **Download cleanup** — remove already-installed setup DMGs and old installers

## Success Criteria

- Free space increases from 30 GB to 50+ GB (target: 86% or lower utilization)
- No breaking changes to active development workflows
- Docker services still functional after volume prune
- All changes are safe/reversible where possible

## Scope

- **Config-only change:** `skip_specs: true` — no OpenSpec delta needed
- Affects: `~/.npm`, `~/.cache`, `~/Library/Caches`, `~/Developer`, `~/.bun`, Docker
