# Spec: Android Docs Mirror Retirement

## ADDED Requirements

### Requirement: AMR-1 — Local Android rule mirror is archived

The directory `poems-mobile3-android/docs/rules/categories/` SHALL be moved to `docs/.archived-rules-mirror/YYYY-MM-DD/` (where `YYYY-MM-DD` is the date of this change landing). A `README.md` inside the archived directory MUST note the retirement date and that the canonical source is now `poems-mobile3-docs/50.RCA/20.AOS/rules/categories/`.

#### Scenario: Mirror directory is archived
- GIVEN `poems-mobile3-android/docs/rules/categories/` contains 9 category files
- WHEN this change is applied
- THEN the directory is moved to `docs/.archived-rules-mirror/2026-07-09/README.md`
- AND `docs/rules/categories/` no longer exists in the working tree.

### Requirement: AMR-2 — `load-project-rulebook.mdc` references canonical path

`poems-mobile3-android/.agents/load-project-rulebook.mdc` SHALL reference `~/Developer/tdt/poems-mobile3-docs/20.Developments/40.AI/50.RCA/20.AOS/rules/categories/` instead of `docs/rules/categories/`.

#### Scenario: Rulebook path updated
- GIVEN `load-project-rulebook.mdc` contains `docs/rules/categories/`
- WHEN this change is applied
- THEN the path is updated to `poems-mobile3-docs/20.Developments/40.AI/50.RCA/20.AOS/rules/categories/`.
