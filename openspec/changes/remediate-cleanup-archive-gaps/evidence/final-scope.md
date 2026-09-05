# Final Scope Record

**Change:** remediate-cleanup-archive-gaps
**Date:** 2026-09-05
**Mode:** read-only corrective evidence; no archived files edited, no destructive actions performed

## Scope Completed

- Corrective planning artifacts (proposal, spec delta, design, tasks) for the two cleanup archives.
- Value-blind verification evidence recorded:
  - `evidence/cleanup-verification.json` (sha256 `15c19eccd0fbdecb8c828820823731b6b7ec11f6269a3f2814ab71eb1ca683e2`)
  - `evidence/repository-inventory.txt` (sha256 `e025d0ef17967da8efe18ab3040f5e62f612bb4c35147bbe0448b7a9816087df`)
  - `evidence/cleanup-verification.md`
- 19/19 repository inventory rows; worktree/venv/branch/status evidence; embedded-copy divergence recorded.
- Executable-aware verification for all 8 archive-targeted applications (plist-declared CFBundleExecutable vs. actual executable path, bytes, mode).
- Orca identity/version (`com.stablyai.orca` v1.4.197) and Caskroom `.upgrading` state recorded.
- `brew doctor` read-only result recorded; target-app warnings false, unrelated findings classified.
- Full `/Applications` executable-aware scan: 0 missing declared executables.
- Sideloaded reinstall gate: resolved/currently unnecessary (both executables nonzero + executable mode); no provenance claimed.

## Explicitly Not Done (Boundaries)

- No archive files modified (git status: only untracked corrective change directory).
- No applications reinstalled/removed; no worktrees/branches/venvs touched.
- tdt-scheduler embedded-copy divergence (62/44/30/28 entries) left for owner decision.
- 5 dirty repos (`agent-docs-sync`, `agent-harness`, `ai-review`, `jira-epic-report`, `jira-skill`) classified as unrelated, untouched.
- `brew doctor` `cockpit-tools`/`antigravity-cli` warnings outside archive scope.
- No credential or provider surface changed.

## Commit Readiness

- Files remain untracked until commit; this pathspec-limited commit stages exactly `openspec/changes/remediate-cleanup-archive-gaps/` and nothing else.
- Not archived; this record closes task 3.4 without archiving.
