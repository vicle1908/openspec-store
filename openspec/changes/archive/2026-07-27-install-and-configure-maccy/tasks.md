## 1. Preflight and Safe Evidence Setup

Manual-only acceptance checkpoints are documented in
[`manual-operations.md`](manual-operations.md). Complete and record those
checkpoints before marking the corresponding tasks below done.

- [x] 1.1 Create `artifacts/workstation/maccy/<run-id>/manifest.json`, using UTC `YYYYMMDDTHHMMSSZ` and schema `microservices.maccy-workstation-validation/v1`; record only `runId`, timestamps, redacted host/cask/settings, check `id`/`status`/`exitCode`/`evidenceRef`, soak, and rollback fields, with no username or clipboard/OCR payloads.
- [x] 1.2 Re-check current official Maccy, Homebrew, and Apple guidance and record the live cask version, source URL, SHA-256, self-update flag, macOS requirement, zap targets, bundle version, signer, Team ID, architecture, and notarization result; stop for review if official signer/team or provenance differs from the researched baseline rather than treating 2.6.1 as a permanent pin.
- [x] 1.3 Capture and verify the live host baseline: macOS/build, arm64 architecture, two-display topology, `/opt/homebrew` health, Maccy state, Paste version/helper/process state, Spotlight Clipboard Search state, and relevant shortcut conflicts.
- [x] 1.4 Prepare synthetic positive and negative fixtures for text, rich text, URL, image OCR, file, application/type ignore, pause, and clear tests; compile and fixture-test the exact private-key regex `(?s)-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----.*?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----` and credential-assignment regex `(?im)^\s*(?:export\s+)?(?:[A-Z0-9_]+_)?(?:PASSWORD|PASSWD|SECRET|TOKEN|API[_-]?KEY|PRIVATE[_-]?KEY)(?:_[A-Z0-9_]+)?\s*[:=]\s*["']?[^\s"']{8,}["']?\s*$`; verify that no fixture contains a real credential or personal clipboard content.

## 2. Single-Recorder Migration

- [x] 2.1 Show the user the exact Spotlight history and Paste background targets, confirm the destructive Spotlight-history clear, and confirm that required Paste data remains available without inspecting or exporting its contents.
- [x] [historical] 2.2 Clear Spotlight Clipboard History, turn Clipboard Search off, and verify with the neutral-marker protocol: copy unique marker B only while Spotlight is inactive, immediately replace the system clipboard with neutral C, and inspect only for marker B.
- [x] 2.3 Disable Paste launch/background activity, quit Paste, preserve `/Applications/Paste.app` and its data, and verify with process, background-item, and the same neutral-marker protocol that Paste no longer records; do not inspect unrelated history.

## 3. Verified Maccy Installation

- [x] 3.1 Refresh Homebrew metadata, fail safely on an incompatible or untrusted cask, and install the live official Maccy cask with `brew install --cask maccy` when preflight passes.
- [x] 3.2 Verify Homebrew inventory, `/Applications/Maccy.app`, bundle identifier `org.p0deje.Maccy`, bundle/cask version agreement, universal `x86_64`/`arm64` slices, SHA-256, strict code signature, expected signer/Team ID, and Gatekeeper assessment with `source=Notarized Developer ID`; stop before permission grant if any check fails or provenance changes.
- [x] 3.3 Launch only the verified application, confirm a single Maccy process and no competing recorder process, and record the installed identity without capturing application history content.

## 4. Permissions and Settings Convergence

- [x] [historical] 4.1 Guide the user through explicit Accessibility and notification authorization, set Maccy's visual notification destinations off and previews to `Never`, keep sound on, prove Accessibility through a synthetic automatic-paste test, and prove a synthetic sound-only notification with no visual body; stop for review if Full Disk Access, Input Monitoring, Automation, Screen Recording, Developer Tools, or another unexpected permission is requested.
- [x] 4.2 Configure launch at login, automatic update checks, `Control-Shift-Command-V` open (fallback `Control-Option-Command-V` only after a live conflict), `Option-P` pin, `Option-Delete` delete, Mixed search, automatic paste on, and paste-without-formatting-by-default off; verify every General value and shortcut.
- [x] 4.3 Configure cursor popup on the active display, pins at top, 80-pixel images, 700-millisecond preview, color highlighting, visible special symbols/menu/search/title/source icons/footer, hidden recent-copy menu text, all three storage classes, 999-item history, and last-copy sort; verify every Appearance and Storage value.
- [x] 4.4 Configure normal recording on, clear-on-quit off, clear-system-clipboard-with-history on, preserved default confidential/transient types, ignored Universal Clipboard type, and the two exact compiled regexes from task 1.4; retain only redacted setting names and outcomes.

## 5. Functional and Security Acceptance

- [x] 5.1 Verify one-time round trips for synthetic plain text, rich text, URL, image, and file copies, including correct source-application icon behavior and absence of duplicate records.
- [x] 5.2 Verify OCR search on a generated synthetic image and exercise exact, regular-expression, and fuzzy-fallback results through Mixed search without retaining the copied phrase or OCR output in evidence.
- [x] [historical] 5.3 Verify copy-only, automatic paste, paste without formatting, repeated-shortcut cycle selection, page navigation, pin/edit/unpin, delete, clear-unpinned, explicit clear-all, and system-clipboard clear semantics with synthetic content.
- [x] [historical] 5.4 Verify ignored application, ignored pasteboard type, both exact positive and negative regex fixture suites, pause-recording, and ignore-next-copy behavior; correct and retest any invalid or overbroad pattern before retaining it.
- [x] [historical] 5.5 Verify the popup and shortcut on both displays and in representative applications/password fields, verify sound-only notification behavior with visual destinations off and previews `Never`, and resolve any reproducible shortcut conflict before acceptance.

## 6. Persistence, Resource Soak, and Recovery

- [x] [historical] 6.1 Restart Maccy and, at a user-coordinated checkpoint, log out and back in; verify one launch-at-login instance, retained settings and safe pin, sole-recorder state, and a synthetic capture-and-paste smoke test.
- [x] 6.2 Verify update ownership by comparing Homebrew and bundle versions, documenting the serialized Homebrew-preferred update procedure, and rerunning identity/signature/settings/smoke checks if an update occurs.
- [x] [historical] 6.3 Record redacted CPU, memory, disk-size, and popup-latency baselines in the required manifest, complete the default three-day soak with Paste installed but inactive, and extend to seven days or remediate before acceptance if resource or functional behavior is unstable.
- [x] [historical] 6.4 Rehearse non-destructive recovery by pausing and quitting Maccy, restoring exactly one prior recorder, proving synthetic capture/paste, then returning to the accepted Maccy-only state without deleting Paste or Maccy data.
- [x] [historical] 6.5 After soak acceptance, record the decision to leave Paste inactive or request a separate destructive-removal change; do not run `--zap` or delete either history under this task.

## 7. OpenSpec and Handoff Validation

- [x] 7.1 Validate the affected change with `openspec validate install-and-configure-maccy --type change --strict --no-interactive` and correct every issue before handoff.
- [x] 7.2 Run `openspec validate --all --strict --no-interactive`, distinguish any pre-existing repository failures from this change, and retain the exact result without claiming unrelated failures were fixed.
- [x] [historical] 7.3 Review proposal, design, capability scenarios, completed task evidence, required manifest path/schema, privacy redaction, rollback status, and soak outcome together; then run the OpenSpec verify workflow before any sync or archive decision.


---

> **Historical record:** This change was archived with 10 incomplete task(s) (17/27 completed). The remaining tasks were not implemented or were superseded by subsequent changes.
