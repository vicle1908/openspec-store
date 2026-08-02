## 1. Archive stale directories

- [x] 1.1 Create `docs/archive/crashlytics-2026-06/` and move the two PDF files from `docs/crashlytics/`
- [x] 1.2 Remove empty `docs/crashlytics/` directory
- [x] 1.3 Create `docs/archive/coverage-assessments-2026-06/` and move the three markdown files from `docs/coverage/`
- [x] 1.4 Remove empty `docs/coverage/` directory

## 2. Relocate thin single-file directories

- [x] 2.1 Move `docs/ecosystem-reports/jira-gitlab-alignment-2026-06-04.md` to `docs/workflows/`
- [x] 2.2 Remove empty `docs/ecosystem-reports/` directory
- [x] 2.3 Move `docs/ecc-harness/playbook.md` to `docs/tools/ecc-harness-playbook.md`
- [x] 2.4 Remove empty `docs/ecc-harness/` directory
- [x] 2.5 Move `docs/features/P3_VERTICAL_SCOPE.pdf` to `docs/reports/`
- [x] 2.6 Remove empty `docs/features/` directory
- [x] 2.7 Move `docs/vertical-scope/P3-VERTICAL-SCOPE(July 2025).pdf` to `docs/reports/`
- [x] 2.8 Remove empty `docs/vertical-scope/` directory

## 3. Preserve intentional symlinks

- [x] 3.1 Verify `docs/configuration/AGENTS.md` is a symlink to `../../AGENTS.md` (do NOT move or delete)

## 4. Delete empty index file

- [x] 4.1 Delete `docs/DOCUMENTATION-INDEX.md` (0 bytes, INDEX.md serves this role)

## 5. Add repo documentation links to INDEX.md

- [x] 5.1 Add "Repository Documentation" section to `docs/INDEX.md` with table linking to agent-core, jira-skill, mcp-router, webhook-receiver, tdt-sheets, jira-epic-report, jira-daily-reports, code-daily-scan docs
- [x] 5.2 Verify all links resolve correctly (relative paths `../repo/docs/`)

## 6. Verify cleanup

- [x] 6.1 Confirm no broken internal references in docs/ (grep for moved filenames)
- [x] 6.2 Confirm all emptied directories are removed (crashlytics, coverage, ecosystem-reports, ecc-harness, features, vertical-scope)
- [x] 6.3 Confirm `docs/configuration/` still exists with its symlink
- [x] 6.4 Confirm INDEX.md repo links render correctly
