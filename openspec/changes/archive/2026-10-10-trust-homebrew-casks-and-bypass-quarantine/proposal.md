# Proposal

## Why

When Homebrew installs GUI applications and developer tools via Casks without explicit quarantine exclusion, macOS attaches the `com.apple.quarantine` extended attribute. This triggers recurring Gatekeeper confirmation dialogs ("Homebrew Cask downloaded this file today at ... Apple checked it for malicious software and none was detected"), interrupting unattended automation and agent workflows. Establishing standard Homebrew Cask trust options (`HOMEBREW_CASK_OPTS="--no-quarantine"`) and purging existing quarantine attributes from installed bundles ensures developer tooling runs seamlessly without interactive prompts.

## What Changes

- Configure `HOMEBREW_CASK_OPTS="--no-quarantine"` persistently across interactive and login shell initialization files (`~/.zshrc`, `~/.zprofile`).
- Recursively strip legacy `com.apple.quarantine` extended attributes from all applications in `/Applications` and `/opt/homebrew/Caskroom`.
- Update `workstation-remote-and-agent-permissions` specification to establish quarantine-bypass and cask trust standards for developer workstations.

## Capabilities

### New Capabilities
<!-- None -->

### Modified Capabilities
- `workstation-remote-and-agent-permissions`: Expanded to include Gatekeeper quarantine bypass and declarative Homebrew Cask trust options.

## Impact

- Affected systems: Developer shell environments (`~/.zshrc`, `~/.zprofile`), `/Applications/*.app`, `/opt/homebrew/Caskroom`.
- Dependencies: Homebrew Caskroom, macOS Gatekeeper (`spctl`/`xattr`).
- Non-goals: Disabling system Gatekeeper globally (`spctl --master-disable`); changes are targeted at trusted developer cask installations.
