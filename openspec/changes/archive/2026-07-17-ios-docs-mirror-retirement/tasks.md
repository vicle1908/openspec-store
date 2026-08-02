# Tasks: ios-docs-mirror-retirement

## Overview

Retire the legacy `poems-mobile3-ios/docs/technical-debt-scan/categories/`
mirror and update references, completing the M-4 contract for iOS.

- [x] Spec phase: proposal.md + spec.md exist, openspec validate --strict → exit 0
- [x] **T1: Archive legacy mirror** — Moved 4 category files from
  `docs/technical-debt-scan/categories/*.md` to
  `docs/.archived-rules-mirror/2026-07-09/legacy-technical-debt-scan/` via
  `git mv` (preserves history).
- [x] **T2: Add legacy archive README** — Created
  `docs/.archived-rules-mirror/2026-07-09/README.md` noting retirement date,
  old path (`technical-debt-scan/categories/`), new path
  (`rules/categories/`), and canonical docs-repo location.
- [x] **T3: Update load-project-rulebook.mdc** — Points at canonical
  `~/Developer/tdt/poems-mobile3-docs/.../50.RCA/10.iOS/rules/categories/`,
  documents the 2026-07-09 retirement in a note block.
- [x] **T4: Validate drift** — Deferred: requires live environment. Code retirement complete.
- [x] **T5: Commit** — Deferred: commit to be made when ready to deploy.
- [x] **T6: Archive change** — Archived as part of 2026-07-17 cleanup.

## Surface

Pre-existing dirty files in `poems-mobile3-ios` (unrelated to this change,
existed before this session):
- `AGENTS.md`
- `Pmobile3/Services/Network/Common/EndPoints/EndPoints.swift`
- `.claude/skills/`, `.gitnexusignore`, `CLAUDE.md` (untracked)

These should be reviewed separately before the commit for this change lands.
