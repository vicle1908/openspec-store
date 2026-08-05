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
- [x] 4.3 Remove installed setup DMGs from Downloads — ~1.5 GB
- [x] 4.4 Remove stale debug zips and empty setup dir
- [x] 4.5 Remove Chrome OptGuideOnDeviceModel (AI model) — 4.0 GB
- [x] 4.6 Remove Chrome Snapshots — 682 MB
- [x] 4.7 Remove GoogleUpdater crx_cache — 706 MB

## Phase 5: Extended Safe Cleanup ✅
- [x] 5.1 Remove Go module cache (`~/go/pkg`) — 4.1 GB
- [x] 5.2 Remove OmniRoute `node_modules` — 3.7 GB
- [x] 5.3 Remove Codex runtimes cache — 1.5 GB
- [x] 5.4 Remove all stale developer worktrees — 8.2 GB
- [x] 5.5 Remove Hermes state-snapshots — 259 MB

## Phase 6: Validation ✅
- [x] 6.1 Free space: 30 GB → 82 GB (+52 GB recovered)
- [x] 6.2 Capacity: 94% → 84%
- [x] 6.3 All changes safe/reversible where applicable

## Pending User Decision
- [ ] 7.1 Remove `jenkins_home` (1.8 GB) — local Jenkins not in use?
- [ ] 7.2 Remove `~/.Genymobile` (2.0 GB) — Genymotion emulator images?
- [ ] 7.3 Remove `Downloads/project/` (8.9 GB) — ghtk + ghtk-ios projects?
- [ ] 7.4 Chrome stale profiles (Profile 2-21) — ~850 MB
