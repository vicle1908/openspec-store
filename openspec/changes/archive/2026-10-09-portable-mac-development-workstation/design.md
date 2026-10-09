# Design

## Context

The development workstation currently exhibits multiple installation roots and competing package update authorities:
- Executables are distributed across `/opt/homebrew`, `~/.npm-global`, `~/.local/bin`, and an isolated toolchain at `~/.local/share/home-toolchain`. Several CLIs (`codex`, `qoder`, `gitnexus`) have colliding or shadowed copies across these roots.
- A scheduled daily maintenance runner at `scripts/workstation-daily-update.sh` executes automated updates across multiple stages, creating potential concurrency conflicts if an operator performs manual package management.
- Existing knowledge sync scripts (`scripts/knowledge-refresh/sync-notion-knowledge.sh`) contain known issues where `--dry-run` mutates discovery state and API errors are swallowed.
- Routine storage cleanup scripts risk destroying persistent Docker named volumes (such as OmniRoute's SQLite WAL database volume `omniroute-data`) if invoked with `--volumes`.

The user has explicitly mandated: **"update changes, we prefer homebrew and minimize or no customization , no code update needed"**.
In accordance with this directive:
1. All custom automation code—including Python/Bash inventory scripts, JSON Schemas, template render engines, shell startup benchmarking harnesses, custom watchdog plists, and deletion wrappers—is completely **eliminated**.
2. Existing codebase scripts (`workstation-daily-update.sh`, `sync-notion-knowledge.sh`, `toolchain_updater_registry.py`) remain **unmodified**. Their known limitations are handled via native operator runbooks rather than new code.
3. Planned implementation assets in `platform/openspec-store` are strictly bounded to two files:
   - `config/Brewfile`: Canonical Homebrew Bundle manifest declaring direct formulae, casks, and taps.
   - `docs/mac-development-setup.md`: Operator runbook detailing setup, native package commands, vendor exceptions, updater schedule controls, and verification procedures.

## Goals / Non-Goals

**Goals:**
- Define a clean, declarative Homebrew-first manifest (`config/Brewfile`) using standard `tap`, `brew`, and `cask` stanzas.
- Author an actionable operator runbook (`docs/mac-development-setup.md`) enabling reproducible workstation setup and second-Mac portability using standard native tools.
- Align tool ownership with official vendor distribution channels: OpenAI Codex via Homebrew Cask, Bun via Homebrew core formula, Node/pnpm/uv via Homebrew formulae.
- Document explicit native exceptions for tools lacking maintained Homebrew packages: Qoder (standalone dispatcher), GitNexus (global npm), Newman/Bruno (isolated toolbelt), and Prime Agent (local TypeScript build).
- Document native `launchctl` pause and resume procedures for the scheduled daily updater to prevent update collisions during manual maintenance.
- Enforce volume-preserving Docker cleanup semantics, protecting named volume `omniroute-data` and databases.
- Provide manual operator runbook instructions for AgentMemory health verification (`/agentmemory/health` on port 3111) and Notion documentation updates (`ntn pages`), bypassing buggy automation scripts without code edits.

**Non-Goals:**
- No custom Python or Bash scripts, JSON schemas, template render engines, or synthetic test harnesses.
- No modifications to existing codebase scripts, updater registries, launchd plists, or application repositories.
- No live package installations, removals, or service mutations during planning. (Operator execution requires separate, explicit authorization).
- No migration of credentials, `.zshenv`, API keys, SSH keys, private keys, Docker volume data, or raw SQLite databases to another Mac.
- No broad or un-gated filesystem deletions (`rm -rf`, `brew bundle --force --cleanup`).
- No automated Notion publication during planning.
- No promise of deterministic version locking or guaranteed automatic version rollback in Homebrew.

## Decisions

### 1. Homebrew-First Architecture and Central Authoring Scope

Workstation tooling is centralized in `platform/openspec-store` under two concrete deliverables:
- `config/Brewfile`: Defines the intentional set of Homebrew formulae, casks, and taps.
- `docs/mac-development-setup.md`: Serves as the operator runbook for bootstrapping, tool installation, vendor exceptions, and verification.

All external machine modifications (package installs, uninstalls, service restarts) are treated as **operator-executed actions** requiring explicit scope authorization, rather than automated scripts.

### 2. Standard Brewfile DSL and Preflight Verification

Modern Homebrew Bundle supports extended DSL entries via `bundle/extensions/` (`npm`, `uv`, `cargo`), but mixing package managers within `Brewfile` introduces dual package writers and complex ownership disputes.
- **Strict Stanza Boundaries**: `config/Brewfile` uses only standard `tap`, `brew`, and `cask` stanzas. It contains no embedded Ruby hooks, inline shell scripts, or credentials.
- **Read-Only Preflight**: Preflight inspection is performed using:
  ```bash
  HOMEBREW_NO_AUTO_UPDATE=1 brew bundle check --file config/Brewfile --no-upgrade
  ```
  Setting `HOMEBREW_NO_AUTO_UPDATE=1` ensures the check is strictly read-only and does not trigger auto-update side effects.
- **Idempotent Installation**: Applying the manifest is executed via:
  ```bash
  brew bundle install --file config/Brewfile --no-upgrade
  ```
- **Absence of Version Locking**: A `Brewfile` declares package dependencies, not locked revisions. Formula bottles roll upstream and older revisions are deleted from CDNs. The design explicitly avoids false claims of guaranteed automatic version rollbacks.

### 3. Upstream Distribution Alignment and Exception Matrix

Official vendor guidance and repository audits establish the authoritative installation owner and update authority for each CLI:

| Tool | Official Upstream Channel | Authoritative Owner | Update Authority | Rationale & Status | Native Smoke Command |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **OpenAI Codex** | `https://github.com/openai/codex` | `cask "codex"` | `brew upgrade --cask codex` | Switched from npm-global to official Cask. Eliminates npm self-update errors (`refuse self-update`). npm and standalone shadow copies staged for removal. | `codex --version` |
| **Bun** | `https://bun.sh/docs/installation` | `brew "bun"` (core) | `brew upgrade bun` | Core formula in `homebrew/core`. Upstream docs specifically advise Homebrew users: *"To avoid conflicts with Homebrew, use `brew upgrade bun` instead"*. | `bun --version` |
| **Node.js** | `https://nodejs.org/` | `brew "node"` | `brew upgrade node` | System JavaScript runtime managed cleanly via Homebrew. | `node --version && npm --version` |
| **pnpm** | `https://pnpm.io/` | `brew "pnpm"` | `brew upgrade pnpm` | Fast, disk-efficient package manager in `homebrew/core`. | `pnpm --version` |
| **uv** | `https://github.com/astral-sh/uv` | `brew "uv"` | `brew upgrade uv` | Python environment and tool manager in `homebrew/core`. | `uv --version` |
| **Qoder** | `https://docs.qoder.com/cli/installation` | Vendor Standalone Script | `qoder update` | **Standalone Exception**. Official docs specify standalone binary at `~/.local/bin/qodercli` via `~/.qoder/entry`. No official Homebrew formula/tap exists. Shadowing npm package staged for removal. | `qoder --version` |
| **GitNexus** | `https://github.com/abhigyanpatwari/GitNexus` | npm Global Package | `npm install -g gitnexus@latest` | **npm Global Exception**. Upstream requires global npm installation; compiles native bindings (`@ladybugdb/core`). No Homebrew formula or cask exists upstream. | `gitnexus --version && gitnexus status` |
| **Newman** | Pinned Postman Tooling | Isolated JS Toolchain | npm in isolated root | **Isolated Toolchain Exception**. Retained at 6.2.2 in `~/.local/share/home-toolchain` with `newman-reporter-htmlextra` and Faker v5 compatibility for Postman collection runtimes. | `newman --version` |
| **Bruno** | Pinned API Client | Isolated JS Toolchain | npm in isolated root | **Isolated Toolchain Exception**. Retained at 4.2.1 alongside Newman in isolated toolchain root. | `bru --version` |
| **Prime Agent** | Local Monorepo Build | Local Node Module | Manual Build | **Local Development Exception**. Linked from `platform/prime-agent` to `/opt/homebrew/lib/node_modules/prime-agent`. Decoupled from upstream `origin/main` Rust rewrite. | `prime-agent --version` |
| **Docker** | Docker Desktop | Docker Desktop / Cask | Desktop App Updater | Official Docker Desktop application managing VM and Docker CLI. Protects persistent named volume `omniroute-data`. | `docker --version && docker compose version` |
| **AgentMemory** | Agent Memory Service | Global npm package (`@agentmemory/agentmemory`) | npm in global prefix | Version 0.9.30 strictly pins `iii-engine` 0.22.1. Note: native health check requires resolved engine/service on port 3111; if port or runtime conflicts exist, service must be investigated manually rather than assuming kickstart recovery. | `curl -s http://localhost:3111/agentmemory/health` |

### 4. Native Maintenance Concurrency and Schedule Management

The existing daily updater at `scripts/workstation-daily-update.sh` and its LaunchAgent `com.developer.workstation-daily-update.plist` remain **unmodified**.
Potential concurrency conflicts between manual operator updates and the scheduled runner are managed via native operator controls:
- **Environment Variable Scope**: The existing script checks `DISABLE_UPDATES=1`. However, exporting `DISABLE_UPDATES=1` in an interactive shell only affects sub-processes that inherit that environment; it does **not** pause already running or persistently scheduled launchd jobs.
- **Persistent Launchd Pause**: When performing manual maintenance, the operator persistently pauses the scheduled updater via native launchd commands:
  ```bash
  # Stop active running job immediately
  launchctl stop com.developer.workstation-daily-update

  # Persistent disable and stop of scheduled runner
  launchctl disable gui/$(id -u)/com.developer.workstation-daily-update
  launchctl bootout gui/$(id -u)/com.developer.workstation-daily-update 2>/dev/null || true
- **Resuming Scheduled Updates**: Once manual maintenance is complete and verified, the operator re-enables the schedule:
  # Re-enable and bootstrap runner schedule only after verifying runner compatibility
  launchctl enable gui/$(id -u)/com.developer.workstation-daily-update
  launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.developer.workstation-daily-update.plist

### 5. Services, Watchdogs, and Port Conflict Management

- **Formula Services**: Managed strictly via standard `brew services` commands (`brew services list`, `brew services start <formula>`).
- **User Daemons & Watchdogs**: Managed via standard `launchctl`. Bespoke watchdog script proposals, custom template rendering engines, and daemon generators are eliminated.
- **AgentMemory Invariants**:
  - The installed `agentmemory` package (0.9.30, npm global) strictly pins `iii-engine` 0.22.1. An arbitrary Homebrew engine must not be substituted.
  - Native health verification uses HTTP GET `/agentmemory/health` on port 3111 (the root path `/` returns 404). Note: if port 3111 or 49134 is occupied by an orphaned or conflicting engine process, `launchctl kickstart` alone will not resolve the conflict; operator must inspect and resolve port occupancy first.
  - Preserves the local SQLite WAL database intact with zero raw database schema edits.
- **Port Conflict Triage**: Service port collisions (e.g. Ollama daemon on port 11434, AgentMemory on port 3111) are inspected manually using native `lsof -i :<port>` without custom python conflict daemons.

### 6. Persistent State and Docker Volume Protection

Inspections of `/Users/androidteam/Omniroute/docker-compose.override.yml` confirm that OmniRoute's named SQLite WAL database volume is `omniroute-data` (hyphenated).
- **Safe Routine Prune**: Standard disk hygiene uses volume-preserving commands:
  ```bash
  docker system prune
  ```
  Omitting `--volumes` and `-a` reclaims stopped containers, dangling images, and build cache while preserving all named volumes.
- **Prohibited Destructive Prunes**: Commands that purge named volumes (`docker system prune --volumes`, `docker system prune -a --volumes`, or `docker compose down -v`) are strictly prohibited in routine operations.

### 7. Shell Environment and Secrets Exclusion

- **Standard Shellenv**: Shell configuration relies on standard Homebrew shell environment initialization in `~/.zprofile` or `~/.zshrc`:
  ```bash
  eval "$(/opt/homebrew/bin/brew shellenv)"
  ```
- **Retaining Existing Plugins**: Existing shell plugins and completions are retained without custom completion benchmarking harnesses or lazy NVM wrappers.
- **Secrets Protection**: Secret-bearing files (`~/.zshenv`), API keys, SSH keys, and session tokens are strictly excluded from git tracking, manifests, and runbooks.

### 8. Knowledge Documentation and Notion Operations

- **Source of Truth**: The Markdown runbook `docs/mac-development-setup.md` in `platform/openspec-store` serves as the version-controlled source of truth.
- **Manual Notion Updates**: Because `sync-notion-knowledge.sh` has known error-swallowing and dry-run mutation bugs and the user rejected code updates, automated sync scripts are bypassed. Documentation updates to the Notion knowledge hub are performed manually using documented `ntn pages` CLI commands and read-back verification:
  ```bash
  ntn pages edit <page-id> < platform/openspec-store/docs/mac-development-setup.md
  # or: ntn pages edit <page-id> --content "$(cat platform/openspec-store/docs/mac-development-setup.md)"
  ```

## Candidate Classification & Operational Action Table

| Candidate | Current Resolution | Action Classification | Rationale & Native Procedure |
| :--- | :--- | :--- | :--- |
| `codex` | `~/.npm-global/bin/codex`, standalone copy | Migrate to Homebrew Cask | Install via `brew install --cask codex`; verify `codex --version`; stage duplicate npm and standalone copies for operator removal. |
| `bun` | `~/.bun/bin/bun` (standalone) | Migrate to Homebrew Core | Install via `brew install bun`; update via `brew upgrade bun`; stage standalone binary removal after PATH verification. |
| `node` | `/opt/homebrew/bin/node` | Retain Homebrew Formula | Aligned with `homebrew/core`. Update via `brew upgrade node`. |
| `pnpm` | `/opt/homebrew/bin/pnpm` | Retain Homebrew Formula | Aligned with `homebrew/core`. Update via `brew upgrade pnpm`. |
| `uv` | `/opt/homebrew/bin/uv` | Retain Homebrew Formula | Aligned with `homebrew/core`. Update via `brew upgrade uv`. |
| `qoder` | `~/.local/bin/qodercli` + dispatcher, npm shadow | Retain Standalone Exception | Retain official standalone dispatcher; remove shadowing npm package `@qoder-ai/qodercli` after reference check. |
| `gitnexus` | `~/.npm-global/bin/gitnexus` | Retain npm Global Exception | Retain official npm global install; compile native bindings; verify via `gitnexus status`. |
| `newman` | `~/.local/share/home-toolchain/bin/newman` | Retain Isolated Toolchain | Retain pinned 6.2.2 in isolated toolchain for Postman collection execution and Faker v5 compatibility. |
| `bruno` | `~/.local/share/home-toolchain/bin/bru` | Retain Isolated Toolchain | Retain 4.2.1 in isolated toolchain alongside Newman. |
| `prime-agent`| `/opt/homebrew/lib/node_modules/prime-agent` | Retain Local Development | Retain local TypeScript build link; exclude from upstream git pulls and package updaters. |
| `opencode` | `/opt/homebrew/bin/opencode`, npm shadow | Retain Homebrew Formula | Formula maintained in Homebrew; remove shadowing npm package after verification. |

## Risks / Trade-offs

- **No Deterministic Version Locking**: Homebrew formulae roll upstream and older bottle revisions are frequently removed from CDNs. The operator must be aware that `brew bundle` installs current available formula versions.
- **Manual Operator Handoffs**: Shifting from custom automation scripts to operator runbooks eliminates custom code maintenance but requires deliberate human execution of external machine actions.
- **Unmodified Daily Updater Schedule**: Because `workstation-daily-update.sh` is not modified, operators must use `launchctl bootout` / `launchctl bootstrap` to prevent automated runs during manual maintenance.
- **Manual Notion Documentation Updates**: Bypassing the buggy `sync-notion-knowledge.sh` script requires manual `ntn pages` invocations when publishing documentation changes.
