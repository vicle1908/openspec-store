# ponytail-agent-skills Specification

## Purpose

Defines the installation, lockfile provenance tracking, multi-agent discovery fanout, recurring `npx skills update` refresh compatibility, and runtime hook/statusline non-interference contract for the official `DietrichGebert/ponytail` Agent Skills suite across the developer workspace.

## Requirements

### Requirement: Canonical Ponytail skill installation and lockfile tracking

The workspace SHALL maintain the six official `DietrichGebert/ponytail` skills (`ponytail`, `ponytail-review`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help`) as canonical directories under `~/Developer/.agents/skills/` and MUST record their GitHub source, `skills/<name>/SKILL.md` paths, and computed hashes in both `~/Developer/skills-lock.json` and `~/Developer/.agents/skills-lock.json`.

#### Scenario: Official skills are installed and recorded in workspace lockfiles
- **WHEN** `/opt/homebrew/bin/skills add DietrichGebert/ponytail --skill '*' --agent universal claude-code hermes-agent -y` is executed in `~/Developer/` and lockfile entries are synchronized
- **THEN** `~/Developer/.agents/skills/` SHALL contain direct child directories `ponytail`, `ponytail-review`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, and `ponytail-help`, each with an uppercase `SKILL.md`
- **AND** both `~/Developer/skills-lock.json` and `~/Developer/.agents/skills-lock.json` SHALL record each skill with `"source": "DietrichGebert/ponytail"`, `"sourceType": "github"`, and `"skillPath": "skills/<name>/SKILL.md"`

#### Scenario: Exact skillPath disambiguates OpenClaw duplicate paths during updates
- **WHEN** `skills update -y` clones `DietrichGebert/ponytail` with `fullDepth: true` and discovers both `skills/<name>/SKILL.md` and `.openclaw/skills/<name>/SKILL.md`
- **THEN** the recorded `"skillPath": "skills/<name>/SKILL.md"` SHALL disambiguate each skill via `exactPathDisambiguates`
- **AND** `skills update -y` SHALL emit zero `Multiple current paths match` warnings for `DietrichGebert/ponytail`

### Requirement: Multi-agent manifest declaration and user-scope symlink fanout

All six `ponytail*` skill slugs SHALL be declared in both `platform/openspec-store/config/codex-user-skill-manifest.txt` and `platform/openspec-store/config/claude-user-skill-manifest.txt` so `sync-workspace-agent-skills.py` reconciles user-scope symlinks into `~/.agents/skills/` and `~/.claude/skills/`.

#### Scenario: Workspace skill synchronizer links Ponytail skills cleanly
- **WHEN** `python3 ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py --check` is executed after manifest declaration and reconciliation
- **THEN** the command SHALL exit with status code `0` and report `malformed_entries=0`, `conflicts=0`, and `broken=0`
- **AND** `~/.agents/skills/<name>` and `~/.claude/skills/<name>` for all six `ponytail*` skills SHALL resolve as symlinks to `/Users/androidteam/Developer/.agents/skills/<name>`

#### Scenario: Workspace project agent mirrors and Codex isolation are preserved
- **WHEN** `DietrichGebert/ponytail` skills are installed and synchronized in `~/Developer/`
- **THEN** `~/Developer/.claude/skills/ponytail*` and `~/Developer/.hermes/skills/ponytail*` SHALL resolve as relative symlinks (`../../.agents/skills/<name>`)
- **AND** `~/Developer/.codex/skills/` SHALL remain restricted to `.system/` and `migrate-to-codex` without duplicate shared skill copies

### Requirement: Unmodified upstream content for idempotent npx skills updates

The canonical `~/Developer/.agents/skills/ponytail*/SKILL.md` files MUST remain unmodified upstream copies so on-demand `npx skills update` (or `skills update -y`) and scheduled daily maintenance (`shb-schedule` `step_skills_refresh` and `workstation-daily-update.sh` Stage 11) refresh them cleanly without local merge conflicts or frontmatter validation failures.

#### Scenario: On-demand and scheduled skill updates succeed idempotently
- **WHEN** `skills update -y` or `/opt/homebrew/bin/skills update ponytail ponytail-review ponytail-audit ponytail-debt ponytail-gain ponytail-help -y` executes in `~/Developer/`
- **THEN** the CLI SHALL check `https://github.com/DietrichGebert/ponytail.git` against `~/Developer/skills-lock.json` and exit with status code `0`
- **AND** every refreshed `SKILL.md` frontmatter description SHALL remain within the 1,024 UTF-8 byte `skill-index-hygiene` ceiling

#### Scenario: Upstream unreachable during refresh degrades gracefully
- **WHEN** `https://github.com/DietrichGebert/ponytail.git` is unreachable during a scheduled refresh
- **THEN** existing `~/Developer/.agents/skills/ponytail*/SKILL.md` files and symlinks SHALL remain intact
- **AND** the refresh stage SHALL report the failure without aborting subsequent maintenance stages

### Requirement: Skills-only boundary preserving existing hooks and statusline telemetry

The adoption of `DietrichGebert/ponytail` SHALL strictly follow the official Skills CLI installation tier (`skills/*/SKILL.md` only) and MUST NOT install Ponytail's runtime Node.js lifecycle hooks, `ponytail-map.js` regex scanner, Pi/OMP runtime extension, or Claude Code `band` / `statusLine` scripts.

#### Scenario: Orca Claude Code statusline and AgentMemory hooks remain unmutated
- **WHEN** Ponytail skills are installed and updated in the workspace
- **THEN** `~/.claude/settings.json` `statusLine` SHALL remain bound to `/Users/androidteam/.orca/agent-hooks/claude-statusline.sh`
- **AND** no `~/.claude/.ponytail-active` flag, `~/.claude/ponytail-statusline.sh` script, or Ponytail `SessionStart`/`SubagentStart`/`UserPromptSubmit` hook entry SHALL be added to `~/.claude/settings.json`, `~/Developer/.claude/settings.json`, or `~/.codex/hooks.json`
