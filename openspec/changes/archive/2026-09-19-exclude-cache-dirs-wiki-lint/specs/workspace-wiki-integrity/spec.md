# Spec Delta

## MODIFIED Requirements

### Requirement: Wiki lint SHALL be deterministic and read-only

The wiki lint cron job and CLI runner SHALL perform validation only. It SHALL NOT modify files, create commits, or perform any mutation. Wiki persistence is a separate human action. Furthermore, page discovery SHALL exclude hidden dot-directories and runner cache directories from frontmatter audits, link validation, and orphan detection.

#### Scenario: Hidden and cache directories are excluded from lint
- **WHEN** the wiki directory contains untracked cache artifacts or hidden directories (such as `.pytest_cache/README.md`, `.git/`, `.ruff_cache/`, or `.venv/`)
- **THEN** page discovery SHALL skip those directories entirely
- **AND** SHALL NOT report missing frontmatter or orphan warnings for files within them.

#### Scenario: Lint detects issues
- **WHEN** the lint job finds structural problems in wiki pages
- **THEN** it SHALL report findings as a successful report (exit 0)
- **AND** it SHALL NOT modify any files
- **AND** it SHALL NOT commit to the wiki repository

#### Scenario: Lint finds no issues
- **WHEN** all pages pass validation
- **THEN** the job SHALL emit empty stdout (suppressing delivery)

#### Scenario: Lint script itself fails
- **WHEN** the lint script encounters a parser error, missing dependency, or filesystem error
- **THEN** the script SHALL exit nonzero
- **AND** the nonzero exit SHALL indicate script failure, not validation findings
