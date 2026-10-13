# Spec Delta: portable-workstation-toolchain

## ADDED Requirements

### Requirement: Mac App Store applications SHALL be discovered and safely updated with running-process exclusion

The workstation maintenance engine SHALL discover outdated Mac App Store applications via `mas outdated` and SHALL upgrade idle applications while strictly skipping applications currently active in the user session, executing completely non-interactively without privilege elevation.

#### Scenario: Outdated Mac App Store discovery
- **WHEN** the maintenance pipeline reaches the Mac App Store update step
- **THEN** it SHALL execute `mas outdated` non-interactively to determine pending application updates
- **AND** it SHALL parse each pending application's numeric identifier and exact application name matching regex `^[A-Za-z0-9._@/+-]+$`

#### Scenario: Running application update exclusion
- **WHEN** an outdated Mac App Store application is actively running in the host session (detected via `pgrep -x "$APP_NAME"`, ignoring updater subprocesses)
- **THEN** the maintenance pipeline SHALL skip upgrading that application
- **AND** it SHALL record that the application was skipped due to an active process lock
- **AND** it SHALL NOT terminate, disrupt, signal, or restart the running application

#### Scenario: Non-interactive unattended execution and privilege boundaries
- **WHEN** `mas upgrade "$APP_ID"` is invoked for an idle application
- **THEN** the command SHALL execute without `sudo` and without requesting interactive password or Keychain prompts
- **AND** if an application requires graphical authentication or privilege escalation, the step SHALL fail-fast and record the item as skipped rather than blocking on standard input

---

### Requirement: Global package ecosystems SHALL maintain initialized manifests and non-interactive update paths

All global package managers (NPM, Bun, and UV) SHALL maintain valid global manifests and SHALL execute upgrades dynamically using sanitized identifiers without hardcoded package lists or clobbering pinned coding agent binaries.

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

---

### Requirement: Scheduled maintenance SHALL execute via durable workflow with discrete step recovery, strict isolation, and structured telemetry

Daily workstation maintenance SHALL be orchestrated as a durable, multi-step workflow registered under `shb-schedule`, guaranteeing checkpointed progress, strict file permission boundaries, credential isolation, and immutable JSON run reports.

#### Scenario: Declarative schedule manifest registered under shb-schedule
- **WHEN** workstation update scheduling is inspected
- **THEN** a validated YAML manifest conforming to `shb-schedule/v1` SHALL exist in `~/.shb/schedules/workstation-daily-update.yaml` with mode `0600` inside directory mode `0700`
- **AND** the manifest SHALL declare schedule `0 8 * * *`, timezone `Asia/Ho_Chi_Minh`, timeout bounds of 3600s, and a maximum of 2 retry attempts

#### Scenario: Step-level failure isolation and checkpoint recovery
- **WHEN** a transient network or rate-limit error occurs during a specific step (e.g. remote skills git pull)
- **THEN** the durable execution engine SHALL record the error for that step
- **AND** prior successfully completed steps SHALL remain checkpointed in PostgreSQL without requiring full execution replay on retry

#### Scenario: Secret isolation in telemetry and alerts
- **WHEN** a maintenance run finishes or encounters failures
- **THEN** the workflow SHALL load communication tokens strictly from `~/.shb/.env` at runtime
- **AND** it SHALL NOT log, write to database checkpoints, or export secret values to run artifacts
- **AND** alert notifications dispatched to the Telegram channel SHALL carry structured summary counts and stage names, strictly omitting raw stderr buffers

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
