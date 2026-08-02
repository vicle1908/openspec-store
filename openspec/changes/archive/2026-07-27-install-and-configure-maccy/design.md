## Context

The target is the current developer's Apple M1 workstation running macOS 26.5.2 with two active 1920x1080 displays and Homebrew 6.0.12 under `/opt/homebrew`. Read-only inspection on 2026-07-27 established:

- Homebrew reports the system ready, Maccy not installed, and the official `maccy` cask at 2.6.1 with a macOS 14 minimum, a GitHub release URL, a recorded SHA-256, and `auto_updates: true`.
- The researched 2.6.1 artifact has SHA-256 `84b95baf1961bdf30045188c855237f90c1426ac8f123b4ae8f74191f9f38682`, bundle version `60`, universal `x86_64` and `arm64` Mach-O slices, bundle identifier `org.p0deje.Maccy`, signer `Developer ID Application: Alexey Rodionov (MN3X4648SC)`, Team ID `MN3X4648SC`, a valid strict deep signature, a sandbox entitlement, and a Gatekeeper result of `source=Notarized Developer ID`. This is a verification baseline, not a permanent version pin; implementation must compare the live official artifact and stop for review if its signer or Team ID changes.
- `/Applications/Paste.app` 6.6.3 remains installed. Its background helper is registered as enabled, although no active Paste process was observed during inspection.
- macOS 26 provides Spotlight Clipboard Search, and the user's Spotlight preferences contain `PasteboardHistoryVersion = 2`.
- Maccy's 2.6.1 source exposes General, Appearance, Storage, Pins, Ignore, and Advanced settings. Automatic pasting requires explicit Accessibility authorization; storage supports text, images, and files; image history supports OCR search; exclusions support applications, pasteboard types, and regular expressions.
- No installed password-manager application was found under the normal Applications directories. Browser-extension copies still require pasteboard-type, regular-expression, or temporary-pause protection because their source application appears as the browser.

The evidence output is a redacted manifest at `artifacts/workstation/maccy/<run-id>/manifest.json`, where `<run-id>` is UTC `YYYYMMDDTHHMMSSZ` and the schema identifier is `microservices.maccy-workstation-validation/v1`. It contains only `runId`, timestamps, a host summary (OS/build/architecture/display count), cask metadata (version/URL/SHA-256/signer), redacted settings, check records (`id`, `status`, `exitCode`, `evidenceRef`), soak measurements, and rollback status. It never contains a username, clipboard payload, OCR text, notification body, TCC database content, or unrelated personal paths.

Primary implementation references:

- [Maccy 2.6.1 documentation](https://github.com/p0deje/Maccy/blob/2.6.1/README.md)
- [Maccy 2.6.1 settings source](https://github.com/p0deje/Maccy/tree/2.6.1/Maccy/Settings)
- [Maccy releases](https://github.com/p0deje/Maccy/releases)
- [Homebrew Maccy cask](https://formulae.brew.sh/cask/maccy)
- [Homebrew cask definition](https://github.com/Homebrew/homebrew-cask/blob/HEAD/Casks/m/maccy.rb)
- [Apple Accessibility authorization](https://support.apple.com/guide/mac-help/mh43185/mac)
- [Apple Spotlight Clipboard Search settings](https://support.apple.com/guide/mac-help/mchl54d95e8a/mac)
- [Apple Login Items and App Background Activity](https://support.apple.com/guide/mac-help/mtusr003/mac)

This change has no service ownership boundary, database transaction, delivery guarantee, event ordering, idempotency contract, event version, container image, or cross-service dependency. Homebrew owns installation of the app bundle; macOS owns consent and login/background integration; Maccy owns its local clipboard database and preferences; the current macOS user owns all retained clipboard content and approval decisions.

## Goals / Non-Goals

**Goals:**

- Make Maccy the sole active clipboard-history recorder after a reversible migration.
- Enable the complete useful feature surface while keeping sensitive display and destructive-retention toggles at safe values.
- Use the official Homebrew cask resolved at execution time and verify the resulting application before granting privileged access.
- Require explicit user consent for Accessibility and notifications.
- Validate behavior with synthetic content across text, rich text, image OCR, files, search, paste, pins, exclusions, clearing, two displays, and login persistence.
- Retain redacted, reproducible evidence without retaining clipboard payloads, OCR text, actual secrets, or personal application data.

**Non-Goals:**

- Change microservice code, deployment assets, CI, public contracts, or canonical platform behavior.
- Automate or bypass TCC, edit TCC databases, or infer permission success from preference-file presence alone.
- Keep Paste, Spotlight Clipboard Search, and Maccy recording concurrently.
- Expose recent clipboard text in the menu bar, store Universal Clipboard entries by default, or pin secrets.
- Delete Paste data or run a Maccy/Paste zap as part of initial rollout.
- Guarantee that a version researched during proposal authoring remains current at implementation time.

## Decisions

### 1. Use one active clipboard-history recorder

Maccy will be the only active history recorder. Before Maccy begins normal recording, the operator will clear Spotlight Clipboard History, turn Spotlight Clipboard Search off, disable Paste's launch/background activity, and quit Paste. Paste remains installed and its data remains untouched through the soak period. Recorder shutdown is verified with a neutral-marker protocol: capture a baseline without inspecting payloads, copy a unique marker B only after the recorder is inactive, immediately replace the system clipboard with neutral C, and inspect only for marker B in the disabled recorder.

This avoids duplicate sensitive retention, ambiguous shortcuts, and unclear deletion semantics. Coexistence is technically possible but rejected because it would make a successful Maccy clear or exclusion test insufficient: another recorder could still retain the same payload. Using only Spotlight was rejected because it does not provide Maccy's pins, exclusion controls, direct paste workflow, source icons, or configurable search behavior. Retaining Paste was rejected because the requested target is Maccy and Paste's helper is already an overlapping recorder.

### 2. Resolve the Homebrew cask live and verify before trust

Implementation will run a non-mutating host and Homebrew preflight, refresh Homebrew metadata, and inspect `brew info --json=v2 --cask maccy` before installation. It will refuse to continue if the live cask does not support the detected OS/architecture, does not resolve to the official project release, or Homebrew health is unsuitable.

Installation uses `brew install --cask maccy`. Before Accessibility authorization, implementation verifies:

- Homebrew inventory reports the resolved version.
- `/Applications/Maccy.app` exists with bundle identifier `org.p0deje.Maccy`.
- the live artifact signer and Team ID match the official release provenance; for the researched 2.6.1 baseline this is `Developer ID Application: Alexey Rodionov (MN3X4648SC)` / `MN3X4648SC`.
- the researched 2.6.1 baseline has bundle version `60`, universal `x86_64`/`arm64` slices, and Gatekeeper reports `source=Notarized Developer ID`; a changed live signer, Team ID, or provenance stops setup for review.
- `codesign --verify --deep --strict` succeeds.
- `spctl --assess --type execute` succeeds.
- the installed bundle version agrees with the Homebrew-resolved artifact or a documented self-update transition.

Direct release downloads and the Mac App Store were rejected because Homebrew is already healthy, provides a versioned SHA-256 and official release URL, and supplies explicit uninstall/zap metadata. The proposal records 2.6.1 only as the researched baseline, not as a permanent pin.

### 3. Use UI-backed configuration for consent and schema safety

Maccy's settings UI is the authority for initial configuration. This avoids writing undocumented serialized values for keyboard shortcuts, launch-at-login state, or settings whose storage schema may change. Documented `defaults` commands may be used for the temporary `ignoreEvents` and `ignoreOnlyNextEvent` controls after the UI baseline is established, but not to bypass consent.

The operator must explicitly grant Accessibility through System Settings after verifying the application identity. The operator may approve Maccy's notification authorization and sound capability, but must disable every Maccy visual notification destination (Desktop, Notification Center, and Lock Screen where shown) and set per-app notification previews to `Never`; Maccy must not surface clipboard titles in a visual notification body. The acceptance check triggers a synthetic selection/paste and confirms a sound-only result with no visual body. No Full Disk Access, Input Monitoring, Automation, Screen Recording, or Developer Tools permission is expected; any unexpected permission request stops implementation for review.

### 4. Apply a capability-complete secure profile

The selected profile is:

| Area | Setting | Target |
| --- | --- | --- |
| General | Launch at login | On |
| General | Check for updates automatically | On |
| General | Open shortcut | `Control-Shift-Command-V` (fallback `Control-Option-Command-V` only after a live conflict check) |
| General | Pin shortcut | `Option-P` |
| General | Delete shortcut | `Option-Delete` |
| General | Search | Mixed |
| General | Paste automatically | On |
| General | Paste without formatting by default | Off |
| Appearance | Popup location | Cursor on active display |
| Appearance | Pinned items | Top |
| Appearance | Image height | 80 px |
| Appearance | Preview delay | 700 ms |
| Appearance | Highlight matches | Color |
| Appearance | Special symbols | On |
| Appearance | Menu icon | On, Maccy icon |
| Appearance | Recent copy beside menu icon | Off |
| Appearance | Search field | On, always visible |
| Appearance | Title | On |
| Appearance | Source application icons | On |
| Appearance | Footer | On |
| Storage | Stored types | Text, images, and files |
| Storage | History size | 999 |
| Storage | Sort order | Time of last copy |
| Advanced | Recording paused | Off during normal use |
| Advanced | Clear history on quit | Off |
| Advanced | Clear system clipboard with history | On |

“All features” is interpreted as making every useful workflow available, not setting every Boolean to true. Plain-text paste remains available through its modifier rather than becoming the default. Clear-on-quit remains off so launch/restart validation and ordinary history retention are meaningful. Recent-copy menu text remains off because it can disclose secrets during screen sharing.

Maccy's in-app update check remains enabled, but Homebrew remains the installation inventory. When an update is offered, the operator first checks the current cask and prefers `brew upgrade --cask maccy` when the cask has caught up; simultaneous in-app and Homebrew upgrades are avoided. `Shift-Command-C` is not used because Apple documents it as Finder's Computer shortcut; the target shortcut is `Control-Shift-Command-V`, with `Control-Option-Command-V` as the fallback only if a live conflict is reproducible.

### 5. Treat clipboard history and OCR-derived text as sensitive local data

The default confidential/transient pasteboard protections remain intact. `com.apple.is-remote-clipboard` is added to ignored pasteboard types so Universal Clipboard content is not retained locally by default. Application ignore behavior is tested temporarily with a harmless application and then removed unless an installed application needs a durable exclusion.

Regular-expression exclusions use these exact `NSRegularExpression` patterns:

1. `(?s)-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----.*?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----`
2. `(?im)^\s*(?:export\s+)?(?:[A-Z0-9_]+_)?(?:PASSWORD|PASSWD|SECRET|TOKEN|API[_-]?KEY|PRIVATE[_-]?KEY)(?:_[A-Z0-9_]+)?\s*[:=]\s*["']?[^\s"']{8,}["']?\s*$`

Pattern 1 is exercised with synthetic RSA/EC/OpenSSH private-key blocks and public-key/documentation negatives. Pattern 2 is exercised with synthetic `API_KEY=...`, `export SERVICE_TOKEN=...`, and `db_password: ...` positives plus short-token, documentation, `DATABASE_URL`, and empty-value negatives. Both patterns must compile under `NSRegularExpression`, be tested for false positives before retention, and never receive real tokens, passwords, private keys, or production values.

Pins use synthetic, non-secret snippets only. The temporary pause and “ignore next copy” controls are exercised with dummy content and documented as the primary fallback for sensitive copies that cannot be reliably classified.

### 6. Validate observable behavior and retain redacted evidence

Acceptance validation covers:

- plain text, rich text, URL, image, file, and source-application capture;
- OCR search using a generated image containing synthetic text;
- exact-result, regular-expression, and fuzzy-fallback behavior through Mixed search;
- copy-only, automatic paste, paste without formatting, cycle selection, page navigation, pin/edit/unpin, deletion, and clearing;
- ignored application, ignored pasteboard type, ignored regular expression, temporary pause, and ignore-next-copy behavior;
- both displays, menu/footer access, sound-only notification behavior with no visual body, and login restart;
- Homebrew inventory, process state, login item state, Accessibility behavior, and absence of active Paste/Spotlight recording;
- non-destructive rollback rehearsal.

Evidence records commands, exit status, app and OS versions, selected settings, test identifiers, and pass/fail results in `artifacts/workstation/maccy/<run-id>/manifest.json` using schema `microservices.maccy-workstation-validation/v1`. The `run-id` is UTC `YYYYMMDDTHHMMSSZ`; fields are `runId`, timestamps, redacted `host`, `cask`, `settings`, `checks` (`id`, `status`, `exitCode`, `evidenceRef`), `soak`, and `rollback`. It must not include a username, clipboard database contents, copied payloads, OCR output, private paths beyond what is necessary, secrets, TCC database dumps, notification bodies, or personal history content. Permission is proven by successful automatic-paste behavior and the visible System Settings state, not by attempting to read protected TCC storage.

### 7. Keep migration and rollback staged

The migration retains a working escape path at every stage. Existing Paste data is not imported because there is no required or source-verified lossless migration contract. Paste remains installed but inactive until Maccy completes a soak period. Spotlight history is cleared before its recorder is disabled.

Normal rollback:

1. Pause and quit Maccy.
2. Disable Maccy's launch-at-login entry and revoke Accessibility if abandoning the app.
3. Run `brew uninstall --cask maccy` without `--zap`.
4. Re-enable either Paste or Spotlight Clipboard Search, but not both by default.
5. Verify capture and paste behavior with synthetic content.

Full cleanup with `brew uninstall --cask --zap maccy` removes the login item, container, preferences, and history. It is outside initial rollback and requires explicit confirmation after the exact targets are re-resolved.

## Risks / Trade-offs

- **[Clipboard managers inherently retain sensitive data]** -> Keep one recorder, preserve confidential pasteboard exclusions, add tested regex/type filters, ignore Universal Clipboard by default, teach temporary pause, and retain no clipboard payloads in evidence.
- **[Accessibility permission grants broad control]** -> Verify provenance and code signature first, grant only Accessibility, stop on unexpected permission requests, and revoke on abandonment.
- **[Multiple recorders could silently retain excluded test data]** -> Clear and disable Spotlight, disable and quit Paste, then verify process/background and functional state before testing Maccy exclusions.
- **[A 999-item history with images and OCR consumes more disk and exposes more data]** -> Record database size, use only synthetic acceptance images, validate clear behavior, and reduce the limit later if the soak period shows unacceptable resource or privacy cost.
- **[Regular expressions can miss secrets or hide legitimate copies]** -> Use multiple synthetic fixtures, verify positive and negative behavior, keep patterns simple, and retain temporary pause as the fail-safe.
- **[Maccy self-update and Homebrew inventory can drift]** -> Enable checks but serialize update actions, compare bundle and cask versions, and record any self-update transition.
- **[Keyboard shortcuts can conflict with macOS or another app]** -> Disable Paste first, test the default Maccy shortcut across representative apps and password fields, and change it only if the conflict is reproducible.
- **[GUI-only consent prevents fully unattended implementation]** -> Treat the user approval step as an explicit checkpoint and continue automatically after approval rather than modifying protected databases.
- **[Clearing Spotlight history is destructive]** -> Confirm the target and capture only non-content baseline evidence before clearing; retain Paste unchanged as the initial rollback source.

## Migration Plan

1. Capture a redacted baseline: OS/architecture, displays, Homebrew health and cask metadata, Maccy absence, Paste version/helper/process state, Spotlight Clipboard Search state, current shortcut conflicts, and the preservation checkpoint. Write it to `artifacts/workstation/maccy/<run-id>/manifest.json` with the required schema and no payloads.
2. Confirm any Paste history that the user needs remains available for rollback; do not export or inspect its contents without a separate request.
3. Clear Spotlight Clipboard History, disable Clipboard Search, disable Paste launch/background activity, quit Paste, and verify neither recorder captures a synthetic marker using the neutral-marker protocol: record baseline, copy unique marker B only while the recorder is inactive, immediately replace the system clipboard with neutral C, then inspect only for marker B in Paste/Spotlight. Do not inspect or retain unrelated history.
4. Install the live official Maccy cask and verify Homebrew inventory, bundle identity, code signature, Gatekeeper assessment, and launch.
5. Grant Accessibility and notification authorization explicitly, set Maccy notifications to sound-only (visual destinations off and previews `Never`), then apply the target profile through Maccy's settings UI.
6. Configure and test exclusions with synthetic data before performing broad feature tests.
7. Run the complete two-display, restart/login, security, and rollback acceptance matrix; retain redacted evidence and fix any failed item before marking its task complete.
8. Run a three-to-seven-day soak with Paste still installed but inactive. Record only resource measurements and functional failures, never clipboard content.
9. After soak acceptance, leave Paste inactive or request a separate destructive removal decision. Do not zap either application as part of this change.

Rollback can be invoked after any failed stage using Decision 7. Repeated execution must be idempotent: preflight detects already-completed steps, installation accepts an already-current cask, configuration converges to the selected values, and recorder shutdown does not delete Paste.

## Resolved Follow-ups

- Use a three-day soak by default; extend to seven days only when image/OCR or multi-display behavior is unstable or resource measurements require more evidence.
- Leave Paste installed but inactive after acceptance. Permanent removal is a separate explicit change.
- Keep Universal Clipboard retention off by default. Enabling it later is a conscious privacy trade-off and requires repeating the exclusion and single-recorder tests.
