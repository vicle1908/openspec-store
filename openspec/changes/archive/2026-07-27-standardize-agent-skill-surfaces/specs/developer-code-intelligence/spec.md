## MODIFIED Requirements

### Requirement: Skills-first agent integration

The repository SHALL expose a project-scoped Graphify Codex skill and
CLI-backed usage instructions, and SHALL expose GitNexus MCP plus its standard
Codex skills through one supported stable setup route. Skill installation SHALL
be idempotent, generator-owned files SHALL be marked as such, and strict
read-blocking behavior SHALL remain disabled. Native Graphify and GitNexus
platform layouts SHALL take precedence over a shared directory-level skill
symlink.

#### Scenario: Codex setup is performed

- **WHEN** a developer runs `gitnexus setup -c codex` followed by
  `graphify install --project --platform codex`
- **THEN** Codex receives GitNexus MCP and standard skills, the project receives
  Graphify `SKILL.md` plus references, and the Graphify marked `AGENTS.md`
  section and soft `PreToolUse` hook are installed

#### Scenario: Setup is repeated

- **WHEN** the same setup commands run twice against valid configuration files
- **THEN** MCP, skills, guidance sections, and Graphify hook entries are not
  duplicated

#### Scenario: Existing project hook JSON is invalid

- **WHEN** Graphify project setup encounters invalid `.codex/hooks.json`
- **THEN** setup stops before writing, reports the file as a manual repair
  blocker, and preserves the invalid file byte-for-byte

#### Scenario: Graphify strict mode is requested

- **WHEN** a setup command includes Graphify strict mode
- **THEN** the bootstrap rejects it for this rollout and directs the developer
  to the default soft hook

#### Scenario: Native project skill layouts are preserved

- **WHEN** Graphify and GitNexus install their project-native skill surfaces
- **THEN** `.agents/skills` remains the canonical shared surface while
  `.claude/skills` remains a real directory containing the native Graphify,
  GitNexus, generated, OpenSpec, and hand-authored layouts
