# skill-index-hygiene Delta Specification

## MODIFIED Requirements

### Requirement: Skill discovery enforces directory ownership and unique names
The canonical generator SHALL accept skill entry points only at `.agents/skills/<directory>/SKILL.md`. It SHALL reject root-level or more deeply nested `SKILL.md` entry points, duplicate normalized skill names, malformed frontmatter, backup scrap files (`*.bak`, `*.orig`, `*~`), and a direct child skill directory whose entry point cannot be parsed.

#### Scenario: Audited workspace has one entry per valid skill directory
- **WHEN** validation runs after the duplicate root-level `.agents/skills/SKILL.md` is removed
- **THEN** it SHALL discover 131 valid direct-child skill entry points on the audited workspace
- **AND** every normalized skill name SHALL be unique

#### Scenario: Stray or duplicate entry point fails validation
- **WHEN** a root-level or nested stray `SKILL.md` exists, backup scrap files (`*.bak`, `*.orig`, `*~`) exist within skill directories, or two entry points declare the same normalized name
- **THEN** validation SHALL fail with every conflicting path and the violated placement, cleanliness, or uniqueness rule
- **AND** existing generated indexes SHALL remain unchanged
