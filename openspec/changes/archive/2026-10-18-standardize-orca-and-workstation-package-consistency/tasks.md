# Tasks

## 1. Orca IDE Standardization and Process Lifecycle Remediation

- [x] 1.1 Inspect host process table and discover Orca bundle identity (`com.stablyai.orca` / `stablyai/homebrew-orca` tap) and stalled PID 485 with disconnected runtime (`runtimeState: starting`).
- [x] 1.2 Terminate stale detached Orca processes and Electron helpers via SIGTERM/SIGKILL.
- [x] 1.3 Reinstall and upgrade `/Applications/Orca.app` and `/opt/homebrew/bin/orca` to latest official stable release v1.4.229 using `brew reinstall --cask stablyai/orca/orca`.
- [x] 1.4 Launch Orca via `open -a /Applications/Orca.app` and verify normal operational health via `orca status` (`appRunning: true`, `runtimeState: ready`, `graphState: ready`, `runtimeReachable: true`, `runtimeConnectionState: connected`, 1 active window).

## 2. Multi-Package Manager Upgrades & Active Session Protection

- [x] 2.1 Upgrade Python `uv tool` environments (`graphifyy`, `infinity-emb`) via `uv tool upgrade --all`.
- [x] 2.2 Upgrade global npm tools (`codexuse-cli` to latest 7.2.3) via `npm install -g --prefix ~/.npm-global -- codexuse-cli@latest`.
- [x] 2.3 Upgrade eligible Homebrew Casks (`gcloud-cli`, `postman-cli`, `lark`) via `brew upgrade --cask`.
- [x] 2.4 Verify standalone coding agent CLIs (`claude`, `pi`, `bun`, and 8 remote skills) are up to date without disruption.
- [x] 2.5 Protect active user applications (`cloudflare-warp`, `zed`, `onedrive`, `Telegram`) by holding back in-flight process termination per `workstation-toolchain-maintenance`.

## 3. Declarative Manifest Governance in `platform/openspec-store`

- [x] 3.1 Update `config/Brewfile` to declare `cask "orca"` under official developer applications.
- [x] 3.2 Update `config/workstation-toolchain-manifest.json` to register `tools.orca` under `profiles.ai-agents` with `brew-cask` authoritative ownership and `orca --version` verification.
- [x] 3.3 Verify declarative bundle compliance using `HOMEBREW_NO_AUTO_UPDATE=1 brew bundle check --file config/Brewfile --no-upgrade`.
- [x] 3.4 Verify toolchain governance unit suite using `python3 scripts/test-version-authority-governance.py` (26 passed).
- [x] 3.5 Verify portable workstation test suite using `uv run pytest tests/test_portable_workstation_slice_a.py tests/test_portable_workstation_slice_b.py tests/test_portable_workstation_slice_c.py` (68 passed).

## 4. System Consistency & Non-Standard Installation Audit

- [x] 4.1 Audit and document Caskroom metadata defects for `/opt/homebrew/Caskroom/antigravity-cli` and `cleanmymac`.
- [x] 4.2 Audit and document orphaned and deprecated formulae (`qi`, `python@3.10`).
- [x] 4.3 Audit and document shadowed duplicate binaries (`newman` in `~/.local/share/home-toolchain/node_modules/` vs authoritative Homebrew binary).
- [x] 4.4 Audit subshell non-login PATH precedence where `/usr/bin` precedes `/opt/homebrew/bin`.

## 5. OpenSpec Specification & Validation

- [x] 5.1 Author delta specifications under `specs/portable-workstation-toolchain/spec.md` and `specs/workstation-toolchain-inventory/spec.md`.
- [x] 5.2 Validate change artifacts strictly using `openspec validate standardize-orca-and-workstation-package-consistency --strict --store openspec-store`.
