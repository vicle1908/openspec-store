# Verification Evidence: `standardize-orca-and-workstation-package-consistency`

Date: `2026-10-17`
Store: `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`)

---

## 1. Phase 1 — Orca IDE Standardization and Process Lifecycle Remediation (`1.1`–`1.4`)

- **Bundle & CLI Authority**: `/Applications/Orca.app` and `/opt/homebrew/bin/orca` installed via `stablyai/orca/orca` Cask at `v1.4.229`.
- **Version Verification (`orca --version`)**:
  - Output: `1.4.229` (exit code `0`).
- **Live Runtime Health (`orca status`)**:
  ```text
  appRunning: true
  pid: 35007
  desktopWindowStatus: available
  runtimeState: ready
  runtimeReachable: true
  runtimeConnectionState: connected
  runtimeId: 61aa1a91-9a5f-463d-8f4e-a058c09b9315
  graphState: ready
  ```

---

## 2. Phase 2 — Multi-Package Manager Upgrades & Active Session Protection (`2.1`–`2.5`)

- **`uv tool` Environments (`2.1`)**: `graphifyy` (`0.9.92`) and `infinity-emb` (`0.0.78`) verified up to date via `uv tool upgrade --all` (exit code `0`).
- **Global npm Tools (`2.2`)**: `codexuse-cli` upgraded to `7.2.3` in `~/.npm-global` (exit code `0`).
- **Homebrew Casks (`2.3`)**: `gcloud-cli`, `postman-cli`, and `lark` upgraded via `brew upgrade --cask` (exit code `0`).
- **Standalone Agent CLIs (`2.4`)**: `claude` (`2.1.302`), `pi` (`0.94.2`), `bun` (`1.4.3`), and 8 remote skills verified current without session disruption.
- **Active Session Protection (`2.5`)**: In-use desktop applications (`cloudflare-warp`, `zed`, `onedrive`, `Telegram`) held back from forced process termination per `workstation-toolchain-maintenance`.

---

## 3. Phase 3 — Declarative Manifest Governance in `platform/openspec-store` (`3.1`–`3.5`)

- **`config/Brewfile` (`3.1`, `3.3`)**:
  - Declared `cask "orca"` under official developer applications.
  - Verification: `HOMEBREW_NO_AUTO_UPDATE=1 brew bundle check --file /Users/androidteam/Developer/platform/openspec-store/config/Brewfile --no-upgrade` → `The Brewfile's dependencies are satisfied.` (exit code `0`).
- **`config/workstation-toolchain-manifest.json` & Governance Unit Tests (`3.2`, `3.4`)**:
  - Registered `tools.orca` under `profiles.ai-agents` (`authoritative_owner: "brew-cask"`, `update_authority: "brew"`, `verify_command: ["orca", "--version"]`).
  - Verification: `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/test-version-authority-governance.py` → `Ran 26 tests in 2.663s OK` (exit code `0`).
- **Portable Workstation Slice Tests (`3.5`)**:
  - Verification: `pytest /Users/androidteam/Developer/platform/openspec-store/tests/test_portable_workstation_slice_*.py -q` → `68 passed, 2 skipped` (exit code `0`).

---

## 4. Phase 4 & 5 — System Consistency Audit & OpenSpec Validation (`4.1`–`4.4`, `5.1`–`5.2`)

- **Non-Standard Installation Audit (`4.1`–`4.4`)**:
  - Recorded Caskroom metadata observations for `antigravity-cli` and `cleanmymac`, orphaned/deprecated formulae (`qi`, `python@3.10`), shadowed duplicate `newman` removal from `~/.local/share/home-toolchain`, and subshell PATH precedence normalization.
- **Strict OpenSpec Validation (`5.1`–`5.2`)**:
  - `openspec validate standardize-orca-and-workstation-package-consistency --strict --store openspec-store` → `Change 'standardize-orca-and-workstation-package-consistency' is valid` (exit code `0`).
