# Design

## Context

See `proposal.md` for initial motivation.
macOS Transparency, Consent, and Control (TCC) enforces strict application sandboxing and permission requirements for Accessibility (`kTCCServiceAccessibility`), Screen Recording (`kTCCServiceScreenCapture`), and Full Disk Access (`kTCCServiceSystemPolicyAllFiles`). The underlying system SQLite database (`/Library/Application Support/com.apple.TCC/TCC.db`) is protected by System Integrity Protection (SIP) against direct mutation, requiring authorization changes to occur via user approval, System Settings privacy toggles, or official application triggers.

Additionally, Homebrew Caskroom maintains application packages in `/opt/homebrew/Caskroom/<cask>/<version>`, symlinking or copying application bundles into `/Applications`. When multiple versions or incomplete uninstalls occur, legacy launch daemons, privileged helpers, or duplicate bundles can conflict with running instances.

## Goals / Non-Goals

**Goals:**
- Manage AnyDesk strictly through official Homebrew Cask (`anydesk`), pulling the latest available release (9.8.1).
- Ensure zero duplicate AnyDesk bundles or rogue background processes exist across `/Applications` or user directories.
- Register AnyDesk's native privileged helper (`com.philandro.anydesk.Helper`) and system daemon (`com.philandro.anydesk.service`) under launchd.
- Authorize all required TCC permissions (`kTCCServiceAccessibility`, `kTCCServiceScreenCapture`, `kTCCServiceSystemPolicyAllFiles`) with `auth_value = 2` (Allowed).
- Audit and ensure complete TCC permissions for key AI coding assistants (Orca, OMP, ChatGPT, and Codex).

**Non-Goals:**
- Disabling System Integrity Protection (SIP) to bypass macOS security frameworks.
- Automating unmanaged filesystem deletions outside standard package manager lifecycle.
- Granting unnecessary permissions (e.g., Camera or Microphone) to tools that do not require them.

## Decisions

1. **Clean Reinstallation via `brew reinstall --cask anydesk`**:
   - *Decision*: Execute official Homebrew cask uninstallation and fresh reinstallation rather than manual DMG dragging or ad-hoc binary patching.
   - *Rationale*: Homebrew cleanly executes cask uninstall hooks (terminating running services and cleaning obsolete launchd plists) before installing the new bundle into `/Applications/AnyDesk.app`.
   - *Alternative*: Manual curl and mount was considered, but violates workstation Homebrew-first management principles.

2. **UI-Driven TCC Authorization through System Settings**:
   - *Decision*: Trigger application permission requests and toggle switches via System Settings (`x-apple.systempreferences:com.apple.preference.security`) rather than trying direct `TCC.db` sqlite modifications.
   - *Rationale*: Direct writes to `/Library/Application Support/com.apple.TCC/TCC.db` are blocked by SIP (`Operation not permitted` / `attempt to write a readonly database`). Interacting with System Settings updates both the in-memory `tccd` daemon state and persistent database cleanly.
   - *Alternative*: Mobileconfig profile injection requires MDM enrollment, which is absent on this standalone developer workstation.

3. **Composite Agent Permission Verification Matrix**:
   - *Decision*: Audit Orca, OMP, ChatGPT, and Codex across bundle IDs (`com.stablyai.orca`, `com.stablyai.orca.computer-use`, `com.openai.codex`, `com.openai.sky.CUAService`, `com.codexuse.desktop`, and OMP's Mach-O designated requirement) in `/Library/Application Support/com.apple.TCC/TCC.db`.
   - *Rationale*: Confirms actual runtime authorization state and guarantees that computer-use/screen-capture capabilities are available without permission crashes.

## Risks / Trade-offs

- **Risk**: AnyDesk restart requirement after toggling Full Disk Access.
  - *Mitigation*: Handled by responding to the System Settings "Quit & Reopen" prompt, allowing AnyDesk to boot with full disk access privileges active.
- **Risk**: Upstream Caskroom metadata caching `9.8.0` while upstream DMG serves `9.8.1`.
  - *Mitigation*: Confirmed that `url "https://download.anydesk.com/anydesk.dmg"` carries `sha256 :no_check`, delivering latest version 9.8.1 with matching Info.plist bundle verification.
