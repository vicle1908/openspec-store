## Why

Six Homebrew casks have corrupted installations — their `.app` bundles in `/Applications/` are empty shells (missing `Info.plist`, no executable). This happened because `brew upgrade --cask` failed mid-upgrade: the old version was moved to a `<version>.upgrading/` directory, but the new version's install to `/Applications/` never completed. The affected apps (Orca, VS Code, Ollama, Google Chrome, Postman, Warp) cannot launch.

## What Changes

- Reinstall 6 corrupted Homebrew casks with `brew reinstall --cask --force` to restore working app bundles
- Clean up stale `.upgrading/` directories left behind by failed upgrades
- No code changes — this is a tooling/infrastructure fix

**Non-goals:**
- Investigating why the upgrades failed (likely disk pressure or interrupted process)
- Fixing the 2 non-Homebrew corrupted apps (AutoForward Messages, Nicegram) — those need manual attention
- Changing Homebrew upgrade behavior or adding automation

## Capabilities

### New Capabilities

_(none — `skip_specs: true`, pure tooling fix)_

### Modified Capabilities

_(none)_

## Impact

- **Affected apps**: Orca, Visual Studio Code, Ollama, Google Chrome, Postman, Warp
- **Affected system**: Homebrew Caskroom at `/opt/homebrew/Caskroom/`
- **Risk**: Low — reinstalling casks is idempotent; worst case is re-downloading the same version
- **Downtime**: Apps must be closed during reinstall (~30s each, mostly download time)
