## ADDED Requirements

### Requirement: Central index links to repository documentation

The `docs/INDEX.md` file SHALL contain a "Repository Documentation" section that links to each non-mobile repository's `docs/` directory.

#### Scenario: Repository documentation section exists
- **WHEN** a contributor opens `docs/INDEX.md`
- **THEN** they see a "Repository Documentation" section with a markdown table

#### Scenario: Each repo entry has link, count, and description
- **WHEN** the "Repository Documentation" table is rendered
- **THEN** each row contains a linked repo name pointing to `../<repo>/docs/`, a file count, and a brief description of key content

#### Scenario: Non-mobile repos are included
- **WHEN** the table is populated
- **THEN** it includes at minimum: agent-core, jira-skill, mcp-router, webhook-receiver, tdt-sheets, jira-epic-report, jira-daily-reports, code-daily-scan

#### Scenario: Mobile repos are excluded
- **WHEN** the table is populated
- **THEN** it does NOT include poems-mobile3-ios, poems-mobile3-android, or their release variants

### Requirement: Stale directories are archived

One-time investigation directories in `docs/` SHALL be moved to `docs/archive/` with descriptive subdirectory names.

#### Scenario: Crashlytics reports archived
- **WHEN** the cleanup is complete
- **THEN** `docs/crashlytics/` no longer exists
- **AND** `docs/archive/crashlytics-2026-06/` contains the two PDF files:
  - `crashlytics_root_cause_analysis_2026-06-11(android).pdf`
  - `crashlytics_root_cause_analysis_2026-06-11 1(ios).pdf`

#### Scenario: Coverage assessments archived
- **WHEN** the cleanup is complete
- **THEN** `docs/coverage/` no longer exists
- **AND** `docs/archive/coverage-assessments-2026-06/` contains the three markdown files:
  - `live-replay-assessment-2026-06-28.md`
  - `openspec-backlog-triage-2026-06-28.md`
  - `ship-wave-2026-06-27-mapping.md`

### Requirement: Thin single-file directories are relocated

Directories containing exactly one real file (not symlinks) SHALL have that file moved to a thematic parent directory, and the empty directory removed.

#### Scenario: Ecosystem-reports file relocated
- **WHEN** the cleanup is complete
- **THEN** `docs/ecosystem-reports/jira-gitlab-alignment-2026-06-04.md` exists at `docs/workflows/jira-gitlab-alignment-2026-06-04.md`
- **AND** `docs/ecosystem-reports/` no longer exists

#### Scenario: Ecc-harness file relocated
- **WHEN** the cleanup is complete
- **THEN** `docs/ecc-harness/playbook.md` exists at `docs/tools/ecc-harness-playbook.md`
- **AND** `docs/ecc-harness/` no longer exists

#### Scenario: Features file relocated
- **WHEN** the cleanup is complete
- **THEN** `docs/features/P3_VERTICAL_SCOPE.pdf` exists at `docs/reports/P3_VERTICAL_SCOPE.pdf`
- **AND** `docs/features/` no longer exists

#### Scenario: Vertical-scope file relocated
- **WHEN** the cleanup is complete
- **THEN** `docs/vertical-scope/P3-VERTICAL-SCOPE(July 2025).pdf` exists at `docs/reports/P3-VERTICAL-SCOPE(July 2025).pdf`
- **AND** `docs/vertical-scope/` no longer exists

### Requirement: Intentional symlinks are preserved

The `docs/configuration/AGENTS.md` symlink (pointing to `../../AGENTS.md`) SHALL NOT be moved or deleted — it is an intentional link to the root AGENTS.md.

#### Scenario: Configuration symlink preserved
- **WHEN** the cleanup is complete
- **THEN** `docs/configuration/AGENTS.md` still exists as a symlink to `../../AGENTS.md`
- **AND** `docs/configuration/` is NOT removed (it contains the intentional symlink)

### Requirement: Empty DOCUMENTATION-INDEX.md is removed

The empty `docs/DOCUMENTATION-INDEX.md` file (0 bytes) SHALL be deleted.

#### Scenario: Empty index file removed
- **WHEN** the cleanup is complete
- **THEN** `docs/DOCUMENTATION-INDEX.md` does not exist
