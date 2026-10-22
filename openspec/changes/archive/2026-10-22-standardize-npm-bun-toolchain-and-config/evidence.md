# Implementation & Verification Evidence: `standardize-npm-bun-toolchain-and-config`

**Date**: 2026-10-22  
**Change**: `standardize-npm-bun-toolchain-and-config`  
**Store**: `openspec-store` (`/Users/androidteam/Developer/platform/openspec-store`)

---

## 1. Central Store Manifests, Updater Registry, and Inventory (`platform/openspec-store`)

- **Task 1.1 (`config/workstation-toolchain-manifest.json`)**:
  - Added `"~/.bun"` to `sanctioned_roots` (`line 8`).
  - Added `"npm"`, `"pnpm"`, and `"bun"` to `profiles.core` (`lines 20–22`) and `tools.{npm,pnpm,bun}` (`lines 92–135`) with `authoritative_owner: "brew-formula"`, `update_authority: "brew"`, `writer_binary: "brew"`, and `known_shadow_paths`.
  - SHA-256: `2a8d55625a51f3406145192a78b4be9d6df65fb75d2c145e93d7fe4fac16835a`.
- **Task 1.2 (`config/npm-global-tools.json`)**:
  - Expanded from 5 to all 15 sanctioned `~/.npm-global` CLI packages (`openspec`, `gitnexus`, `kilo`, `auggie`, `happy`, `agentmemory`, `agentmemory-mcp`, `brightdata`, `anydoc`, `grepai`, `mcpr`, `deepwiki`, `codexuse`, `exa`, `node-gyp`), verified disjoint from `config/Brewfile` and `config/uv-tools.json`.
  - SHA-256: `aa69aae2a8d26a9742f80e49a14630ad3d878d8a23d6ab5f48c5487ceba0456a`.
- **Task 1.3 (`scripts/toolchain_updater_registry.py` & `scripts/inventory-workstation-toolchain.py`)**:
  - Registered `("npm", "brew-formula")`, `("pnpm", "brew-formula")`, and `("bun", "brew-formula")` in `SUPPORTED_UPDATER_REGISTRY` (`toolchain_updater_registry.py:265-293`).
  - Added `home / ".bun"` to `is_path_sanctioned()`, classified `/opt/homebrew/lib/node_modules/npm` (and `/usr/local/lib/node_modules/npm`) under `"brew-formula"` in `derive_install_root_and_source()`, updated shadow-path checks in `inventory-workstation-toolchain.py` to evaluate manifest `known_shadow_paths` via `sh_path.is_symlink() or sh_path.exists()`, and added regression tests for dangling symlink shadow detection and Homebrew `npm` provenance in `scripts/test-version-authority-governance.py` (`Ran 36 tests, OK`).
- **Task 1.4 (`scripts/workstation-daily-update.sh`, `config/launchd/com.agentmemory.server.plist.tmpl`, `scripts/seed-agentmemory-decisions.py`, `tests/test_portable_workstation_slice_b.py`, `docs/mac-development-setup.md`)**:
  - Synchronized `/Users/androidteam/Developer/platform/openspec-store/scripts/workstation-daily-update.sh` and `/Users/androidteam/Developer/scripts/workstation-daily-update.sh` byte-for-byte (SHA-256: `fcd31a5a333a336c682e9e23a4e024b8a0e5a9d662c63e46509ac1f14cf79961`).
  - Verified `python3 -m unittest tests/test_portable_workstation_slice_a.py tests/test_portable_workstation_slice_b.py tests/test_portable_workstation_slice_c.py` (`Ran 70 tests, OK`) and `python3 scripts/test-version-authority-governance.py` (`Ran 36 tests, OK`).

---

## 2. Scheduler Workflow Alignment (`shb/shb-schedule`)

- **Task 2.1 (`src/shb_schedule/workflows/workstation_update.py` & `tests/test_workstation_update_workflow.py`)**:
  - Removed `[bun_bin, "upgrade"]` from `step_bun_global_update()` (`lines 311–395`) so Homebrew (`brew upgrade bun`) remains the sole runtime updater.
  - Added empty-safe v2 `bun.lock` initialization (`{"lockfileVersion": 2, "configVersion": 1, "workspaces": {"": {}}, "packages": {}}`) when `dependencies` is `{}` and single-pass `bun update -g --save-text-lockfile` when `dependencies` is non-empty, enforcing `os.chmod(bun_lock, 0o600)` after both branches.
  - Verified `uv run --project /Users/androidteam/Developer/shb/shb-schedule pytest /Users/androidteam/Developer/shb/shb-schedule/tests/test_workstation_update_workflow.py -p no:cacheprovider` (`39 passed`) and `ruff check` (`All checks passed!`).

---

## 3. Host Configuration & Hygiene (`/Users/androidteam`, Value-Blind)

- **Task 3.1 (`~/.npmrc` & `~/.bunfig.toml`)**:
  - `/Users/androidteam/.npmrc`: mode `0600`, SHA-256 `5667c80029bd08d7bab9a981cc4ef04c413196d47a3cb088aeb462f817d4d12a`, 13 native keys (`prefix`, `dangerously-allow-all-scripts`, `allow-remote`, `allow-git`, `allow-file`, `allow-directory`, `ignore-scripts`, `foreground-scripts`, `maxsockets`, `prefer-dedupe`, `fund`, `audit`, `update-notifier`), `0` bytes `stderr` on `/opt/homebrew/bin/npm config list`.
  - `/Users/androidteam/.bunfig.toml`: mode `0600`, SHA-256 `fe85c047b52ded89d636b673692e34ae9c93688a64e86c6da8e0e446bec64021`, `[install]`, `[install.cache]`, and `[run]` configured.
- **Task 3.2 (`~/.bun/bin/omp` & `~/.bun/install/global/bun.lock`)**:
  - Removed dangling `/Users/androidteam/.bun/bin/omp` symlink (`test ! -L ~/.bun/bin/omp && test ! -e ~/.bun/bin/omp` -> exit `0`).
  - Initialized `/Users/androidteam/.bun/install/global/bun.lock` (`mode 0600`, SHA-256 `6e78621cbddc1686d8c4817fad51b7f41d1b6323566ab5b047e04445cdb5ed49`); `/opt/homebrew/bin/bun pm ls -g` exits `0`.
- **Task 3.3 (`~/.zshrc`, `nvm`, & `~/Library/pnpm`)**:
  - Removed `_load_nvm` wrapper from `/Users/androidteam/.zshrc` (mode `0600`, SHA-256 `35bf2a48...`), uninstalled Homebrew `nvm@0.40.8`, moved `PNPM_HOME` / `PNPM_HOME/bin` after `/opt/homebrew/bin`, and removed stale iCloud shims (`~/Library/pnpm/context-please-mcp` and `~/Library/pnpm/global/5`).

---

## 4. End-to-End Verification

- **Task 4.1 (`zsh -ilc` & `zsh -ic` Resolution)**:
  - `zsh -ilc 'which -a node npm npx bun bunx pnpm pnpx omp'` resolves `/opt/homebrew/bin/{node,npm,npx,bun,bunx,pnpm,pnpx,omp}` first with zero shell wrapper functions.
  - `PATH="$HOME/.orbstack/bin:$PATH" zsh -ic 'print -l $path'` strips `~/.orbstack/bin`, deduplicates all entries, and places `/opt/homebrew/bin` ahead of `~/.bun/bin`, `~/Library/pnpm/bin`, `~/Library/pnpm`, and `~/.npm-global/bin`.
- **Task 4.2 (Toolchain Inventory & OpenSpec Validation)**:
  - `inventory-workstation-toolchain.py --json`: `prefix_reconciliation.status == "reconciled"`, `authority_reconciliation.conflict_count == 0`, `authority_reconciliation.unknown_count == 0`, `manifest_reconciliation.status == "aligned"`, `declared_tools_count == 40`, `drift_count == 0`, `missing_count == 0`, `unsanctioned_count == 0`, `unknown_count == 0`.
  - `openspec validate standardize-npm-bun-toolchain-and-config --strict --json --store openspec-store`: `"valid": true, "issues": []`.
