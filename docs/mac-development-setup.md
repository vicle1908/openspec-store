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
| **Qoder** | Standalone Script | Vendor Standalone | `~/.qoder/entry update` / `qoder update` | `qoder --version` | **Standalone Exception**. Managed via `~/.qoder/entry/qoder` dispatcher and `~/.local/bin/qodercli`. |
| **GitNexus** | npm Registry | npm Global Prefix (`~/.npm-global`) | `npm --prefix "$HOME/.npm-global" install --global gitnexus@latest` | `gitnexus --version && gitnexus status` | **npm Global Exception**. Distributed via npm; compiles native `@ladybugdb/core` bindings into explicit user prefix. |
| **OpenSpec** | npm Registry | npm Global Prefix (`~/.npm-global`) | `npm --prefix "$HOME/.npm-global" install --global @fission-ai/openspec` | `openspec --version` | **npm Global Authoritative Owner**. Governed under `~/.npm-global/bin/openspec`. |
| **Newman** | Homebrew Formula | `brew "newman"` | `brew upgrade newman` | `newman --version` | **Homebrew Formula**. Authoritative package and update owner at `/opt/homebrew/bin/newman`. |
| **Bruno** | Pinned JS Toolbelt | Isolated Toolchain | npm in isolated root | `bru --version` | **Isolated Toolchain Exception**. Active verified at 4.2.1 via `~/.local/bin/bru -> ~/.local/share/home-toolchain/node_modules/.bin/bru` (alongside `yaml-language-server` 2.0.0, `newman-reporter-htmlextra` 1.23.1, and `pyright` 1.1.414). |
| **Muse Code** | Official Cask | `cask "muse-code"` | `brew upgrade --cask muse-code` | `muse --version` | **Official Homebrew Cask**. Meta Muse Code CLI assistant installed via Homebrew Cask. |
| **Qwen Code** | Homebrew Formula | `brew "qwen-code"` | `brew upgrade qwen-code` | `qwen --version` | **Homebrew Formula**. Qwen Code CLI installed via `qwen-code` formula. |
| **Herdr** | Homebrew Formula | `brew "herdr"` | `brew upgrade herdr` | `herdr --version && herdr status` | **Homebrew Formula (Package) + Host-Local LaunchAgent**. Package owned by `brew "herdr"` (`v0.9.5+`; formula has no `service do` block). Daemon supervised via host-local `~/Library/LaunchAgents/homebrew.mxcl.herdr.plist`. |
| **Oh My Pi (OMP)** | Homebrew Tap Formula | `brew "can1357/tap/omp"` (`brew-formula`) | `brew upgrade can1357/tap/omp` | `omp --version` | **Homebrew Tap Formula**. Active binary verified at `/opt/homebrew/bin/omp` (`can1357/tap/omp`, `brew-formula`). |
| **Hermes Agent** | Standalone Installer | Vendor Standalone | `hermes update` | `hermes --version` | **Standalone Exception**. Standalone runtime in `~/.hermes` and `~/.local/bin/hermes-agent`. |
| **Notion CLI** | Standalone Binary | Vendor Standalone | `ntn update` | `ntn --version` | **Standalone Exception**. Managed standalone binary in `~/.local/bin/ntn`. |
| **Google Workspace CLI** | Homebrew Formula | `brew "googleworkspace-cli"` | `brew upgrade googleworkspace-cli` | `gws --version` | **Homebrew Formula**. Google Workspace CLI (`gws`). |
| **Ollama** | Homebrew Formula | `brew "ollama"` | `brew upgrade ollama` | `ollama --version` | **Homebrew Formula**. Local LLM runner and model server. |
| **Prime Agent** | Local Dev Exception | Local Node Entry | Manual / Pinned | `prime-agent --version` | **Local Dev Exception**. Observed Node.js entry point at `/opt/homebrew/bin/prime-agent` (version 0.9.8). Consult the source checkout's applicable repository policy before building or relinking; this runbook does not authorize those operations. |
| **Docker** | Docker Desktop | Docker Desktop / Cask | Desktop App Updater | `docker --version && docker compose version` | Official Docker Desktop application managing VM and Docker CLI. Protects persistent volumes. |
| **AgentMemory** | npm Global | npm Global Prefix (`~/.npm-global`) | npm in global prefix | `agentmemory status` | **npm Global Exception**. Package `@agentmemory/agentmemory` (v0.9.30) pins `iii-engine` 0.22.1. Native health check verified healthy via `agentmemory status`. |

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
- **Global npm Audit Semantics (`EAUDITGLOBAL`)**: During `npm update -g`, `Arborist.reify()` submits a quick audit of `~/.npm-global/lib/node_modules` and prints `run npm audit fix`, whereas `npm audit -g` fails by npm design with `EAUDITGLOBAL`. Never run `npm audit fix` in `~/Developer` (or `$HOME`); global packages (`@agentmemory/agentmemory@0.9.30` and `happy@1.2.5`, which carry upstream transitive advisories) must be audited per-package in isolated temporary lockfiles, and `~/.npm-global/bin` / `~/.npm-global/lib/node_modules` must remain free of retired `.bin-HASH` dot-symlinks and empty `@scope` directories.


### Maximized Permissive `~/.npmrc` & `~/.bunfig.toml` Configuration Baseline
- **`~/.npmrc` (`mode 0600`, 13 verified `npm@11.20.0` keys, zero stderr warnings)**:
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
- **`~/.bunfig.toml` (`mode 0600`)**:
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

### Newman & Bruno (Isolated Toolbelt)
```bash
mkdir -p ~/.local/share/home-toolchain
cd ~/.local/share/home-toolchain
# Install pinned dependencies deterministically from package-lock.json
npm ci --no-audit --no-fund
```
- Active binaries: `~/.local/share/home-toolchain/node_modules/.bin/bru`, `yaml-language-server`, `newman-reporter-htmlextra` (symlinked into `~/.local/bin`)

#### Active vs. Declared Target State

1. **Newman (v6.2.3)**:
   - **Authoritative Owner**: Homebrew Formula (`brew "newman"`).
   - **Active Host Resolution**: `/opt/homebrew/bin/newman` (v6.2.3 in Cellar). Authoritative package and update owner.
   - **De-duplication**: `newman` is not declared as a direct dependency in `~/.local/share/home-toolchain/package.json` (`~/.local/share/home-toolchain/node_modules/newman` v6.2.3 is installed automatically only as an unlinked peer dependency of `newman-reporter-htmlextra@1.23.1`), leaving `/opt/homebrew/bin/newman` as the single authoritative binary on `$PATH`.
   - **Read-Only Verification**:
     ```bash
     which -a newman
     /opt/homebrew/bin/newman --version
     ```
2. **Bruno (v4.2.1 Active) & Isolated Toolbelt (`~/.local/share/home-toolchain`)**:
   - **Declared & Active Target**: `@usebruno/cli` 4.2.1 (and `yaml-language-server` 2.0.0, `newman-reporter-htmlextra` 1.23.1, `pyright` 1.1.414, plus peer `newman` 6.2.3).
   - **Active Host Resolution**: `~/.local/bin/bru` -> `~/.local/share/home-toolchain/node_modules/.bin/bru` (v4.2.1), and `~/.local/bin/yaml-language-server` -> `~/.local/share/home-toolchain/node_modules/.bin/yaml-language-server` (v2.0.0).
   - **Read-Only Verification**:
     ```bash
     which -a bru
     realpath ~/.local/bin/bru
     /Users/androidteam/.local/share/home-toolchain/node_modules/.bin/bru --version
     /Users/androidteam/.local/bin/bru --version
     /Users/androidteam/.local/bin/yaml-language-server --version
     ```
   - **Parent Decision & Operator Gate**: Package updates in `~/.local/share/home-toolchain` require operator-approved lockfile updates (`npm update`). In-place package mutations without explicit approval are forbidden.
### Prime Agent (Local Dev Exception)
- Active entry point: `/opt/homebrew/bin/prime-agent` (Node.js script entry point; verified v0.9.8)
- Verification: `prime-agent --version`
- *Source Checkout Policy*: Consult the applicable repository instructions in `~/Developer/platform/prime-agent` before any build, link, or update. This runbook does not authorize unbounded builds, `npm link`, or self-update operations. Retain the observed Node.js runtime entry until an explicit, verified installation decision is made.

### Google Workspace CLI (`gws`)

- **Authoritative Owner**: Homebrew Formula (`brew "googleworkspace-cli"`).
- **Active Binary**: `/opt/homebrew/bin/gws`
- **Verification**: `gws --version && gws auth status`
- **Authentication & Encryption Health**:
  When `gws auth status` reports `"encryption_valid": false` on `~/.config/gws/credentials.enc`, run:
  ```bash
  gws auth login
  ```
  to re-authenticate and re-encrypt the stored credentials.

## 4. Maintenance Concurrency & Scheduled Runner Controls

Workstations run scheduled daily maintenance via `com.developer.workstation-daily-update.plist` (registered in the user GUI domain under `/opt/homebrew/opt/python@3.15/Frameworks/Python.framework/Versions/3.15/Resources/Python.app/Contents/MacOS/Python`, `CFBundleIdentifier = org.python.python`, `client_type = 0` so scheduled runs inherit Full Disk Access across Python upgrades), which delegates to the durable DBOS workflow `shb-schedule run-now workstation-daily-update` with native fallback.

### 0. Durable Update Architecture & Workflow Steps
The update engine executes as a durable, 9-step transactional pipeline governed by `shb-schedule` (`~/.shb/schedules/workstation-daily-update.yaml`, schedule `0 8 * * *` Asia/Ho_Chi_Minh, timeout 3600s):
1. **Pre-flight Power & Lock Check**: Validates AC power (`pmset -g batt`), verifies 0 lockfile contentions, and respects `DISABLE_UPDATES`.
2. **Homebrew Maintenance**: Upgrades formulae and casks non-interactively without `sudo`, inspecting active GUI process locks (`pgrep -x`) before cask upgrades, then executes `sign_agent_binaries()` to heal missing/broken `/opt/homebrew/bin/goose` symlinks (`brew link --overwrite block-goose-cli`) and re-sign `Python.app` (`org.python.python`), `python3`, and `goose` with `Developer Agent Code Signing` (`H"65340d85afd298131c682d8463087891292a2b59"`).
3. **Mac App Store (`mas`)**: Discovers outdated App Store apps via `mas outdated` and skips actively running apps without terminating sessions.
4. **Bun Global Ecosystem**: Single-owner Homebrew authority (`brew upgrade bun` in Stage 1; never `bun upgrade`). Ensures `~/.bun/install/global` (`mode 0700`), `~/.bun/install/global/package.json` (`mode 0600`), and `~/.bun/install/global/bun.lock` (`mode 0600`) exist, running `bun update -g --save-text-lockfile` only when global dependencies are declared so `bun pm ls -g` always exits `0`.
5. **Python / uv Standalone Tools & Managed Runtime**: Dynamically queries `uv tool list`, upgrades each managed venv (`browser-use`, `graphifyy`, `infinity-emb`, `tavily-cli` on `uv`-managed Python `3.15.1`), and executes `uv python upgrade`.
6. **Global NPM Packages**: Discovers outdated tools via `npm outdated -g --json`, shielding pinned coding agents (`codex`, `claude`, `pi`, `kilo`).
7. **Coding Agent CLIs**: Executes time-bounded updates (900s) from static maps with pre/post-update version probes and post-update `sign_agent_binaries()`.
8. **Remote Skills Refresh & Parity**: Runs `skills update -y` (1800s bound), automatically prunes unallowlisted `~/Developer/data/skills` and `~/Developer/agent/skills` directories (in `step_skills_refresh()`, `workstation-daily-update.sh`, and `sync-workspace-agent-skills.py`), and verifies symlink parity across `.agents/skills/`.
9. **Integrity, Native TCC Provenance & Strict Store Validation**: Executes `scripts/tcc_provenance.py` (`verify_tcc_provenance()` evaluating role-scoped TCC grants and stored `csreq` signatures via `Security.framework` strictly read-only `mode=ro`), reconciles script copy provenance against `script-provenance-manifest.tsv`, checks snapshot store growth bounds, reconciles `authority_reconciliation` against `manifest_reconciliation` via `has_unaligned_authority_drift()` (`Reconciled Authority Status`) and agent CLI coverage, and runs `openspec validate --all --store openspec-store`. Any Darwin TCC verification error/drift, reporter failure, or unaligned inventory drift propagates to non-success (`DEGRADED` / `PARTIAL` in `shb-schedule`, nonzero exit in `workstation-daily-update.sh`).
Every run persists an immutable JSON telemetry artifact to `~/Developer/data/updates/YYYY-MM-DD.json` (mode `0600`). If degraded or failed, alert payloads are dispatched to the Telegram channel (`Home` `88d95325258b`).

To prevent package manager lock collisions during manual maintenance, use native launchd controls:

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
- Use `stat -L -f '%Mp%Lp %N'` when auditing MCP/provider configuration file permissions so symlinked paths (like `~/.gemini/antigravity/mcp_config.json`) resolve to their target file permissions (`0600`) rather than the symlink inode mode (`0777`).

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
  # Check health via native authenticated CLI:
  agentmemory status
  ```
  *Health Contract:* The native CLI authenticates with the internal client secret and queries health, session counts, and graph status. Direct curl requests to `/agentmemory/health` require bearer authentication via `Authorization: Bearer <secret>`.
- If port 49134 or 3111 is occupied by an orphaned or incompatible engine process, operator runs `agentmemory stop --force` to clear the conflicting engine before restarting the launchd service via `launchctl kickstart -k gui/$(id -u)/com.agentmemory.server`.
- The local SQLite WAL database must remain intact with zero schema mutations.

#### Snapshot Store Integrity & Repack Maintenance
- **Routine Integrity Check**: Execute `git -C ~/.agentmemory/snapshots fsck --connectivity-only` for routine `<1s` snapshot store checks vs full `git fsck --no-dangling` during repack maintenance windows.
- **Repack Maintenance**: When loose objects accumulate, run the owner repack command:
  ```bash
  git -C ~/.agentmemory/snapshots -c pack.windowMemory=1g -c pack.threads=2 repack -a -d --window=10 --depth=10 && git -C ~/.agentmemory/snapshots prune-packed
  ```
  Follow with `git -C ~/.agentmemory/snapshots fsck --no-dangling` during the maintenance window to confirm complete pack integrity.


### Herdr Multiplexer Daemon, Native TCC Provenance & HerdrChat Notifier Supervision
- **Package Ownership vs. Host-Local Service Supervision (`homebrew.mxcl.herdr`)**:
  - **Package Authority**: Herdr is installed and upgraded via Homebrew formula `brew "herdr"` (`brew upgrade herdr`). Self-update commands (`herdr update`, `herdr update --handoff`) remain disabled so `~/.local/bin/herdr` never shadows `/opt/homebrew/bin/herdr` (standalone installer reference: `https://herdr.dev/install.sh`).
  - **Host-Local LaunchAgent**: The upstream `herdr` Homebrew formula has no `service do` block, so `brew services` cannot create, manage, or restart the daemon. Instead, supervision is owned by the host-local LaunchAgent `~/Library/LaunchAgents/homebrew.mxcl.herdr.plist`, which runs `/opt/homebrew/opt/herdr/bin/herdr server` over Unix domain socket `~/.config/herdr/herdr.sock`.
  - **Staged Disk `PATH` vs. Live Process `PATH` & Destructive Restart Gate**:
    - Setting `EnvironmentVariables.PATH` (`$HOME/.local/bin:$HOME/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin`) in `~/Library/LaunchAgents/homebrew.mxcl.herdr.plist` and validating with `plutil -lint` establishes **staged disk configuration only**.
    - Running `herdr server reload-config` reloads `~/.config/herdr/config.toml` (`onboarding = false`, `[session] resume_agents_on_restore = true`), **not** the `launchd` job definition or an existing server process's environment (a running `herdr server` keeps its launch-time `PATH` until the `launchd` job is reloaded).
    - **Operator Approval Gate**: Stopping or reloading `homebrew.mxcl.herdr` (`launchctl bootout`, `launchctl kickstart -k`, or `herdr server stop`) terminates active pane processes. Preserving layout metadata in `~/.config/herdr/session.json` is not lossless process preservation. When active panes are preserved, live `PATH` activation remains an open operator-gated maintenance step; applying it requires explicit operator approval after preserving active agent sessions, followed by verifying the replacement PID's live `PATH` (`ps eww -p <pid>`) and `herdr status`.
- **Native TCC Provenance Verifier (`scripts/tcc_provenance.py`) & Permission Roles**:
  - Both `shb-schedule` (`verify_tcc_provenance()` in `workstation_update.py`) and `workstation-daily-update.sh` delegate to the central read-only helper `scripts/tcc_provenance.py`, which queries `/Library/Application Support/com.apple.TCC/TCC.db` strictly read-only (`mode=ro`).
  - **Stored `csreq` Code-Signing Verification**: Path strings and `auth_value = 2` alone are insufficient. For every required identity and service, the verifier checks that the resolved executable exists and is executable (`os.X_OK`), matches the expected `client_type` (`1` for absolute paths, `0` for bundle identifiers), holds `auth_value = 2`, and satisfies the record's stored `csreq` blob via native macOS `Security.framework` APIs (`SecRequirementCreateWithData`, `SecStaticCodeCreateWithPath`, `SecStaticCodeCheckValidity`) with deterministic `CFRelease` cleanup. Both ad-hoc linker-signed `CDHash` requirements (which change on `brew upgrade` or same-path binary replacement) and certificate-signed designated requirements are evaluated. Missing/malformed `csreq`, denied services, wrong `client_type`, missing executables, unresolved required binary names, or empty target sets report `DRIFT`; Darwin missing/unreadable/corrupt `TCC.db` or missing/malformed helper output reports `ERROR` (never a `SKIPPED` success fallback; only non-Darwin platforms return `SKIPPED`).
  - **Role-Scoped Permission Policy (Dynamic Runtime Resolution, No Hardcoded Cellar Versions)**:
    - *Canonical Agent CLIs (`omp`, `node`, `opencode`, `goose`, `claude`, `kimi`, `herdr`)*: Resolved dynamically from `$PATH` to active Mach-O `realpath` (`client_type = 1`); all seven require `kTCCServiceAccessibility` and `kTCCServiceScreenCapture`.
    - *Herdr PTY Supervisor & OMP Host Automation (`herdr`, `omp`)*: Additionally require `kTCCServiceSystemPolicyAllFiles` (Full Disk Access). Because `herdr server` owns the PTY master/slave descriptors for managed panes (`HERDR_ENV=1`), macOS `launchd` attributes child shells and coding agents inside Herdr panes to `herdr`'s `responsible path`, and `omp` performs host computer-use and read-only system `TCC.db` audits. Full Disk Access and `TCC.db` rows do not imply root/SIP bypass or blanket AppleEvents authorization to arbitrary receivers (in-pane `osascript` verification tests `System Events` specifically).
    - *Shared Host Python Automation (`python3` active `realpath` `client_type = 1` and resolved framework bundle `org.python.python` `client_type = 0`)*: Derived dynamically from the active `python3` executable (`.../Resources/Python.app/Contents/Info.plist` when framework-backed) across `kTCCServiceAccessibility`, `kTCCServiceScreenCapture`, and `kTCCServiceSystemPolicyAllFiles`. **Role Classification**: These three-service Python grants are retained as **shared host automation privileges** for workstation automation scripts — they are **not** required by `herdr-notifier.py`, which only polls `herdr api snapshot`, reads user-owned transcript files, and sends outbound HTTP push notifications. Existing grants are preserved unless revocation is separately authorized.
  - **Supported macOS Consent Behavior (No Permanent Reminder Suppression Guarantee)**:
    - Prior far-future timestamps (`3026-01-01 00:00:00 +0000`) in `~/Library/Group Containers/group.com.apple.replayd/ScreenCaptureApprovals.plist` are recorded strictly as **historical unsupported private state** and left untouched. Reading back private plist values proves neither `replayd` runtime interpretation nor permanent reminder suppression, and Apple's `forceBypassScreenCaptureAlert` restriction applies only to MDM-managed profiles. No recurring plist-rewrite job or consent-bypass automation is used; standard macOS operator consent handling governs any future system reminder.
    - **Mandatory Plist `<date>` (`NSDate`) Serialization Invariant (`com.apple.replayd` Crash Prevention)**: All timestamp keys (`kScreenCapturePrivacyHintDate`, `kScreenCaptureApprovalLastAlerted`, `kScreenCaptureApprovalLastUsed`) in `~/Library/Group Containers/group.com.apple.replayd/ScreenCaptureApprovals.plist` MUST be serialized as native plist `<date>` (`NSDate` / `datetime.datetime` in Python `plistlib`), never `<string>` (`__NSCFString`). When serialized as `<string>`, `/usr/libexec/replayd` (`-[SCAlertStatsManager requirePrivacyHintWithCanonicalBundleID:auditToken:]`) invokes `-[NSDate timeIntervalSinceDate:]` on `__NSCFString`, crashing `replayd` with `NSInvalidArgumentException: -[__NSCFString timeIntervalSinceReferenceDate]: unrecognized selector` (`SIGABRT`) and causing `launchd` to throttle `gui/502/com.apple.replayd` (`minimum runtime = 1200`), which blocks AnyViewer (`CGDisplayStreamCreateWithDispatchQueue` / `SLSDisplayStreamCreateProxying`) on the main thread and crashes RealVNC `vncagent` (`+[SCShareableContent createShareableContentWithWindows:...]`).
    - **Remote Desktop TCC Provenance & Legacy Bundle Classification**: Active remote desktop servers (`com.aomei.mac.anyviewer` at `/Applications/AnyViewer.app`, `com.teamviewer.TeamViewer` at `/Applications/TeamViewer.app`, `com.realvnc.vncagent` and `/Library/vnc/vncagent` at `/Library/vnc/RealVNC Server Agent.app`, and `com.realvnc.vncserver_service` at `/Applications/RealVNC/RealVNC Server.app`) satisfy `auth_value = 2` and `SecStaticCodeCheckValidity = 0`, whereas historical `TCC.db` rows for `com.realvnc.vncconnect` and `com.realvnc.vncviewer` match no installed bundle on disk (`/Library/vnc/RealVNC Server.app` uses `com.realvnc.vncserverui` and `/Applications/RealVNC Connect Viewer.app` uses `com.realvnc.rvncconnect`) and are classified as unverified stale rows.
- **HerdrChat Companion Notifier (`dev.herdr.herdrchat-notifier`) & Preview Privacy**:
  - Supervised via `~/Library/LaunchAgents/dev.herdr.herdrchat-notifier.plist` executing `/opt/homebrew/bin/python3 ~/.local/share/herdrchat/herdr-notifier.py` (`WATCHER_VERSION = 5`).
  - **Polling & Trigger States**: Polls `herdr api snapshot` every **3 seconds** by default (`POLL_SECONDS = 3`) and notifies on `NOTIFY_ON = "blocked,done"` state transitions.
  - **Relay-Default Delivery vs. Optional Direct APNs**: By default (`HERDRCHAT_RELAY_URL = "https://push.herdrchat.cobanov.dev/v1/push"`), push payloads are sent through the third-party HerdrChat relay (which holds the App Store build's APNs signing key). Direct APNs delivery (`api.push.apple.com`) is optional and used only when `APNS_KEY_ID`, `APNS_TEAM_ID`, and `APNS_KEY_PATH` are configured for a self-signed build.
  - **Transcript Preview Privacy (`NOTIFY_PREVIEW`)**: By default (`NOTIFY_PREVIEW = "1"`), the notifier reads recent lines from the session's JSONL transcript (`~/.claude/projects/`, `~/.codex/sessions/`, etc.) and includes a message snippet in the notification body sent to the relay or APNs. Set `NOTIFY_PREVIEW=0` in `~/.config/herdrchat/apns.env` to transmit only workspace/chat labels and state transitions without transcript snippets.
- **Built-in Agent Integrations (Installed vs. Activated) & Official CLI Surface**:
  - **16 Installed Integrations (`herdr integration install <target>`)**: Installed for all 16 provisioned coding agent directories (`pi`, `omp`, `claude`, `codex`, `copilot`, `devin`, `droid`, `kimi`, `opencode`, `kilo`, `hermes`, `qodercli`, `qwen`, `cursor`, `antigravity-cli`, `grok`), while leaving unprovisioned optional roots (`~/.letta`, `~/.mastracode`) absent and keeping `PI_CODING_AGENT_DIR` / `PI_CONFIG_DIR` unset so `pi` (`~/.pi/agent/extensions/herdr-agent-state.ts`) and `omp` (`~/.omp/agent/extensions/herdr-omp-agent-state.ts`) remain isolated.
  - **5 Lifecycle Reporters vs. 11 Session-Only Hooks**: Only **five** integrations (`pi`, `omp`, `kimi`, `opencode`, `kilo`) report live lifecycle state transitions (`herdr agent-state`) in addition to session identity; the other 11 installed hooks record session resume references while relying on Herdr's screen-based state detection.
  - **Installation vs. Runtime Activation**: `herdr integration status` reporting `current` verifies installed hook files on disk only — existing running agent processes must load hooks on a new session/startup event before reporting live state, and session restoration remains unverified until exercised.
  - **Official Skill & CLI Subcommands**: Synchronized via `config/claude-user-skill-manifest.txt`, `config/codex-user-skill-manifest.txt`, and `python3 scripts/sync-workspace-agent-skills.py`. Use the installed subcommand surface (`herdr pane split`, `herdr pane run`, `herdr pane send`, `herdr pane capture`, `herdr pane wait`, `herdr agent-state`, `herdr api snapshot`, `herdr server reload-config`), gated by `test "${HERDR_ENV:-}" = 1` when orchestrating panes from inside a Herdr session.

### Ponytail Official Agent Skills (Skills-Only Installation Tier & Snapshot Acceptance)
- **Canonical Source & User-Scope Manifest Fanout (`DietrichGebert/ponytail`)**:
  - The six official Ponytail skills (`ponytail`, `ponytail-review`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help`) reside as unmodified upstream copies under `/Users/androidteam/Developer/.agents/skills/ponytail*/SKILL.md` (`142–371` YAML-decoded UTF-8 description bytes; `141–370` trimmed bytes).
  - Selected user-scope symlinks are reconciled by `python3 /Users/androidteam/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py` from `config/codex-user-skill-manifest.txt` (`~/.agents/skills/ponytail*`), `config/claude-user-skill-manifest.txt` (`~/.claude/skills/ponytail*`), and `config/hermes-user-skill-manifest.txt` (`~/.hermes/skills/ponytail*`), while preserving existing Grok (`~/.grok/skills/ponytail*`), Goose (`~/.config/goose/skills/ponytail*`), and unrelated Hermes skills.
- **Host-Accurate Standalone Invocation Syntax**:
  - **Codex CLI**: Invoke as standalone skills without a plugin namespace prefix: `$ponytail`, `$ponytail-review`, `$ponytail-audit`, `$ponytail-debt`, `$ponytail-gain`, `$ponytail-help` (do **not** use the plugin-namespaced `$ponytail:ponytail` syntax shown in upstream's plugin-oriented `ponytail-help/SKILL.md`).
  - **Claude Code & Hermes**: Loaded on demand through each host's verified user-scope skill catalog (`~/.claude/skills/ponytail*` and `~/.hermes/skills/ponytail*`). In hosts exposing slash skill commands, `/ponytail*` invokes the corresponding skill; do not assume identical slash-command parity across hosts that load skills through catalog selection rather than slash commands.
- **Omitted Plugin & Extension Tier Features**:
  - Because Ponytail is installed in the standalone **skills-only tier** (keeping canonical `SKILL.md` files unmodified and Claude Code's installation authority unchanged), plugin/extension features referenced in upstream `ponytail-help/SKILL.md` are intentionally inactive on this workstation:
    - Automatic session-start hook activation (`PONYTAIL_DEFAULT_MODE`, `~/.config/ponytail/config.json`)
    - Claude statusline band (`/ponytail band`, `ponytail-statusline.sh`)
    - Pre-prompt regex mapper (`ponytail-map.js`)
    - Pi/OMP extension (`pi-extension/index.js`)
    - Plugin marketplace updater (`/plugin update ponytail`, `/plugin marketplace update ponytail`)
- **Single-Writer Lockfile & `--accept-refresh` Post-Update Workflow**:
  - `/Users/androidteam/Developer/skills-lock.json` is the sole writable project registry mutated by `/opt/homebrew/bin/skills` (`npx skills`). `/Users/androidteam/Developer/.agents/skills-lock.json` is a generated read-only compatibility replica published only after acceptance verification succeeds.
  - Bounded recoverable snapshots are maintained at `/Users/androidteam/Developer/.agents/.skill-snapshots/{current,previous}/`.
  - Standard commands (matching `python3 scripts/sync-workspace-agent-skills.py --help`):
    ```bash
    # Reconcile declared user-scope symlinks (Codex, Claude, Hermes)
    python3 /Users/androidteam/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py

    # Initialize accepted snapshots and publish .agents/skills-lock.json
    python3 /Users/androidteam/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py --bootstrap-snapshot

    # Refresh upstream skills via official Skills CLI, then verify and accept
    (cd /Users/androidteam/Developer && /opt/homebrew/bin/skills update -y)
    python3 /Users/androidteam/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py --accept-refresh

    # Non-mutating parity, YAML frontmatter budget, and snapshot digest check
    python3 /Users/androidteam/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py --check

    # Restore mutated registry-tracked skills and root lockfile from current snapshot after a failed refresh
    python3 /Users/androidteam/Developer/platform/openspec-store/scripts/sync-workspace-agent-skills.py --recover-from-snapshot
    ```
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
   herdr --version && herdr status && herdr integration status
   qoder --version
   gitnexus --version && gitnexus status
   which -a newman bru
   /opt/homebrew/bin/newman --version
   /Users/androidteam/.local/bin/bru --version
   /Users/androidteam/.local/bin/yaml-language-server --version
   /Users/androidteam/.local/bin/newman-reporter-htmlextra --version
   prime-agent --version
   agentmemory status
   docker --version && docker compose version
   ```
5. Confirm zero duplicate binary resolution via `which -a <tool>`.
   *Note on Brewfile Casks & Formulae:* On any target Mac, `brew bundle install` provisions declared casks (including `cask "codex"`) and formulae (including `brew "bun"`). Verify binary receipts (`brew list --cask`, `brew list --formula`) and active paths (`which -a codex bun`) to confirm clean Homebrew resolution without uncoordinated package manager duplicates.
   *Note on Newman & Bruno Toolchain State:* Active `newman` resolves to Homebrew Formula `/opt/homebrew/bin/newman` (6.2.3). Active `bru` resolves via `~/.local/bin/bru` to isolated `~/.local/share/home-toolchain/node_modules/.bin/bru` at 4.2.1 (alongside `yaml-language-server` at 2.0.0).
6. Verification Semantics:
   A unified verification PASS indicates that the read-only inspection protocol was executed successfully and declared manifests align without tool invocation errors. Any future host mutations, duplicate removals, or service changes require explicit operator authorization and verified read-back checks.
