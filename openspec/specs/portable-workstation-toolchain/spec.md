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
- **WHEN** a tool has an official standalone binary installer but no maintained official Homebrew formula or tap (e.g. `qoder`, `kimi`)
- **THEN** the configuration SHALL classify the tool as a vendor standalone exception
- **AND** the setup runbook and `toolchain_updater_registry.py` SHALL document the vendor-supported installation root and built-in update dispatcher (`qodercli update`, `kimi update`)
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

#### Scenario: Decoupled version probing and standalone registry parity
- **WHEN** the maintenance engine probes and updates covered coding agent CLIs (`claude`, `codex`, `pi`, `kilo`, `qoder`, `kimi`)
- **THEN** pre- and post-update version checks SHALL invoke each agent's own binary (`codex --version`, `qodercli --version`, `kimi --version`) rather than probing the package manager executable (`npm --version`)
- **AND** `STANDARD_PATH` SHALL include `~/.kimi-code/bin`, `~/.local/bin`, and `~/.npm-global/bin` so standalone binaries resolve deterministically

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

### Requirement: Mac App Store applications SHALL be discovered and safely updated with running-process exclusion

The workstation maintenance engine SHALL discover outdated Mac App Store applications via `mas outdated` and SHALL upgrade idle applications while strictly skipping applications currently active in the user session, executing completely non-interactively without privilege elevation.

#### Scenario: Outdated Mac App Store discovery
- **WHEN** the maintenance pipeline reaches the Mac App Store update step
- **THEN** it SHALL execute `mas outdated` non-interactively to determine pending application updates
- **AND** it SHALL parse each pending application's numeric identifier and full multi-word application name (such as `Telegram 2` or `Parallels Desktop`) matching regex `^(\d+)\s+(.+?)\s+\((.+?)\s*->\s*(.+?)\)$` and character class `^[A-Za-z0-9 ._@/+-]+$`
#### Scenario: Running application update exclusion
- **WHEN** an outdated Mac App Store application is actively running in the host session (detected via `pgrep -x "$APP_NAME"`, ignoring updater subprocesses)
- **THEN** the maintenance pipeline SHALL skip upgrading that application
- **AND** it SHALL record that the application was skipped due to an active process lock
- **AND** it SHALL NOT terminate, disrupt, signal, or restart the running application

#### Scenario: Non-interactive unattended execution and privilege boundaries
- **WHEN** `mas upgrade "$APP_ID"` is invoked for an idle application
- **THEN** the command SHALL execute without `sudo` and without requesting interactive password or Keychain prompts
- **AND** multi-gigabyte bundles exceeding unattended window bounds (such as `Xcode` `497799835`) SHALL be explicitly skipped with a recorded reason rather than timing out at 300 seconds and degrading the run
---

### Requirement: Global package ecosystems SHALL maintain initialized manifests and non-interactive update paths

All global package managers (NPM, Bun, and UV) SHALL maintain valid global manifests, SHALL execute upgrades dynamically using sanitized identifiers without hardcoded package lists or clobbering pinned coding agent binaries, SHALL keep `~/.npm-global/bin` and `~/.npm-global/lib/node_modules` free of orphaned `.bin-HASH` retired symlinks and empty `@scope` directories, and SHALL document that `npm audit -g` is unsupported (`EAUDITGLOBAL`) despite `npm update -g` printing a quick-audit summary.

#### Scenario: Bun global manifest initialization
- **WHEN** Bun global packages are audited or updated
- **THEN** the maintenance pipeline SHALL verify the existence of `~/.bun/install/global/package.json`
- **AND** if absent, it SHALL initialize directory `~/.bun/install/global` with mode `0700` and write an empty dependencies object `{}` before running package commands
- **AND** it SHALL execute `bun upgrade` followed by `bun update -g` non-interactively

#### Scenario: Dynamic uv tool list upgrade with sanitized arguments
- **WHEN** Python standalone CLI tools are upgraded
- **THEN** the maintenance pipeline SHALL query installed tools dynamically via `uv tool list`
- **AND** it SHALL validate each tool identifier against character class `^[A-Za-z0-9._@/+-]+$`
- **AND** it SHALL pass each validated tool name as a discrete argument preceded by `--` to `uv tool upgrade -- "$TOOL"`
- **AND** it SHALL execute upgrades in isolated venvs rather than relying on a static hardcoded package list

#### Scenario: NPM global upgrades exclude pinned coding agents
- **WHEN** `npm outdated -g --json` identifies outdated packages in `~/.npm-global`
- **THEN** the upgrade process SHALL validate discovered package names against `^[A-Za-z0-9._@/+-]+$`
- **AND** it SHALL filter out all tools declared in the authoritative deny and pinned agent rosters (`codex`, `claude`, `pi`, `kilo`)
- **AND** only non-governed packages SHALL be upgraded via `npm install -g -- "$PKG@latest"`

#### Scenario: NPM global prefix directory hygiene and EAUDITGLOBAL documentation
- **WHEN** `~/.npm-global/bin` and `~/.npm-global/lib/node_modules` are inspected after global npm maintenance
- **THEN** no dangling retired `.bin-HASH` dot-symlinks (such as `.amp-*`, `.dgrep-*`, `.tsc-*`) SHALL remain in `~/.npm-global/bin` and no empty `@*` scope directories SHALL remain in `~/.npm-global/lib/node_modules`
- **AND** workstation runbook and audit evidence SHALL record that `npm audit -g` fails by npm design with `EAUDITGLOBAL` and that global package trees (`@agentmemory/agentmemory` and `happy`) MUST be audited per-package in isolated temporary lockfiles rather than by running `npm audit fix` in `~/Developer`

### Requirement: Scheduled maintenance SHALL execute via durable workflow with discrete step recovery, strict isolation, and structured telemetry

Daily workstation maintenance SHALL be orchestrated as a durable, multi-step workflow registered under `shb-schedule`, guaranteeing checkpointed progress, strict file permission boundaries, credential isolation, and immutable JSON run reports.

#### Scenario: Declarative schedule manifest registered under shb-schedule
- **WHEN** workstation update scheduling is inspected
- **THEN** a validated YAML manifest conforming to `shb-schedule/v1` SHALL exist in `~/.shb/schedules/workstation-daily-update.yaml` with mode `0600` inside directory mode `0700`
- **AND** the manifest SHALL declare `execution_target: host`, schedule `0 8 * * *`, timezone `Asia/Ho_Chi_Minh`, timeout bounds of 3600s, and a maximum of 2 retry attempts

#### Scenario: Step-level failure isolation and checkpoint recovery
- **WHEN** a transient network or rate-limit error occurs during a specific step (e.g. remote skills git pull)
- **THEN** the durable execution engine SHALL record the error for that step
- **AND** prior successfully completed steps SHALL remain checkpointed without requiring full execution replay on retry
- **AND** `step_integrity_and_store_validation` SHALL execute `openspec validate` with explicit working directory `~/Developer/platform/openspec-store`

#### Scenario: Secret isolation in telemetry and alerts
- **WHEN** a maintenance run finishes or encounters failures
- **THEN** the workflow SHALL load communication tokens strictly from `~/.shb/.env` at runtime without logging or exporting secret values
- **AND** alert notifications SHALL be dispatched to the Telegram channel ONLY when the run status is degraded or failed (`status not in ("SUCCESS", "completed")`), never on clean `SUCCESS` runs
- **AND** `workstation-daily-update.sh` SHALL NOT duplicate stdout lines via `tee -a` when standard output is already redirected to the log file by `launchd`
#### Scenario: Structured JSON run telemetry file modes
- **WHEN** a maintenance run completes
- **THEN** the runner SHALL write an immutable telemetry report to `~/Developer/data/updates/YYYY-MM-DD.json` with file mode `0600` inside directory mode `0700`

---

### Requirement: Obsolete updater plists and uncoordinated duplicate scripts SHALL be deprecated and safely retired via explicit allowlist

The workspace SHALL eliminate competing, disabled, and uncoordinated auto-update artifacts, reconciling script copy drift and maintaining a single authoritative maintenance pipeline under strict authorization boundaries.

#### Scenario: Allowlist-bound removal of disabled duplicate LaunchAgents
- **WHEN** workstation LaunchAgents are retired
- **THEN** the removal SHALL be strictly limited to allowlisted paths `~/Library/LaunchAgents/com.user.brew-npm-update.plist.disabled` and `~/Library/LaunchAgents/com.microservices.developer-workstation-tool-update.plist.disabled`
- **AND** each target file SHALL be verified as a regular file (not a symlink) before removal
- **AND** `launchctl bootout` SHALL be invoked if the job label is active before removing the plist
- **AND** glob-based wildcards SHALL NOT be used for LaunchAgent deletion

#### Scenario: Allowlist-bound removal of uncoordinated duplicate scripts
- **WHEN** legacy updater scripts are retired
- **THEN** the removal SHALL be strictly limited to allowlisted paths `~/.local/bin/brew-npm-update.sh` and `~/Library/Application Support/com.microservices.developer-workstation-tool-update/`
- **AND** each path SHALL be verified as an existing regular file or directory (not a symlink) before removal

#### Scenario: Script copy drift reconciliation against store mirror
- **WHEN** `~/Developer/scripts/workstation-daily-update.sh` and its version-controlled mirror in `platform/openspec-store/scripts/` are checked
- **THEN** both copies SHALL match the expected SHA-256 byte digest recorded in `platform/openspec-store/config/script-provenance-manifest.tsv`
- **AND** any detected drift SHALL halt the validation step and raise a degradation notice

### Requirement: Kimi Code CLI SHALL maintain official vendor standalone installation and single-owner PATH resolution

The Kimi coding agent SHALL be installed exclusively through Moonshot AI's official standalone native installer, isolated in `~/.kimi-code/bin`, eliminating outdated Homebrew shims, and resolving consistently across login and interactive shells.

#### Scenario: Vendor-supported standalone native installation
- **WHEN** Kimi Code CLI is provisioned or upgraded
- **THEN** it SHALL be installed using Moonshot AI's official installer into `~/.kimi-code/bin/kimi`
- **AND** outdated Homebrew formulae (`kimi-code`) SHALL be uninstalled to avoid path shadowing and version drift

#### Scenario: Single-owner PATH resolution
- **WHEN** user and system login, interactive, and non-login subshells execute
- **THEN** `export PATH="$HOME/.kimi-code/bin:$PATH"` SHALL be declared in shell profiles
- **AND** a companion symlink `~/.local/bin/kimi -> ~/.kimi-code/bin/kimi` SHALL ensure non-login subshells resolve the binary
- **AND** all instances SHALL resolve to the single authoritative binary in `~/.kimi-code/bin/kimi`
#### Scenario: Legacy data migration to kimi-code
- **WHEN** legacy Kimi data exists in `~/.kimi`
- **THEN** `kimi migrate --run` SHALL migrate configurations, MCP servers, history, and sessions into `~/.kimi-code`
- **AND** a completion marker SHALL be recorded to prevent repeated interactive migration prompts

### Requirement: Meta Muse Code CLI SHALL be governed under Homebrew cask `muse-code` with explicit collision disambiguation

Meta Muse Code (`muse`) SHALL be installed and updated exclusively through the official Homebrew cask `muse-code` (`/opt/homebrew/bin/muse`), registered in the workstation toolchain authority, manifest, and coverage registries as a Homebrew-managed cask, and explicitly disambiguated from the unrelated disabled desktop cask `muse`.

#### Scenario: Official Homebrew cask installation and single-owner PATH resolution
- **WHEN** Meta Muse Code CLI is provisioned or audited on macOS `arm64`
- **THEN** it SHALL be installed via `brew install --cask muse-code` into `/opt/homebrew/Caskroom/muse-code/` with its canonical executable symlinked at `/opt/homebrew/bin/muse`
- **AND** `which -a muse` across login and interactive shells SHALL resolve exclusively to `/opt/homebrew/bin/muse` without unmanaged duplicate binaries in `~/.local/bin` or `~/.npm-global/bin`

#### Scenario: Toolchain updater registry, manifest, and inventory disambiguation from disabled cask `muse`
- **WHEN** `toolchain_updater_registry.py`, `inventory-workstation-toolchain.py`, `config/workstation-toolchain-manifest.json`, and `reconcile-agent-cli-coverage.py` evaluate `muse`
- **THEN** `toolchain_updater_registry.py` SHALL declare `("muse", "brew-cask")` (and alias `("muse-code", "brew-cask")`) with `source_type="brew-cask"`, `supported_verb=None`, `updater_dispatch="none"`, `delegating_to="brew"`, and `status="uncovered_declared"`
- **AND** `inventory-workstation-toolchain.py` and `config/workstation-toolchain-manifest.json` SHALL classify executable `muse` under `authority="brew-cask"`, `writer="brew"`, `updater_dispatch="none"`, `preferred_source="cask muse-code"`, and `drift_status="clean"` with `0` unknown tools
- **AND** the inventory collision map SHALL record that Homebrew cask `muse` is an unrelated disabled desktop productivity app (`muse.ai`) and MUST NOT be substituted for `cask "muse-code"`

#### Scenario: Running Muse Code session exclusion during scheduled Homebrew cask upgrades
- **WHEN** the scheduled maintenance workflow (`workstation_update.py`) evaluates `muse-code` for a Homebrew cask upgrade while an active Muse Code CLI process is running
- **THEN** the process guard in `step_homebrew_update` SHALL check `pgrep -x` across `"muse-code"`, `"muse"`, and the resolved Mach-O binary name `"muse-aarch64-macos"`
- **AND** if any matching process is actively running, the upgrade of `muse-code` SHALL be skipped and recorded in `casks_skipped_running` without terminating or disrupting the active coding session

### Requirement: Interactive zsh startup SHALL defer synchronous provider helpers and maintain sub-200ms latency

The workstation `~/.zshrc` configuration SHALL lazy-load or defer synchronous `cce` provider initialization (`__cce_apply_current_provider`) until first invocation so interactive shell startup does not fork external helper processes, keeping `zsh -i -c exit` latency under 200ms.

#### Scenario: Deferred cce initialization during interactive shell startup
- **WHEN** a new interactive zsh session starts (`zsh -i -c exit`)
- **THEN** `~/.zshrc` SHALL define the `cce` shell wrapper without synchronously executing `$_cce_binary use` during shell initialization
- **AND** median interactive shell startup latency SHALL remain below 200ms

#### Scenario: Runaway AddressBookSourceSync background CPU loop is suppressed
- **WHEN** workstation process health is audited
- **THEN** `AddressBookSourceSync` SHALL NOT consume sustained runaway CPU (`>50%`) in the background

### Requirement: Fallback shell updater and toolchain inventory SHALL cover Kimi Code standalone binary

Both the fallback shell maintenance runner (`workstation-daily-update.sh` and its store mirror) and `inventory-workstation-toolchain.py` SHALL include `kimi` (`~/.kimi-code/bin/kimi`) in their sanctioned PATH, known root, and agent coverage lists.

#### Scenario: Fallback shell script and inventory recognize Kimi Code
- **WHEN** `workstation-daily-update.sh` and `inventory-workstation-toolchain.py` evaluate installed AI agent CLIs
- **THEN** `workstation-daily-update.sh` SHALL include `~/.kimi-code/bin` in `PATH`, `~/.kimi-code` in `known_root`, and `kimi` in `AGENT_CLI_COVERED`
- **AND** `inventory-workstation-toolchain.py` SHALL classify `~/.kimi-code/bin/kimi` as `[CLEAN]` under `vendor_download` authority with `0` unknown manifest tools

### Requirement: Script provenance verification and telemetry alert suppression SHALL match live manifest structure

Script drift validation between `~/Developer/scripts/workstation-daily-update.sh` and `platform/openspec-store/scripts/workstation-daily-update.sh` SHALL compute and compare live SHA-256 digests across the path pairs declared in `config/script-provenance-manifest.tsv`, and telemetry notifications SHALL suppress failure alerts when workflow status is `"SUCCESS"`, `"completed"`, or `"paused"`.

#### Scenario: Dynamic paired-file SHA-256 comparison via script-provenance-manifest.tsv
- **WHEN** `step_integrity_and_store_validation` or `detect_script_drift` reads `config/script-provenance-manifest.tsv`
- **THEN** it SHALL parse the 3-column TSV (`<executed_path>`, `<recorded_path>`, `<authority>`) and verify that both files have identical SHA-256 digests

#### Scenario: Paused workflow status suppresses failure alert notifications
- **WHEN** `workstation-daily-update` finishes with status `"SUCCESS"`, `"completed"`, or `"paused"`
- **THEN** `step_record_telemetry_and_notify` SHALL record the JSON report without firing a macOS failure alert notification

### Requirement: Declarative Brewfile coverage for workstation CLIs and local embedding services

`config/Brewfile` in `platform/openspec-store` SHALL declare `tap "anomalyco/tap"`, `brew "anomalyco/tap/opencode"`, `brew "block-goose-cli"`, `brew "googleworkspace-cli"`, `brew "newman"`, `brew "ollama"`, `brew "qwen-code"`, `brew "ruff"`, `cask "copilot-cli"`, `cask "droid"`, `cask "grok-build"`, and `cask "muse-code"` alongside the core workstation formulae and casks so `brew bundle check` verifies the complete Homebrew-governed tool surface.

#### Scenario: Brewfile declares all Homebrew-governed agent CLIs, utilities, and embedding services
- **WHEN** `config/Brewfile` is inspected or validated via `HOMEBREW_NO_AUTO_UPDATE=1 brew bundle check --file config/Brewfile --no-upgrade`
- **THEN** `tap "anomalyco/tap"`, `brew "anomalyco/tap/opencode"`, `brew "block-goose-cli"`, `brew "googleworkspace-cli"`, `brew "newman"`, `brew "ollama"`, `brew "qwen-code"`, `brew "ruff"`, `cask "copilot-cli"`, `cask "droid"`, `cask "grok-build"`, and `cask "muse-code"` SHALL be present in `config/Brewfile`
- **AND** `brew bundle check` SHALL exit `0` without missing dependency findings

### Requirement: Deterministic Zsh PATH deduplication and Homebrew-first precedence

Interactive and login Zsh initialization (`~/.zshenv`, `~/.zprofile`, `~/.zshrc`) SHALL enforce unique `PATH` entries via `typeset -U path PATH`, maintain `/opt/homebrew/bin` ahead of `~/.npm-global/bin` as documented in `docs/mac-development-setup.md`, expose `/opt/homebrew/opt/libpq/bin` for `psql`, explicitly filter out inherited `~/.orbstack/bin` entries via `path=(${path:#"$HOME/.orbstack/bin"})`, and guard `~/.iterm2_shell_integration.zsh` behind `[[ -t 0 && -t 1 ]]`.

#### Scenario: Interactive and inherited shells preserve Homebrew precedence, deduplicate PATH, and strip OrbStack
- **WHEN** a fresh login shell (`zsh -ilc 'print -l $path'`) or a subshell inheriting `PATH="$HOME/.orbstack/bin:$PATH"` (`PATH="$HOME/.orbstack/bin:$PATH" zsh -ic 'print -l $path'`) is evaluated
- **THEN** `/opt/homebrew/bin` SHALL appear before `/Users/androidteam/.npm-global/bin`
- **AND** `/opt/homebrew/opt/libpq/bin` SHALL be present on `PATH` so `which psql` resolves to `/opt/homebrew/opt/libpq/bin/psql`
- **AND** `/Users/androidteam/.orbstack/bin` SHALL be absent from `$path`
- **AND** no directory entry (including `/Users/androidteam/.kimi-code/bin`) SHALL appear more than once in `$path`

#### Scenario: Non-TTY interactive subshells do not emit iTerm2 OSC escape sequences
- **WHEN** a non-TTY interactive subshell (`zsh -ic 'echo READY' </dev/null`) is executed by an automation or diagnostic runner
- **THEN** `~/.iterm2_shell_integration.zsh` SHALL be skipped when standard input or output is not a TTY
- **AND** stdout SHALL begin cleanly with `READY` without leading `\e]1337;` escape sequences

### Requirement: Primary DBOS daily workflow executes health, snapshot, and inventory reporters

The primary scheduled maintenance workflow (`shb-schedule` `workstation_update.py`) and its fallback wrapper (`workstation-daily-update.sh`) SHALL execute `measure-snapshot-growth.py`, `inventory-workstation-toolchain.py`, and `reconcile-agent-cli-coverage.py` on every `apply` run before recording final run telemetry, and SHALL include `ntn update` in the standalone CLI update stage.

#### Scenario: Apply mode executes Stages 8-10 health reporters before completion
- **WHEN** `workstation-daily-update.sh` runs in `apply` mode via `shb-schedule run-now workstation-daily-update`
- **THEN** the workflow SHALL execute snapshot growth measurement, toolchain inventory drift inspection, and agent CLI coverage reconciliation before writing `~/Developer/data/updates/YYYY-MM-DD.json`
- **AND** any exceeded snapshot ceiling or authority conflict SHALL mark the run status degraded rather than silently exiting `0`

#### Scenario: Standalone Notion CLI update included in daily maintenance
- **WHEN** the standalone CLI update stage runs in `workstation_update.py` or `workstation-daily-update.sh`
- **THEN** `ntn` (`~/.local/bin/ntn`) SHALL be probed via `ntn --version` and updated via `ntn update`

### Requirement: LaunchAgent directory hygiene and script provenance completeness

`~/Library/LaunchAgents/` SHALL contain only active `.plist` definitions without backup `.bak*` files sharing active `Label` identifiers, and all active workstation helper scripts invoked by LaunchAgents (including `~/Developer/scripts/omniroute-watchdog.sh`) SHALL be tracked in `config/script-provenance-manifest.tsv` and documented in `~/Developer/scripts/README.md`.

#### Scenario: No duplicate-label backup plists in LaunchAgents directory
- **WHEN** `~/Library/LaunchAgents/` is scanned for plist and backup files
- **THEN** backup files such as `ai.hermes.gateway.plist.bak-*` SHALL reside outside `~/Library/LaunchAgents/`
- **AND** every active LaunchAgent script under `~/Developer/scripts/` SHALL have a matching SHA-256 entry in `config/script-provenance-manifest.tsv`

#### Scenario: Failing LaunchAgents are remediated against SIGPIPE and stale paths
- **WHEN** `launchctl list` is inspected for `com.omniroute.update-check`, `com.victory1908.hermes-webui`, and `Antigravity Tools`
- **THEN** `~/Omniroute/scripts/check-upstream.sh` SHALL guard `REMOTE_DIGEST` against `awk` early-exit `SIGPIPE` (`awk '/^Digest:/ && !found {print $2; found=1}' || true`) with `HOME` and `/opt/homebrew/bin` exported so `com.omniroute.update-check` exits `0` instead of `255`
- **AND** `com.victory1908.hermes-webui.plist` SHALL reference `/Users/androidteam/Developer/platform/hermes-webui` and `Antigravity Tools.plist` SHALL reference `/Applications/Antigravity Tools.app/Contents/MacOS/antigravity-tools` so neither exits with `EX_CONFIG` (`78`)

### Requirement: Declarative Brewfile coverage for Orca IDE and active agent orchestrators

`config/Brewfile` in `platform/openspec-store` SHALL declare `cask "orca"` for the official Stably AI Orca IDE orchestrator (`stablyai/orca/orca` tap) alongside standard development applications, and operators SHALL verify its operational readiness via `orca status` following any install or upgrade.

#### Scenario: Brewfile declares Orca cask and bundle check passes
- **WHEN** `config/Brewfile` is evaluated via `HOMEBREW_NO_AUTO_UPDATE=1 brew bundle check --file config/Brewfile --no-upgrade`
- **THEN** `cask "orca"` SHALL be declared in `config/Brewfile`
- **AND** `brew bundle check` SHALL exit `0` confirming dependencies are satisfied

#### Scenario: Orca lifecycle and runtime health verification
- **WHEN** Orca is installed or updated on macOS
- **THEN** any hung, detached, or deadlocked background processes SHALL be terminated prior to bundle replacement
- **AND** `orca status` SHALL report `appRunning: true`, `runtimeState: ready`, `graphState: ready`, and `runtimeReachable: true` with an active desktop window

### Requirement: Declarative Brewfile and LaunchAgent PATH governance for Herdr

The workstation SHALL declare Herdr's Homebrew package owner separately from its host-local LaunchAgent owner. A staged plist MUST NOT be reported as effective runtime configuration. Applying a changed daemon environment SHALL require explicit operator authorization because restarting Herdr can terminate active pane processes.

#### Scenario: Brewfile declares Herdr formula
- **WHEN** the configured Brewfile is inspected and checked without upgrades
- **THEN** it SHALL declare `brew "herdr"` and report any missing dependency without installing it

#### Scenario: LaunchAgent environment is applied to the actual server
- **WHEN** the operator authorizes reloading the exact Herdr LaunchAgent after preserving relevant work
- **THEN** the replacement server process SHALL contain the configured Homebrew/user-local PATH and report normal server availability
- **AND** plist syntax or `herdr server reload-config` alone MUST NOT satisfy this acceptance condition

#### Scenario: Operator preserves active panes
- **WHEN** the operator declines a disruptive LaunchAgent reload
- **THEN** the workflow SHALL leave the daemon running and report PATH activation as staged but incomplete
- **AND** the corresponding implementation task SHALL remain unchecked

#### Scenario: Package and service ownership remain distinct
- **WHEN** the installed formula lacks a service declaration
- **THEN** the runbook SHALL identify the LaunchAgent as host-local rather than claim `brew services` can create or restart it
- **AND** Herdr package updates SHALL remain owned by `brew upgrade herdr`, with running-server activation handled separately

### Requirement: Herdr built-in agent integrations and skill synchronization

The workstation SHALL retain the official integrations and skill for provisioned agents, preserve separate Pi/OMP roots, and distinguish installed files from active session reporting. Integration installation MUST NOT imply that existing agents loaded hooks or that session restoration was exercised.

#### Scenario: Integrations are installed for provisioned agents
- **WHEN** `herdr integration status` is inspected
- **THEN** `pi`, `omp`, `claude`, `codex`, `copilot`, `devin`, `droid`, `kimi`, `opencode`, `kilo`, `hermes`, `qodercli`, `qwen`, `cursor`, `antigravity-cli`, and `grok` SHALL report their installed versions
- **AND** Pi and OMP extensions SHALL remain in separate resolved directories

#### Scenario: Optional agents remain unprovisioned
- **WHEN** `~/.letta` or `~/.mastracode` is absent
- **THEN** provisioning SHALL leave those directories absent rather than create unused hook roots

#### Scenario: Lifecycle reporting is described accurately
- **WHEN** integration capabilities are documented
- **THEN** the runbook SHALL distinguish the five installed lifecycle reporters from session-only integrations and explain any startup/restart requirement
- **AND** verification SHALL label unexercised activation and restore behavior as unverified without forcing agent restarts

#### Scenario: Official skill is synchronized
- **WHEN** the skill manifests and resolved user skill roots are inspected
- **THEN** both manifests SHALL declare `herdr` and the installed skill SHALL retain its `HERDR_ENV=1` caller guard

### Requirement: Herdr operational documentation SHALL describe notifier privacy and execution behavior accurately

The runbook SHALL document the notifier's three-second default polling, blocked/done states, relay-default delivery, optional direct APNs, and enabled-by-default transcript previews. It SHALL use the installed pane/agent CLI surface and MUST NOT imply that notifications are always delivered directly to Apple.

#### Scenario: Relay-default notification data flow
- **WHEN** APNs direct-mode credentials are not configured
- **THEN** documentation SHALL identify the configured relay path and explain that enabled previews can include transcript snippets in notification bodies
- **AND** verification MUST NOT send a push or disclose transcript contents merely to test documentation

### Requirement: Post-cask-upgrade Docker Desktop helper and stack restoration

The workstation daily maintenance pipeline (`shb-schedule` durable workflows and `workstation-daily-update.sh`) SHALL restore Docker Desktop and its Compose stacks after Homebrew cask upgrades, gate `docker-service.sh up` behind successful `docker-service.sh start` execution, and track `docker-service.sh` in `config/script-provenance-manifest.tsv`.

#### Scenario: Daily maintenance restores Docker Desktop after Homebrew cask upgrade
- **WHEN** the Homebrew cask upgrade stage updates `docker-desktop` in `shb-schedule`'s `workstation-daily-update` workflow, or when `workstation-daily-update.sh` completes `brew upgrade --cask` and detects that `docker info` fails or `/var/run/com.docker.vmnetd.sock`, `/Library/PrivilegedHelperTools/com.docker.vmnetd`, or `/Library/PrivilegedHelperTools/com.docker.socket` is missing
- **THEN** the maintenance runner SHALL execute `docker-service.sh start` and, only if `docker-service.sh start` exits `0`, execute `docker-service.sh up`
- **AND** Docker Desktop privileged helpers (`com.docker.vmnetd`, `com.docker.socket`), the Docker daemon, and all registered Compose stacks (`~/Omniroute` and `~/Developer/shb/shb-schedule`) SHALL be restored to running state without redundant Compose restarts on no-op cask runs.

#### Scenario: Failed Docker Desktop start after cask upgrade skips stack bring-up and records error
- **WHEN** `step_homebrew_update()` in `shb-schedule` upgrades `docker-desktop` and `docker-service.sh start` returns a non-zero exit code
- **THEN** `step_homebrew_update()` SHALL record the `docker-service.sh start` failure in `errors`, report step status `DEGRADED`, and skip invoking `docker-service.sh up` against the unreachable daemon.

#### Scenario: Docker service script provenance is tracked in manifest
- **WHEN** `detect_script_drift` in `workstation-daily-update.sh` evaluates `/Users/androidteam/Developer/platform/openspec-store/config/script-provenance-manifest.tsv`
- **THEN** `/Users/androidteam/Developer/scripts/docker-service.sh` SHALL be listed with recorded mirror `scripts/docker-service.sh` and authority `executed`
- **AND** the SHA-256 digest of `/Users/androidteam/Developer/scripts/docker-service.sh` SHALL match `/Users/androidteam/Developer/platform/openspec-store/scripts/docker-service.sh` with zero drift.
