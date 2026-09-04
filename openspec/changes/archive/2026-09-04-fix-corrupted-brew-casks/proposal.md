## Why

Eight applications in `/Applications/` have corrupted installations — their `.app` bundles are empty shells or missing executables. The corruption affects three distinct categories:

1. **Homebrew casks** (5 apps): `brew upgrade --cask` failed mid-upgrade, leaving empty shells in `/Applications/` while the actual bundles were stranded in `.upgrading/` directories. Already fixed: VS Code, Ollama, Google Chrome, Postman, Warp.
2. **Stably AI Orca** (1 app): Same `.upgrading/` failure, but the Homebrew `orca` cask is for Plotly Orca (a different app). The user's Orca is `com.stablyai.orca` (v1.4.197), installed from Stably AI's GitHub releases.
3. **Sideloaded iOS apps** (2 apps): AutoForward Messages (`com.autoforward.teleforwarder` v1.0.55) and Nicegram (`app.nicegram` v2.5.9) are iOS apps sideloaded on macOS. Their bundle structures use `Wrapper/Runner.app/` (Flutter/Catalyst pattern) and the main executables are missing.

## What Changes

- Install Stably AI Orca via the official Homebrew tap: `brew install --cask stablyai/orca/orca`
- Document manual reinstall steps for AutoForward Messages and Nicegram (sideloaded iOS apps, not managed by any package manager)
- Clean up stale `.upgrading/` directories from the Caskroom
- No code changes — this is a tooling/infrastructure fix

**Non-goals:**
- Investigating why the upgrades failed (likely disk pressure or interrupted process)
- Adding automated corruption detection or self-healing
- Changing Homebrew upgrade behavior

## Capabilities

### New Capabilities

_(none — `skip_specs: true`, pure tooling fix)_

### Modified Capabilities

_(none)_

## Impact

- **Affected apps**: Orca (Stably AI), AutoForward Messages, Nicegram (plus 5 already fixed: VS Code, Ollama, Chrome, Postman, Warp)
- **Affected systems**: Homebrew Caskroom at `/opt/homebrew/Caskroom/`, `/Applications/`
- **Risk**: Low — Orca restore is a file copy from an existing bundle; sideloaded apps require manual action
- **Downtime**: Apps must be closed during restore (~30s each)
