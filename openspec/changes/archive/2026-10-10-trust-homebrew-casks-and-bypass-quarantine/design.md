# Design

## Context

See `proposal.md` for background.
macOS Gatekeeper inspects extended attribute `com.apple.quarantine` on application bundles downloaded through browsers and non-notarized external pipelines. By default, Homebrew attaches this attribute during cask downloads unless `--no-quarantine` is supplied. When an agent or developer launches a quarantined application, WindowServer presents a blocking modal dialog requiring manual confirmation ("Homebrew Cask downloaded this file today...").

## Goals / Non-Goals

**Goals:**
- Guarantee all current and future Homebrew Casks install without `com.apple.quarantine`.
- Purge legacy quarantine attributes from all developer applications across `/Applications` and `/opt/homebrew/Caskroom`.
- Maintain standard system security posture without disabling system-wide Gatekeeper (`spctl`).

**Non-Goals:**
- Completely disabling macOS System Integrity Protection or global assessment policies.

## Decisions

1. **Declarative Environment Export in Zsh Profiles**:
   - *Decision*: Export `HOMEBREW_CASK_OPTS="--no-quarantine"` in both `~/.zprofile` (login shells) and `~/.zshrc` (interactive shells).
   - *Rationale*: Guarantees that commands run from GUI wrappers, automated background agents, and interactive terminal sessions consistently pass `--no-quarantine` to Homebrew.

2. **Recursive Extended Attribute Stripping**:
   - *Decision*: Strip `com.apple.quarantine` across `/opt/homebrew/Caskroom` and `/Applications/*.app` using `xattr -dr com.apple.quarantine`.
   - *Rationale*: Eliminates existing quarantine tags immediately without requiring reinstalling dozens of gigabytes of developer casks.

## Risks / Trade-offs

- **Risk**: Overwriting application bundle code signatures.
  - *Mitigation*: Extended attributes live outside Mach-O code signatures; stripping `com.apple.quarantine` does not invalidate `_CodeSignature/CodeResources` or designated requirements.
