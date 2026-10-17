# portable-workstation-toolchain Specification Delta

## MODIFIED Requirements

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
