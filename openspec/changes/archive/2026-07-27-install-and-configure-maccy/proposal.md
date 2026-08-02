## Why

This macOS 26 Apple Silicon workstation currently has Paste installed and an initialized Spotlight clipboard history, but no Maccy installation or validated single-recorder policy. Installing Maccy without first resolving those overlapping recorders would increase sensitive-data retention, shortcut ambiguity, and rollback risk instead of providing a dependable keyboard-first clipboard workflow.

## What Changes

- Install the current compatible Maccy Homebrew cask only after a live Homebrew metadata and host-compatibility check, then verify the installed application with Homebrew inventory, code-signature validation, and Gatekeeper assessment.
- Establish Maccy as the only active clipboard-history recorder by clearing and disabling Spotlight Clipboard Search and disabling and quitting Paste while retaining Paste for a reversible trial period.
- Configure Maccy's useful feature surface: launch at login, update checks, global shortcuts and cycle selection, mixed search, automatic and plain-text paste paths, text/image/file history, OCR-backed image search, source-application icons, editable safe pins, sound-only notifications with visual destinations and previews disabled, and dual-display popup behavior.
- Grant only the macOS permissions required for the selected behavior through explicit user approval; the change will not bypass or reset Transparency, Consent, and Control permissions.
- Apply a security-oriented retention profile that preserves Maccy's confidential/transient pasteboard protections, ignores Universal Clipboard history by default, exercises application/type/regular-expression exclusions with synthetic fixtures, keeps recent clipboard text out of the menu bar, and prevents secrets from appearing in retained evidence.
- Validate feature behavior, privacy controls, login persistence, single-recorder operation, and rollback end to end, then retain a redacted configuration and verification record.
- Roll out in reversible stages: preflight and a non-destructive preservation checkpoint, competing-recorder shutdown, installation, permission grant, configuration, acceptance testing, and a soak period before any optional Paste removal.
- Keep rollback non-destructive by default: quit and uninstall Maccy without `--zap`, restore the prior recorder if needed, and require separate confirmation before deleting Maccy or Paste history.

### Goals

- Provide a fast, keyboard-first clipboard history that works across both attached displays.
- Make all useful Maccy capabilities available while treating clipboard history as sensitive local data.
- Produce concrete evidence that installation, configuration, permissions, exclusions, and rollback work on this Mac.

### Non-goals

- Change any microservice, public API, Protobuf contract, deployment topology, or service-owned data.
- Enable every preference indiscriminately when a toggle would expose recent clipboard text or defeat retained history.
- Synchronize Maccy history across devices or retain Universal Clipboard entries by default.
- Automate macOS consent prompts, modify the TCC database, delete existing Paste data, or run Homebrew `--zap` without a later explicit destructive-action decision.
- Permanently pin a remembered Maccy version; implementation must resolve and record the current official cask at execution time.

### Compatibility, Rollout, and Rollback

- The supported target is this macOS 26.5.2 arm64 workstation with Homebrew under `/opt/homebrew`; implementation must re-check the live OS, architecture, Homebrew health, and cask requirements before mutation.
- Rollout is local to the current macOS user and does not affect repository services, containers, CI, or other developers.
- Rollback restores the previous clipboard workflow before any old recorder is removed. A normal Homebrew uninstall preserves Maccy preferences and history for recovery; a full zap remains an explicit, separately approved cleanup action.

## Capabilities

### New Capabilities

- `maccy-workstation-clipboard-management`: Safe installation, single-recorder migration, full useful-feature configuration, sensitive-data exclusions, verification, retained evidence, and reversible rollback for Maccy on the designated macOS workstation.

### Modified Capabilities

None.

## Impact

- **Host applications:** `/Applications/Maccy.app`; the existing `/Applications/Paste.app` is disabled during the trial but not removed by this change.
- **macOS integration:** the current user's login items/background activity, Spotlight Clipboard Search, Accessibility permission, notification settings, menu bar, and two-display popup behavior.
- **Local data ownership:** clipboard history, OCR-derived search text, pins, exclusions, and preferences remain owned by the current macOS user and must be treated as sensitive workstation data.
- **Dependencies:** the official Homebrew `maccy` cask and the Maccy release it resolves to at implementation time. The researched baseline on 2026-07-27 is cask 2.6.1, macOS 14 or newer, with self-update support.
- **Repository:** this OpenSpec change and redacted validation evidence only; no service code, APIs, event contracts, persistence schemas, or cross-service dependencies change.
