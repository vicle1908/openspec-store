## ADDED Requirements

### Requirement: First-class install into the TDT skills root via `npx skills add --copy`
The TDT workspace SHALL install the `callstack/agent-device` bundled skill into the **first-class TDT skills root** (`tdt-meta/.agents/skills/agent-device/SKILL.md`) by running `npx skills add callstack/agent-device -a universal -a codex -a cursor --copy -y` from the `tdt-meta/` directory. The `--copy` flag SHALL be used so the installed `SKILL.md` is a regular file (not a symlink) and is committed to git alongside the 95 existing TDT skills.

#### Scenario: Skill install succeeds with the canonical `.agents/skills/` path
- **WHEN** the operator runs `npx skills add callstack/agent-device -a universal -a codex -a cursor --copy -y` from `tdt-meta/`
- **THEN** the skill file is created at `tdt-meta/.agents/skills/agent-device/SKILL.md` as a regular file
- **AND** the skill's `name` frontmatter field is `agent-device`
- **AND** the file is committed to git (verifiable via `git ls-files tdt-meta/.agents/skills/agent-device/SKILL.md`)

#### Scenario: Skill install lands in `.claude/skills/` only (rejected)
- **WHEN** the operator runs `npx skills add callstack/agent-device -a claude-code -y` from `tdt-meta/`
- **THEN** the skill file is created at `tdt-meta/.claude/skills/agent-device/SKILL.md` instead of `.agents/skills/`
- **AND** `config/codex/scripts/build-skills-index.sh` does NOT discover the skill
- **AND** the spec treats this as the wrong install location for TDT

#### Scenario: Default symlink install (rejected for git portability)
- **WHEN** the operator runs `npx skills add callstack/agent-device -a universal -a codex -a cursor -y` (without `--copy`)
- **THEN** the installed `SKILL.md` is a symlink into the operator's `npx` cache
- **AND** the symlink breaks on other contributors' machines after `git pull` (broken symlink)
- **AND** the spec treats this as the wrong install method for committed skills

#### Scenario: Skill install fails (npx not available)
- **WHEN** `npx` is not available on the operator machine
- **THEN** the skill installation fails with a clear message directing the operator to install Node.js >= 22 first

#### Scenario: Skill is already installed and is refreshed
- **WHEN** `npx skills add callstack/agent-device -a universal -a codex -a cursor --copy -y` is run and the skill already exists
- **THEN** the skill file is overwritten with the latest version from the callstack registry without prompting
- **AND** the operator can `git diff tdt-meta/.agents/skills/agent-device/SKILL.md` to inspect the upstream changes

### Requirement: Operator-level CLI install with a pinned version is mandatory
The operator SHALL install `agent-device` globally via `npm install -g agent-device@<pinned-version>` where `<pinned-version>` is a specific version chosen by the operator (the current latest is `0.17.6`; the version floor is `>= 0.14.0`). The agent MUST NOT run `npm install -g agent-device@<pinned-version>`, `npm install -g agent-device@latest`, or `npx -y agent-device@<latest|pinned-version>` without an explicit user prompt per turn. The version pin is the operator's choice; the agent's job is to verify (`agent-device --version` returns a string `>= 0.14.0`) and use it.

#### Scenario: Agent encounters missing agent-device binary
- **WHEN** the agent runs `agent-device --version` and the binary is not on PATH
- **THEN** the agent MUST report the missing binary and print the exact install command the user should run: `npm install -g agent-device@<pinned-version>`
- **AND** the agent MUST NOT run any npm install command autonomously
- **AND** the agent MUST NOT include a version/upgrade command in any plan it presents to the user without explicit approval

#### Scenario: Binary missing but operator has a global install
- **WHEN** the binary is not on the agent's PATH but the operator has it installed globally
- **THEN** the agent SHALL resolve the absolute binary path by checking the operator's shell environment, npm global prefix (`npm config get prefix`), or package manager location
- **AND** the agent MUST NOT silently fall back to `npx -y agent-device@latest`

#### Scenario: Operator provides a pinned version
- **WHEN** the operator specifies `agent-device@<pinned-version>`
- **THEN** the agent SHALL verify the installed version matches the specified version via `agent-device --version` and proceed only if the result is `>= 0.14.0`

#### Scenario: Installed version is below the floor
- **WHEN** `agent-device --version` returns a version string below `0.14.0`
- **THEN** the agent MUST stop and tell the user to upgrade their trusted install to `>= 0.14.0`
- **AND** the agent MUST NOT autonomously run `npm install -g agent-device@latest` or `npx -y agent-device@latest`
- **AND** the agent MUST NOT include a version/upgrade command in any plan it presents to the user without explicit approval

### Requirement: Operator-side prerequisites are documented
The skill SHALL include a reference section that documents the operator-side prerequisites that MUST be met before any device verification work.

#### Scenario: iOS verification requested but Xcode is missing
- **WHEN** the operator attempts iOS verification without Xcode installed
- **THEN** the skill's prerequisite table documents that Xcode and Command Line Tools are required for iOS targets

#### Scenario: Android verification requested but Android SDK is missing
- **WHEN** the operator attempts Android verification without the Android SDK
- **THEN** the skill's prerequisite table documents that Android SDK and ADB are required for Android targets

#### Scenario: Desktop verification requested but Accessibility permission not granted
- **WHEN** the operator attempts macOS desktop automation without granting Accessibility permission
- **THEN** the skill documents that macOS Accessibility permission is required for desktop targets

### Requirement: Skill is read-only; TDT workspace overrides go in `.agents/INDEX.md`
The TDT workspace SHALL NOT modify the installed Callstack skill file (it is an upstream-mirrored copy refreshed via `npx skills add ... --copy`). Any TDT-specific configuration rules SHALL be added to `.agents/INDEX.md` or a TDT-specific supplemental document, not to the installed `SKILL.md`.

#### Scenario: TDT needs a workspace-specific device name rule
- **WHEN** TDT needs a rule such as "always use simulator named `iPhone 16`"
- **THEN** the rule is added to `.agents/INDEX.md` as a supplemental bullet under the "Mobile Device Automation" section; the installed `SKILL.md` is not modified

### Requirement: Skill is discoverable by the TDT skills index builder
The skill SHALL be discoverable by `config/codex/scripts/build-skills-index.sh` and SHALL appear in both the human-readable `.agents/SKILLS_INDEX.md` and the generated `.codex/skills-index.json` after a build run.

#### Scenario: Index build picks up the new skill
- **WHEN** the operator runs `bash config/codex/scripts/build-skills-index.sh` from `tdt-meta/` after the skill is installed
- **THEN** `jq '.skills[] | select(.name == "agent-device")' tdt-meta/.codex/skills-index.json` returns the new entry
- **AND** `tdt-meta/.agents/SKILLS_INDEX.md` lists `agent-device` under a "Mobile Device Automation" category
- **AND** the total count in `.agents/SKILLS_INDEX.md` increments from 95 to 96

### Requirement: Skill stays a thin router; TDT-specific rules live in TDT-owned files
The TDT workspace SHALL keep the installed Callstack skill a thin router. Per upstream `callstack/agent-device` AGENTS.md, the skill must focus on when to use the skill, version gating, which `agent-device help <topic>` page to read, and a short default loop. The TDT-specific documentation layer lives in the OpenSpec (`agent-device-command-surface`, `agent-device-verify-loop`) and in `.agents/INDEX.md`, NOT in the skill.

#### Scenario: TDT needs a TDT-specific rule
- **WHEN** TDT needs a TDT-specific rule (e.g., "use the POEMS Mobile 3 staging simulator name")
- **THEN** the rule is added to `.agents/INDEX.md` or to the OpenSpec, not to the installed `SKILL.md`
- **AND** the next `npx skills add callstack/agent-device --copy -y` refresh will not overwrite the TDT-specific rule (because the rule is in TDT-owned files, not in the skill)
