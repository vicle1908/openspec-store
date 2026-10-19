# portable-workstation-toolchain Specification Delta

## MODIFIED Requirements

### Requirement: Global package ecosystems SHALL maintain initialized manifests and non-interactive update paths

All global package managers (NPM, Bun, and UV) SHALL maintain valid global manifests, SHALL execute upgrades dynamically using sanitized identifiers without hardcoded package lists or clobbering pinned coding agent binaries, SHALL keep `~/.npm-global/bin` and `~/.npm-global/lib/node_modules` free of orphaned `.bin-HASH` retired symlinks and empty `@scope` directories, and SHALL document that `npm audit -g` is unsupported (`EAUDITGLOBAL`) despite `npm update -g` printing a quick-audit summary.

#### Scenario: Bun global manifest initialization
- **WHEN** Bun global packages are audited or updated
- **THEN** the maintenance pipeline SHALL verify the existence of `~/.bun/install/global/package.json`
- **AND** if absent, it SHALL initialize directory `~/.bun/install/global` with mode `0700` and write an empty dependencies object `{}` before running package commands
- **AND** it SHALL execute `bun upgrade` followed by `bun update -g` non-interactively

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
