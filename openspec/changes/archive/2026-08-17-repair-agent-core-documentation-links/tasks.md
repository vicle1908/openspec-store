# Tasks: Repair agent-core documentation links

## 1. Baseline

- [x] 1.1 Run `docs-sync validate --repo ~/Developer/agent-core` → 2 broken links, exit 1
- [x] 1.2 Record broken links:
  - `docs/README.md → model-resolution.md` (file does not exist)
  - `docs/extending.md → docs/scheduling.md` (double-path resolves to `docs/docs/scheduling.md`)

## 2. Clickable link repairs

- [x] 2.1 Fix `docs/README.md` line 19: `model-resolution.md` → `architecture.md`
- [x] 2.2 Fix `docs/extending.md` lines 265–270: replace two scheduling paragraphs with one truthful `scheduling.md` link

## 3. Stale plain-text reference repairs

- [x] 3.1 Fix `docs/scheduling.md` line 59: remove stale `docs/scheduler/ARCHITECTURE.md` backtick reference
- [x] 3.2 Fix `docs/architecture.md` line 124: remove stale `docs/scheduler/ARCHITECTURE.md` backtick reference
- [x] 3.3 Fix `docs/building-agents.md` line 370: remove stale `docs/scheduler/ARCHITECTURE.md` backtick reference

## 4. Verification

- [x] 4.1 Stale-reference grep → empty (clean)
- [x] 4.2 `git diff --check` → clean
- [x] 4.3 CLI `docs-sync validate --repo <worktree>` → 37 links checked, exit 0
- [x] 4.4 Post-merge CLI validation → 37 links checked, exit 0

## 5. Closure

- [x] 5.1 Commit clickable repairs: `ded5fac`
- [x] 5.2 Commit stale-reference repairs: `7a89372`
- [x] 5.3 Fast-forward merge to agent-core main
- [x] 5.4 OpenSpec validate → pass
- [x] 5.5 Archive with `--skip-specs --yes`
- [x] 5.6 Remove worktree and branch
