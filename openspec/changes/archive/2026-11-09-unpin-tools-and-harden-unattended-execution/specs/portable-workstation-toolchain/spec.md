# portable-workstation-toolchain Specification Delta

## MODIFIED Requirements

### Requirement: Global package ecosystems SHALL maintain initialized manifests and non-interactive update paths

Global package managers (NPM, Bun, and UV) SHALL maintain valid global manifests and lockfiles, upgrade packages dynamically with sanitized identifiers without clobbering pinned coding agents or Homebrew runtimes, keep `~/.npm-global` free of retired `.bin-HASH` symlinks and empty `@scope` directories, document `EAUDITGLOBAL` (`npm audit -g`), and automatically unpin tools to track latest available upstream releases while skipping authority-conflicted Mac App Store applications.

#### Scenario: Bun global manifest initialization
- **WHEN** Bun global packages are audited or updated by `workstation_update.py` or `workstation-daily-update.sh`
- **THEN** the maintenance pipeline SHALL verify the existence of `~/.bun/install/global/package.json` (mode `0600` inside directory mode `0700`) and `~/.bun/install/global/bun.lock`
- **AND** if `package.json` is absent, it SHALL initialize `~/.bun/install/global/package.json` with `{"dependencies": {}}` and mode `0600`
- **AND** when `package.json` has empty `dependencies` (`{}`), it SHALL write the minimal v2 text lockfile (`{"lockfileVersion": 2, "configVersion": 1, "workspaces": {"": {}}, "packages": {}}`) to `~/.bun/install/global/bun.lock` if absent and skip `bun install` and `bun update -g` so `bun@1.4+` does not delete the empty lockfile and `bun pm ls -g` exits `0`
- **AND** when `package.json` declares one or more dependencies, it SHALL execute single-pass `bun update -g --save-text-lockfile` non-interactively, and in both cases it SHALL enforce mode `0600` on `~/.bun/install/global/bun.lock`
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

#### Scenario: Unpinned tool upgrading and automatic unpin recovery
- **WHEN** `uv tool upgrade` reports that a tool has an exact version pin or outputs a pinned hint
- **THEN** the maintenance runner SHALL automatically reinstall with `uv tool install --upgrade "<tool>@latest"` to unpin and upgrade the tool to latest
- **AND** `platform/openspec-store/config/uv-tools.json` SHALL declare `"version": "latest"` across all standalone tools

#### Scenario: Mac App Store skips Cask-managed applications and authority collisions
- **WHEN** `mas outdated` reports an application that is already installed or managed by Homebrew Cask (e.g. `Telegram` / `747648890`)
- **THEN** the maintenance pipeline SHALL skip the application to prevent installer receipt corruption, interactive Apple ID prompts, and package manager collisions
- **AND** it SHALL record the skip as an authority-gated bypass rather than an error

#### Scenario: Headless non-interactive environment and zero-sudo execution
- **WHEN** scheduled maintenance workflows execute unattended
- **THEN** all subprocess environments SHALL export `NONINTERACTIVE=1`, `CI=1`, `DEBIAN_FRONTEND=noninteractive`, `HOMEBREW_NO_AUTO_UPDATE=1`, `HOMEBREW_NO_INTERVENTIONS=1`, `HOMEBREW_NO_INSTALL_CLEANUP=1`, `PIP_NO_INPUT=1`, and `NPM_CONFIG_YES=true`
- **AND** standard input SHALL be closed or redirected from `/dev/null`
- **AND** no automated step SHALL invoke `sudo` or request interactive administrator credentials

### Requirement: Sanctioned uv Tool Receipt Reconciliation

The declarative `config/uv-tools.json` manifest in `platform/openspec-store` SHALL accurately record every sanctioned CLI tool installed under `~/.local/share/uv/tools/` using unpinned `version: latest` so tools always track the latest available releases, while preserving package extras and companion `--with` dependency constraints recorded in `uv-receipt.toml`.

#### Scenario: Reconciling uv-tools.json with installed uv tool receipts
- **WHEN** inspecting `platform/openspec-store/config/uv-tools.json` against `uv tool list --show-version-specifiers` and `~/.local/share/uv/tools/*/uv-receipt.toml`
- **THEN** every installed `uv` tool (`graphifyy`, `tavily-cli`, `browser-use`, and `infinity-emb`) SHALL be declared in `config/uv-tools.json` with `"version": "latest"`
- **AND** `graphifyy` SHALL record its required `[mcp,watch,office,pdf,postgres]` extras and `infinity-emb` SHALL record its `[server]` extra and companion `--with` requirements so automated or manual workstation setup reproduces the exact tool environment on Python `3.15`.
