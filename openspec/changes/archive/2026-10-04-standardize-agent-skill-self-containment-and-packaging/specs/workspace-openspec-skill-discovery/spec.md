## ADDED Requirements

### Requirement: Shared Agent Skills SHALL be self-contained and modularly packaged

Shared Agent Skills in canonical skill roots under `~/Developer/.agents/skills/` SHALL be self-contained, encapsulating their own execution scripts, operational documentation, and templates rather than depending on ambient machine tools or undocumented external shell scripts. When a skill executes automated commands, it SHALL bundle executable CLI scripts under a `scripts/` directory with explicit argument handling and error boundaries. Complex or secondary reference documentation SHALL be separated into `references/` subfiles to optimize system prompt injection overhead.

#### Scenario: A skill bundles portable execution scripts and reference documentation
- **GIVEN** an agent skill wraps automated verification or execution workflows
- **WHEN** the skill root is inspected
- **THEN** it SHALL contain an executable CLI script under `scripts/`
- **AND** detailed failure taxonomies or manuals SHALL be isolated under `references/`

#### Scenario: A skill provides structured machine-readable CLI interfaces
- **GIVEN** a bundled execution script within a skill
- **WHEN** invoked with `--json`
- **THEN** it SHALL emit valid, machine-readable JSON summarizing operation success, execution details, and diagnostic violations
- **AND** it SHALL exit non-zero when violations are detected

### Requirement: Shared Agent Skills SHALL conform to progressive disclosure and frontmatter standards

Every shared skill `SKILL.md` SHALL start with standard YAML frontmatter defining `name`, `description`, and platform metadata. The `description` field MUST contain a self-contained, unambiguous trigger condition within the first 57 characters and SHALL NOT exceed 60 characters total, preventing prompt truncation in compact agent catalog listings. The body of `SKILL.md` SHALL follow progressive disclosure with explicit invocation criteria, quick start commands, procedural workflows framed through native agent tools (`terminal`, `read_file`), negative counter-triggers ("When NOT to use"), and testable verification criteria.

#### Scenario: Frontmatter description defines a self-contained trigger within 57 characters
- **GIVEN** a shared agent skill's `SKILL.md`
- **WHEN** the frontmatter `description` is parsed
- **THEN** the active trigger phrase SHALL be fully self-contained within the first 57 characters
- **AND** the entire description string SHALL NOT exceed 60 characters

#### Scenario: Negative counter-triggers prevent inappropriate invocation
- **GIVEN** a shared agent skill's `When to Use` section
- **WHEN** evaluated by an autonomous agent
- **THEN** it SHALL explicitly define scenarios where the skill MUST NOT be used
- **AND** all command executions SHALL be framed through native agent tools
