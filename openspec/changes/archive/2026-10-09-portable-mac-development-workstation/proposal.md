# Proposal

## Why

The development Mac currently has multiple installation roots and conflicting package update authorities: Homebrew, npm-global, standalone vendor binaries, and isolated directory toolchains (`~/.local/share/home-toolchain`) resolve competing copies of the same CLIs. This creates shadowed executables, PATH inconsistencies across shells and background jobs, risks to persistent Docker named volumes during cleanup, and an environment that cannot be reproduced reliably on a second Mac.

The user has explicitly specified a **Homebrew-first approach with minimal or no customization and no code updates**. Rather than building custom orchestration daemons, Python/Bash wrappers, JSON Schema manifest engines, or custom template renderers, this change establishes a clean, declarative configuration in `platform/openspec-store` using a canonical `config/Brewfile` and an operator setup runbook in `docs/mac-development-setup.md`. Tooling decisions favor standard Homebrew formulae and casks where vendor-supported, document explicit native exceptions, protect persistent data, and provide clear operator-executed procedures for workstation setup and portability.

## What Changes

- **Homebrew-First Declarative Manifest (`config/Brewfile`)**: Author a canonical Homebrew Bundle manifest declaring direct, intentional formulae, casks, and taps. To avoid dual-writer conflicts and maintain simplicity, the Brewfile strictly uses standard `tap`, `brew`, and `cask` stanzas, omitting extended DSL types (`npm`, `uv`, `cargo`), embedded Ruby hooks, shell scripts, or credentials.
- **Workstation Portability Runbook (`docs/mac-development-setup.md`)**: Author a comprehensive operator setup guide documenting step-by-step Homebrew bootstrapping, tool installation, vendor exceptions, verification commands, shell configuration, and maintenance procedures for new or existing Macs.
- **Explicit 'No Code Changes' Boundary**: Zero modifications to existing codebase scripts, updater registries, launchd plists, test suites, or application repositories. Specifically, `scripts/workstation-daily-update.sh`, `scripts/knowledge-refresh/sync-notion-knowledge.sh`, and `platform/openspec-store/scripts/toolchain_updater_registry.py` remain entirely untouched. Known issues in existing scripts are documented as operational constraints handled via native operator workflows.
- **Tool Ownership & Distribution Alignment**:
  - **OpenAI Codex**: Switch from npm-global to the official Homebrew Cask (`cask "codex"`). Updated exclusively via `brew upgrade --cask codex`. Shadowing npm-global and standalone binary copies are staged for operator removal after verification.
  - **Bun**: Align to the official core Homebrew formula (`brew "bun"`). Updated via `brew upgrade bun` per official upstream guidance ("To avoid conflicts with Homebrew, use brew upgrade bun instead").
  - **Node.js, pnpm, uv**: Manage via standard Homebrew formulae (`brew "node"`, `brew "pnpm"`, `brew "uv"`).
  - **Qoder**: Classify as a **Vendor Standalone Exception** (`~/.local/bin/qodercli` via dispatcher `~/.qoder/entry`, updated via `qoder update`). Official documentation confirms no maintained Homebrew formula or tap exists. Shadowing npm packages (`@qoder-ai/qodercli`) are staged for operator removal.
  - **GitNexus**: Classify as an **npm Global Exception** (`npm install -g gitnexus@latest`). No official Homebrew formula or cask exists upstream; requires native binding compilation (`@ladybugdb/core`). Documented as an explicit native npm runbook command.
  - **Newman & Bruno**: Retain existing isolated JavaScript toolchain exception (`~/.local/share/home-toolchain`) to preserve critical `newman-reporter-htmlextra` and Faker v5 compatibility for Postman collections without global npm collisions.
  - **Prime Agent**: Retain local TypeScript development build exception linked to `/opt/homebrew/lib/node_modules/prime-agent`, keeping it decoupled from upstream `origin/main` Rust rewrite.
- **Native Concurrency & Maintenance Runner Controls**: Address potential concurrency between manual updates and scheduled daily maintenance using native operating system mechanisms rather than custom gating code:
  - Distinguish process-level environment variable pause (`DISABLE_UPDATES=1`, which pauses only processes that inherit the variable) from persistent launchd job scheduling.
  - Document operator launchd commands (`launchctl stop`, `launchctl bootout`, `launchctl bootstrap`) to persistently pause and resume the scheduled updater during manual maintenance.
- **Service Management via Native Commands**: Use `brew services` exclusively for formula-managed services (e.g. `brew services list`). Manage vendor daemons and user background jobs via native `launchctl` commands. No custom plist template render engines or synthetic watchdog daemons.
- **Persistent State & Docker Volume Protection**: Document volume-preserving storage hygiene using native `docker system prune` (strictly omitting `--volumes` and `-a`). Explicitly protect named Docker volumes—including OmniRoute's named SQLite volume `omniroute-data` (hyphenated) and database volumes—against destructive prune commands (`docker system prune --volumes` or `docker compose down -v`).
- **Manual AgentMemory & Notion Operations**:
  - **AgentMemory**: Operate via native CLI and MCP tools, preserving the pinned vendor version pairing (`agentmemory` 0.9.30 with `iii-engine` 0.22.1). Verify health via HTTP GET `/agentmemory/health` on port 3111. Unhealthy service recovery is documented as an operator runbook step (`launchctl kickstart -k gui/$(id -u)/com.agentmemory.server`) without modifying SQLite databases.
  - **Notion Mirror**: Document manual, curated documentation publishing via supported `ntn pages` CLI commands and read-back verification. Unedited `sync-notion-knowledge.sh` is bypassed to avoid unhandled errors and dry-run mutation bugs.
- **Two Planned Store Assets Only**: Planning deliverables for future implementation are strictly bounded to `platform/openspec-store/config/Brewfile` and `platform/openspec-store/docs/mac-development-setup.md`. (These files need not exist now; only the four planning artifacts are being revised).

## Capabilities

### New Capabilities

- `portable-workstation-toolchain`: Declarative Homebrew-first configuration, native runbooks, tool ownership alignment, and operator-governed portability for macOS development tooling without custom code.

### Preserved Existing Capability Contracts

This change integrates with and preserves the requirements of existing canonical specifications in `platform/openspec-store`:

- `openspec/specs/workstation-toolchain-inventory/spec.md`: Preserves sanctioned install roots (`/opt/homebrew`, `~/.npm-global`, `~/.local/share/home-toolchain`), preferred package managers, and read-only duplication reporting before any duplicate copy is removed.
- `openspec/specs/agent-cli-inventory-coverage/spec.md`: Preserves reconciliation between declared covered agent CLIs and installed CLIs, ensuring undeclared tools are never silently modified.
- `openspec/specs/workstation-storage-hygiene/spec.md`: Preserves safety-gated storage cleanup, classification of candidates, protection of stateful volumes, and the requirement that package modifications use owning tool commands.
- `openspec/specs/notion-knowledge-sync/spec.md`: Preserves documentation mirroring intent while shifting execution to documented, operator-verified `ntn` commands.
- `openspec/specs/secrets/spec.md` & `openspec/specs/coding-agent-credential-loading/spec.md`: Preserves fail-closed secret exclusion, ensuring credentials, tokens, and secret-bearing `.zshenv` are never tracked or published.
- `openspec/specs/memory-core/spec.md` & `openspec/specs/agentmemory-provider-stability/spec.md`: Preserves structured memory contracts and pinned engine stability without raw database tampering.

## Non-Goals

- No custom automation code, Python/Bash helper scripts, JSON Schemas, template render engines, or synthetic benchmarking harnesses.
- No modifications to existing codebase scripts (`workstation-daily-update.sh`, `sync-notion-knowledge.sh`, `toolchain_updater_registry.py`), launchd plists, or application repositories.
- No automated package installations, upgrades, uninstalls, or service mutations during planning. (Operator execution requires separate, explicit authorization).
- No migration of credentials, `.zshenv`, API keys, SSH keys, private keys, Docker volume data, or raw SQLite databases to another Mac.
- No broad or un-gated filesystem deletions (`rm -rf`, `brew bundle --force --cleanup`).
- No automated Notion publication during planning.
- No promise of deterministic version locking or guaranteed automatic version rollback in Homebrew (formula bottles roll upstream; old bottles are frequently removed from Homebrew CDNs).

## Official Distribution Decisions & Ownership Matrix

Official vendor guidance, repository evidence, and read-only audits establish the following authoritative ownership assignments:

| Tool | Authoritative Installation Owner | Active Path Pattern | Update Authority | Release Channel | Dispatch Mode | Verification Smoke Command | Status / Exception Notes |
|---|---|---|---|---|---|---|---|
| `codex` | Homebrew Cask | `/opt/homebrew/bin/codex` | Homebrew (`brew upgrade --cask codex`) | stable | delegating | `codex --version` | Official upstream Cask `cask "codex"`. Switched from npm-global to eliminate self-update and multi-root conflicts. |
| `bun` | Homebrew Core Formula | `/opt/homebrew/bin/bun` | Homebrew (`brew upgrade bun`) | stable | delegating | `bun --version` | Upstream core formula `brew "bun"`. Vendor docs explicitly advise `brew upgrade bun` to avoid Homebrew collisions. |
| `node` | Homebrew Core Formula | `/opt/homebrew/bin/node` | Homebrew (`brew upgrade node`) | stable | delegating | `node --version && npm --version` | Standard system JavaScript runtime and npm package manager. |
| `pnpm` | Homebrew Core Formula | `/opt/homebrew/bin/pnpm` | Homebrew (`brew upgrade pnpm`) | stable | delegating | `pnpm --version` | Fast, disk-efficient package manager. |
| `uv` | Homebrew Core Formula | `/opt/homebrew/bin/uv` | Homebrew (`brew upgrade uv`) | stable | delegating | `uv --version` | Manages Python environments and tools. |
| `qoder` | Vendor Standalone Installer | `~/.local/bin/qodercli` | Vendor Dispatcher (`~/.qoder/entry`) | stable | native | `qoder --version` | **Standalone Exception**. Official docs specify standalone script with `qoder update`. No official Homebrew formula/tap exists. |
| `gitnexus` | Global npm Package | `~/.npm-global/bin/gitnexus` | npm authority (`npm install -g gitnexus@latest`) | latest | delegating | `gitnexus --version && gitnexus status` | **npm Global Exception**. Official upstream docs specify npm install; native binding compilation required. No Homebrew formula exists. |
| `newman` | Isolated JS Toolchain | `~/.local/share/home-toolchain/bin/newman` | npm in isolated root | 6.2.2 | delegating | `newman --version` | **Isolated Toolchain Exception**. Pinned with `newman-reporter-htmlextra` and Faker v5 compatibility for Postman collections. |
| `bruno` | Isolated JS Toolchain | `~/.local/share/home-toolchain/bin/bru` | npm in isolated root | 4.2.1 | delegating | `bru --version` | **Isolated Toolchain Exception**. Retained alongside Newman in isolated toolchain root. |
| `prime-agent` | Local Development Module | `/opt/homebrew/lib/node_modules/prime-agent` | Manual Workspace Build | local-dev | none | `prime-agent --version` | **Local Development Exception**. Linked to local TypeScript packages; decoupled from upstream Rust rewrite. |
| `docker` | Docker Desktop / CLI | `/opt/homebrew/bin/docker` | Docker Desktop / Homebrew Cask | stable | delegating | `docker --version && docker compose version` | Official Docker Desktop engine. Managed via standard CLI lifecycle; protects named volume `omniroute-data`. |
| `agentmemory` | Global npm Package (`@agentmemory/agentmemory`) | Pinned CLI / Service | npm in global prefix | 0.9.30 | native | `curl -s http://localhost:3111/agentmemory/health` | Pinned with `iii-engine` 0.22.1. Native health check on `/agentmemory/health` (port 3111). Recoverable via `launchctl kickstart`. |

## Research Basis

- **Homebrew Bundle & Brewfile**: `https://docs.brew.sh/Brew-Bundle-and-Brewfile` (verified standard DSL stanzas for `tap`, `brew`, `cask`; verified `brew bundle check --file <Brewfile> --no-upgrade`; confirmed absence of deterministic version locking).
- **OpenAI Codex CLI**: `https://github.com/openai/codex` and Homebrew Cask repository (`Casks/c/codex.rb`) (verified official cask availability and absence of native self-update verb in npm installs).
- **Bun**: `https://bun.sh/docs/installation` and `https://formulae.brew.sh/api/formula/bun.json` (verified core Homebrew formula availability and upstream directive to use `brew upgrade bun` when installed via Homebrew).
- **Qoder CLI**: `https://docs.qoder.com/cli/installation` and `https://docs.qoder.com/cli/quickstart` (verified standalone binary architecture, `~/.qoder/entry` dispatcher, native `qoder update`, and absence of official Homebrew formula or tap).
- **GitNexus**: `https://github.com/abhigyanpatwari/GitNexus` (verified official npm-global installation method, requirement for native binding compilation `@ladybugdb/core`, and absence of official Homebrew formula).
- **Docker Storage & Volume Semantics**: Official Docker documentation and local inspection of `docker-disk-guard.sh` and `/Users/androidteam/Omniroute/docker-compose.override.yml` (verified named volume `omniroute-data`; confirmed `docker system prune` without `--volumes` preserves named volumes).
- **AgentMemory Runtime**: Local package inspection (verified `agentmemory` 0.9.30 pins `iii-engine` 0.22.1; verified HTTP GET `/agentmemory/health` on port 3111 returns status ok).
