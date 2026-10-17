# Proposal: Standardize Orca and Workstation Package Consistency

## Why

An operational and toolchain health audit revealed multiple anomalies across host development applications and package managers:
1. **Orca IDE Stale Process & Runtime Drift**: Stably AI Orca IDE (`com.stablyai.orca`, `onorca.dev`) was running a zombie process (PID 485, v1.4.225 launched over 2 days prior) in a detached CoreGraphics session (`!cgsConnection`, 0 open windows) with its internal runtime stuck in `runtimeState: starting` and disconnected. Orca was installed via official tap `stablyai/orca/orca` but was omitted from the declarative `config/Brewfile` and `config/workstation-toolchain-manifest.json`.
2. **Workstation Package Freshness & Upstream Alignment**: Host package managers (`uv tool`, `npm -g`, Homebrew casks/formulae, and coding agent CLIs) held outdated dependencies that missed upstream bug fixes and security improvements.
3. **Non-Standard Installation & Metadata Anomalies**: `brew doctor` and toolchain inventory checks revealed non-standard installation states, including corrupt Caskroom metadata (`antigravity-cli`, `cleanmymac`), orphaned/deprecated formulae (`qi`, `python@3.10`), and duplicate shadowed binaries (`newman` in `~/.local/share/home-toolchain`).

Standardizing Orca's lifecycle, bringing host packages up to date, declaring authoritative ownership in central manifests, and auditing system consistency restores deterministic single-owner toolchain governance across the workstation.

## What Changes

- **Orca IDE Standardization & Lifecycle Restoration (`portable-workstation-toolchain`, `workstation-toolchain-inventory`)**:
  - Terminate hung detached Orca processes (PID 485 and child helpers).
  - Cleanly reinstall and upgrade `/Applications/Orca.app` and `/opt/homebrew/bin/orca` to latest official stable version **1.4.229** via `brew reinstall --cask stablyai/orca/orca`.
  - Validate healthy application and runtime startup (`orca status` reporting `ready`, `runtimeReachable: true`, `runtimeConnectionState: connected`, and 1 active window).
  - Declare `cask "orca"` in `config/Brewfile` and register `tools.orca` under `profiles.ai-agents` in `config/workstation-toolchain-manifest.json` with `brew-cask` authority.

- **System-Wide Package Upgrades & Freshness**:
  - Upgrade Python `uv tool` environments: `graphifyy` and `infinity-emb`.
  - Upgrade global npm packages: `codexuse-cli` (`7.2.2` -> `7.2.3`).
  - Upgrade Homebrew Casks: `gcloud-cli` (`588.0.0` -> `589.0.0`), `postman-cli` (`1.73.0` -> `1.75.0`), and `lark` (`8.1.22` -> `8.2.16`).
  - Verify up-to-date state for standalone coding agent CLIs: Claude Code (`2.1.302`), Pi (`v1.3.0`), Bun (`v1.4.3`), and remote skills.
  - Preserve active user sessions and running applications (`cloudflare-warp`, `zed`, `onedrive`, `Telegram`) during maintenance.

- **System Consistency & Standard Audit**:
  - Audit and document non-standard installation findings:
    - Broken Caskroom metadata for `antigravity-cli` and `cleanmymac`.
    - Orphaned formula `qi` (removed upstream).
    - Deprecated formula `python@3.10`.
    - Duplicate shadowed `newman` in `~/.local/share/home-toolchain`.
    - Subshell non-login PATH precedence where `/usr/bin` precedes `/opt/homebrew/bin`.

## Capabilities

### Modified Capabilities
- `portable-workstation-toolchain`: Add `cask "orca"` to `config/Brewfile` and mandate health verification (`orca status`) after Orca installation or upgrade.
- `workstation-toolchain-inventory`: Register `orca` as a first-class AI agent tool in `config/workstation-toolchain-manifest.json` with `brew-cask` authoritative ownership and verification command `orca --version`.

## Impact

- **Planning & Governance**: `~/Developer/platform/openspec-store` (`config/Brewfile`, `config/workstation-toolchain-manifest.json`).
- **Host Runtime**: `/Applications/Orca.app`, `/opt/homebrew/bin/orca`, global package managers (`uv tool`, `npm -g`, `brew`).
- **Reliability**: Eliminates zombie Electron processes, ensures reproducible Homebrew bundle verification, and surfaces non-standard package metadata for operator remediation.
