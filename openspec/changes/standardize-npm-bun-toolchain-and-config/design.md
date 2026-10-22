# Design

## Context

See `proposal.md` for motivation. Across the workstation (`darwin 27.0.0 arm64`), `node@26.12.0`, `npm@11.20.0`, `bun@1.4.3`, and `pnpm@12.14.0` are installed via Homebrew (`homebrew/core`) under `/opt/homebrew/bin`. The operator requires a zero-friction, maximum-throughput, and fully permissive script/source posture ("keep allow all and also allow all scripts, maximize all") combined with clean single-owner update authority, deterministic `PATH` ordering, and zero drift in `inventory-workstation-toolchain.py`.

Empirical verification uncovered six critical implementation constraints:
1. **`bun@1.4.3` Empty-Manifest Lockfile Deletion**: Running `bun install` or `bun update -g` when `~/.bun/install/global/package.json` has `"dependencies": {}` prints `No packages! Deleted empty lockfile` and **deletes `bun.lock`**, causing subsequent `bun pm ls -g` invocations to exit `1` (`error: missing lockfile, nothing to list`). Conversely, writing the minimal v2 text lockfile (`{"lockfileVersion": 2, "configVersion": 1, "workspaces": {"": {}}, "packages": {}}`) directly when `dependencies` is `{}` (and only invoking `bun install` / `bun update -g` when `dependencies` is non-empty) causes `bun pm ls -g` to exit `0`.
2. **`npm@11.20.0` & `pnpm@12.14.0` `.npmrc` Schema Validation**: `npm@11.20.0` (`@npmcli/config/lib/definitions/definitions.js`) natively defines `prefix`, `dangerously-allow-all-scripts`, `allow-remote`, `allow-git`, `allow-file`, `allow-directory`, `ignore-scripts`, `foreground-scripts`, `maxsockets`, `prefer-dedupe`, `fund`, `audit`, and `update-notifier` with `0` stderr warnings, whereas legacy `enable-pre-post-scripts` emits `npm warn Unknown user config` in `npm@11.20.0` and is rejected globally in `pnpm@12.14.0`.
3. **Homebrew `node` Bundled `npm` Symlink Chain**: On macOS Homebrew, `/opt/homebrew/bin/npm` resolves through `../Cellar/node/26.12.0/bin/npm` to `/opt/homebrew/lib/node_modules/npm/bin/npm-cli.js` (outside `/Cellar/`). `derive_install_root_and_source()` in `scripts/inventory-workstation-toolchain.py` must recognize `/opt/homebrew/lib/node_modules/npm` (and `/usr/local/lib/node_modules/npm`) as `"brew-formula"` rather than `"npm"`.
4. **Dangling Symlink Blindness (`Path.exists()` vs `os.path.lexists()`)**: `/Users/androidteam/.bun/bin/omp` is a dangling symlink (`-> ../../node_modules/@oh-my-pi/pi-coding-agent/dist/cli.js`), which `sh_path.exists()` misses because `exists()` follows symlinks.
5. **Slice B `PATH` Test & Script Mirror Parity Gate**: `tests/test_portable_workstation_slice_b.py` (`test_daily_update_script_path_precedence_order`, lines 502–518) currently asserts `npm_idx < brew_idx`, and `scripts/test-version-authority-governance.py` (`test_workstation_daily_update_mirror_parity_and_bash_fail_closed`, lines 338–346) asserts byte-for-byte SHA-256 equality between `platform/openspec-store/scripts/workstation-daily-update.sh` and `~/Developer/scripts/workstation-daily-update.sh`.
6. **Preserved `newman` Peer Dependency in `home-toolchain`**: In `~/.local/share/home-toolchain/package.json`, `newman@6.2.3` is an auto-installed peer dependency of `newman-reporter-htmlextra@^1.23.1` governed by `npm-audit-remediation/spec.md` (lines 10–35); deleting `~/.local/share/home-toolchain/node_modules/newman` would break `npm ls` / `npm update` in `home-toolchain`.

## Goals / Non-Goals

**Goals:**
- Codify a maximally permissive, high-concurrency, zero-warning user configuration in `~/.npmrc` and `~/.bunfig.toml` (`mode 0600`, value-blind, zero embedded secrets).
- Enforce single-owner Homebrew update authority (`brew upgrade`) for `node`, `npm`, `pnpm`, and `bun`, removing `bun upgrade` from maintenance pipelines while maintaining `~/.bun/install/global/bun.lock`.
- Eliminate shell wrapper latency (`_load_nvm`) and `PATH` precedence inversions across `~/.zshrc`, `workstation-daily-update.sh`, and `tests/test_portable_workstation_slice_b.py`.
- Achieve full manifest, updater registry, and symlink-aware inventory parity in `platform/openspec-store` and `shb/shb-schedule`.

**Non-Goals:**
- Introducing script blocks (`ignore-scripts=true`), release-age cooldowns (`min-release-age`), or remote/git source restrictions.
- Deleting `~/.local/share/home-toolchain/node_modules/newman` (peer dependency of `newman-reporter-htmlextra`), altering `/opt/homebrew/lib/prime-agent` (`local-dev` uncovered bundle), or modifying secret values in `~/.zshenv`.

## Decisions

### 1. Maximized Permissive & High-Throughput `~/.npmrc` and `~/.bunfig.toml`
- **Decision**:
  - In `~/.npmrc` (`mode 0600`), configure the 13 verified native `npm@11.20.0` keys:
    ```ini
    prefix=/Users/androidteam/.npm-global
    dangerously-allow-all-scripts=true
    allow-remote=all
    allow-git=all
    allow-file=all
    allow-directory=all
    ignore-scripts=false
    foreground-scripts=false
    maxsockets=64
    prefer-dedupe=true
    fund=false
    audit=false
    update-notifier=false
    ```
  - In `~/.bunfig.toml` (`mode 0600`), configure:
    ```toml
    [install]
    auto = "auto"
    saveTextLockfile = true
    concurrentScripts = 32
    networkConcurrency = 64
    linker = "hoisted"
    globalDir = "/Users/androidteam/.bun/install/global"
    globalBinDir = "/Users/androidteam/.bun/bin"
    exact = false
    production = false
    optional = true
    dev = true
    peer = true

    [install.cache]
    dir = "/Users/androidteam/.bun/install/cache"
    disable = false
    disableManifest = false

    [run]
    shell = "bun"
    ```
- **Rationale**: Honors the operator's explicit requirement to keep all remote/git/file/directory sources and all lifecycle scripts enabled while maximizing socket/network/script concurrency (`maxsockets=64`, `networkConcurrency=64`, `concurrentScripts=32`), hoisted linking, and text lockfiles across `npm@11.20.0`, `pnpm@12.14.0`, and `bun@1.4.3` with zero `stderr` configuration warnings.
- **Alternatives Considered**: Including `enable-pre-post-scripts=true` in `~/.npmrc` — rejected because empirical testing on `npm@11.20.0` showed it emits `npm warn Unknown user config "enable-pre-post-scripts"` and `pnpm@12.14.0` rejects it globally (`ERR_PNPM_CONFIG_SET_UNSUPPORTED_YAML_CONFIG_KEY`).

### 2. Single-Owner Homebrew Authority for `bun` & Empty-Safe Global Lockfile Management
- **Decision**:
  - Remove `bun upgrade` from `scripts/workstation-daily-update.sh` (and `~/Developer/scripts/workstation-daily-update.sh`) and `shb-schedule`'s `step_bun_global_update()` (`src/shb_schedule/workflows/workstation_update.py` and `tests/test_workstation_update_workflow.py`).
  - Ensure both runners verify `~/.bun/install/global` (`mode 0700`) and `~/.bun/install/global/package.json` (`mode 0600`, default `{"dependencies": {}}`).
  - Inspect `dependencies` (and `devDependencies` / `optionalDependencies`) in `~/.bun/install/global/package.json`:
    - When empty (`{}`): if `~/.bun/install/global/bun.lock` is absent, write `{"lockfileVersion": 2, "configVersion": 1, "workspaces": {"": {}}, "packages": {}}\n` with mode `0600`, and skip `bun install` / `bun update -g` (preventing `bun@1.4.3` from unlinking the empty lockfile).
    - When non-empty: if `bun.lock` is absent, run `bun install --cwd ~/.bun/install/global --save-text-lockfile`, then run `bun update -g`.
- **Rationale**: Preserves single-owner Homebrew authority (`brew upgrade bun`) and guarantees `bun pm ls -g` exits `0` whether 0 or $N$ global Bun packages are installed.

### 3. Symlink-Aware Shadow Detection (`os.path.lexists`) and Homebrew Bundled `npm` Attribution
- **Decision**:
  - In `scripts/inventory-workstation-toolchain.py:1476`, replace `if sh_path.exists():` with `if sh_path.is_symlink() or sh_path.exists():` and fall back to `sh_path.lstat().st_size` when `sh_path.stat()` raises `OSError` on a dangling symlink. Remove `/Users/androidteam/.bun/bin/omp`.
  - In `derive_install_root_and_source()` (`scripts/inventory-workstation-toolchain.py`), before classifying general `/opt/homebrew/lib/node_modules/<pkg>` paths as `"npm"`, check if the package root is `/opt/homebrew/lib/node_modules/npm` or `/usr/local/lib/node_modules/npm` and return `(pkg_root, "brew-formula")`.
- **Rationale**: Ensures dangling shadow symlinks like `~/.bun/bin/omp` are detected by inventory checks, and ensures Homebrew's bundled `npm`/`npx` executables (`../Cellar/node/<ver>/bin/npm -> /opt/homebrew/lib/node_modules/npm/bin/npm-cli.js`) are attributed to `brew-formula` rather than misclassified as standalone `npm` installs.

### 4. Zsh Startup Optimization (`nvm` Removal) and Deterministic `PATH` Precedence
- **Decision**:
  - Remove the `_load_nvm` lazy-loader block (`NVM_DIR`, `nvm()`, `node()`, `npm()`, `npx()`) from `~/.zshrc:99-114` and uninstall the unused Homebrew `nvm` formula (`brew uninstall nvm`) under operator apply authorization.
  - Change `PNPM_HOME` in `~/.zshrc:144-145` from `_path_prepend` to `_path_append` so `/opt/homebrew/bin/{pnpm,pnpx}` precede `~/Library/pnpm/bin/pnpx`, and remove the stale iCloud global shim (`~/Library/pnpm/context-please-mcp` and `~/Library/pnpm/global/5`).
  - Set `export PATH="${HOME}/.kimi-code/bin:${HOME}/.qoder/entry:${HOME}/.local/bin:/opt/homebrew/bin:/opt/homebrew/sbin:/opt/homebrew/opt/libpq/bin:${HOME}/.pi/agent/bin:${HOME}/.npm-global/bin:${HOME}/.bun/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"` in `scripts/workstation-daily-update.sh:41` (and synchronize `~/Developer/scripts/workstation-daily-update.sh`), update `config/launchd/com.agentmemory.server.plist.tmpl:16` (`{{HOME}}/.local/bin:{{HOMEBREW_PREFIX}}/bin:{{HOME}}/.npm-global/bin:/usr/local/bin:/usr/bin:/bin`), update `CANONICAL_DECISIONS` (`shell-path-precedence`) in `scripts/seed-agentmemory-decisions.py:63-67`, and update `test_daily_update_script_path_precedence_order` in `tests/test_portable_workstation_slice_b.py:502-518` to assert `self.assertLess(brew_idx, npm_idx, "/opt/homebrew/bin must precede .npm-global/bin")` and `self.assertLess(local_idx, brew_idx, "local/bin must precede /opt/homebrew/bin")`.

### 5. Manifest & Profile Completeness (`workstation-toolchain-manifest.json` & `npm-global-tools.json`)
- **Decision**:
  - Add `~/.bun` to `sanctioned_roots` in `config/workstation-toolchain-manifest.json` and `is_path_sanctioned()` in `scripts/inventory-workstation-toolchain.py`.
  - Register `npm`, `pnpm`, and `bun` in `config/workstation-toolchain-manifest.json` (`profiles.core` and `tools.{npm,pnpm,bun}`) and in `scripts/toolchain_updater_registry.py` under `brew-formula` (`writer_binary: "brew"`).
  - Update `config/npm-global-tools.json` to include all 15 sanctioned CLI packages installed in `~/.npm-global` (`openspec`, `gitnexus`, `kilo`, `auggie`, `happy`, `agentmemory`, `agentmemory-mcp`, `brightdata`, `anydoc`, `grepai`, `mcpr`, `deepwiki`, `codexuse`, `exa`, `node-gyp`).
- **Transaction Boundaries**:
  - Central store (`platform/openspec-store`), scheduler repository (`shb/shb-schedule`), and host dotfiles (`~/.npmrc`, `~/.bunfig.toml`, `~/.zshrc`, `~/.bun`, `~/Library/pnpm`, `~/Developer/scripts/workstation-daily-update.sh`) have independent Git/filesystem transaction boundaries. Because `test-version-authority-governance.py` asserts SHA-256 parity between `platform/openspec-store/scripts/workstation-daily-update.sh` and `~/Developer/scripts/workstation-daily-update.sh` whenever the host file exists, both copies MUST be updated in lockstep during apply.

## Risks / Trade-offs

- **[Risk] Permissive lifecycle scripts (`dangerously-allow-all-scripts=true`, `ignore-scripts=false`) execute arbitrary `preinstall`/`postinstall` hooks during package installation** → **Mitigation**: Explicitly requested by the operator to maximize compatibility with native/compiled agent and MCP tooling (`gitnexus`, `tree-sitter`, `better-sqlite3`, `node-gyp`); pinned coding agents (`codex`, `claude`, `pi`, `kilo`) remain protected by `GOVERNED_NPM_AGENTS` / `DENY_ROSTER_NPM` in automated maintenance runs.
- **[Risk] `bun@1.4.3` unlinks `bun.lock` if `bun install` or `bun update -g` is invoked on an empty `{"dependencies": {}}` manifest** → **Mitigation**: Guard `bun install` / `bun update -g` behind a non-empty `dependencies` check and write the v2 JSON lockfile directly when `dependencies` is `{}`.
