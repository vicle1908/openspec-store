# workspace-wiki-integrity Specification

## Purpose
Define requirements for automated wiki integrity validation: consistent frontmatter, valid relative links, and deterministic read-only checking.

## Requirements

### Requirement: Wiki pages SHALL have complete frontmatter

Every Markdown page in the wiki directory SHALL have `title`, `tags`, `created`, `updated`, and `status` fields in its YAML frontmatter. The `status` field SHALL be one of `active`, `draft`, or `archived`. The current lint prompt validates `title`, `tags`, `created`, `updated`, and `status`. The `type` field exists in some pages' frontmatter but is not part of the current lint audit. This change does not alter the set of audited fields.

#### Scenario: Page with complete frontmatter passes

- **WHEN** a wiki page has all required frontmatter fields (`title`, `tags`, `created`, `updated`, `status`)
- **THEN** the lint check SHALL pass for that page

#### Scenario: Page missing status fails

- **WHEN** a wiki page is missing the `status` field
- **THEN** the lint check SHALL report the page as failing
- **AND** the report SHALL name the missing field

#### Scenario: Page with invalid status fails

- **WHEN** a wiki page has a `status` value not in [active, draft, archived]
- **THEN** the lint check SHALL report the page as failing
- **AND** the report SHALL name the invalid value

### Requirement: Wiki SCHEMA SHALL match audit requirements

The SCHEMA.md frontmatter template SHALL declare every field that the lint audit checks. The schema and the audit rule SHALL not diverge.

#### Scenario: Schema template includes all required fields

- **WHEN** SCHEMA.md is inspected
- **THEN** its frontmatter template SHALL include `title`, `type`, `tags`, `created`, `updated`, and `status`
- **AND** the lint audit SHALL check exactly these fields

#### Scenario: Schema page types table is documented but not modified in this change

- **WHEN** SCHEMA.md page type table is compared to actual wiki directories
- **THEN** discrepancies (e.g., missing `architecture` and `reference` types) SHALL be noted as a documented improvement
- **AND** they SHALL NOT block this change's validation

### Requirement: Wiki links SHALL use correct relative paths

All relative markdown links in wiki pages SHALL resolve to existing files. Links from subdirectory pages to files in other subdirectories SHALL use `../` prefixes.

#### Scenario: Cross-directory link resolves

- **WHEN** a page in `comparisons/` links to `entities/graphify.md`
- **THEN** the link SHALL be `../entities/graphify.md`
- **AND** the lint check SHALL verify the target file exists

#### Scenario: Same-directory link resolves

- **WHEN** a page links to another page in the same directory
- **THEN** the link SHALL use the bare filename
- **AND** the lint check SHALL verify the target file exists

#### Scenario: Link to nonexistent target fails

- **WHEN** a wiki page contains a relative link whose target file does not exist
- **THEN** the lint check SHALL report the broken link with source page and target path

### Requirement: Wiki lint SHALL be deterministic and read-only

The wiki lint cron job SHALL perform validation only. It SHALL NOT modify files, create commits, or perform any mutation. Wiki persistence is a separate human action.

#### Scenario: Lint detects issues

- **WHEN** the lint job finds structural problems
- **THEN** it SHALL report findings as a successful report (exit 0)
- **AND** it SHALL NOT modify any files
- **AND** it SHALL NOT commit to the wiki repository

#### Scenario: Lint finds no issues

- **WHEN** all pages pass validation
- **THEN** the job SHALL emit empty stdout or empty stdout (suppressing delivery)

#### Scenario: Lint script itself fails

- **WHEN** the lint script encounters a parser error, missing dependency, or filesystem error
- **THEN** the script SHALL exit nonzero
- **AND** the nonzero exit SHALL indicate script failure, not validation findings

### Requirement: Reference page creation date SHALL be preserved

When correcting frontmatter on the references page, the original semantic date SHALL be preserved.

#### Scenario: date field renamed to created

- **WHEN** `references/agent-ecosystem-evaluation-2026-08.md` has `date: 2026-08-20`
- **THEN** the field SHALL be set to `created: 2026-08-23` + `date: 2026-08-20`
- **AND** the value 2026-08-20 SHALL be preserved (not overwritten with git log date)
