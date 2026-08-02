## MODIFIED Requirements

### Requirement: Skills doctor reports profile-aware diagnostics
The system SHALL provide a `skills doctor` command that validates the active
profile and reports issues. Diagnostics SHALL operate on logical skill
identities, canonicalize filesystem sources, ignore non-skill catalog
documents, and emit one machine-readable result per logical issue. Candidate
parse failures SHALL remain visible, but loadability of an explicitly included
skill SHALL be decided only after all ordered fallback candidates are evaluated.

#### Scenario: Doctor reports missing directories
- **WHEN** a profile references a directory that does not exist on disk
- **THEN** doctor reports a warning with the missing path

#### Scenario: Doctor reports duplicate skill names across directories
- **WHEN** the same skill name exists in distinct canonical source directories
- **THEN** doctor reports once which version is active (shadow winner) and
  which distinct versions are shadowed

#### Scenario: Same canonical skill appears through two paths

- **WHEN** repository and global profile paths resolve through symlinks to the
  same canonical `SKILL.md`
- **THEN** doctor SHALL compare their resolved physical file identity and treat
  them as one source
- **AND** it SHALL NOT emit a shadow warning for that alias

#### Scenario: Catalog documents are present

- **WHEN** a skill directory contains indexes, provider guides, workflow
  documents, or other Markdown files not named `SKILL.md`
- **THEN** doctor SHALL not parse them as skills or report them as malformed

#### Scenario: Explicitly included skill cannot load

- **WHEN** an active profile explicitly includes a skill that has no valid candidate after all ordered source directories are evaluated
- **THEN** doctor SHALL emit a structured error identifying the skill and cause
- **AND** the command SHALL exit non-zero

#### Scenario: Later source provides valid included skill fallback

- **WHEN** an earlier source contains a malformed candidate for an explicitly included skill and a later ordered source contains a valid candidate
- **THEN** doctor SHALL retain a malformed-candidate warning
- **AND** it SHALL NOT emit an included-skill-unloadable error
- **AND** the valid fallback SHALL appear in the active set

#### Scenario: Doctor reports conflicts in active set
- **WHEN** two active skills declare `conflicts_with` referencing each other
- **THEN** doctor reports the conflict pair and suggests adding one to the profile's exclude list

#### Scenario: Doctor reports repo-scoped skills outside intended repo
- **WHEN** a skill has `repositories: ["webhook-receiver"]` but is loaded from a different repo context
- **THEN** doctor reports a scope mismatch warning

#### Scenario: Doctor JSON output

- **WHEN** `agent-core skills doctor --json` is run
- **THEN** standard output SHALL be one valid JSON object with `warnings`,
  `errors`, and `info` arrays containing structured diagnostic objects
- **AND** operational logs SHALL be routed separately so they do not corrupt
  the JSON document
