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
- [x] 2.1 Prune dangling Docker images — 610 MB
- [x] 2.2 Prune unused Docker volumes — 0 B (kept active volumes)

## Phase 3: Development Artifacts ✅
- [x] 3.1 Remove OmniRoute `.build/` — 6.3 GB
- [x] 3.2 Remove `.tdt-backup` archives — 2.0 GB
- [x] 3.3 Remove Chromium browser snapshots — 324 MB
- [x] 3.4 Remove Bun install cache — 1.9 GB
- [x] 3.5 Remove Lingma (`~/.lingma`) — 2.6 GB

## Phase 4: Application Cleanup (In Progress)
- [ ] 4.1 Remove TabNine (`~/.tabnine` + App Support) — ~460 MB
- [ ] 4.2 Enable macOS Photos storage optimization — 14 GB potential
- [ ] 4.3 Audit and remove installed setup DMGs from Downloads
- [ ] 4.4 Audit `Downloads/project/` for stale content — 8.9 GB

## Phase 5: Validation
- [ ] 5.1 Verify free space target reached (50+ GB)
- [ ] 5.2 Verify Docker services functional
- [ ] 5.3 Verify development workflows unaffected
