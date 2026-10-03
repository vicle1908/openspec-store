# ecosystem-tooling-and-skills-upgrade Specification

## Purpose
Defines formal requirements, baseline snapshots, verification sentinels, validation criteria, and daily scheduled automation for upgrading and maintaining developer runtimes, coding agent engines, utility CLIs, Homebrew casks, and cross-agent skills manifests.

## Requirements

### Requirement: Baseline state preservation and recovery snapshotting

The upgrade automation SHALL capture full inventory snapshots of all installed Homebrew casks, global npm packages, and store-wide OpenSpec validation results before executing any package modifications.

#### Scenario: Pre-upgrade snapshots are recorded
- **WHEN** the upgrade pipeline initializes
- **THEN** it SHALL write the active Homebrew bundle and global npm package list to local backup files
- **AND** it SHALL record the full strict validation baseline of `openspec-store`.

### Requirement: Desktop application and Homebrew cask modernization

The system SHALL upgrade identified outdated Homebrew casks without disruption to background services, and verify that container runtimes and network daemons remain operational post-upgrade.

#### Scenario: Homebrew casks are upgraded and verified
- **WHEN** outdated casks (`docker-desktop`, `zed`, `chatgpt`, `cleanmymac`, `onedrive`, `tailscale-app`, `gcloud-cli`, `postman-cli`, `cockpit-tools`, `copilot-cli`, `antigravity-cli`, `orca`, `droid`) are upgraded
- **THEN** the system SHALL invoke targeted cask upgrade commands
- **AND** verify that `docker ps` responds and existing Kind clusters remain accessible.

### Requirement: Developer utility CLIs and research tools alignment

The system SHALL upgrade global npm utility CLIs, align GitNexus to version `1.6.12` across all global prefixes, and update Graphify to version `0.9.68` via uv tool.

#### Scenario: Utility CLIs and intelligence tools are aligned
- **WHEN** utility CLIs are upgraded
- **THEN** `@brightdata/cli`, `@kilocode/cli`, `@qoder-ai/qodercli`, `codexuse-cli`, and `happy` SHALL be updated in `~/.npm-global`
- **AND** `gitnexus` SHALL be updated to `1.6.12` in `~/.npm-global`
- **AND** `graphifyy` SHALL be upgraded to `0.9.68` via `uv tool upgrade`.

### Requirement: Cross-agent skills ecosystem manifest reconciliation

The system SHALL regenerate Graphify platform skills across Pi, OpenCode, and Copilot, update user skill manifests with all unmapped skills, and ensure `sync-workspace-agent-skills.py` exits cleanly with code 0.

#### Scenario: Skills manifests are reconciled and verified
- **WHEN** the skills reconciliation phase executes
- **THEN** `graphify install --platform <platform>` SHALL be executed for `pi`, `opencode`, and `copilot`
- **AND** all 24 missing skills SHALL be declared in `codex-user-skill-manifest.txt` and `claude-user-skill-manifest.txt`
- **AND** `python3 ~/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py --check` SHALL exit with returncode 0.

#### Scenario: Undeclared user-scope links are declared rather than deleted
- **WHEN** user-scope fanout links exist whose names are absent from the codex manifest
- **THEN** each SHALL be declared in `config/codex-user-skill-manifest.txt` so the curation is explicit
- **AND** reconciliation SHALL NOT delete a resolvable fanout link merely because it is undeclared.

### Requirement: Coding agent CLIs upgrade and headless probe verification

The system SHALL upgrade Claude Code, OpenAI Codex, OpenCode, Droid, and Pi extensions, and SHALL verify each agent through live headless PONG execution probes.

#### Scenario: Coding agents are upgraded and probed
- **WHEN** coding agent packages are upgraded
- **THEN** `claude` SHALL be updated via `claude update` to `2.1.283`
- **AND** `@openai/codex` (`0.157.0`) and `opencode-ai` (`1.18.32`) SHALL be installed in `~/.npm-global`
- **AND** `pi` plugins (`pi-subagents`, `pi-mcp-adapter`, `pi-web-access`, `pi-lens`, `pi-intercom`) SHALL be updated in `~/.npm-global`
- **AND** each agent SHALL successfully execute a non-interactive probe command verifying model passthrough.

### Requirement: OpenSpec store validation gate and zero-regression enforcement

The system SHALL upgrade the OpenSpec CLI to version `1.13.2` and SHALL execute a full store validation across all 400 specs to verify zero new validation failures or schema regressions.

#### Scenario: OpenSpec validator is upgraded and store validated
- **WHEN** `@fission-ai/openspec` is upgraded to `1.13.2` in `~/.npm-global`
- **THEN** the system SHALL execute `openspec validate --all --strict --store openspec-store`
- **AND** the validation SHALL confirm zero regression delta compared to the pre-upgrade baseline.

### Requirement: Unified daily scheduled maintenance and check-and-update automation

The system SHALL deploy a unified daily maintenance script supporting `--check` and `--apply` modes, register a LaunchAgent scheduled daily at 08:00 AM, retire legacy failing update plists, and filter global npm package updates to prevent 404 errors on git-installed packages.

#### Scenario: Unified daily maintenance job is registered and verified
- **WHEN** daily maintenance automation is deployed
- **THEN** obsolete update LaunchAgents (`com.user.brew-npm-update` and `com.microservices.developer-workstation-tool-update`) SHALL be unloaded and disabled
- **AND** `~/Developer/scripts/workstation-daily-update.sh` SHALL execute across Homebrew, Bun, filtered npm, uv tools, coding agents, skills sync, and store validation
- **AND** `com.developer.workstation-daily-update.plist` SHALL be loaded into launchd and scheduled for daily execution at 08:00 AM.

### Requirement: Canonical skill store entries resolve to readable content

Every entry in the canonical store `~/Developer/.agents/skills/` SHALL resolve to a readable `SKILL.md` containing parseable frontmatter. A self-referential or dangling symlink SHALL be reported as a broken entry.

#### Scenario: Broken entries are reported
- **WHEN** canonical-root verification runs and an entry is a self-referential or dangling symlink
- **THEN** the entry SHALL be reported as broken
- **AND** verification SHALL exit non-zero.

#### Scenario: A repair restores real content
- **WHEN** a skill previously recorded as a broken entry is restored
- **THEN** `~/Developer/.agents/skills/<skill>/SKILL.md` SHALL exist as a regular readable file with parseable frontmatter
- **AND** the entry SHALL no longer be reported as broken.

#### Scenario: Unrecoverable skills are restored from an authoritative source
- **WHEN** a broken skill is recoverable from a declared upstream source
- **THEN** it SHALL be restored from that source
- **AND** when no upstream source exists, it SHALL be restored from an authoritative local backup copy rather than deleted.

#### Scenario: Entry points use the canonical filename casing
- **WHEN** a canonical entry resolves its `SKILL.md` on a case-insensitive filesystem
- **THEN** the on-disk filename SHALL use the canonical `SKILL.md` casing rather than a variant
- **AND** a store-wide scan SHALL report no entry whose on-disk casing differs from the canonical name.

#### Scenario: Non-official plugin directories do not shadow skill entry points
- **WHEN** a canonical entry contains a directory that would cause an agent to treat the entry as a plugin container
- **THEN** that directory SHALL be reported as a malformed entry, because it stops the catalog walk before `SKILL.md`
- **AND** a directory not part of the Agent Skills layout and absent from upstream sources SHALL be removed rather than retained.

#### Scenario: Undiscoverable entries fail verification
- **WHEN** verification runs against entries that resolve but are not discoverable
- **THEN** it SHALL name each affected entry and its defect
- **AND** verification SHALL exit non-zero so the scheduled maintenance step fails.

### Requirement: User-scope fanout links resolve to canonical content

Each entry in the user-scope fanout directory `~/.agents/skills/` SHALL resolve to the corresponding canonical skill or to an agent-owned skill root, so that agents whose discovery depends on user scope reach workspace skills regardless of working directory.

#### Scenario: Fanout entries resolve from any working directory
- **WHEN** an agent resolves a declared user-scope skill entry
- **THEN** that entry SHALL resolve to a readable `SKILL.md`
- **AND** resolution SHALL NOT depend on the process working directory.

#### Scenario: User-scope coverage survives leaving the workspace directory
- **WHEN** an agent enumerates skills from a working directory outside the workspace root
- **THEN** skills that are only reachable through project scope SHALL be absent, as the official project scope is working-directory-relative
- **AND** skills declared in user scope SHALL remain reachable.

#### Scenario: Unresolved fanout entries are detected
- **WHEN** a user-scope fanout entry does not resolve to readable content
- **THEN** verification SHALL report it as broken
- **AND** reconciliation SHALL NOT report success while it remains unresolved.

### Requirement: Scheduled maintenance fails closed on unresolved skill links

The scheduled skills maintenance step SHALL treat any unresolved canonical or fanout skill link as a failure condition and SHALL NOT report success while such links remain.

#### Scenario: Broken links fail the maintenance run
- **WHEN** the scheduled skills parity step runs and one or more skill links are unresolved
- **THEN** the step SHALL report failure
- **AND** the overall maintenance run SHALL NOT conclude with a success status.

#### Scenario: Reconciliation that does not resolve the failure still fails
- **WHEN** the scheduled step attempts reconciliation and unresolved links remain afterward
- **THEN** re-verification SHALL report failure
- **AND** the overall maintenance run SHALL NOT conclude with a success status.

#### Scenario: Clean state passes the maintenance run
- **WHEN** the scheduled skills parity step runs and no skill link is unresolved
- **THEN** the step SHALL report success.
