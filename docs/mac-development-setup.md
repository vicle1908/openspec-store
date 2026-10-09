# macOS Development Workstation Setup & Portability Runbook

## Overview

This runbook documents the reproducible setup, maintenance, and verification procedures for developer macOS workstations (`arm64` and `x86_64`). The environment is governed by standard **Homebrew Bundle (`config/Brewfile`)** alongside explicit, vendor-supported native exceptions.

---

## 1. Upstream Toolchain Authority Matrix

Every development CLI is governed by exactly one authoritative installation owner and update mechanism.

| Tool | Upstream Channel | Authoritative Owner | Update Authority | Verification Smoke Command | Status / Exception Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **OpenAI Codex** | Official Cask | `cask "codex"` | `brew upgrade --cask codex` | `codex --version` | **Official Homebrew Cask**. Authoritative package and update owner. Active binary verified at `/opt/homebrew/bin/codex` (Mach-O arm64, v0.162.0). Eliminates npm self-update errors. |
| **Bun** | Core Formula | `brew "bun"` | `brew upgrade bun` | `bun --version` | **Homebrew Core Formula**. Standardized on core formula. Active binary verified at `/opt/homebrew/bin/bun`. Avoids standalone updater collisions. |
| **Node.js** | Core Formula | `brew "node"` | `brew upgrade node` | `node --version && npm --version` | Standard system JavaScript runtime and npm package manager. |
| **pnpm** | Core Formula | `brew "pnpm"` | `brew upgrade pnpm` | `pnpm --version` | Fast, disk-efficient package manager. |
| **uv** | Core Formula | `brew "uv"` | `brew upgrade uv` | `uv --version` | Fast Python package and environment manager. |
| **Qoder** | Standalone Script | Vendor Standalone | `qoder update` | `qoder --version` | **Standalone Exception**. Managed via `~/.local/bin/qodercli` and `~/.qoder/entry` dispatcher. |
| **GitNexus** | npm Registry | npm Global Prefix (`~/.npm-global`) | `npm --prefix "$HOME/.npm-global" install --global gitnexus@latest` | `gitnexus --version && gitnexus status` | **npm Global Exception**. Distributed via npm; compiles native `@ladybugdb/core` bindings into explicit user prefix. |
| **Newman** | Pinned JS Toolbelt | Isolated Toolchain | npm in isolated root | `newman --version` | **Isolated Toolchain Exception**. Retained at 6.2.2 in `~/.local/share/home-toolchain`. |
| **Bruno** | Pinned JS Toolbelt | Isolated Toolchain | npm in isolated root | `bru --version` | **Isolated Toolchain Exception**. Retained at 4.2.1 in `~/.local/share/home-toolchain`. |
| **Prime Agent** | Local Dev Exception | Local Node Entry | Manual / Pinned | `prime-agent --version` | **Local Dev Exception**. Observed Node.js entry point at `/opt/homebrew/bin/prime-agent` (version 0.9.8). Consult the source checkout's applicable repository policy before building or relinking; this runbook does not authorize those operations. |
| **Docker** | Docker Desktop | Docker Desktop / Cask | Desktop App Updater | `docker --version && docker compose version` | Official Docker Desktop application managing VM and Docker CLI. Protects persistent volumes. |
| **AgentMemory** | npm Global | npm Global Prefix | npm in global prefix | `curl -fsS http://localhost:3111/agentmemory/health` | **npm Global Exception**. Package `@agentmemory/agentmemory` pins `iii-engine` 0.22.1. |

---

## 2. Bootstrapping a New Mac

### Prerequisites
1. Install Apple Xcode Command Line Tools:
   ```bash
   xcode-select --install
   ```
2. Install Homebrew (if absent):
   ```bash
   # Download vendor installer to a secure temporary file with failure guard (subshell protects interactive shell)
   INSTALLER=$(mktemp -t homebrew-install.XXXXXX.sh)
   ( curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh -o "$INSTALLER" ) || { rm -f "$INSTALLER"; echo "Homebrew installer download failed" >&2; }

   # Inspect entire script before execution (never pipe directly to shell)
   [ -s "$INSTALLER" ] && less "$INSTALLER"
   ```
   Execute only after explicit operator review and confirmation:
   ```bash
   # Operator-confirmed execution:
   [ -s "$INSTALLER" ] && /bin/bash "$INSTALLER"
   rm -f "$INSTALLER"
   ```
3. Initialize Homebrew in the shell environment (`~/.zprofile`):
   ```bash
   # Dynamically detect and initialize Homebrew prefix
   if [ -x /opt/homebrew/bin/brew ]; then
     eval "$(/opt/homebrew/bin/brew shellenv)"
   elif [ -x /usr/local/bin/brew ]; then
     eval "$(/usr/local/bin/brew shellenv)"
   fi
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
   HOMEBREW_NO_AUTO_UPDATE=1 HOMEBREW_NO_INSTALL_CLEANUP=1 brew bundle check --file config/Brewfile --no-upgrade --verbose
   ```
   *Note: Native `brew bundle check` inspects unmet formulae and casks non-destructively. When missing casks (e.g. `codex`) are reported, exit code is 1 without mutating packages.*

3. Pre-Cutover Collision & Binary Shadowing Preflight:
   Before executing package installations or cask cutovers, the operator must inspect for existing binary collisions and shadowed executables:
   ```bash
   # Inspect multi-path resolution and symlink targets
   which -a codex bun
   ls -l $(which -a codex 2>/dev/null)
   ls -l $(which -a bun 2>/dev/null)
   ```
   *Collision Invariants & Safety Gates:*
   - **Identify Owning Authority**: The operator must identify the owning package manager, parent prefix, and backing symlink destination before touching existing binaries. For example, legacy npm-managed global symlinks or standalone vendor installs at Homebrew paths can conflict with cask or formula linkage; operators must inspect symlink destinations (`ls -l`) and active resolution (`which -a`) before executing installations.
   - **Never Force Overwrite**: NEVER use `brew install --cask --force <cask>` or un-scoped package removal to clobber existing binaries without understanding their origin and dependencies.
   - **Exact-Target Operator Approval**: Never run blind `npm uninstall -g` against an unverified default prefix. Duplicate binary removals require separate, exact-path operator review and explicit approval.
   - **Check Running Processes**: Confirm no active process or daemon holds the target binary before proceeding (`pgrep -f codex`, `pgrep -f bun`).

4. Install declared packages (operator review required before execution):
   ```bash
   # Note: --no-upgrade skips routine dependency checks for existing packages,
   # but dependency-driven installs or upgrades may still occur if required by new formulae.
   brew bundle install --file config/Brewfile --no-upgrade
   ```

---

## 3. Installing Native Tool Exceptions

For tools without maintained upstream Homebrew formulae or casks, apply standard vendor-supported installation methods:

### Qoder CLI (Standalone Script)
```bash
# Download vendor installer to a secure temporary file with failure guard (subshell protects interactive shell)
INSTALLER=$(mktemp -t qoder-install.XXXXXX.sh)
( curl -fsSL https://download.qoder.com/qodercli/install.sh -o "$INSTALLER" ) || { rm -f "$INSTALLER"; echo "Qoder installer download failed" >&2; }

# Inspect entire script before execution (never execute without inspection)
[ -s "$INSTALLER" ] && less "$INSTALLER"
```
Execute only after explicit operator review and confirmation:
```bash
# Operator-confirmed execution:
[ -s "$INSTALLER" ] && bash "$INSTALLER"
rm -f "$INSTALLER"
```
- Active binary: `~/.local/bin/qodercli`
- Dispatcher: `~/.qoder/entry/qoder` (added to PATH via `~/.zshrc`)
- Update command: `qoder update`

### GitNexus (npm Global)
On a fresh Mac or default Homebrew Node setup, global npm prefix may point to `/opt/homebrew` or a system directory. To maintain an unprivileged user directory and avoid colliding with Homebrew:
```bash
mkdir -p ~/.npm-global
npm --prefix "$HOME/.npm-global" install --global gitnexus@latest
```
- Active binary: `~/.npm-global/bin/gitnexus`
- Update command: `npm --prefix "$HOME/.npm-global" install --global gitnexus@latest`
- Verification: `gitnexus --version && gitnexus status`

### Newman & Bruno (Isolated Toolbelt)
```bash
mkdir -p ~/.local/share/home-toolchain
cd ~/.local/share/home-toolchain
# Install pinned dependencies deterministically from package-lock.json
npm ci --no-audit --no-fund
```
- Active binaries: `~/.local/share/home-toolchain/node_modules/.bin/newman`, `bru`

### Prime Agent (Local Dev Exception)
- Active entry point: `/opt/homebrew/bin/prime-agent` (Node.js script entry point; verified v0.9.8)
- Verification: `prime-agent --version`
- *Source Checkout Policy*: Consult the applicable repository instructions in `~/Developer/platform/prime-agent` before any build, link, or update. This runbook does not authorize unbounded builds, `npm link`, or self-update operations. Retain the observed Node.js runtime entry until an explicit, verified installation decision is made.

---

## 4. Maintenance Concurrency & Scheduled Runner Controls

Workstations run scheduled daily maintenance via `com.developer.workstation-daily-update.plist` (registered in the user GUI domain and idle when no update window is active). To prevent package manager lock collisions during manual maintenance, use native launchd controls:

### 1. Read-Only Status Preflight Check
Before touching runner state, inspect the exact service target and process table without mutations:
```bash
# Check service target registration and state (read-only)
# Note: Do not log or paste full launchctl print output, as it can expose environment variables/secrets
launchctl print gui/$(id -u)/com.developer.workstation-daily-update | grep -E "(state =|pid =|service =)"

# Check if an updater process is actively running (PID-only check to prevent leaking command arguments)
pgrep -f workstation-daily-update
```

### 2. Operator Approval & Manual Pause Procedure
Pausing the scheduled updater requires explicit operator approval before execution:
```bash
# Optional: Immediately stop running instance using legacy service label (not domain target)
launchctl stop com.developer.workstation-daily-update

# Persistently disable the LaunchAgent job schedule
launchctl disable gui/$(id -u)/com.developer.workstation-daily-update

# Unload the service domain target (do NOT swallow errors via 2>/dev/null || true)
launchctl bootout gui/$(id -u)/com.developer.workstation-daily-update
```
*Note on bootout error semantics:*
- If `launchctl bootout` reports that the service is already not running or not loaded (e.g. exit code indicating service absent), this is an expected no-op confirming absence.
- Any other error (e.g. permission or domain errors) indicates an unexpected condition that MUST NOT be masked or ignored.
*Note: Exporting `DISABLE_UPDATES=1` only affects sub-processes in the active shell and does NOT pause scheduled launchd jobs.*

### 3. Absence Verification Gate
Before starting manual package maintenance, verify service absence:
1. `launchctl print gui/$(id -u)/com.developer.workstation-daily-update` explicitly outputs `Could not find service "com.developer.workstation-daily-update" in domain for gui/...` (exact service-not-found diagnostic in the specified gui domain, not an arbitrary failure).
2. `pgrep -f workstation-daily-update` returns exit code 1 with no matching PIDs.
### 4. Resuming the Scheduled Runner
Only resume scheduled updates after verifying runner compatibility and confirming no active package collisions:
```bash
launchctl enable gui/$(id -u)/com.developer.workstation-daily-update
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.developer.workstation-daily-update.plist
```

---

## 5. Storage Hygiene & Docker Volume Protection

### Volume Preservation Contract
Routine disk cleanup commands must preserve persistent container data.
- **Distinguishing Logical Compose Keys vs Physical Engine Volume Names**:
  - `omniroute-data` is the logical Compose key; the physical Docker engine volume is `omniroute_omniroute-data` (mounted at `/app/data` containing SQLite WAL and database files).
  - `shb-scheduler-pgdata` is the logical Compose key; the physical Docker engine volume is `shb-schedule_shb-scheduler-pgdata` (mounted at `/var/lib/postgresql/data`).
  - Base images may also create anonymous 64-hex SHA mounts (e.g. at `/var/lib/postgresql`).
- **Inspection Command (Non-Destructive Metadata Inspection)**:
  ```bash
  # List all local Docker engine volumes
  docker volume ls
  # Inspect container mount mappings without reading database contents
  docker inspect <container-name> --format '{{range .Mounts}}{{.Type}}: {{.Name}} -> {{.Destination}}{{"\n"}}{{end}}'
  ```
- **Safe Docker Cleanup**:
  ```bash
  # Reclaims unused containers, networks, dangling images, and build cache
  # NEVER pass --volumes to avoid destroying anonymous or stateful volumes
  docker system prune -f
  ```
- **Protected Stateful Volumes**:
  - Protect ALL actual state volumes (`omniroute_omniroute-data`, `shb-schedule_shb-scheduler-pgdata`, etc.). Never assume exact unprefixed names.
- **Strict Prohibition**: Never run `docker system prune -a --volumes -f` or uncoordinated `docker compose down -v`. Passing `--volumes` permanently wipes persistent database volumes and anonymous data mounts.

---

## 6. Shell Environment & Secrets Protection

### PATH Precedence Policy
Interactive shells (`~/.zshrc`) evaluate paths in deterministic order. Homebrew prefix must be detected dynamically and take precedence over npm-global to prevent shadowed npm binaries from masking Homebrew formulae or casks:

```zsh
# 1. Native exception tools (standalone binaries)
export PATH="$HOME/.local/bin:$HOME/.qoder/entry:$PATH"

# 2. Dynamic Homebrew shell environment initialization
if [ -x /opt/homebrew/bin/brew ]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -x /usr/local/bin/brew ]; then
  eval "$(/usr/local/bin/brew shellenv)"
fi

# 3. Keg-only Homebrew client utilities (libpq for psql)
# libpq is keg-only on macOS; only add to PATH after Homebrew prefix detection
if [ -n "$HOMEBREW_PREFIX" ] && [ -d "$HOMEBREW_PREFIX/opt/libpq/bin" ]; then
  export PATH="$HOMEBREW_PREFIX/opt/libpq/bin:$PATH"
fi

# 4. npm global prefix (placed AFTER Homebrew to ensure Homebrew formulae/casks
# take precedence, avoiding shadowed npm packages like npm-managed codex masking Homebrew)
if [ -d "$HOME/.npm-global/bin" ]; then
  export PATH="$PATH:$HOME/.npm-global/bin"
fi
```
*Toolchain Precedence & Duplicate Resolution:* Placing Homebrew ahead of `~/.npm-global/bin` ensures that Homebrew-managed formulae and casks take precedence over any shadowed global npm packages. Always verify active binary resolution with `which -a <tool>` to ensure no non-authoritative duplicates mask system tools.

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
  # Check health endpoint with fail-on-error flag (root path '/' returns 404; check /agentmemory/health specifically)
  curl -fsS http://localhost:3111/agentmemory/health
  # Or inspect HTTP status and response body explicitly:
  curl -s -w "\nHTTP_STATUS: %{http_code}\n" http://localhost:3111/agentmemory/health
  ```
  *Health Contract:* A healthy AgentMemory instance responds with HTTP status `200` and JSON `{"status":"ok",...}`. HTTP `503` (degraded/standby) or connection failure MUST NOT be masked by silent `curl -s`.
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
   HOMEBREW_NO_AUTO_UPDATE=1 HOMEBREW_NO_INSTALL_CLEANUP=1 brew bundle check --file config/Brewfile --no-upgrade --verbose
   codex --version
   bun --version
   node --version && npm --version
   pnpm --version
   uv --version
   qoder --version
   gitnexus --version && gitnexus status
   newman --version
   bru --version
   prime-agent --version
   curl -fsS http://localhost:3111/agentmemory/health
   docker --version && docker compose version
   ```
5. Confirm zero duplicate binary resolution via `which -a <tool>`.
   *Note on Brewfile Casks & Formulae:* On any target Mac, `brew bundle install` provisions declared casks (including `cask "codex"`) and formulae (including `brew "bun"`). Verify binary receipts (`brew list --cask`, `brew list --formula`) and active paths (`which -a codex bun`) to confirm clean Homebrew resolution without uncoordinated package manager duplicates.
6. Verification Semantics:
   A unified verification PASS indicates that the read-only inspection protocol was executed successfully and declared manifests align without tool invocation errors. Any future host mutations, duplicate removals, or service changes require explicit operator authorization and verified read-back checks.
