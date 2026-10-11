# Tasks

## 1. Configure Persistent Homebrew Cask Quarantine Bypass

- [x] 1.1 Export `HOMEBREW_CASK_OPTS="--no-quarantine"` in `~/.zprofile` for login shell environments
- [x] 1.2 Export `HOMEBREW_CASK_OPTS="--no-quarantine"` in `~/.zshrc` for interactive shell environments
- [x] 1.3 Verify `brew config` reflects `HOMEBREW_CASK_OPTS: ["--no-quarantine"]`

## 2. Eliminate Quarantine Attributes on Installed Applications

- [x] 2.1 Recursively strip `com.apple.quarantine` from `/opt/homebrew/Caskroom`
- [x] 2.2 Recursively strip `com.apple.quarantine` from `/Applications/*.app`
- [x] 2.3 Verify zero remaining `com.apple.quarantine` attributes across primary developer apps (AnyDesk, Orca, ChatGPT, Zed, Antigravity)

## 3. OpenSpec Spec Synchronization & Archive

- [x] 3.1 Synchronize delta spec to canonical `workstation-remote-and-agent-permissions` main spec
- [x] 3.2 Record verification evidence ledger in `evidence.md`
- [x] 3.3 Validate and archive change in `openspec-store`
