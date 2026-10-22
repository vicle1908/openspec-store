# Proposal

## Why

The macOS development workstation's `npm`, `bun`, `pnpm`, and `node` runtime/package-manager layer exhibits configuration, PATH precedence, single-owner update authority, and manifest-reconciliation drift across `~/.npmrc`, `~/.bunfig.toml`, `~/.zshrc`, `platform/openspec-store`, and `shb-schedule`. Standardizing these configurations and governance manifests now eliminates competing `bun` updaters, dead `nvm` shell wrapper overhead, `PNPM_HOME` binary shadowing, broken `~/.bun` global lockfiles/symlinks, and manifest omissions while maximizing script and remote package execution throughput across `npm` and `bun`.

## What Changes

- **Maximized Permissive & High-Throughput `npm` and `bun` Configuration (`~/.npmrc` & `~/.bunfig.toml`)**:
  - Preserve and standardize full script and remote/git/file/directory permissiveness in `~/.npmrc` (`mode 0600`) using the 13 verified native `npm@11.20.0` configuration keys (`0` unknown-config warnings on `stderr`): `prefix=/Users/androidteam/.npm-global`, `dangerously-allow-all-scripts=true`, `allow-remote=all`, `allow-git=all`, `allow-file=all`, `allow-directory=all`, `ignore-scripts=false`, `foreground-scripts=false`, `maxsockets=64`, `prefer-dedupe=true`, `fund=false`, `audit=false`, and `update-notifier=false`.
  - Author `~/.bunfig.toml` (`mode 0600`) for `bun@1.4.3+` to maximize script concurrency, network concurrency, and frictionless execution (`[install]` `auto = "auto"`, `saveTextLockfile = true`, `concurrentScripts = 32`, `networkConcurrency = 64`, `linker = "hoisted"`, `globalDir = "/Users/androidteam/.bun/install/global"`, `globalBinDir = "/Users/androidteam/.bun/bin"`, `exact = false`, `production = false`, `optional = true`, `dev = true`, `peer = true`, `[install.cache]` enabled, and `[run]` `shell = "bun"`).
- **Single-Owner `bun` Authority & Initialized Global Lockfile (`~/.bun/install/global`)**:
  - Enforce Homebrew (`brew "bun"`, `brew upgrade bun`) as the sole binary updater for `/opt/homebrew/bin/bun`; remove competing standalone `bun upgrade` invocations from `scripts/workstation-daily-update.sh`, `~/Developer/scripts/workstation-daily-update.sh`, `shb-schedule`'s `step_bun_global_update()`, and `portable-workstation-toolchain` spec requirements.
  - Account for `bun@1.4.3`'s empty-manifest lockfile deletion behavior (`No packages! Deleted empty lockfile`): when `~/.bun/install/global/package.json` has empty `dependencies` (`{}`), write the minimal v2 text lockfile (`{"lockfileVersion": 2, "configVersion": 1, "workspaces": {"": {}}, "packages": {}}`) to `~/.bun/install/global/bun.lock` if absent and skip `bun install` / `bun update -g`; when `dependencies` is non-empty, execute single-pass `bun update -g --save-text-lockfile`, and enforce mode `0600` on `bun.lock` across both branches so `bun pm ls -g` always exits `0` with private lockfile permissions.
- **Dangling Symlink Remediation & Symlink-Aware Shadow Auditing (`~/.bun/bin/omp` & `inventory-workstation-toolchain.py`)**:
  - Remove the dangling `/Users/androidteam/.bun/bin/omp` symlink (`-> ../../node_modules/@oh-my-pi/pi-coding-agent/dist/cli.js`).
  - Update `scripts/inventory-workstation-toolchain.py` (`inventory_tools` and `reconcile_with_manifest`) to evaluate manifest `known_shadow_paths` across all tools using `sh_path.is_symlink() or sh_path.exists()` (`os.path.lexists`) and cover both dangling symlinks and `/opt/homebrew/lib/node_modules/npm` provenance in `scripts/test-version-authority-governance.py`.
- **Zsh Startup & `PATH` Precedence Normalization (`~/.zshrc`, `workstation-daily-update.sh`, & `test_portable_workstation_slice_b.py`)**:
  - Remove the unused `_load_nvm` lazy-loader wrapper (`nvm()`, `node()`, `npm()`, `npx()`) from `~/.zshrc` and uninstall the undeclared Homebrew `nvm` formula (`0` NVM Node versions exist) so `/opt/homebrew/bin/{node,npm,npx}` resolve directly without wrapper overhead.
  - Change `PNPM_HOME` registration in `~/.zshrc` from `_path_prepend` to `_path_append` so `/opt/homebrew/bin/{pnpm,pnpx}` are never shadowed by `~/Library/pnpm/bin/pnpx`, and remove the stale iCloud global shim (`~/Library/pnpm/context-please-mcp` and `~/Library/pnpm/global/5`).
  - Reorder `PATH` in `scripts/workstation-daily-update.sh` (and synchronize its executed mirror `~/Developer/scripts/workstation-daily-update.sh` in lockstep) and `config/launchd/com.agentmemory.server.plist.tmpl` so `/opt/homebrew/bin` (`{{HOMEBREW_PREFIX}}/bin`) precedes `~/.npm-global/bin` and `~/.bun/bin` while keeping `~/.local/bin` ahead of `/opt/homebrew/bin`, update `CANONICAL_DECISIONS["shell-path-precedence"]` in `scripts/seed-agentmemory-decisions.py`, and update `TestReconciledToolchainUpdaterAndDailyRunner.test_daily_update_script_path_precedence_order` in `tests/test_portable_workstation_slice_b.py` to enforce `/opt/homebrew/bin` ahead of `~/.npm-global/bin`.
- **Toolchain Manifest & Global NPM Profile Alignment (`config/workstation-toolchain-manifest.json`, `config/npm-global-tools.json`, & `inventory-workstation-toolchain.py`)**:
  - Register `bun`, `pnpm`, and `npm` in `config/workstation-toolchain-manifest.json` (`profiles.core` and `tools.{bun,pnpm,npm}`), add `~/.bun` to `sanctioned_roots` in `config/workstation-toolchain-manifest.json` and `is_path_sanctioned()` in `scripts/inventory-workstation-toolchain.py`, register `("bun", "brew-formula")`, `("pnpm", "brew-formula")`, and `("npm", "brew-formula")` in `scripts/toolchain_updater_registry.py`, and update `derive_install_root_and_source()` in `scripts/inventory-workstation-toolchain.py` to classify Homebrew's bundled `/opt/homebrew/lib/node_modules/npm` (and `/usr/local/lib/node_modules/npm`) under `brew-formula`.
  - Expand `config/npm-global-tools.json` from 5 tools to the full 15-package sanctioned `~/.npm-global` CLI roster (adding `agentmemory`, `agentmemory-mcp`, `brightdata`, `anydoc`, `grepai`, `mcpr`, `deepwiki`, `codexuse`, `exa`, `node-gyp`) while preserving disjoint ownership against `Brewfile` and `uv-tools.json`.

## Non-Goals

- Restricting or blocking lifecycle scripts (`ignore-scripts=true`), remote tarballs, git dependencies, or adding `min-release-age` / `minimumReleaseAge` quarantine windows (the operator explicitly mandates keeping all scripts and remote/git/file/directory sources allowed and maximized).
- Switching `node`, `bun`, or `pnpm` ownership away from Homebrew (`homebrew/core`) to `nvm`, `fnm`, `volta`, or `corepack`.
- Deleting `~/.local/share/home-toolchain/node_modules/newman` (which is a required peer dependency of `newman-reporter-htmlextra@^1.23.1` per `npm-audit-remediation` spec) or migrating `/opt/homebrew/lib/prime-agent` (`local-dev` uncovered bundle).
- Modifying secret values (`NPMJS_TOKEN`) in `~/.zshenv` or performing automated host mutations during the OpenSpec planning phase.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `portable-workstation-toolchain`: Update Bun global maintenance requirements to forbid `bun upgrade` on Homebrew-managed `bun` while maintaining a valid v2 `~/.bun/install/global/bun.lock` across empty and non-empty manifests, codify maximized permissive `~/.npmrc` and `~/.bunfig.toml` runtime configurations, enforce `/opt/homebrew/bin` precedence ahead of `~/.npm-global/bin`, `~/.bun/bin`, and `PNPM_HOME` across both interactive Zsh and `workstation-daily-update.sh`, and remove the unused `nvm` wrapper.
- `workstation-toolchain-inventory`: Register `bun`, `pnpm`, and `npm` in `config/workstation-toolchain-manifest.json` and `scripts/toolchain_updater_registry.py`, classify Homebrew's bundled `/opt/homebrew/lib/node_modules/npm` as `brew-formula` in `derive_install_root_and_source()`, include `~/.bun` in `sanctioned_roots`, expand `config/npm-global-tools.json` to match the 15-package sanctioned `~/.npm-global` CLI inventory, and require `os.path.lexists` (`is_symlink() or exists()`) when scanning `known_shadow_paths`.
- `omp-installation-management`: Require symlink-aware absence verification (`test ! -L ~/.bun/bin/omp && test ! -e ~/.bun/bin/omp`) so dangling `~/.bun/bin/omp` symlinks are detected and removed, and ensure `bun pm ls -g` exits `0` against an initialized v2 global lockfile.

## Impact

- **Ownership Boundaries**:
  - **Central OpenSpec Store (`/Users/androidteam/Developer/platform/openspec-store`)**: Owns `config/workstation-toolchain-manifest.json`, `config/npm-global-tools.json`, `scripts/inventory-workstation-toolchain.py`, `scripts/toolchain_updater_registry.py`, `scripts/workstation-daily-update.sh`, `docs/mac-development-setup.md`, and governance unit tests (`tests/test_portable_workstation_slice_a.py`, `tests/test_portable_workstation_slice_b.py`, `tests/test_portable_workstation_slice_c.py`, `scripts/test-version-authority-governance.py`).
  - **SHB Scheduler Repository (`/Users/androidteam/Developer/shb/shb-schedule`)**: Owns `src/shb_schedule/workflows/workstation_update.py` (`step_bun_global_update`) and its unit tests (`tests/test_workstation_update_workflow.py`).
  - **Host Workstation Environment (`/Users/androidteam`)**: Owns operator-scoped host configuration files (`~/.npmrc`, `~/.bunfig.toml`, `~/.zshrc`, `~/.bun/install/global/bun.lock`, `~/.bun/bin/omp`, `~/Library/pnpm`, and `~/Developer/scripts/workstation-daily-update.sh`), gated behind explicit operator apply execution.
