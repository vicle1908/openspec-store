# Spec Delta: agent-skills-standard-and-portability

## ADDED Requirements

### Requirement: Zero-shadowing client skill symlink integrity
All client-specific skill roots (`~/.claude/skills/`, `~/.agents/skills/`, `~/Developer/.claude/skills/`) SHALL expose shared agent skills exclusively via relative symlinks pointing to canonical workspace skills in `~/Developer/.agents/skills/`. Duplicate physical skill directories and uncanonical alias symlinks SHALL NOT exist in client skill roots.

#### Scenario: User-level Claude skill root uses canonical symlinks
- **WHEN** inspecting shared skills in `~/.claude/skills/`
- **THEN** every shared skill entry SHALL be a valid symbolic link resolving to `~/Developer/.agents/skills/<name>`
- **AND** no duplicate physical skill directories SHALL exist to shadow canonical skills

#### Scenario: Uncanonical skill alias is rejected
- **WHEN** a symlink in a skill root maps an alias directory name (such as `computer-use`) to a differently-named canonical skill (`orca-computer-use`)
- **THEN** validation SHALL flag the alias as a name-directory mismatch violation
- **AND** the uncanonical alias symlink SHALL be removed

### Requirement: Bundled skill script executable permissions
All executable helper scripts bundled within a skill's `scripts/` directory SHALL have POSIX execute permissions (`0755` / `chmod +x`).

#### Scenario: Bundled script executes without permission errors
- **WHEN** an agent executes a bundled shell or Python script in a skill's `scripts/` directory
- **THEN** the operating system SHALL execute the script directly
- **AND** execution SHALL NOT fail with `Permission denied` (EACCES)

## MODIFIED Requirements

### Requirement: Progressive disclosure layout and size boundaries
Skills SHALL follow the 3-tier progressive disclosure model: Tier 1 (name and description), Tier 2 (`SKILL.md` body, <= 500 lines), and Tier 3 (on-demand `references/`, `scripts/`, `assets/`). Locally authored skills exceeding 500 lines SHALL factor secondary documentation, schemas, and walkthroughs into `references/` or `assets/` with conditional triggers in `SKILL.md`. Upstream vendor skills tracked in `skills-lock.json` SHALL remain exempt from local file splitting.

#### Scenario: Lean skill body delegates deep references to secondary files
- **WHEN** a locally authored skill defines extensive domain documentation or schema catalogs
- **THEN** the `SKILL.md` body SHALL remain under 500 lines and cite the relative path in `references/`
- **AND** the instruction SHALL specify the exact condition under which the agent should read the reference

#### Scenario: Upstream vendor skill integrity preserved
- **WHEN** an upstream vendor skill tracked in `skills-lock.json` exceeds 500 lines
- **THEN** the file SHALL NOT be split into local reference files
- **AND** its upstream layout and provenance hash SHALL remain tracked without divergence

#### Scenario: Locally authored skill body stays within size budget
- **WHEN** validating locally authored skills in `~/Developer/.agents/skills/` or `openspec-store`
- **THEN** every local `SKILL.md` body SHALL NOT exceed 500 lines
- **AND** detailed guides and templates SHALL be located in `references/` or `assets/`
