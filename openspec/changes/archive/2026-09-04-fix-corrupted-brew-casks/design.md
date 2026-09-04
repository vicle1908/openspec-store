## Context

Eight applications in `/Applications/` have corrupted installations across three categories:

1. **Homebrew casks** (5 already fixed): VS Code, Ollama, Google Chrome, Postman, Warp — reinstalled via `brew reinstall --cask --force`. Their `.upgrading/` directories are cleaned up.

2. **Stably AI Orca** (`com.stablyai.orca`, v1.4.197): An Electron-based AI assistant from Stably AI, distributed via GitHub releases (`stablyai/orca`). The Homebrew cask `orca` is for Plotly Orca (a completely different app, v1.3.1, disabled 2026-09-01). The complete Orca bundle exists in `/opt/homebrew/Caskroom/orca/1.4.196.upgrading/Orca.app/` but cannot be restored via Homebrew because the cask doesn't match.

3. **Sideloaded iOS apps** (2 apps):
   - AutoForward Messages (`com.autoforward.teleforwarder`, v1.0.55) — Flutter-based iOS app sideloaded on macOS. Bundle at `/Applications/AutoForward Messages.app/` has `Wrapper/Runner.app/Info.plist` but the `Runner` executable is missing.
   - Nicegram (`app.nicegram`, v2.5.9) — Telegram client fork, also sideloaded iOS app. Bundle at `/Applications/Nicegram.app/` has `Wrapper/Telegram.app/Info.plist` but the `Telegram` executable is missing.

## Goals / Non-Goals

**Goals:**
- Restore Stably AI Orca to working state
- Provide clear reinstall guidance for the two sideloaded iOS apps
- Clean up all stale `.upgrading/` directories from the Caskroom

**Non-Goals:**
- Root-cause analysis of why upgrades failed
- Adding automated corruption detection or self-healing
- Automating sideloaded app reinstallation (requires user action)

## Decisions

### D1: Use `brew reinstall --cask --force` for Homebrew casks (completed)

**Choice:** Reinstall each cask via Homebrew rather than manually copying the `.app` from `.upgrading/` to `/Applications/`.

**Rationale:** `brew reinstall --cask --force` atomically removes the corrupted entry, downloads/extracts a fresh copy, and registers it properly in the Caskroom metadata. Manual copy would leave stale metadata causing future `brew upgrade` to fail again.

**Status:** ✓ Completed for VS Code, Ollama, Google Chrome, Postman, Warp.

### D2: Sequential execution (completed)

**Choice:** Reinstall casks one at a time. Homebrew holds a lockfile; parallel would serialize anyway. Sequential allows verifying each app.

### D3: Verify after each reinstall (completed)

**Choice:** After each reinstall, verify `Info.plist` exists and executable is present.

### D4: Install Orca via official Homebrew tap

**Choice:** `brew install --cask stablyai/orca/orca` — the official method from [github.com/stablyai/orca](https://github.com/stablyai/orca).

**Rationale:**
- The default Homebrew `orca` cask is for Plotly Orca (different app, disabled by Gatekeeper)
- Stably AI Orca has its own tap: `stablyai/orca/orca`
- Official install ensures correct version, proper Caskroom metadata, and future `brew upgrade` support
- Must first remove the corrupted empty shell and stale Caskroom entry to avoid conflicts

**Alternative considered:** Copy from `.upgrading/` directory → rejected because it leaves stale Caskroom metadata and doesn't register with the correct tap.

### D5: Document manual reinstall for sideloaded iOS apps

**Choice:** Provide clear instructions for AutoForward Messages and Nicegram rather than attempting automated fixes.

**Rationale:**
- These are sideloaded iOS apps (Flutter/Catalyst pattern with `Wrapper/Runner.app/` structure)
- No package manager tracks them — they were installed via AltStore, Sideloadly, or similar tools
- The executables are missing but the bundle structure and Info.plist are intact — likely a partial filesystem corruption
- Re-sideloading requires the original IPA file and signing credentials, which only the user has
- Providing instructions is more helpful than pretending automation is possible

**Alternative considered:** Delete corrupted bundles and let user rediscover them → rejected; poor UX. Attempting to extract executables from IPA → rejected; too complex and fragile.

## Risks / Trade-offs

- **[Risk] Orca copy fails (permissions/disk)** → Mitigated: `/Applications/` is user-writable; bundle is ~200MB, disk space verified
- **[Risk] Copied Orca fails Gatekeeper** → Mitigated: Bundle is already signed (`_CodeSignature/CodeResources` present); macOS should trust it
- **[Risk] Sideloaded apps lose data on reinstall** → Mitigated: App data lives in `~/Library/Containers/`, not in `/Applications/`; reinstall only replaces the bundle
- **[Risk] User doesn't have IPA files for sideloaded apps** → Mitigated: Instructions include where to re-download (App Store for Nicegram, developer site for AutoForward Messages)
