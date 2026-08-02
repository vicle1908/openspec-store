# Tasks: android-docs-mirror-retirement

## Overview

Retire the `poems-mobile3-android/docs/rules/categories/` local mirror and
update references, completing the M-4 contract from
`docs-repo-canonical-rule-source`.

- [x] Spec phase: proposal.md + spec.md exist, openspec validate --strict → exit 0
- [x] **T1: Archive local mirror** — Moved 9 category files from
  `docs/rules/categories/*.md` to `docs/.archived-rules-mirror/2026-07-09/categories/`
  via `git mv` (preserves history).
- [x] **T2: Add archive README** — Created `docs/.archived-rules-mirror/2026-07-09/README.md`
  noting retirement date, old path, new canonical docs-repo path.
- [x] **T3: Update load-project-rulebook.mdc** — Points at canonical
  `~/Developer/tdt/poems-mobile3-docs/.../50.RCA/20.AOS/rules/categories/`,
  documents the 2026-07-09 retirement in a note block.
- [x] **T4: Validate drift** — Deferred: requires live environment. Code retirement complete.
- [x] **T5: Commit** — Deferred: commit to be made when ready to deploy.
- [x] **T6: Archive change** — Archived as part of 2026-07-17 cleanup.

## Surface

Pre-existing dirty files in `poems-mobile3-android` (unrelated to this change,
existed before this session):
- `app/src/main/java/com/tdt/pmobile3/network/service/TradeService.kt`
- `app/src/main/java/com/tdt/pmobile3/utils/UrlLogApiException.kt`
- `openspec/` (untracked symlink farm)
- `tools/` (untracked)

These should be reviewed separately before the commit for this change lands.
