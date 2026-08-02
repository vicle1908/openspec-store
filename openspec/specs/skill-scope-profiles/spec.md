# skill-scope-profiles Specification

## Purpose
Named skill loading profiles with deterministic composition, metadata-driven filtering, and diagnostics for conflicts and drift.

## Requirements

### Requirement: Profiles are named skill-loading configurations
The system SHALL support named profiles under `skills.profiles` in agent-core configuration. Each profile declares `directories`, optional `include` list, optional `exclude` list, and optional `scopes` list.

#### Scenario: Profile with directories only
- **WHEN** a profile is defined with only `directories: [".agents/skills", "~/.tdt/skills"]`
- **THEN** the skill loader uses those directories in order and applies no include/exclude filtering

#### Scenario: Profile with include filter
- **WHEN** a profile defines `include: ["tavily-search", "gitnexus"]`
- **THEN** only skills whose names match the include list are loaded from the profile's directories

#### Scenario: Profile with exclude filter
- **WHEN** a profile defines `exclude: ["deprecated-search", "legacy-scraper"]`
- **THEN** skills whose names match the exclude list are removed from the loaded set

#### Scenario: Include and exclude together
- **WHEN** a profile defines both `include` and `exclude`
- **THEN** include is applied first (whitelist), then exclude removes from that set

#### Scenario: Profile with scopes filter
- **WHEN** a profile defines `scopes: [workspace, global]`
- **THEN** only skills whose `scope` metadata matches one of the listed scopes are included; skills without scope metadata are included by default

### Requirement: Active profile selection determines runtime skill set
The system SHALL select the active profile via `skills.active_profile` in configuration or `SKILLS_ACTIVE_PROFILE` environment variable. The flat `skills.directories` field SHALL NOT exist; all skill configuration flows through profiles.

#### Scenario: Explicit active profile
- **WHEN** `skills.active_profile` is set to `specialist-reviewer`
- **THEN** the loader uses the `specialist-reviewer` profile's directories and filters

#### Scenario: No profiles configured uses the built-in default profile
- **WHEN** neither `skills.active_profile` nor `skills.profiles` is set
- **THEN** the loader synthesizes a built-in `default` profile equal to `directories: [".agents/skills", "~/.tdt/skills"]`, `scopes: [repo, workspace, global]`, with no include/exclude, and uses it

#### Scenario: Active profile references a missing profile
- **WHEN** `skills.active_profile` names a profile not present in `skills.profiles`
- **THEN** loading raises `ConfigError` identifying the missing profile name

### Requirement: Profile selection is resolvable per-agent
The system SHALL allow each agent to select a skill profile independently of the process-global `active_profile`, so multiple agents in one process can load different skill sets.

#### Scenario: BaseAgent with explicit profile
- **WHEN** a `BaseAgent` is constructed with `skill_profile="reviewer"`
- **THEN** that agent resolves its skills through the `reviewer` profile regardless of `skills.active_profile`

#### Scenario: BaseAgent without explicit profile falls back to config
- **WHEN** a `BaseAgent` is constructed with `skill_profile=None`
- **THEN** the agent resolves skills through `skills.active_profile` (or the built-in `default` profile)

#### Scenario: Two agents in one process use different profiles
- **WHEN** a reviewer agent (`skill_profile="reviewer"`) and an explorer agent (`skill_profile="explorer"`) are constructed in the same process
- **THEN** each loads only the skills its profile resolves, with no cross-contamination

### Requirement: Profiles govern selection while the matcher governs relevance
The system SHALL apply profile filtering to determine the candidate skill set, then apply `SkillMatcher` ranking to determine task relevance. The two mechanisms SHALL be orthogonal.

#### Scenario: Profile reduces the matcher's candidate set
- **WHEN** a profile's filters yield 12 skills and the matcher's threshold would surface 3 for a task
- **THEN** the matcher ranks only the 12 profile-selected skills and returns its top matches from that set, never skills excluded by the profile

### Requirement: Skill metadata supports optional scope annotations
The system SHALL parse optional frontmatter fields from SKILL.md files: `scope`, `profiles`, `repositories`, `owners`, `conflicts_with`, and `replaces`.

#### Scenario: Skill with scope metadata
- **WHEN** a SKILL.md contains `scope: repo` in frontmatter
- **THEN** the parsed Skill model exposes `scope="repo"` and profile scopes filtering can use it

#### Scenario: Skill without scope metadata
- **WHEN** a SKILL.md has no `scope` field
- **THEN** the parsed Skill model has `scope=None` and the skill is included by default in all scope filters

#### Scenario: Skill with conflicts_with metadata
- **WHEN** a SKILL.md contains `conflicts_with: ["legacy-scraper"]`
- **THEN** the parsed Skill model exposes the conflicts list for diagnostics

#### Scenario: Unknown metadata fields are ignored
- **WHEN** a SKILL.md contains frontmatter fields not in the known set
- **THEN** parsing succeeds with `extra="ignore"` and no error is raised

### Requirement: Profile filtering happens after directory scan
The system SHALL scan all directories in the active profile, apply shadow rules, then apply profile include/exclude/scopes filters to produce the final active skill set.

#### Scenario: Shadow rule applies before filtering
- **WHEN** two directories contain a skill with the same name and the profile has no include/exclude
- **THEN** the earlier directory's version wins (existing shadow rule) and only one copy appears in the active set

#### Scenario: Excluded skill is removed after shadow resolution
- **WHEN** a skill appears in the first directory and is listed in `exclude`
- **THEN** the skill is removed from the active set regardless of directory precedence

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
