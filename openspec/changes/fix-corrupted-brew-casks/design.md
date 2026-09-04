## Context

Six Homebrew casks are in a corrupted state: `/Applications/<App>.app` directories exist but contain no `Info.plist`, no executable, and no frameworks — they are empty shells. The actual application bundles (v1.4.197, v1.136.1, v0.33.3, v152.0.7977.83, v12.25.3, v0.2026.09.02) are stranded in `/opt/homebrew/Caskroom/<cask>/<version>.upgrading/` directories, which Homebrew leaves behind when an upgrade is interrupted before the new version's install step completes.

Two additional non-Homebrew apps (AutoForward Messages, Nicegram) also have corrupted bundles but are outside the scope of this fix.

## Goals / Non-Goals

**Goals:**
- Restore all 6 corrupted apps to working state
- Clean up stale `.upgrading/` directories from the Caskroom
- Verify each app launches correctly after fix

**Non-Goals:**
- Root-cause analysis of why upgrades failed (likely disk pressure or SIGTERM during install)
- Fixing non-Homebrew corrupted apps (AutoForward Messages, Nicegram)
- Adding automated corruption detection or self-healing
- Upgrading to newer versions beyond what's already downloaded

## Decisions

### D1: Use `brew reinstall --cask --force` (not manual file copy)

**Choice:** Reinstall each cask via Homebrew rather than manually copying the `.app` from `.upgrading/` to `/Applications/`.

**Rationale:**
- `brew reinstall --cask --force` atomically removes the corrupted entry, downloads/extracts a fresh copy, and registers it properly in the Caskroom metadata
- Manual copy would leave stale Caskroom metadata (`.metadata/`, `INSTALL_RECEIPT.json`) that doesn't match what's in `/Applications/`, causing future `brew upgrade` to fail again
- The `.upgrading/` directories are automatically cleaned up by Homebrew after a successful install

**Alternative considered:** Copy `.app` from `.upgrading/` directly → rejected because it leaves metadata inconsistent and doesn't fix the root state.

### D2: Sequential execution (not parallel)

**Choice:** Reinstall casks one at a time rather than in parallel.

**Rationale:**
- Homebrew holds a lockfile during operations; parallel installs would serialize anyway
- Sequential allows verifying each app before moving to the next
- Easier to diagnose if one reinstall fails

### D3: Verify after each reinstall

**Choice:** After each `brew reinstall`, verify the app has a valid `Info.plist` and executable before proceeding.

**Rationale:**
- Confirms the fix actually worked
- Early exit if a systematic issue affects all casks (e.g., Homebrew itself is broken)

## Risks / Trade-offs

- **[Risk] App data/settings lost** → Mitigated: Homebrew casks install to `/Applications/` only; user data lives in `~/Library/Application Support/` which is untouched by reinstall
- **[Risk] Download fails for one cask** → Mitigated: Sequential execution allows retry; each cask is independent
- **[Risk] New version differs from what was expected** → Low risk: `brew reinstall` fetches the latest version in the current tap, which may be newer than the stranded `.upgrading/` version — this is desirable
