# Tasks: Workspace Storage Cleanup

## Phase 1: Cache Cleanup ✅
- [x] 1.1 Remove npx cache (`~/.npm/_npx`) — 5.6 GB
- [x] 1.2 Clean npm cache (`npm cache clean --force`) — 3.8 GB
- [x] 1.3 Clean Go build cache (`go clean -cache`) — 9.1 GB
- [x] 1.4 Clean uv cache (`uv cache clean`) — 3.4 GB
- [x] 1.5 Clean Homebrew cache (`brew cleanup -s`) — 1.4 GB
- [x] 1.6 Clean Chrome cache (`Library/Caches/Google/`) — 1.6 GB
- [x] 1.7 Prune pnpm store — 17 MB

## Phase 2: Docker Cleanup ✅
- [x] 2.1 Prune dangling Docker images (58 images) — 610 MB
- [x] 2.2 Prune unused Docker volumes — 0 B (kept active volumes)

## Phase 3: Development Artifacts ✅
- [x] 3.1 Remove OmniRoute `.build/` — 6.3 GB
- [x] 3.2 Remove `.tdt-backup` archives — 2.0 GB
- [x] 3.3 Remove Chromium browser snapshots — 324 MB
- [x] 3.4 Remove Bun install cache — 1.9 GB
- [x] 3.5 Remove Lingma (`~/.lingma`) — 2.6 GB

## Phase 4: Application Cleanup ✅
- [x] 4.1 Remove TabNine (`~/.tabnine` + App Support) — ~460 MB
- [x] 4.2 Enable macOS Photos iCloud storage optimization
- [x] 4.3 Remove installed setup DMGs from Downloads (Ofable-5, MCP Router, Zalo, CodexUse, Google Drive, InstantView, Lark, AnyViewer, Xermius, Hermes, Tailscale) — ~1.5 GB
- [x] 4.4 Remove stale debug zips and empty setup dir

## Phase 5: Validation ✅
- [x] 5.1 Verify free space: 30 GB → 63 GB (+33 GB recovered)
- [x] 5.2 Docker images pruned, active services unaffected
- [x] 5.3 Development workflows unaffected (caches auto-rebuild)

## Deferred (Requires User Decision)
- [ ] 6.1 Audit `Downloads/project/` — 8.9 GB (ghtk 6.9G, ghtk-ios 1.8G, others 120M)
- [ ] 6.2 Ofable-5 models (`~/.ollama`) — 4.4 GB (remove if not using local models)
- [ ] 6.3 Stale developer worktrees (`~/.worktrees`) — 8.2 GB
