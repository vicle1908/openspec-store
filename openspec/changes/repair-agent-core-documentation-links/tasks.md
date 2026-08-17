# Tasks: Repair agent-core documentation links

## 1. Baseline

- [x] 1.1 Run `docs-sync validate --repo ~/Developer/agent-core` → 2 broken links, exit 1
- [x] 1.2 Record broken links:
  - `docs/README.md → model-resolution.md` (file does not exist)
  - `docs/extending.md → docs/scheduling.md` (double-path resolves to `docs/docs/scheduling.md`)

## 2. Implementation

- [ ] 2.1 Fix `docs/README.md` line 19: `model-resolution.md` → `architecture.md`
- [ ] 2.2 Fix `docs/extending.md` lines 265–270: replace two paragraphs with one truthful `scheduling.md` link
- [ ] 2.3 Verify no other references to `docs/scheduler/ARCHITECTURE.md` or `model-resolution.md`

## 3. Verification

- [ ] 3.1 Run `docs-sync validate --repo <worktree>` → 0 broken links, exit 0
- [ ] 3.2 Run `git diff --check` → clean

## 4. Closure

- [ ] 4.1 Commit with conventional message
- [ ] 4.2 Fast-forward merge to agent-core main (preserve graphify-out/ changes)
- [ ] 4.3 OpenSpec validate → pass
- [ ] 4.4 Archive with `--skip-specs --yes`
- [ ] 4.5 Remove worktree and branch
