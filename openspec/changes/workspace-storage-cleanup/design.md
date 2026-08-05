# Design: Workspace Storage Cleanup

## Architecture

The cleanup operates in 3 tiers by risk level:

### Tier 1 — Safe & Immediate (no rebuild needed)
- npm/npx cache removal (`~/.npm/_npx`, `~/.npm/_cacache`)
- Docker image prune + volume prune
- OmniRoute `.build/` removal
- Homebrew cache cleanup (`brew cleanup -s`)
- Chromium browser snapshots removal
- `.tdt-backup` archive removal

### Tier 2 — Rebuildable (auto-rebuilds on next use)
- Go build cache (`go clean -cache`)
- uv cache (`uv cache clean`)
- pnpm store prune
- Bun install cache removal

### Tier 3 — Manual/Decision Required
- Chrome cache (`Library/Caches/Google/`)
- TabNine removal (App Support + cache)
- Lingma removal
- Photos library optimization (macOS setting)
- Downloaded setup DMG removal

## Data Flow

```
Identify → Categorize by risk → Execute safe items → Verify free space → Log results
```

## Recovery

- Go/uv/npm caches rebuild automatically on next build/install
- Docker images can be re-pulled
- Worktrees are git-tracked (recoverable from remote)
- TabNine/Lingma are reinstallable
