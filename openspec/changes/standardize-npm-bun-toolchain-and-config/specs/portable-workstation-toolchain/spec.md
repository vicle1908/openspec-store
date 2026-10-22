# portable-workstation-toolchain Specification Delta

## MODIFIED Requirements

### Requirement: Global package ecosystems SHALL maintain initialized manifests and non-interactive update paths

All global package managers (NPM, Bun, and UV) SHALL maintain valid global manifests and lockfiles, SHALL execute upgrades dynamically using sanitized identifiers without hardcoded package lists or clobbering pinned coding agent binaries or Homebrew-owned runtimes, SHALL keep `~/.npm-global/bin` and `~/.npm-global/lib/node_modules` free of orphaned `.bin-HASH` retired symlinks and empty `@scope` directories, and SHALL document that `npm audit -g` is unsupported (`EAUDITGLOBAL`) despite `npm update -g` printing a quick-audit summary.

#### Scenario: Bun global manifest initialization
- **WHEN** Bun global packages are audited or updated by `workstation_update.py` or `workstation-daily-update.sh`
- **THEN** the maintenance pipeline SHALL verify the existence of `~/.bun/install/global/package.json` (mode `0600` inside directory mode `0700`) and `~/.bun/install/global/bun.lock`
- **AND** if `package.json` is absent, it SHALL initialize `~/.bun/install/global/package.json` with `{"dependencies": {}}` and mode `0600`
- **AND** when `package.json` has empty `dependencies` (`{}`), it SHALL write the minimal v2 text lockfile (`{"lockfileVersion": 2, "configVersion": 1, "workspaces": {"": {}}, "packages": {}}`, mode `0600`) to `~/.bun/install/global/bun.lock` if absent and skip `bun install` and `bun update -g` so `bun@1.4+` does not delete the empty lockfile and `bun pm ls -g` exits `0`
- **AND** when `package.json` declares one or more dependencies, it SHALL initialize any missing `bun.lock` via `bun install --cwd ~/.bun/install/global --save-text-lockfile` and execute `bun update -g` non-interactively
- **AND** it SHALL NOT execute `bun upgrade` against the Homebrew-managed `/opt/homebrew/bin/bun` binary (which is updated exclusively via `brew upgrade bun` in the Homebrew stage)

#### Scenario: Dynamic uv tool list upgrade with sanitized arguments
- **WHEN** Python standalone CLI tools are upgraded
- **THEN** the maintenance pipeline SHALL query installed tools dynamically via `uv tool list`
- **AND** it SHALL validate each tool identifier against character class `^[A-Za-z0-9._@/+-]+$`
- **AND** it SHALL pass each validated tool name as a discrete argument preceded by `--` to `uv tool upgrade -- "$TOOL"`
- **AND** it SHALL execute upgrades in isolated venvs rather than relying on a static hardcoded package list

#### Scenario: NPM global upgrades exclude pinned coding agents
- **WHEN** `npm outdated -g --json` identifies outdated packages in `~/.npm-global`
- **THEN** the upgrade process SHALL validate discovered package names against `^[A-Za-z0-9._@/+-]+$`
- **AND** it SHALL filter out all tools declared in the authoritative deny and pinned agent rosters (`codex`, `claude`, `pi`, `kilo`)
- **AND** only non-governed packages SHALL be upgraded via `npm install -g -- "$PKG@latest"`

#### Scenario: NPM global prefix directory hygiene and EAUDITGLOBAL documentation
- **WHEN** `~/.npm-global/bin` and `~/.npm-global/lib/node_modules` are inspected after global npm maintenance
- **THEN** no dangling retired `.bin-HASH` dot-symlinks (such as `.amp-*`, `.dgrep-*`, `.tsc-*`) SHALL remain in `~/.npm-global/bin` and no empty `@*` scope directories SHALL remain in `~/.npm-global/lib/node_modules`
- **AND** workstation runbook and audit evidence SHALL record that `npm audit -g` fails by npm design with `EAUDITGLOBAL` and that global package trees (`@agentmemory/agentmemory` and `happy`) MUST be audited per-package in isolated temporary lockfiles rather than by running `npm audit fix` in `~/Developer`

### Requirement: Deterministic Zsh PATH deduplication and Homebrew-first precedence

Interactive and login Zsh initialization (`~/.zshenv`, `~/.zprofile`, `~/.zshrc`) and the fallback maintenance runner (`workstation-daily-update.sh`) SHALL enforce unique `PATH` entries via `typeset -U path PATH`, maintain `/opt/homebrew/bin` ahead of `~/.npm-global/bin`, `~/.bun/bin`, and `~/Library/pnpm` (`PNPM_HOME`), expose `/opt/homebrew/opt/libpq/bin` for `psql`, omit unused `nvm` shell function wrappers when Homebrew `node` is authoritative, explicitly filter out inherited `~/.orbstack/bin` entries via `path=(${path:#"$HOME/.orbstack/bin"})`, and guard `~/.iterm2_shell_integration.zsh` behind `[[ -t 0 && -t 1 ]]`.

#### Scenario: Interactive and inherited shells preserve Homebrew precedence, deduplicate PATH, and strip OrbStack
- **WHEN** a fresh login shell (`zsh -ilc 'print -l $path'`) or a subshell inheriting `PATH="$HOME/.orbstack/bin:$PATH"` (`PATH="$HOME/.orbstack/bin:$PATH" zsh -ic 'print -l $path'`) is evaluated
- **THEN** `/opt/homebrew/bin` SHALL appear before `/Users/androidteam/.npm-global/bin` and before `/Users/androidteam/Library/pnpm` (`PNPM_HOME` and `PNPM_HOME/bin`)
- **AND** `which pnpm` and `which pnpx` SHALL resolve to `/opt/homebrew/bin/pnpm` and `/opt/homebrew/bin/pnpx` without shadowing from `~/Library/pnpm/bin/pnpx`
- **AND** `which node`, `which npm`, and `which npx` SHALL resolve directly to `/opt/homebrew/bin/{node,npm,npx}` without `_load_nvm` shell function interception
- **AND** `/opt/homebrew/opt/libpq/bin` SHALL be present on `PATH` so `which psql` resolves to `/opt/homebrew/opt/libpq/bin/psql`
- **AND** `/Users/androidteam/.orbstack/bin` SHALL be absent from `$path`
- **AND** no directory entry (including `/Users/androidteam/.kimi-code/bin`) SHALL appear more than once in `$path`

#### Scenario: Maintenance runner PATH preserves Homebrew precedence over npm-global and bun
- **WHEN** `scripts/workstation-daily-update.sh` (and its executed copy `~/Developer/scripts/workstation-daily-update.sh`), `config/launchd/com.agentmemory.server.plist.tmpl`, and `scripts/seed-agentmemory-decisions.py` (`shell-path-precedence`) are inspected and validated by `tests/test_portable_workstation_slice_b.py`
- **THEN** `${HOME}/.local/bin` SHALL precede `/opt/homebrew/bin` (`{{HOMEBREW_PREFIX}}/bin`), and `/opt/homebrew/bin` SHALL precede `${HOME}/.npm-global/bin` and `${HOME}/.bun/bin`
- **AND** `test_daily_update_script_path_precedence_order` in `tests/test_portable_workstation_slice_b.py` SHALL assert `brew_idx < npm_idx` and `local_idx < brew_idx`

#### Scenario: Non-TTY interactive subshells do not emit iTerm2 OSC escape sequences
- **WHEN** a non-TTY interactive subshell (`zsh -ic 'echo READY' </dev/null`) is executed by an automation or diagnostic runner
- **THEN** `~/.iterm2_shell_integration.zsh` SHALL be skipped when standard input or output is not a TTY
- **AND** stdout SHALL begin cleanly with `READY` without leading `\e]1337;` escape sequences

## ADDED Requirements

### Requirement: Maximized permissive and high-throughput npm and Bun user configuration

User-level package manager configurations (`~/.npmrc` and `~/.bunfig.toml`) SHALL be maintained with file mode `0600`, zero hardcoded secret values, unrestricted lifecycle script and remote/git/file/directory source execution, and maximized concurrency/deduplication settings for `npm@11+`, `pnpm@12+`, and `bun@1.4+`.

#### Scenario: User npmrc preserves full script/source permissiveness and maximized throughput
- **WHEN** `~/.npmrc` is inspected via value-blind configuration audit and `npm config list`
- **THEN** `~/.npmrc` SHALL have file mode `0600`, contain zero secret tokens, and emit `0` bytes of `npm warn Unknown user config` on `stderr`
- **AND** it SHALL configure `prefix=/Users/androidteam/.npm-global`, `dangerously-allow-all-scripts=true`, `allow-remote=all`, `allow-git=all`, `allow-file=all`, `allow-directory=all`, `ignore-scripts=false`, `foreground-scripts=false`, `maxsockets=64`, `prefer-dedupe=true`, `fund=false`, `audit=false`, and `update-notifier=false`

#### Scenario: User bunfig.toml configures maximized concurrency and hoisted global/workspace defaults
- **WHEN** `~/.bunfig.toml` is inspected via value-blind configuration audit
- **THEN** `~/.bunfig.toml` SHALL exist with file mode `0600` and contain zero secret tokens
- **AND** its `[install]` section SHALL configure `auto = "auto"`, `saveTextLockfile = true`, `concurrentScripts = 32`, `networkConcurrency = 64`, `linker = "hoisted"`, `globalDir = "/Users/androidteam/.bun/install/global"`, `globalBinDir = "/Users/androidteam/.bun/bin"`, `exact = false`, `production = false`, `optional = true`, `dev = true`, and `peer = true`
- **AND** its `[install.cache]` section SHALL configure `dir = "/Users/androidteam/.bun/install/cache"`, `disable = false`, and `disableManifest = false`
- **AND** its `[run]` section SHALL configure `shell = "bun"`
