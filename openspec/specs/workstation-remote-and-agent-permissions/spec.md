# workstation-remote-and-agent-permissions Specification

## Purpose

Defines workstation standards for remote access software, AI coding assistant runtimes, and scripting automation interpreters on macOS, enforcing single-version installation via Homebrew Cask, Gatekeeper quarantine bypass, and complete system TCC permissions across Accessibility, Screen Recording, Full Disk Access, and programmatic computer control.

## Requirements

### Requirement: Workstation remote desktop applications SHALL maintain single-version Homebrew Cask installation

Remote desktop utilities SHALL be installed exclusively through official Homebrew Casks, maintaining exactly one application bundle on the filesystem, purging obsolete versions from Caskroom, and deploying native background services.

#### Scenario: Official Homebrew Cask installation and upgrade
- **WHEN** a remote desktop utility such as AnyDesk is provisioned or reinstalled
- **THEN** it SHALL be managed via `brew reinstall --cask anydesk` (or `brew upgrade --cask anydesk`)
- **AND** the installed application bundle in `/Applications` SHALL reflect the latest upstream release

#### Scenario: Single version integrity and duplicate elimination
- **WHEN** the host filesystem is inspected for application bundles matching the tool
- **THEN** exactly one application bundle SHALL exist across `/Applications` and user directories
- **AND** no duplicate binary versions or shadow bundles SHALL remain on disk

#### Scenario: Background service and privileged helper registration
- **WHEN** the application is installed and initialized
- **THEN** required system launch services (`com.philandro.anydesk.service`) and privileged helper tools (`com.philandro.anydesk.Helper`) SHALL be registered in `/Library/LaunchDaemons` and `/Library/PrivilegedHelperTools`
- **AND** the background service SHALL execute under native launchd supervision

### Requirement: Remote access and automation agents SHALL maintain verified macOS TCC permissions

Remote access utilities and automated AI coding assistants requiring screen capture, synthetic input, or filesystem access SHALL possess verified macOS Transparency, Consent, and Control (TCC) authorizations with active status in the system authorization database.

#### Scenario: Full permissions granted for remote desktop tooling
- **WHEN** AnyDesk is configured for complete remote assistance operations
- **THEN** `kTCCServiceAccessibility` (Accessibility), `kTCCServiceScreenCapture` (Screen Recording), and `kTCCServiceSystemPolicyAllFiles` (Full Disk Access) SHALL evaluate to `auth_value = 2` (Allowed) in the system TCC store
- **AND** no pending permission prompts or warning dialogs SHALL block unattended connection

#### Scenario: Full permissions verified for AI coding assistants and automation harnesses
- **WHEN** AI developer tools (Orca, OMP, ChatGPT, and Codex) execute on the host workstation
- **THEN** their associated application bundles and agent helpers (`com.stablyai.orca`, `com.stablyai.orca.computer-use`, `com.openai.codex`, `com.openai.sky.CUAService`, `com.codexuse.desktop`, and OMP execution runner) SHALL possess active authorizations for required operational domains (`kTCCServiceAccessibility`, `kTCCServiceScreenCapture`, and `kTCCServiceSystemPolicyAllFiles`)
- **AND** computer-use capabilities SHALL report granted status without permission rejection errors

#### Scenario: Value-blind audit of system authorization records
- **WHEN** operator verification is executed against `/Library/Application Support/com.apple.TCC/TCC.db`
- **THEN** audit queries SHALL verify `auth_value = 2` for all target client identifiers
- **AND** the report SHALL emit client identities, service names, and authorization integers without logging sensitive session tokens or system credentials

### Requirement: Runtime scripting interpreters and host automation runners SHALL maintain full computer control permissions

Interpreters and automation harnesses executing on the workstation (Python, Ruby, OMP) SHALL maintain verified host permissions enabling unrestricted programmatic computer control, including accessibility tree inspection, synthetic event posting, screen buffer capture, and full filesystem traversal.

#### Scenario: Python automation runtime control verification
- **WHEN** Python automation scripts execute via host or `uv` environments (`cpython-3.11`, `cpython-3.12`)
- **THEN** `ApplicationServices.AXIsProcessTrusted()` SHALL evaluate to true
- **AND** CoreGraphics display bounds queries SHALL succeed without permission error
- **AND** reading protected directories such as `/Library/Application Support/com.apple.TCC` SHALL succeed under Full Disk Access

#### Scenario: Ruby automation runtime control verification
- **WHEN** Ruby automation scripts execute via Homebrew Ruby runtimes
- **THEN** `ApplicationServices.AXIsProcessTrusted()` SHALL evaluate to true
- **AND** CoreGraphics display ID and bounds queries SHALL succeed without permission error
- **AND** reading protected directories such as `/Library/Application Support/com.apple.TCC` SHALL succeed under Full Disk Access

#### Scenario: OMP native computer-use harness capability verification
- **WHEN** OMP computer-use APIs (`computer.capabilities()`, `computer.windows()`, `computer.screenshot()`, `computer.click()`, `win.ax()`) execute
- **THEN** the capability report SHALL indicate `capturePermission: "granted"`, `inputPermission: "granted"`, and `axPermission: "granted"`
- **AND** window enumeration, AX tree parsing, and synthetic input generation SHALL execute without runtime permission rejection

### Requirement: Homebrew Cask applications SHALL bypass Gatekeeper quarantine attributes

Developer workstations SHALL configure Homebrew Cask options to prevent the attachment of `com.apple.quarantine` extended attributes on installed bundles, and existing application bundles SHALL maintain zero quarantine metadata.

#### Scenario: Persistent Cask options configuration
- **WHEN** user and system shell sessions initialize (`~/.zshrc`, `~/.zprofile`)
- **THEN** `HOMEBREW_CASK_OPTS="--no-quarantine"` SHALL be exported
- **AND** `brew config` SHALL report `HOMEBREW_CASK_OPTS: ["--no-quarantine"]`

#### Scenario: Application bundle quarantine attribute elimination
- **WHEN** installed bundles in `/Applications` and `/opt/homebrew/Caskroom` are inspected via `xattr`
- **THEN** no `com.apple.quarantine` attribute SHALL be present
- **AND** launching applications SHALL execute directly without Gatekeeper download confirmation dialogs

### Requirement: Autonomous AI agents and developer toolchains SHALL maintain complete pre-authorized TCC privileges without modal prompts

All host AI coding assistants, supervisor LaunchAgents, and automation interpreters SHALL possess pre-authorized permissions across Accessibility, Screen Recording, Full Disk Access, and AppleEvents IPC in the macOS TCC store, eliminating interactive authorization dialogs during autonomous execution.

#### Scenario: Pre-authorized Accessibility and Screen Recording for all AI toolchains
- **WHEN** any registered coding assistant or runtime executes (`hermes`, `osascript`, `omp`, `kimi`, `goose`, `claude`, `codex`, `opencode`, `Cursor`, `CuaDriver`, `python3.14`, `python3.11`, `node`, `bun`, `uv`, `bash`, `zsh`)
- **THEN** `kTCCServiceAccessibility` SHALL evaluate to `auth_value = 2` (Allowed) in `/Library/Application Support/com.apple.TCC/TCC.db`
- **AND** `kTCCServiceScreenCapture` SHALL evaluate to `auth_value = 2` (Allowed) for all screen-capturing agents and drivers
- **AND** zero `universalAccessAuthWarn` or `UserNotificationCenter` authorization dialogs SHALL be raised.

#### Scenario: Persistent AppleEvents IPC authorization for osascript supervisor
- **WHEN** Hermes Gateway or scripting tasks execute AppleScript via `/usr/bin/osascript`
- **THEN** `kTCCServiceAppleEvents` SHALL maintain allowed authorization targeting `System Events.app`, `Google Chrome.app`, `Calendar.app`, `iTerm.app`, and `Codex Computer Use.app`
- **AND** queries to `System Events` for window hierarchy and process enumeration SHALL return exit code 0 without prompting.

#### Scenario: Suppression of periodic ScreenCaptureKit privacy alerts and crash dialogs
- **WHEN** ScreenCaptureKit verifies authorization under macOS
- **THEN** `ScreenCaptureApprovals.plist` in `group.com.apple.replayd` SHALL carry far-future hint dates preventing recurring monthly consent popups
- **AND** `com.apple.CrashReporter` SHALL maintain `DialogType = none` to prevent modal error alerts from background processes.

### Requirement: Post-upgrade TCC provenance reconciliation SHALL keep active CLI binaries authorized

Workstation TCC governance SHALL enforce `client_type = 0` (`CFBundleIdentifier`) bundle attribution and responsible-supervisor delegation as the authoritative authorization model in `/Library/Application Support/com.apple.TCC/TCC.db` across `kTCCServiceAccessibility`, `kTCCServiceScreenCapture`, and `kTCCServiceSystemPolicyAllFiles`, eliminating permissions drift caused by versioned directory rotation of `client_type = 1` Mach-O realpaths during automated toolchain upgrades.

#### Scenario: Active upgraded CLI realpaths are enrolled in TCC.db
- **WHEN** `realpath` is resolved for `/opt/homebrew/bin/omp`, `/opt/homebrew/bin/node` (backing `~/.pi/agent/bin/pi`), `/opt/homebrew/bin/opencode`, `/opt/homebrew/bin/goose`, `~/.local/bin/claude`, and `~/.kimi-code/bin/kimi`
- **THEN** each target identity SHALL be attributed to a verified `client_type = 0` bundle or registered Mach-O path with an active `auth_value = 2` record in `/Library/Application Support/com.apple.TCC/TCC.db` across `kTCCServiceAccessibility` and `kTCCServiceScreenCapture`
- **AND** `ScreenCaptureApprovals.plist` in `group.com.apple.replayd` SHALL maintain far-future (`3026-01-01`) suppression dates

#### Scenario: Scheduled maintenance detects TCC path drift after upgrades
- **WHEN** the daily workstation maintenance workflow upgrades Homebrew formulae or standalone agent CLIs on macOS
- **THEN** a read-only post-upgrade TCC provenance check SHALL verify that authoritative `client_type = 0` bundle identities and canonical agent paths retain verified `auth_value = 2` status in `TCC.db` without failing closed on expected package directory rotations

### Requirement: Hermes CUA driver environment variable SHALL point to the system-authorized application bundle

The workstation shell and Hermes runtime configuration SHALL persist `HERMES_CUA_DRIVER_CMD` pointing to `/Applications/CuaDriver.app/Contents/MacOS/cua-driver` so Hermes computer-use sessions invoke the TCC-authorized application bundle rather than legacy bundled tool paths.

#### Scenario: Hermes resolves the TCC-authorized CuaDriver binary
- **WHEN** `HERMES_CUA_DRIVER_CMD` is inspected in the workstation environment (`~/.zshenv` or `~/.hermes/.env`)
- **THEN** it SHALL resolve to `/Applications/CuaDriver.app/Contents/MacOS/cua-driver`
- **AND** `/Applications/CuaDriver.app` (`com.trycua.driver`) SHALL hold `auth_value = 2` in `TCC.db` for Accessibility and ScreenCapture

### Requirement: Herdr multiplexer daemon and companion notifier SHALL maintain full macOS TCC permissions

The workstation SHALL retain verified Accessibility, Screen Recording, and Full Disk Access grants for Herdr and the existing shared host Python automation identities. These grants MUST be classified as host automation authority, not as dependencies of notifier polling or transcript reads. Automation verification SHALL identify its tested receiver explicitly.

#### Scenario: Herdr server executable holds valid grants
- **WHEN** the active Herdr executable is audited
- **THEN** its path-based identity SHALL have allowed Accessibility, Screen Recording, and Full Disk Access records whose signing requirements accept that executable
- **AND** a database row alone MUST NOT be reported as functional proof for every child process

#### Scenario: In-pane verification identifies the tested sender and receiver
- **WHEN** an authorized probe inside a Herdr pane checks Accessibility, Screen Recording, protected read access, and AppleEvents to System Events
- **THEN** the report SHALL record the pane context, actual results, and System Events as the receiver
- **AND** the result MUST NOT imply authorization for arbitrary AppleEvents receivers or root/SIP bypass

#### Scenario: Shared Python grants are not misattributed to the notifier
- **WHEN** the active Python automation executable and applicable framework bundle identity are audited
- **THEN** their existing three-service policy SHALL be verified against their current signing identities
- **AND** documentation SHALL state that the notifier uses configured files, Herdr queries, and outbound delivery, not Accessibility or screen capture

#### Scenario: Authorization audit does not weaken security
- **WHEN** verification or remediation runs
- **THEN** it MUST NOT modify TCC records, relax authorizationdb rights, grant/revoke permissions, or bypass consent as a verification side effect

### Requirement: Post-upgrade TCC provenance verification SHALL include Herdr and active agent CLIs

Scheduled and manual checks SHALL detect required executable, service, and signing-identity failures. A clean result SHALL require a nonempty, fully verified target set. Canonical agents require Accessibility and Screen Recording; Herdr, OMP and the existing shared Python automation identities additionally require Full Disk Access. Required Darwin verification errors MUST NOT be classified as successful skips.

#### Scenario: All required identities satisfy their role policy
- **WHEN** all required executables resolve, exist, and have allowed records satisfying their current code identity and required services
- **THEN** both maintenance runners SHALL report a clean provenance result
- **AND** their output SHALL identify verified identities and no missing required targets

#### Scenario: Signature changes at the same path
- **WHEN** a required executable no longer satisfies a granted record's stored signing requirement
- **THEN** verification SHALL report drift even if the path and authorization integer are unchanged
- **AND** missing or malformed signing requirements MUST NOT pass

#### Scenario: Required executable or service is missing
- **WHEN** a required name cannot resolve, its executable is missing, the target set is empty, or a required grant is absent or denied
- **THEN** verification SHALL report a non-clean result identifying the failure
- **AND** missing Full Disk Access for Herdr or a declared shared automation identity MUST NOT pass

#### Scenario: Required verification infrastructure fails on Darwin
- **WHEN** TCC data is absent, unreadable or corrupt, native identity evaluation is unavailable, or verifier output is invalid
- **THEN** the scheduler SHALL report non-success and the fallback SHALL return nonzero
- **AND** non-Darwin checks MAY be reported as explicitly not applicable without claiming grants were verified

#### Scenario: Reporter failure cannot be masked by aggregate success
- **WHEN** a required reporter fails, returns malformed data, or reports inventory drift, target misalignment or unknown authority
- **THEN** the aggregate maintenance result SHALL be non-successful and retain the reason

### Requirement: Herdr verification SHALL respect supported macOS consent behavior

Verification SHALL distinguish current authorization from future consent or reminder behavior. It MUST NOT promise permanent reminder suppression based on private replayd plist values, mutate that plist, or install a recurring suppression workaround. Existing private values SHALL be recorded only as historical unsupported state.

#### Scenario: Private timestamp values already exist
- **WHEN** prior far-future strings are found in ScreenCaptureApprovals.plist
- **THEN** the report SHALL state that their presence does not prove runtime interpretation or permanent suppression
- **AND** remediation SHALL leave them unchanged unless a separate exact mutation is authorized

#### Scenario: macOS requests renewed consent
- **WHEN** macOS presents a permission or capture reminder
- **THEN** the workflow SHALL retain normal operator consent handling rather than suppress or automatically approve the request

### Requirement: TCC provenance verifier SHALL maintain unified target resolution without dead tables or duplicated error payloads

The TCC provenance verifier SHALL resolve explicit and default target lists through a unified resolution pipeline without dead role tables or duplicated error-result literals while preserving all native `Security.framework` `csreq` checks and public return keys.

#### Scenario: Default and explicit binary sets execute through a single target-resolution loop
- **WHEN** `build_required_targets()` is invoked with `binaries=None` or with an explicit `binaries` list
- **THEN** both paths SHALL resolve canonical CLIs and shared Python automation identities through one shared loop without duplicate branch logic
- **AND** `verify_tcc_provenance()` SHALL return `status: "CLEAN"` across all 9 workstation identities when all required services and `csreq` signatures are valid

#### Scenario: Error and drift results preserve public contract keys via shared constructor
- **WHEN** `verify_tcc_provenance()` encounters non-Darwin skip, missing/unreadable `TCC.db`, empty target list, or helper failure
- **THEN** the returned dictionary SHALL contain `status`, `reason`, `verified_binaries`, `missing_binaries`, `records`, and `errors` constructed via a single helper function

### Requirement: ScreenCaptureApprovals.plist date keys SHALL be serialized as native plist Date objects

All timestamp fields in `~/Library/Group Containers/group.com.apple.replayd/ScreenCaptureApprovals.plist` SHALL be serialized as native plist `<date>` (`NSDate`) objects rather than `<string>` values so `/usr/libexec/replayd` never aborts with `NSInvalidArgumentException`, and remote desktop TCC provenance audits SHALL distinguish verified installed identities from stale uninstalled bundle identifiers.

#### Scenario: ScreenCaptureApprovals.plist contains zero string-typed date values and replayd remains running
- **WHEN** `~/Library/Group Containers/group.com.apple.replayd/ScreenCaptureApprovals.plist` is inspected and `gui/502/com.apple.replayd` is queried
- **THEN** `plutil -lint` SHALL return `OK` and every `kScreenCapturePrivacyHintDate`, `kScreenCaptureApprovalLastAlerted`, and `kScreenCaptureApprovalLastUsed` entry SHALL deserialize as a native `NSDate` (`datetime.datetime`) object with `0` string-typed date fields
- **AND** `gui/502/com.apple.replayd` SHALL remain in `state = running` without `-[__NSCFString timeIntervalSinceReferenceDate]` `SIGABRT` crashes
- **AND** AnyViewer (`com.aomei.mac.anyviewer`) main-thread `CGDisplayStreamCreateWithDispatchQueue` checks SHALL complete without `SLSDisplayStreamCreateProxying` semaphore timeouts

#### Scenario: Remote desktop TCC provenance audit distinguishes verified installed binaries from stale legacy bundle IDs
- **WHEN** macOS TCC grants in `/Library/Application Support/com.apple.TCC/TCC.db` are audited for AnyViewer, TeamViewer, and RealVNC using `SecStaticCodeCheckValidity`
- **THEN** active installed identities (`com.aomei.mac.anyviewer` at `/Applications/AnyViewer.app`, `com.teamviewer.TeamViewer` at `/Applications/TeamViewer.app`, `com.realvnc.vncagent` and `/Library/vnc/vncagent` at `/Library/vnc/RealVNC Server Agent.app`, and `com.realvnc.vncserver_service` at `/Applications/RealVNC/RealVNC Server.app`) SHALL evaluate to `auth_value = 2` and `SecStaticCodeCheckValidity = 0`
- **AND** legacy TCC rows whose bundle identifiers match no installed bundle on disk (`com.realvnc.vncconnect` and `com.realvnc.vncviewer`) SHALL be reported as unverified stale rows rather than claimed as verified against mismatched bundles (`/Library/vnc/RealVNC Server.app` with `com.realvnc.vncserverui` or `/Applications/RealVNC Connect Viewer.app` with `com.realvnc.rvncconnect`)

### Requirement: Application termination routines for maintenance SHALL use POSIX signals and avoid AppleEvents

Workstation automation harnesses and maintenance pipelines SHALL terminate GUI and daemon processes exclusively using POSIX termination signals (`SIGTERM` followed by bounded timeout and `SIGKILL`) rather than AppleEvents automation (`osascript -e 'quit app ...'`), avoiding `kTCCServiceAppleEvents` permission prompts in macOS TCC.

#### Scenario: Graceful application shutdown via POSIX termination signals
- **WHEN** an automated pipeline or operator script requires quitting an application prior to cask upgrade
- **THEN** it SHALL issue `pkill -TERM -x "<binary>"` (or process-specific PID termination)
- **AND** it SHALL poll for process exit using non-blocking signals within a defined timeout (e.g., 5 seconds)
- **AND** it SHALL NOT execute AppleScript or `osascript` quit commands that require `com.apple.security.automation.apple-events` entitlements or trigger user dialogs

#### Scenario: Non-interactive vendor uninstaller execution
- **WHEN** a Homebrew cask upgrade invokes a vendor-provided uninstallation script containing interactive confirmation prompts
- **THEN** the pipeline SHALL supply explicit non-interactive flags or configure non-interactive bypass variables
- **AND** the uninstallation SHALL complete without blocking on standard input or timing out

### Requirement: Application bundle upgrades SHALL preserve permanent bundle attribution under client_type 0

When macOS application bundles subject to TCC controls (such as `ChatGPT.app`, `Orca.app`, `Goose.app`, `Hermes.app`) are updated or replaced through Homebrew Casks or manual staging, they SHALL preserve their canonical bundle identifiers and code signing requirements registered under `client_type = 0` in `TCC.db`.

#### Scenario: Post-upgrade TCC bundle verification
- **WHEN** an application cask upgrade completes in `/Applications`
- **THEN** `tcc_provenance.py --bundles` SHALL verify that the application's executable path exists, its code signature matches the stored requirement, and its entry in `TCC.db` evaluates to `client_type = 0`
- **AND** the verifier SHALL report status `CLEAN` with zero missing binaries or permission drift

### Requirement: Docker Desktop privileged helper lifecycle SHALL use socket-only provisioning without obsolete vmnetd probes

Workstation Docker management tools (`docker-service.sh`) SHALL provision `com.docker.socket` non-interactively via `install config --user <user>` and `install socket-symlink-on-startup --user <user>`, enforce `<string><user></string>` in `/Library/LaunchDaemons/com.docker.socket.plist` and synchronous `/var/run/docker.sock` symlinking, and omit obsolete `com.docker.vmnetd` probes so `com.docker.backend` never invokes `osascript` admin prompts.

#### Scenario: Docker Desktop helper verification without vmnetd
- **WHEN** `docker-service.sh` verifies or provisions privileged helper tools for Docker Desktop
- **THEN** it SHALL verify that `/Library/PrivilegedHelperTools/com.docker.socket` matches `/Applications/Docker.app/Contents/MacOS/com.docker.socket`
- **AND** it SHALL NOT fail or attempt to kickstart `system/com.docker.vmnetd` when `com.docker.vmnetd` is absent from `/Applications/Docker.app`
- **AND** it SHALL NOT trigger `SecurityAgent.ExecuteWithPrivileges` modal authentication dialogs during daemon startup

#### Scenario: Socket startup task plist user argument and synchronous symlink enforcement
- **WHEN** `ensure_helpers()` provisions `com.docker.socket` or `is_socket_helper_up()` checks helper readiness
- **THEN** `ensure_helpers()` SHALL pass `--user "$target_user"` to both `install config --user "$target_user"` and `install socket-symlink-on-startup --user "$target_user"` and execute `sudo -n ln -sfn "$socket_path" /var/run/docker.sock` after `launchctl kickstart -p system/com.docker.socket`
- **AND** `is_socket_helper_up()` SHALL require `/Library/LaunchDaemons/com.docker.socket.plist` to contain `<string>${target_user}</string>` and `/var/run/docker.sock` to resolve to `${socket_path}` so `com.docker.backend.cmdline` never detects an empty `""` plist user argument or missing `/var/run/docker.sock`

#### Scenario: Pre-emptive termination of vendor cask processes
- **WHEN** an application package or cask upgrade contains vendor preinstall scripts that execute `osascript` quit commands
- **THEN** the maintenance pipeline SHALL terminate the application's active processes using POSIX signals (`pkill -TERM`) prior to invoking the package installer
- **AND** the vendor preinstall script's running process check SHALL evaluate to false, preventing `kTCCServiceAppleEvents` permission prompts

### Requirement: Workstation maintenance SHALL enforce macOS user Keychain search-list hygiene and non-interactive CLI file credential stores

Workstation maintenance runners (`workstation-daily-update.sh` and `shb_schedule.workflows.workstation_update`) SHALL restrict the macOS user file-based Keychain search list to the unlocked `login.keychain-db` and SHALL enforce mode-`0600` file-backed credentials (`schema_version: 1` via `TBH_CREDENTIAL_BACKEND=file`) for `muse-aarch64-macos` without retaining `ai.meta.dev.credentials` items in `login.keychain-db`.

#### Scenario: Locked secondary keychains are removed from the user keychain search list
- **WHEN** `ensure_muse_credential_hygiene` inspects `security list-keychains -d user` on macOS
- **THEN** any secondary user keychain file outside `~/Library/Keychains/login.keychain-db` (such as a locked `openvpn.keychain-db`) SHALL be removed from the user search list via `security list-keychains -d user -s ~/Library/Keychains/login.keychain-db`
- **AND** `security list-keychains -d user` SHALL list only `~/Library/Keychains/login.keychain-db`

#### Scenario: Stale ai.meta.dev.credentials keychain entries and schema_version 2 pointers are healed post-upgrade
- **WHEN** `ensure_muse_credential_hygiene` runs during workstation maintenance or when `~/.config/muse/auth.json` is missing or contains `schema_version: 2` (`"storage": "keychain"`)
- **THEN** any `ai.meta.dev.credentials` generic password item in `login.keychain-db` SHALL be deleted via `security delete-generic-password -s "ai.meta.dev.credentials"` without invoking `security add-generic-password -A` (`PartitionID = apple:`, `OSStatus -67050`)
- **AND** `~/.config/muse/auth.json` SHALL be unlinked prior to running `TBH_CREDENTIAL_BACKEND=file /opt/homebrew/bin/muse auth set --provider meta --api-key-stdin` so `FM-008` slot-reference errors cannot occur
- **AND** `~/.config/muse` (`mode 0700`) and `~/.config/muse/auth.json` (`mode 0600`, `schema_version: 1`) SHALL be verified with zero `SecurityAgent` windows spawned
