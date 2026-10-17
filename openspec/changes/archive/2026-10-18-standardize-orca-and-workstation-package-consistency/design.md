# Design: Standardize Orca and Workstation Package Consistency

## Context & Architecture Overview

The workstation environment hosts a variety of developer tools, language runtimes, and autonomous coding agents. Orca IDE (`com.stablyai.orca`, distributed by Stably AI via `onorca.dev`) serves as the orchestrator for running multiple AI coding agents side-by-side in git worktrees with coordinated terminal sessions.

Workstation governance is anchored in `platform/openspec-store`:
- `config/Brewfile`: Authoritative list of Homebrew formulae, casks, and taps.
- `config/workstation-toolchain-manifest.json`: Single-source-of-truth metadata mapping tools to their authoritative package managers, path patterns, update verbs, and verification commands.
- `scripts/inventory-workstation-toolchain.py` and `scripts/test-version-authority-governance.py`: Automated drift detection and unit verification of toolchain ownership.

## Key Technical Decisions & Tradeoffs

### 1. Orca Process Lifecycle & Upgrade Strategy
- **Problem**: Orca had been running for over 2 days (PID 485, v1.4.225) in a detached state with a dead CoreGraphics connection, 0 open windows, and a disconnected internal runtime (`runtimeState: starting`, `runtimeReachable: false`).
- **Decision**: Terminate stale processes and helpers cleanly using SIGTERM followed by SIGKILL before executing any package mutation. Never overwrite an active Electron bundle while background helpers (`Orca Helper`, `Orca Helper (Renderer)`, `chrome_crashpad_handler`) are running.
- **Package Channel**: Adopt the official Homebrew tap `stablyai/homebrew-orca` (`cask "orca"`). The cask manages both `/Applications/Orca.app` and symlinks `/Applications/Orca.app/Contents/Resources/bin/orca` to `/opt/homebrew/bin/orca`.
- **Runtime Verification**: Verify post-upgrade health using `orca status` to assert `runtimeState: ready`, `graphState: ready`, `runtimeReachable: true`, `runtimeConnectionState: connected`, and active window availability.

### 2. Central Manifest Synchronization
- Declare `cask "orca"` in `config/Brewfile` under the developer applications section.
- Add `orca` to `profiles.ai-agents` in `config/workstation-toolchain-manifest.json` with:
  - `authoritative_owner`: `"brew-cask"`
  - `active_path_pattern`: `"{{HOMEBREW_PREFIX}}/bin/orca"`
  - `update_authority`: `"brew"`
  - `supported_verb`: `"brew upgrade --cask stablyai/orca/orca"`
  - `verification_smoke_command`: `"orca --version"`

### 3. Multi-Ecosystem Package Upgrades & Active Session Protection
- In accordance with `workstation-toolchain-maintenance`:
  - Python CLI tools managed via `uv tool` (`graphifyy`, `infinity-emb`) are upgraded via `uv tool upgrade --all`.
  - Global Node tools (`codexuse-cli`) are upgraded via `npm install -g --prefix ~/.npm-global`.
  - Non-running Homebrew casks (`gcloud-cli`, `postman-cli`, `lark`) are upgraded via `brew upgrade --cask`.
  - Actively running GUI apps (`Cloudflare WARP`, `Zed`, `OneDrive`, and `Telegram`) are protected from in-flight termination and left untouched.

### 4. Non-Standard Installation Audit Taxonomy
System consistency checks surface four classes of non-standard installation states:
1. **Caskroom Metadata Loss**: `/opt/homebrew/Caskroom/antigravity-cli` and `cleanmymac` missing receipts, preventing automated upgrades. Remediated via operator-guided `--force` reinstall.
2. **Orphaned / Deprecated Formulae**: Formula `qi` (removed upstream) and `python@3.10` (deprecated in Cellar).
3. **Shadowed Duplicate Binaries**: Duplicate `newman` installation inside `~/.local/share/home-toolchain/node_modules/` alongside authoritative `/opt/homebrew/bin/newman`.
4. **Subshell PATH Inversion**: Non-login subshells where `/usr/bin` precedes `/opt/homebrew/bin`, contrasted with login interactive shells that enforce Homebrew-first precedence.

## Verification & Validation Plan

1. **Orca App Health**: Run `orca status` to confirm operational readiness and inspect process table.
2. **Homebrew Manifest Consistency**: Run `HOMEBREW_NO_AUTO_UPDATE=1 brew bundle check --file config/Brewfile --no-upgrade`.
3. **Governance Test Suite**: Execute `python3 scripts/test-version-authority-governance.py` and `uv run pytest tests/test_portable_workstation_slice_{a,b,c}.py`.
4. **OpenSpec Spec Validation**: Run `openspec validate standardize-orca-and-workstation-package-consistency --strict --store openspec-store`.
