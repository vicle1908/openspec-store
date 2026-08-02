## ADDED Requirements

### Requirement: Live host and dependency preflight
Before changing workstation state, the setup SHALL determine the live macOS version, architecture, display topology, Homebrew prefix and health, current Maccy installation state, current official Maccy cask metadata, Paste application/helper/process state, and Spotlight Clipboard Search state. The setup MUST stop before installation when the live cask is incompatible with the host or does not resolve to the official Maccy project release.

#### Scenario: Supported host passes preflight
- **WHEN** preflight runs on the designated macOS arm64 workstation and the live official cask supports its macOS version
- **THEN** the setup records a redacted baseline and permits the single-recorder migration to begin

#### Scenario: Unsupported or untrusted artifact stops setup
- **WHEN** the cask requirements exclude the detected host or its resolved download is not attributable to the official Maccy project
- **THEN** the setup performs no installation, consent, recorder shutdown, or clipboard-data deletion and reports the blocking mismatch

#### Scenario: Repeated preflight is idempotent
- **WHEN** preflight is repeated without a host or package-state change
- **THEN** it reports the same effective readiness without mutating applications, preferences, permissions, or clipboard history

### Requirement: Single active history recorder
The workstation SHALL use Maccy as its only active clipboard-history recorder during normal operation. Before Maccy acceptance testing, the setup MUST clear and disable Spotlight Clipboard Search, disable Paste launch/background activity, and quit Paste while preserving the Paste application and its data for rollback.

#### Scenario: Competing recorders are disabled
- **WHEN** the migration reaches the recorder-transition checkpoint
- **THEN** Spotlight Clipboard Search and Paste recording are inactive and a synthetic marker is not retained by either recorder; the check uses only a unique marker B copied while the recorder is inactive, immediately replaces the system clipboard with neutral C, and searches only for marker B without inspecting unrelated history

#### Scenario: Competing recorder remains active
- **WHEN** functional verification detects that Paste or Spotlight still records a synthetic marker
- **THEN** Maccy acceptance testing stops until the overlapping recorder is disabled and the marker test passes

#### Scenario: Recorder transition is safely repeatable
- **WHEN** the transition is rerun after Spotlight and Paste are already inactive
- **THEN** it leaves Paste installed, does not delete Paste data again, and preserves the single-recorder state

### Requirement: Verified Homebrew installation
The setup SHALL install the live compatible Maccy cask through Homebrew and MUST verify Homebrew inventory, the `org.p0deje.Maccy` bundle identity, bundle version, universal `x86_64`/`arm64` architecture, strict code signature, expected Developer ID signer/team, and Gatekeeper notarization assessment before requesting privileged macOS access. The researched 2.6.1 baseline signer is `Developer ID Application: Alexey Rodionov (MN3X4648SC)` with Team ID `MN3X4648SC`; a changed live official signer or Team ID MUST stop setup for review.

#### Scenario: Verified installation succeeds
- **WHEN** Homebrew installs Maccy and all identity, inventory, code-signature, and Gatekeeper checks pass
- **THEN** the setup records the resolved version and permits first launch and permission configuration

#### Scenario: Installation verification fails
- **WHEN** any required identity, version, signature, or Gatekeeper check fails
- **THEN** the setup does not grant Accessibility, does not configure launch at login, and reports the failed check without using a manual security override

#### Scenario: Already-current installation is accepted
- **WHEN** the exact live cask version is already installed and passes every verification check
- **THEN** rerunning setup skips reinstallation and continues from the first incomplete checkpoint

#### Scenario: Artifact provenance changes
- **WHEN** the live official artifact has a different signer, Team ID, or Gatekeeper provenance than the recorded baseline
- **THEN** setup stops before Accessibility or notification authorization and records the mismatch for explicit review

### Requirement: Explicit least-privilege consent
The configuration SHALL require the user to explicitly authorize Maccy Accessibility access before automatic paste is accepted. It SHALL authorize Maccy notifications and sounds through macOS settings, then disable all Maccy visual notification destinations and set per-app notification previews to `Never`; no clipboard title or payload may appear in a notification body. It MUST NOT require or silently grant Full Disk Access, Input Monitoring, Automation, Screen and System Audio Recording, or Developer Tools access.

#### Scenario: Required consent is granted
- **WHEN** the verified Maccy application requests Accessibility and notification access and the user approves it in System Settings
- **THEN** automatic paste and a synthetic sound-only test succeed, with Desktop, Notification Center, and Lock Screen visual destinations disabled where available and previews set to `Never`

#### Scenario: Required consent is denied or deferred
- **WHEN** the user denies or defers Accessibility access
- **THEN** setup pauses at the permission checkpoint, preserves the installed application and prior recorder rollback path, and does not claim automatic paste is configured

#### Scenario: Unexpected permission is requested
- **WHEN** Maccy or the setup requests a permission outside the approved Accessibility and notification scope
- **THEN** setup stops and reports the unexpected permission for review

### Requirement: Capability-complete secure settings profile
Maccy SHALL converge to the following externally visible profile: launch at login on; automatic update checks on; open shortcut `Control-Shift-Command-V`; pin shortcut `Option-P`; delete shortcut `Option-Delete`; Mixed search; automatic paste on; paste without formatting by default off; cursor popup on the active display; pins at top; 80-pixel image height; 700-millisecond preview delay; color match highlighting; special symbols, menu icon, always-visible search, title, source-application icons, and footer on; recent-copy menu text off; text, image, and file storage on; history size 999; sort by time of last copy; normal recording on; clear-on-quit off; and clear-system-clipboard-with-history on. `Control-Option-Command-V` SHALL be used only as a fallback after a live conflict with the primary shortcut is reproduced.

#### Scenario: Settings converge from defaults
- **WHEN** the operator applies the profile through Maccy's supported settings interface
- **THEN** every selected value is observable in the application and a redacted settings inventory matches the required profile

#### Scenario: Configuration is reapplied
- **WHEN** setup is rerun after the profile is already active
- **THEN** the effective settings remain unchanged and no history item, pin, permission, or shortcut is duplicated

#### Scenario: Unsafe literal all-on profile is avoided
- **WHEN** the operator reviews settings that could expose menu-bar clipboard text or clear retained history on every quit
- **THEN** recent-copy menu text and clear-on-quit remain off while their corresponding features remain available through safe explicit actions

### Requirement: Complete history, search, and editing behavior
Maccy SHALL retain and retrieve synthetic plain text, rich text, URLs, images, and files; SHALL make synthetic image text searchable through OCR; SHALL expose source-application icons when source metadata exists; and SHALL support Mixed search, page navigation, pinning, pin title/content editing for text, deletion, unpinned clearing, and explicit all-item clearing.

#### Scenario: Supported content round trip
- **WHEN** the operator copies one synthetic item for each supported content class
- **THEN** each item appears once, preserves the appropriate copy/paste representation, and is retrievable through history

#### Scenario: OCR and Mixed search succeed
- **WHEN** a generated image contains a unique synthetic phrase and the operator searches using exact, regular-expression, and fuzzy-fallback inputs
- **THEN** Maccy returns the expected synthetic item without exposing unrelated clipboard content in evidence

#### Scenario: Pin and clear semantics are distinct
- **WHEN** one safe synthetic text item is pinned and the operator clears unpinned history
- **THEN** unpinned synthetic items are removed, the pin remains editable, and an explicitly confirmed all-item clear can remove the pin

### Requirement: Keyboard-first paste and dual-display behavior
Maccy SHALL support copy-only selection, automatic paste, paste without formatting, repeated-shortcut cycle selection, and popup operation on both attached displays. The default shortcut MUST be checked for conflicts in representative applications and password fields before acceptance.

#### Scenario: Paste action variants work
- **WHEN** the operator selects synthetic rich text using copy-only, automatic paste, and paste-without-formatting actions
- **THEN** copy-only does not inject text, automatic paste preserves its stored representation, and plain-text paste removes formatting

#### Scenario: Cycle selection works
- **WHEN** the operator holds the popup modifiers, repeatedly presses the main popup key, and releases the modifiers
- **THEN** selection advances predictably and the selected synthetic item is confirmed once

#### Scenario: Both displays are usable
- **WHEN** the pointer and active application move between the two attached displays and Maccy is opened
- **THEN** the popup appears at the cursor on the active display without becoming unreachable or obscuring the wrong screen

#### Scenario: Shortcut conflict is detected
- **WHEN** the configured global shortcut conflicts with a system or application shortcut
- **THEN** acceptance stops for that shortcut, records the conflict without clipboard content, and requires a non-conflicting replacement followed by repeat testing

### Requirement: Sensitive-data exclusion controls
Maccy SHALL preserve its built-in confidential, transient, and auto-generated pasteboard protections; SHALL ignore `com.apple.is-remote-clipboard` by default; SHALL provide tested application, pasteboard-type, and regular-expression exclusions; and SHALL provide temporary pause and ignore-next-copy controls. The retained regex profile MUST contain exactly these patterns:

1. `(?s)-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----.*?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----`
2. `(?im)^\s*(?:export\s+)?(?:[A-Z0-9_]+_)?(?:PASSWORD|PASSWD|SECRET|TOKEN|API[_-]?KEY|PRIVATE[_-]?KEY)(?:_[A-Z0-9_]+)?\s*[:=]\s*["']?[^\s"']{8,}["']?\s*$`

Validation MUST compile both patterns under `NSRegularExpression`, pass their positive and negative synthetic fixtures, and MUST NOT copy real credentials, tokens, private keys, personal clipboard history, or production values.

#### Scenario: Exclusion mechanisms reject synthetic matches
- **WHEN** synthetic copies match the temporary ignored application, ignored pasteboard type, either exact retained regex, pause mode, or ignore-next-copy mode
- **THEN** none of those synthetic copies appears in Maccy history

#### Scenario: Safe negative fixtures remain available
- **WHEN** similar but non-sensitive synthetic content does not match an exclusion
- **THEN** Maccy retains the content and makes it searchable, proving that the rule is not indiscriminately suppressing history

#### Scenario: Invalid regular expression is rejected
- **WHEN** an exclusion pattern fails to compile or prevents later rules from being evaluated
- **THEN** the pattern is not accepted into the retained profile and the complete positive-and-negative fixture suite is rerun after correction

#### Scenario: Sensitive copy cannot be classified
- **WHEN** the user needs to copy sensitive data that cannot be reliably identified by source, type, or pattern
- **THEN** the user can pause recording or ignore the next copy and verify with a synthetic analogue that the control works

### Requirement: Restart, update, and resource continuity
Maccy SHALL start for the current user after login, preserve the selected profile and safe pins across an application restart, and expose its current version through both the application bundle and Homebrew inventory. Update actions MUST be serialized so an in-app update and Homebrew upgrade do not run concurrently.

#### Scenario: Login continuity succeeds
- **WHEN** the user logs out and back in after configuration
- **THEN** Maccy starts once, remains the sole recorder, retains the selected settings and safe pin, and passes a synthetic capture-and-paste check

#### Scenario: Update is available
- **WHEN** Maccy reports an update
- **THEN** the operator checks live Homebrew cask metadata, uses one update mechanism at a time, and repeats identity, signature, settings, and smoke verification after the update

#### Scenario: Resource use is unacceptable
- **WHEN** the soak period shows sustained unacceptable CPU, memory, disk growth, or popup latency under representative synthetic use
- **THEN** the operator records redacted measurements, reduces retention or image use for diagnosis, and does not declare the profile accepted until the regression is resolved or the rollout is rolled back

### Requirement: Redacted acceptance evidence
The change SHALL retain a redacted manifest at `artifacts/workstation/maccy/<run-id>/manifest.json`, where `<run-id>` is UTC `YYYYMMDDTHHMMSSZ`, using schema `microservices.maccy-workstation-validation/v1`. It SHALL contain `runId`, timestamps, a host summary limited to OS/build/architecture/display count, cask version/URL/SHA-256/signer, redacted settings, checks with `id`/`status`/`exitCode`/`evidenceRef`, soak measurements, and rollback status. Evidence MUST NOT contain a username, clipboard database contents, copied payloads, OCR output, actual secrets, personal history, protected TCC database contents, notification bodies, or unrelated sensitive paths.

#### Scenario: Complete redacted evidence is retained
- **WHEN** all acceptance checks pass
- **THEN** the manifest conforms to the required path, run-id, schema, and fields, identifies the tested host and Maccy version, maps every requirement to passing checks, and contains no clipboard payloads or secrets

#### Scenario: A check fails
- **WHEN** any installation, configuration, security, functional, restart, or rollback check fails
- **THEN** evidence records the failed check and remediation state and the corresponding implementation task remains incomplete

#### Scenario: Permission is verified safely
- **WHEN** Accessibility behavior is validated
- **THEN** evidence uses successful synthetic automatic paste and user-visible System Settings state rather than querying or copying the protected TCC database

### Requirement: Reversible migration and recovery
The rollout SHALL retain Paste unchanged but inactive for a three-day default soak and SHALL provide a non-destructive recovery path that can restore exactly one prior recorder. Normal rollback MUST uninstall Maccy without `--zap`; deletion of Maccy or Paste history MUST require a separate explicit confirmation after exact targets are re-resolved.

#### Scenario: Non-destructive rollback succeeds
- **WHEN** Maccy is paused and quit during the rollback rehearsal
- **THEN** one prior recorder is restored, synthetic capture and paste succeed, Paste data remains untouched, and Maccy can be re-enabled without reinstalling during the trial

#### Scenario: Normal uninstall is requested
- **WHEN** the user abandons Maccy after the trial
- **THEN** launch-at-login and Accessibility access are removed, Homebrew uninstalls the cask without `--zap`, one prior recorder is restored, and recoverable Maccy preferences/history are not intentionally deleted

#### Scenario: Destructive cleanup is requested
- **WHEN** the user separately approves full cleanup after the exact Homebrew zap targets and retained-data impact are shown
- **THEN** only the confirmed Maccy targets are removed and the result reports that the deleted history and preferences are not recoverable through normal uninstall rollback
