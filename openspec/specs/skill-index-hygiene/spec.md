## Purpose

Enforce skill description size limits, YAML frontmatter parsing, directory
ownership, unique naming, and a single canonical index source so that
skill metadata remains consistent and validation is continuously
verifiable.

## Requirements

### Requirement: Skill descriptions stay within the loader budget
Every TDT `SKILL.md` frontmatter description SHALL be measured as UTF-8 bytes after scalar decoding and SHALL be no longer than 1,024 bytes. Descriptions above an advisory 800-byte threshold SHALL produce a non-failing warning so routing metadata remains concise.

#### Scenario: Valid description passes validation
- **WHEN** a skill description is parsed and is at most 1,024 UTF-8 bytes
- **THEN** the skill validation SHALL accept it and preserve the normalized description for indexing

#### Scenario: Oversized description fails validation
- **WHEN** a skill description exceeds 1,024 UTF-8 bytes
- **THEN** validation SHALL fail with the skill path, measured byte count, and a remediation message
- **AND** index generation SHALL not publish a partially updated index

#### Scenario: Advisory threshold warns without failing
- **WHEN** a decoded description is greater than 800 bytes and no greater than 1,024 bytes
- **THEN** validation SHALL report a warning containing the skill path and measured byte count
- **AND** the skill SHALL remain eligible for indexing

### Requirement: Frontmatter parser supports the declared block scalar forms
The canonical index generator SHALL parse folded and literal YAML description scalars using the supported forms `>`, `>-`, `>+`, `|`, `|-`, and `|+`. It SHALL normalize decoded whitespace to the same single-line representation in JSON and Markdown output and SHALL NOT publish a scalar marker as description content.

#### Scenario: Folded scalar is indexed as content
- **WHEN** a skill declares `description: >-` followed by indented lines
- **THEN** the generated index SHALL contain the folded description text rather than the literal marker `>-`

#### Scenario: Literal scalar is indexed as content
- **WHEN** a skill declares `description: |-` followed by indented lines
- **THEN** the generated index SHALL contain the literal description content normalized according to the index format

#### Scenario: Keep modifiers are accepted
- **WHEN** a skill declares `description: >+` or `description: |+` followed by indented lines
- **THEN** validation SHALL accept the scalar header
- **AND** the generated description SHALL contain normalized content rather than the header marker

### Requirement: Skill discovery enforces directory ownership and unique names
The canonical generator SHALL accept skill entry points only at `.agents/skills/<directory>/SKILL.md`. It SHALL reject root-level or more deeply nested `SKILL.md` entry points, duplicate normalized skill names, malformed frontmatter, and a direct child skill directory whose entry point cannot be parsed.

#### Scenario: Audited workspace has one entry per valid skill directory
- **WHEN** validation runs after the duplicate root-level `.agents/skills/SKILL.md` is removed
- **THEN** it SHALL discover 131 valid direct-child skill entry points on the audited workspace
- **AND** every normalized skill name SHALL be unique

#### Scenario: Stray or duplicate entry point fails validation
- **WHEN** a root-level or nested stray `SKILL.md` exists or two entry points declare the same normalized name
- **THEN** validation SHALL fail with every conflicting path and the violated placement or uniqueness rule
- **AND** existing generated indexes SHALL remain unchanged

### Requirement: Generated skill indexes have one canonical source
The canonical JSON index and both human-readable Markdown indexes SHALL be rendered from the same validated in-memory skill metadata by one standard-library Python entry point. The operator-facing shell builder and validation hook SHALL delegate to that entry point through `uv run --no-project python`, and the JSON field schema consumed by both existing skill matcher scripts SHALL remain compatible.

#### Scenario: All index surfaces agree
- **WHEN** the canonical index generator completes successfully
- **THEN** every index surface SHALL contain the same skill names, normalized descriptions, and total skill count
- **AND** no generated entry SHALL contain a block-scalar marker as its description

#### Scenario: Parse or validation failure is atomic
- **WHEN** any skill has malformed frontmatter or an oversized description
- **THEN** the generator SHALL report all failures and SHALL leave existing generated indexes unchanged

#### Scenario: Changed generation replaces all outputs atomically
- **WHEN** validated semantic skill metadata differs from the generated outputs and `--write` runs
- **THEN** the generator SHALL render all three outputs before replacement
- **AND** all three outputs SHALL receive one shared generation timestamp and be replaced as one successful publish operation

#### Scenario: Unchanged generation is idempotent
- **WHEN** semantic skill metadata and all generated entry sets are already current
- **THEN** `--check` SHALL succeed without writing
- **AND** `--write` SHALL preserve the existing generated timestamp, file contents, and file modification times

### Requirement: Skill metadata validation is continuously verifiable
The workspace SHALL provide deterministic standard-library tests and a validation command that check description byte limits, all six scalar forms, frontmatter failures, placement, duplicate names, index consistency, atomic failure, idempotence, matcher-schema compatibility, and the presence of the canonical JTI skill entry.

#### Scenario: Workspace validation catches the current regression
- **WHEN** validation runs against the pre-fix JTI metadata or parser behavior
- **THEN** it SHALL identify the 1,436-byte description or literal `>-` index value as a failure

#### Scenario: Clean metadata produces reproducible output
- **WHEN** validation runs after the skill and parser are corrected
- **THEN** it SHALL pass with the JTI description at or below the limit and identical normalized descriptions across all index surfaces
- **AND** neither direct `python` nor direct `pytest` execution SHALL be required by the JTI skill or index build workflow
