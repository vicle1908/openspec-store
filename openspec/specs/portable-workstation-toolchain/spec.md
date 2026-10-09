# portable-workstation-toolchain Specification

## Purpose

This capability defines reproducible, owner-aware macOS development tooling governed by standard Homebrew declarative configuration and native operator runbooks, minimizing customization and avoiding custom automation code.

## Requirements

### Requirement: Tool ownership and update authority SHALL follow vendor-supported precedence

Development tooling configuration SHALL declare exactly one authoritative installation owner and update authority per tool, prioritizing official Homebrew packages where vendor-supported, and classifying vendor standalone installers or global package managers as documented runbook exceptions. Conflicting duplicate installations SHALL be flagged for operator review without automated unmanaged deletion.

#### Scenario: Vendor-supported Homebrew package precedence
- **WHEN** an official Homebrew formula or cask is maintained and documented by the tool's upstream vendor (e.g. `cask "codex"`, `brew "bun"`, `brew "node"`, `brew "uv"`)
- **THEN** the configuration SHALL assign Homebrew as the authoritative installation owner and update authority
- **AND** the tool's update command SHALL map to standard Homebrew verbs (`brew upgrade --cask <tool>` or `brew upgrade <tool>`)

#### Scenario: Documented vendor standalone exception
- **WHEN** a tool has an official standalone binary installer but no maintained official Homebrew formula or tap (e.g. `qoder`)
- **THEN** the configuration SHALL classify the tool as a vendor standalone exception
- **AND** the setup runbook SHALL document the vendor-supported installation command and built-in update dispatcher (`qoder update`)

#### Scenario: Documented npm global exception
- **WHEN** a tool requires global npm installation and compiles native dependencies but lacks an official Homebrew package (e.g. `gitnexus`)
- **THEN** the configuration SHALL classify the tool as an npm global exception
- **AND** the setup runbook SHALL document the exact native npm installation command (`npm install -g gitnexus@latest`)

#### Scenario: Preserved isolated toolchain exception
- **WHEN** tools require pinned runtime dependencies or specific legacy compatibility that conflict with global packages (e.g. `newman` with Faker v5 compatibility)
- **THEN** the configuration SHALL retain the tool in an isolated directory toolchain (`~/.local/share/home-toolchain`)
- **AND** the configuration SHALL NOT force global migration or unmanaged deletion of the isolated lockfile

#### Scenario: Duplicate executable reported without unmanaged deletion
- **WHEN** multiple installations for a CLI are detected across different roots (e.g. Homebrew, npm-global, standalone)
- **THEN** the operator inventory inspection SHALL report the active path and all duplicate locations
- **AND** the tooling SHALL NOT perform automated or unmanaged deletion of detected duplicate files

### Requirement: Workstation configuration SHALL be declared via standard Homebrew Bundle and runbook

Workstation tooling SHALL be declared centrally in `platform/openspec-store` using a standard `config/Brewfile` (restricting stanzas to `tap`, `brew`, and `cask`) and an operator setup runbook in `docs/mac-development-setup.md`. The configuration SHALL avoid custom schemas, embedded shell hooks, or multi-ecosystem extensions, relying strictly on native Homebrew commands for inspection and installation.

#### Scenario: Declarative Brewfile authoring
- **WHEN** workstation tools are declared in `config/Brewfile`
- **THEN** the file SHALL declare only intentional direct tools using standard `tap`, `brew`, and `cask` stanzas
- **AND** the file SHALL NOT contain embedded Ruby scripts, shell execution hooks, or credentials

#### Scenario: Read-only bundle check with no upgrades by default
- **WHEN** preflight verification is executed against `config/Brewfile`
- **THEN** the operator SHALL run `HOMEBREW_NO_AUTO_UPDATE=1 brew bundle check --file config/Brewfile --no-upgrade`
- **AND** the check SHALL report missing dependencies without triggering automatic updates or package installations

#### Scenario: Repeated bundle install is idempotent
- **WHEN** `brew bundle install --file config/Brewfile --no-upgrade` is executed repeatedly against an aligned workstation
- **THEN** Homebrew SHALL confirm that all declared formulae, casks, and taps are satisfied
- **AND** no redundant rebuilds, package mutations, or configuration alterations SHALL occur

#### Scenario: Rejection of unmanaged ecosystem DSL extensions
- **WHEN** non-Homebrew packages (such as npm, uv, or cargo tools) are evaluated for inclusion in `config/Brewfile`
- **THEN** the configuration SHALL exclude them from the Brewfile to prevent dual-writer conflicts
- **AND** non-Homebrew tools SHALL be managed exclusively via their native package commands documented in the runbook

### Requirement: External execution and machine mutations SHALL require explicit operator authorization

All host-modifying actions—including package installations, upgrades, duplicate removals, service changes, and launchd adjustments—SHALL be executed directly by the human operator under explicit scope authorization. Planning artifacts in `platform/openspec-store` SHALL NOT execute host mutations, and operations SHALL NOT perform broad destructive filesystem deletions.

#### Scenario: Central store authoring boundary
- **WHEN** planning artifacts, Brewfile manifests, or setup runbooks are authored or updated
- **THEN** all file writes SHALL remain strictly within `platform/openspec-store`
- **AND** no external host directories, user profiles, or system roots SHALL be modified by planning tools

#### Scenario: Operator-scoped external execution
- **WHEN** package installations, removals, or service adjustments are required on the host
- **THEN** the actions SHALL be performed manually by the operator under explicit scope authorization
- **AND** the setup runbook SHALL provide exact, copy-pasteable native commands rather than executing automated scripts

#### Scenario: No unmanaged files cleanup or broad deletion
- **WHEN** disk hygiene or duplicate removal is performed
- **THEN** broad destructive commands (`rm -rf`, `brew bundle --force --cleanup`) SHALL NOT be executed
- **AND** removals SHALL target only specific, verified duplicate paths confirmed safe by the operator

#### Scenario: Pre- and post-mutation native verification smoke checks
- **WHEN** an approved tool is installed, updated, or normalized
- **THEN** the operator SHALL execute native smoke checks (`<tool> --version`, `<tool> help`) before and after the mutation
- **AND** if post-mutation verification fails, the operator SHALL halt further changes

#### Scenario: Rollback limitation acknowledged without guaranteed downgrade
- **WHEN** an upgraded package exhibits functional regressions
- **THEN** the runbook SHALL acknowledge that Homebrew does not guarantee automatic version rollbacks when older bottle revisions are purged upstream
- **AND** recovery procedures SHALL prescribe manual reinstallation of cached bottles or explicit fallback version recipes

### Requirement: Concurrency and maintenance runner controls SHALL use native operator mechanisms

Potential concurrency conflicts between manual package management and scheduled maintenance runners SHALL be managed using native operating system and process controls without modifying maintenance script code. Process-level pause flags SHALL be distinguished from persistent launchd job scheduling.

#### Scenario: Distinguishing process pause from scheduled job state
- **WHEN** `DISABLE_UPDATES=1` is exported in a user shell or environment
- **THEN** the setting SHALL pause mutation stages only for runner processes that inherit that environment variable
- **AND** the setting SHALL NOT be claimed to pause or suspend already running or persistently scheduled launchd jobs

#### Scenario: Operator-initiated persistent launchd pause
- **WHEN** manual toolchain updates or maintenance operations are performed by the operator
- **THEN** the operator SHALL persistently pause the scheduled daily updater using native launchctl commands (`launchctl disable` and `launchctl bootout`)
- **AND** no code modifications SHALL be made to `workstation-daily-update.sh` or its LaunchAgent plist

#### Scenario: Resuming scheduled maintenance after manual intervention
- **WHEN** manual maintenance is completed and verified
- **THEN** the operator SHALL conditionally re-enable the scheduled updater using native launchctl commands (`launchctl enable` and `launchctl bootstrap`) only after verifying runner compatibility
- **AND** the scheduled runner SHALL NOT be resumed if it would cause uncoordinated writer collisions with migrated Homebrew packages

### Requirement: Persistent state, secrets, and Docker volumes SHALL be protected

Development configuration and hygiene runbooks SHALL protect persistent local data, secret-bearing dotfiles, and named Docker volumes. Secrets and machine-local credentials SHALL be excluded from central manifests and runbooks, and Docker cleanup instructions SHALL enforce volume-preserving prune semantics.

#### Scenario: Nonportable secrets and credentials exclusion
- **WHEN** configuration manifests and runbooks are authored in `platform/openspec-store`
- **THEN** secret-bearing files (`~/.zshenv`), API keys, SSH keys, session tokens, and local passwords SHALL be strictly excluded
- **AND** documentation SHALL instruct operators to provide secrets out-of-band on secondary machines

#### Scenario: Protection of named Docker volumes
- **WHEN** routine Docker hygiene or disk cleanup instructions are documented
- **THEN** named Docker volumes—including OmniRoute's named SQLite volume `omniroute-data` (hyphenated) and database volumes—SHALL be explicitly documented as protected
- **AND** destructive commands that purge named volumes (`docker system prune --volumes` or `docker compose down -v`) SHALL be explicitly warned against

#### Scenario: Volume-preserving Docker prune enforcement
- **WHEN** disk reclamation is performed by the operator
- **THEN** the runbook SHALL prescribe volume-preserving commands (`docker system prune` without `--volumes` and without `-a`)
- **AND** all existing named volumes and persistent container storage SHALL remain completely intact

### Requirement: Knowledge documentation SHALL be maintained manually without automated publication

Toolchain setup, architectural decisions, and runbooks SHALL be maintained as local Markdown documents within `platform/openspec-store`. Operator documentation for AgentMemory and Notion SHALL prescribe manual CLI and REST operations, bypassing unverified automated synchronization scripts without implementing code changes.

#### Scenario: Central runbook documentation as source of truth
- **WHEN** workstation configuration, vendor decisions, or setup steps are documented
- **THEN** `docs/mac-development-setup.md` in `platform/openspec-store` SHALL serve as the version-controlled source of truth
- **AND** no custom documentation generation or synchronization engines SHALL be implemented

#### Scenario: Manual AgentMemory health check and decision recording
- **WHEN** AgentMemory service health or decisions are evaluated
- **THEN** health SHALL be verified via HTTP GET `http://localhost:3111/agentmemory/health` against the pinned engine
- **AND** toolchain decisions SHALL be recorded via supported AgentMemory CLI or REST tools without raw SQLite database edits

#### Scenario: Offline documentation availability
- **WHEN** the workstation operates without internet connectivity
- **THEN** all setup runbooks and `Brewfile` declarations in `platform/openspec-store` SHALL remain fully readable offline for inspection
- **AND** documentation SHALL explicitly state that package installations or formula updates require network connectivity or pre-warmed local bottle caches
- **AND** offline inspection SHALL NOT trigger network retry machinery or produce stalled synchronization locks

#### Scenario: Prohibition of automated external publication during planning
- **WHEN** planning artifacts are authored and revised
- **THEN** no automated publication to Notion or external services SHALL be executed
- **AND** unedited `sync-notion-knowledge.sh` SHALL be bypassed in favor of documented, operator-verified `ntn pages` commands when publication is explicitly authorized
