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
