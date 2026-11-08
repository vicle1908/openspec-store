# agent-skills-standard-and-portability Specification

## Purpose
Defines the normative requirements for Agent Skills standard compliance (`agentskills.io`), self-contained inline script dependencies, machine-agnostic path portability, progressive disclosure boundaries, upstream vendor preservation, and automated workspace validation across all coding agents.

## Requirements

### Requirement: Agent Skills frontmatter schema compliance

Every locally-authored `SKILL.md` entry point SHALL start with YAML frontmatter containing only allowed top-level keys (`name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility`). The `name` MUST match its parent directory name and satisfy `^[a-z0-9]+(-[a-z0-9]+)*$`. The `description` MUST be non-empty and at most 1,024 UTF-8 bytes. Any client-specific, tool-specific, or custom attributes SHALL be nested inside the `metadata:` string-string map.

#### Scenario: Valid Agent Skills frontmatter passes schema check
- **WHEN** a skill declares conforming top-level fields and nests client extensions under `metadata:`
- **THEN** frontmatter validation SHALL accept the skill without warnings or schema errors
- **AND** the skill SHALL be eligible for catalog indexing and multi-agent discovery

#### Scenario: Unrecognized top-level frontmatter field fails schema validation
- **WHEN** a locally-authored skill declares top-level fields outside the allowed specification whitelist (such as top-level `user-invocable` or `argument-hint`)
- **THEN** validation SHALL reject the skill and report the invalid fields and required remediation

#### Scenario: Upstream vendor skills tracked in lockfile remain immutable
- **WHEN** an external vendor skill is tracked in `skills-lock.json`
- **THEN** local maintenance SHALL NOT mutate its frontmatter or forge its `computedHash`
- **AND** upstream update idempotency via `skills update -y` SHALL be preserved

### Requirement: Self-contained script dependencies and non-interactive execution

Executable scripts in a skill's `scripts/` directory SHALL be self-contained and execute without manual host package installation. Bundled Python scripts SHALL declare a `#!/usr/bin/env -S uv run` shebang and PEP 723 inline dependency metadata, executing via `uv run`. Bundled scripts MUST operate non-interactively without TTY prompts, taking arguments via CLI flags or streams.

#### Scenario: Python script executes in isolated ephemeral environment via uv run
- **WHEN** an agent executes a bundled Python script directly or via `uv run scripts/<name>.py`
- **THEN** the script SHALL resolve all required dependencies declared in its PEP 723 metadata block without relying on pre-installed host packages
- **AND** the script SHALL emit machine-readable output to stdout and diagnostics to stderr

#### Scenario: Script executes non-interactively without blocking
- **WHEN** a bundled script is executed in an unattended agent subshell
- **THEN** the script SHALL NOT prompt for interactive user confirmation or TTY input
- **AND** missing required parameters SHALL produce actionable error messages and exit with non-zero status

### Requirement: Machine-agnostic path portability across operating environments

Every skill instruction body, script, and reference document SHALL resolve filesystem paths dynamically using `$HOME`, `~`, or skill-relative paths (`scripts/`, `references/`, `assets/`). Skills MUST NOT contain hardcoded host user home paths (such as `/Users/<username>/`) or static platform paths that prevent execution across differing workstations, operating systems, or containers.

#### Scenario: Skill resolves paths portably across distinct user home directories
- **WHEN** a skill is executed on different workstations with different usernames (such as `/Users/androidteam` vs `/Users/vinhlk`)
- **THEN** all path resolutions SHALL evaluate dynamically to the current user's environment
- **AND** no command or script SHALL fail due to missing hardcoded path prefixes

#### Scenario: Hardcoded host user path fails portability audit
- **WHEN** a skill's instructions or scripts contain hardcoded `/Users/` paths
- **THEN** the portability audit SHALL flag the file and line number as a non-portable defect

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

### Requirement: Automated specification conformance and lockfile integrity gate

The workspace skill maintenance tooling (`platform/openspec-store/scripts/sync-workspace-agent-skills.py --check`) SHALL assert that all discoverable skills comply with the Agent Skills specification schema, directory-name matching, description byte limits, zero-hardcoded-path portability rules, and content-addressed hash integrity in `skills-lock.json`.

#### Scenario: Automated check validates all workspace skills
- **WHEN** `sync-workspace-agent-skills.py --check` is executed
- **THEN** it SHALL validate frontmatter keys against the specification whitelist on local skills, verify name-directory equality, enforce description byte caps, check for hardcoded host paths, and verify lockfile hash equality on locked skills
- **AND** any non-conforming skill SHALL cause the command to exit with non-zero status and report the exact violations

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
