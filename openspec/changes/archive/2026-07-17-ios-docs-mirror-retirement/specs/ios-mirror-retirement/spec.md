# Spec: iOS Docs Mirror Retirement + Restructure

## ADDED Requirements

### Requirement: IMR-1 — Legacy iOS local mirror is archived

The directory `poems-mobile3-ios/docs/technical-debt-scan/categories/` SHALL be moved to `docs/.archived-rules-mirror/YYYY-MM-DD/` (where `YYYY-MM-DD` is the date of this change landing). A `README.md` inside the archived directory MUST note the retirement date, the old path, and that the canonical source is now `poems-mobile3-docs/50.RCA/10.iOS/rules/categories/`.

#### Scenario: Legacy mirror directory is archived
- GIVEN `poems-mobile3-ios/docs/technical-debt-scan/categories/` contains legacy iOS category files
- WHEN this change is applied
- THEN the directory is moved to `docs/.archived-rules-mirror/2026-07-09/README.md`
- AND `docs/technical-debt-scan/categories/` no longer exists in the working tree.

### Requirement: IMR-2 — iOS adopts 9-file layout at `docs/rules/categories/`

A new directory `poems-mobile3-ios/docs/rules/categories/` SHALL be created. It SHALL contain all 9 canonical category files synced from `poems-mobile3-docs/50.RCA/10.iOS/rules/categories/`. This aligns the iOS layout with the Android layout.

#### Scenario: iOS restructure to 9-file layout
- GIVEN `poems-mobile3-docs/50.RCA/10.iOS/rules/categories/` contains all 9 canonical files
- WHEN this change is applied
- THEN `poems-mobile3-ios/docs/rules/categories/` contains all 9 files
- AND each file is byte-identical to its canonical counterpart.

### Requirement: IMR-3 — `load-project-rulebook.mdc` references new path

`poems-mobile3-ios/.agents/load-project-rulebook.mdc` SHALL reference `docs/rules/categories/` instead of `docs/technical-debt-scan/categories/`.

#### Scenario: Rulebook path updated
- GIVEN `load-project-rulebook.mdc` contains `docs/technical-debt-scan/categories/`
- WHEN this change is applied
- THEN the path is updated to `docs/rules/categories/`.
