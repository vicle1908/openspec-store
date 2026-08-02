# Proposal: Initialize OpenSpec Store as Git Repository

## Why

The openspec-store at `~/Developer/openspec-store/` contains 328 specs, 255
archived changes, 12 active changes, and 8 reports. It is currently NOT
tracked by git, meaning:

1. **Zero backup** — if deleted or corrupted, all specs are lost
2. **No history** — cannot audit what changed, when, or why
3. **No team sharing** — teammates cannot clone the store
4. **Violates official recommendation** — openspec.dev/docs/stores states:
   > "A store is just a git repo. You commit, push, pull, and review it yourself."
   > "Sharing work is git, on purpose."
5. **`openspec store doctor`** reports "Git: not detected"

## What Changes

1. Create `.gitignore` for store (exclude .DS_Store, logs, temp files)
2. `git init` the openspec-store directory
3. `git add .` all specs, archives, changes, reports, config
4. `git commit` with descriptive initial commit
5. Update workspace AGENTS.md to document store git tracking
6. Update go-microservices AGENTS.md to reference store git practices

## Non-Goals

- No remote setup (backup/teams is a separate decision)
- No spec content changes
- No openspec registry changes (per-machine, local-only)

## Compatibility

Additive only. Git tracking has no effect on openspec CLI behavior.

## Rollback

`rm -rf ~/Developer/openspec-store/.git`
