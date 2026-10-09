# macOS Development Workstation Setup & Portability Runbook

## Overview

This runbook documents the reproducible setup, maintenance, and verification procedures for developer macOS workstations (`arm64` and `x86_64`). The environment is governed by standard **Homebrew Bundle (`config/Brewfile`)** alongside explicit, vendor-supported native exceptions.

---

## 1. Upstream Toolchain Authority Matrix

Every development CLI is governed by exactly one authoritative installation owner and update mechanism.

| Tool | Upstream Channel | Authoritative Owner | Update Authority | Verification Smoke Command | Status / Exception Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **OpenAI Codex** | Official Cask | `cask "codex"` | `brew upgrade --cask codex` | `codex --version` | Standardized on official Homebrew Cask. Eliminates npm self-update errors. |
| **Bun** | Core Formula | `brew "bun"` | `brew upgrade bun` | `bun --version` | Standardized on Homebrew core formula. Avoids standalone updater collisions. |
| **Node.js** | Core Formula | `brew "node"` | `brew upgrade node` | `node --version && npm --version` | Standard system JavaScript runtime and npm package manager. |
| **pnpm** | Core Formula | `brew "pnpm"` | `brew upgrade pnpm` | `pnpm --version` | Fast, disk-efficient package manager. |
| **uv** | Core Formula | `brew "uv"` | `brew upgrade uv` | `uv --version` | Fast Python package and environment manager. |
| **Qoder** | Standalone Script | Vendor Standalone | `qoder update` | `qoder --version` | **Standalone Exception**. Managed via `~/.local/bin/qodercli` and `~/.qoder/entry` dispatcher. |
| **GitNexus** | npm Registry | npm Global Prefix | `npm install -g gitnexus@latest` | `gitnexus --version && gitnexus status` | **npm Global Exception**. Distributed via npm; compiles native `@ladybugdb/core` bindings. |
| **Newman** | Pinned JS Toolbelt | Isolated Toolchain | npm in isolated root | `newman --version` | **Isolated Toolchain Exception**. Retained at 6.2.2 in `~/.local/share/home-toolchain`. |
| **Bruno** | Pinned JS Toolbelt | Isolated Toolchain | npm in isolated root | `bru --version` | **Isolated Toolchain Exception**. Retained at 4.2.1 in `~/.local/share/home-toolchain`. |
| **Prime Agent** | Local Repository | Local Node Module | Manual Build | `prime-agent --version` | **Local Dev Exception**. Linked from `platform/prime-agent`; decoupled from upstream Rust rewrite. |
| **Docker** | Docker Desktop | Docker Desktop / Cask | Desktop App Updater | `docker --version && docker compose version` | Official Docker Desktop application managing VM and Docker CLI. Protects persistent volumes. |
| **AgentMemory** | npm Global | npm Global Prefix | npm in global prefix | `curl -s http://localhost:3111/agentmemory/health` | **npm Global Exception**. Package `@agentmemory/agentmemory` pins `iii-engine` 0.22.1. |

---

## 2. Bootstrapping a New Mac

### Prerequisites
1. Install Apple Xcode Command Line Tools:
   ```bash
   xcode-select --install
   ```
2. Install Homebrew (if absent):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
3. Initialize Homebrew in the shell environment (`~/.zprofile`):
   ```bash
   # On Apple Silicon (arm64):
   eval "$(/opt/homebrew/bin/brew shellenv)"
   # On Intel (x86_64):
   eval "$(/usr/local/bin/brew shellenv)"
   ```

### Applying the Declarative Manifest
1. Clone the central configuration repository:
   ```bash
   mkdir -p ~/Developer/platform
   git clone <repo-url> ~/Developer/platform/openspec-store
   cd ~/Developer/platform/openspec-store
   ```
2. Verify package alignment in read-only mode:
   ```bash
   HOMEBREW_NO_AUTO_UPDATE=1 brew bundle check --file config/Brewfile --no-upgrade
   ```
3. Install declared packages without upgrading existing installations:
   ```bash
   brew bundle install --file config/Brewfile --no-upgrade
   ```

---

## 3. Installing Native Tool Exceptions

For tools without maintained upstream Homebrew formulae or casks, apply standard vendor-supported installation methods:

### Qoder CLI (Standalone Script)
```bash
curl -fsSL https://download.qoder.com/qodercli/install.sh -o /tmp/qoder-install.sh
bash /tmp/qoder-install.sh
rm -f /tmp/qoder-install.sh
```
- Active binary: `~/.local/bin/qodercli`
- Dispatcher: `~/.qoder/entry/qoder` (added to PATH via `~/.zshrc`)
- Update command: `qoder update`

### GitNexus (npm Global)
```bash
npm install -g gitnexus@latest
```
- Active binary: `~/.npm-global/bin/gitnexus`
- Update command: `npm install -g gitnexus@latest`
- Verification: `gitnexus --version && gitnexus status`

### Newman & Bruno (Isolated Toolbelt)
```bash
mkdir -p ~/.local/share/home-toolchain
cd ~/.local/share/home-toolchain
# Install pinned dependencies declared in package.json & lockfile
npm install --no-audit --no-fund
```
- Active binaries: `~/.local/share/home-toolchain/node_modules/.bin/newman`, `bru`

### Prime Agent (Local TypeScript Build)
```bash
cd ~/Developer/platform/prime-agent
pnpm install && pnpm build
# Link locally without pulling upstream main (Rust rewrite)
npm link
```

---

## 4. Maintenance Concurrency & Scheduled Runner Controls

Workstations run automated daily maintenance via `com.developer.workstation-daily-update.plist`. To avoid writer conflicts during manual package updates, use native launchd controls:

### Persistently Pausing the Scheduled Runner
```bash
# Stop any active running job process
launchctl stop com.developer.workstation-daily-update

# Persistently disable the LaunchAgent job schedule
launchctl disable gui/$(id -u)/com.developer.workstation-daily-update
launchctl bootout gui/$(id -u)/com.developer.workstation-daily-update 2>/dev/null || true
```
*Note: Exporting `DISABLE_UPDATES=1` only affects sub-processes in the active shell and does NOT pause scheduled launchd jobs.*

### Resuming the Scheduled Runner
Only resume scheduled updates after verifying runner compatibility and confirming no active package collisions:
```bash
launchctl enable gui/$(id -u)/com.developer.workstation-daily-update
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.developer.workstation-daily-update.plist
```

---

## 5. Storage Hygiene & Docker Volume Protection

### Volume Preservation Contract
Routine disk cleanup commands must preserve persistent data.
- **Safe Docker Cleanup**:
  ```bash
  # Reclaims unused containers, networks, dangling images, and build cache
  # NEVER pass --volumes to avoid removing anonymous volumes
  docker system prune -f
  ```
- **Protected Stateful Named Volumes**:
  - `omniroute-data` (OmniRoute SQLite database and WAL files)
  - PostgreSQL database volumes (e.g. `postgres_data`)
- **Strict Prohibition**: Never run `docker system prune -a --volumes -f` or uncoordinated volume deletions.

---

## 6. Shell Environment & Secrets Protection

### PATH Precedence Policy
Interactive shells (`~/.zshrc`) evaluate paths in deterministic order:
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$HOME/.qoder/entry:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
```

### Secrets Exclusion Policy
- **Never commit `.env` or credentials to git**.
- Shared environment credentials reside exclusively in mode `0600` files (such as `~/.zshenv`).
- Manifests and runbooks must never record API keys, tokens, or raw credentials.

---

## 7. Service Supervision & AgentMemory Health

### Formula Services
Managed via standard `brew services`:
```bash
brew services list
brew services start redis    # Starts service and registers LaunchAgent
brew services stop redis
```

### AgentMemory Service Supervision
- Global package `@agentmemory/agentmemory` pins `iii-engine` 0.22.1.
- Service is supervised via `~/Library/LaunchAgents/com.agentmemory.server.plist`.
- Health check:
  ```bash
  curl -s http://localhost:3111/agentmemory/health
  # Root path '/' returns 404; check /agentmemory/health specifically
  ```
- If port 3111 or 49134 is occupied by an orphaned or incompatible engine process, operator must inspect and resolve port occupancy before restarting the service via `launchctl kickstart -k gui/$(id -u)/com.agentmemory.server`.
- The local SQLite WAL database must remain intact with zero schema mutations.

---

## 8. Notion Knowledge Mirror Documentation

Manual documentation updates to the Notion knowledge hub use the official `ntn pages` CLI:
```bash
# Retrieve page content
ntn pages get <page-id>

# Update page content from Markdown runbook
ntn pages edit <page-id> < platform/openspec-store/docs/mac-development-setup.md
# or pass content directly:
ntn pages edit <page-id> --content "$(cat platform/openspec-store/docs/mac-development-setup.md)"
```
*Note: The unedited `sync-notion-knowledge.sh` script is bypassed for workstation runbook publications.*

---

## 9. Second-Mac Verification Protocol

When migrating or verifying a secondary machine:
1. Complete steps in Section 2 (Xcode CLT, Homebrew, `brew bundle install --no-upgrade`).
2. Complete steps in Section 3 for native exceptions.
3. Provision out-of-band secrets (`~/.zshenv`) manually.
4. Execute verification smoke commands across all tools:
   ```bash
   codex --version
   bun --version
   node --version && npm --version
   uv --version
   qoder --version
   gitnexus --version && gitnexus status
   docker --version
   ```
5. Confirm zero duplicate binary resolution via `which -a <tool>`.
