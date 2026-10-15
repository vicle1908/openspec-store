# Spec Delta

## ADDED Requirements

### Requirement: Official Google Workspace agent skills SHALL be maintained via npx skills

The workspace SHALL maintain official Google Workspace Agent Skills (`gws-*`) sourced from upstream `googleworkspace/cli` via `npx skills` in canonical skill roots under `~/Developer/.agents/skills/`, with symlinks established under `~/Developer/.claude/skills/` for Claude Code and state tracked in `~/Developer/.agents/skills-lock.json`. Each skill root contains an official `SKILL.md` specifying command syntax, parameters, and output contracts for `/opt/homebrew/bin/gws`.

#### Scenario: Agent discovers official Google Workspace Calendar skill
- **GIVEN** an agent operates within an independent workspace repository
- **WHEN** the agent invokes or searches for Google Workspace calendar capabilities
- **THEN** the agent SHALL discover `gws-calendar` in `.agents/skills/`
- **AND** the skill entry SHALL reference `/opt/homebrew/bin/gws` subcommands with structured JSON output

#### Scenario: User-scope synchronization exposes official GWS skills
- **GIVEN** `gws-calendar` is registered in `codex-user-skill-manifest.txt`
- **WHEN** `sync-workspace-agent-skills.py` executes
- **THEN** `~/.agents/skills/gws-calendar` SHALL be created as a link to `~/Developer/.agents/skills/gws-calendar`
- **AND** no duplicate copy SHALL be created in product-specific configuration roots

### Requirement: Official Google Workspace skills SHALL support upstream updates via npx skills update

Official Google Workspace skills tracked in `~/Developer/.agents/skills-lock.json` SHALL support recurring automated synchronization against upstream releases using `npx skills update`.

#### Scenario: Updating skills brings latest upstream enhancements
- **WHEN** `npx skills update` runs in `~/Developer/`
- **THEN** the skill manager SHALL query upstream `googleworkspace/cli` for changes
- **AND** updated `SKILL.md` definitions SHALL be synchronized into `.agents/skills/` and `.claude/skills/` with refreshed lockfile hashes
