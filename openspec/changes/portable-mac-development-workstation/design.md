# Design

## Context

See `proposal.md` for motivation. The workstation environment currently relies on several automation scripts with partially overlapping scopes:
- A read-only inventory reporter at `platform/openspec-store/scripts/inventory-workstation-toolchain.py`
- A shared updater registry at `platform/openspec-store/scripts/toolchain_updater_registry.py`
- A scheduled daily maintenance runner at `scripts/workstation-daily-update.sh`
- An ecosystem knowledge synchronization script at `scripts/knowledge-refresh/sync-notion-knowledge.sh`

Live inspection identified the following architectural and operational constraints:
1. **Active Binaries Split Across Multiple Roots**: Executables resolve across `/opt/homebrew`, `~/.npm-global`, `~/.local`, `~/.qoder`, and the isolated toolchain at `~/.local/share/home-toolchain`. Several CLIs (`codex`, `qoder`, `gitnexus`, `opencode`) have colliding or shadowed copies across these roots.
2. **PATH Inversion Between Interactive and Scheduled Environments**: `workstation-daily-update.sh` places `${HOME}/.local/bin` at the end of `PATH`, whereas interactive zsh profiles and `sync-notion-knowledge.sh` place it ahead of system and Homebrew bins. This causes discrepancy in CLI resolution (e.g. `ntn` or vendor wrappers).
3. **Shell Startup Latency**: Startup time is dominated by un-cached `compinit` completion audits and synchronous NVM initialization, rather than lean core runtime loading.
4. **Swallowed Errors in Knowledge Sync**: In `sync-notion-knowledge.sh`, `ntn pages edit` executes under `|| true` and immediately advances the document SHA-256 in `notion-sync-manifest.json` even when the edit fails. Additionally, `--dry-run` mutates the manifest upon discovering section IDs and creates logs, violating read-only guarantees.
5. **AgentMemory Runtime Mismatch**: An orphaned legacy `iii` engine process on an unexpected port causes health check divergence, while the installed `agentmemory` package (0.9.30) expects `iii-engine` 0.22.1.
6. **Docker Volume Data Risk**: Unscoped pruning commands (`docker system prune --volumes` or `docker compose down -v`) delete persistent named volumes (such as OmniRoute's SQLite WAL database volume `omniroute_data`).

## Goals / Non-Goals

**Goals:**

- Establish strict multi-root governance separating central planning in `platform/openspec-store` from external execution gates on the host filesystem and remote services.
- Author a declarative, versioned workstation toolchain manifest backed by JSON Schema, accompanied by tool-native layered profiles (`Brewfile`, `npm-global-tools.json`, `uv-tools.json`).
- Render concrete absolute paths into LaunchAgent plist templates at bootstrap time to account for launchd's lack of `$HOME` expansion.
- Establish one authoritative installation owner and update authority per tool, with pre- and post-mutation native smoke checks.
- Enforce a five-point check before authorizing the removal of any duplicate installation.
- Provide measurable shell startup optimization based on repeated cold/warm medians and variance, retaining system Node as default and deferring NVM.
- Guarantee persistent Docker named volumes are protected from routine cleanup.
- Restore AgentMemory health via `/agentmemory/health` with bounded watchdog parameters and idempotent decision seeding.
- Implement fail-closed, write-receipt gated Notion synchronization that retries cleanly on offline failure and keeps `--dry-run` strictly read-only.

**Non-Goals:**

- No automated package upgrades, removals, or service changes during planning.
- No cross-machine migration of credentials, signed-in states, private keys, Docker volume data, or raw SQLite WAL databases.
- No replacement of OpenSpec, Homebrew, npm, uv, or Docker Desktop.
- No creation of an overarching custom dotfile framework or background daemon.
- No destructive filesystem cleanup without explicit exact-path authorization.

## Decisions

### 1. Central Authoring Store vs External Execution Gates (Multi-Root Governance)

To prevent unauthorized filesystem mutations and concurrent session contamination:
- **Authoring Root**: All schemas, manifests, profile templates, migration runners, and verification suites SHALL be authored within `/Users/androidteam/Developer/platform/openspec-store`. Central `/opsx:apply` `allowedEditRoots` covers `openspec-store` ONLY.
- **External Execution Gates**: Deploying scripts to `~/Developer/scripts/`, modifying user dotfiles (`~/.zshrc`, `~/.zshenv`), writing LaunchAgents (`~/Library/LaunchAgents/`), mutating package prefixes (`/opt/homebrew`, `~/.npm-global`), or calling external APIs (Notion, AgentMemory) are modeled as **External Execution and Evidence Gates**.
- **External Execution Packet**: Each external action MUST produce an audit packet containing:
  - Target root and destination path
  - Source commit identity and script hash
  - Bounded command and parameters
  - Timestamps, exit code, stderr capture
  - Item counts (processed, modified, skipped, failed)
  - Source preservation / backup confirmation
  - Read-back verification (version, SHA-256, permissions)
  - Explicit exclusion of `.git` and credential-bearing files.

### 2. Versioned Manifest Architecture, Schema, and Layered Profiles

Intent manifests are kept separate from observed runtime inventory:
- **JSON Schema**: Defined at `config/workstation-manifest.schema.json` within `openspec-store`.
- **Canonical Manifest**: Defined at `config/workstation-toolchain-manifest.json` declaring tools, authoritative installation owners, active path patterns, update authorities, release channels, dispatch classifications (`native`, `delegating`, `none`), and verification smoke commands.
- **Minimal Layered Profiles**: Rather than creating a custom dotfile framework, utilize tool-native manifests:
  - `config/Brewfile`: Declares Homebrew formulae, casks, and taps. Strictly bounded to Homebrew; while Brewfile DSL supports `npm` and `uv` entries, **Homebrew Bundle MUST NOT own npm-global or uv tools** in this workspace to prevent dual-writer collisions and maintain stage-specific pause controls.
  - `config/npm-global-tools.json`: Declares global npm packages installed under declared `~/.npm-global`.
  - `config/uv-tools.json`: Declares uv-managed CLI tools (`uv tool install`).
  - Optional capability profiles: `profile: db-tools` (psql, redis-cli), `profile: rust-dev` (rustup, cargo), evaluated on demand rather than globally mandated.
- **Projections**: Manifests in the store are the single source of truth. Rendered launchd plists, shell PATH snippets, Notion mirror pages, and AgentMemory decision entries are generated, sanitized projections.

### 3. launchd Template Variable Rendering at Bootstrap Time

Apple launchd plists do NOT evaluate `$HOME`, `~`, or environment variables in string configuration keys (`ProgramArguments`, `WorkingDirectory`, `StandardOutPath`, `StandardErrorPath`).
- Templates in `config/launchd/*.plist.tmpl` SHALL define registered substitution variables:
  - `{{HOME}}`: Target user's home directory
  - `{{HOMEBREW_PREFIX}}`: Detected Homebrew prefix (`/opt/homebrew` or `/usr/local`)
  - `{{WORKSPACE_ROOT}}`: Workspace root (`{{HOME}}/Developer`)
  - `{{OPENSPEC_STORE_ROOT}}`: Canonical store path (`{{WORKSPACE_ROOT}}/platform/openspec-store`)
- The bootstrap engine renders these templates into concrete absolute paths at target bootstrap time, verifying that no unresolved placeholders remain before installation into `~/Library/LaunchAgents/`.

### 4. Official Distribution Decisions & Ownership Matrix for Colliding Tools

Based on official vendor documentation and repository architecture:
- **Codex**:
  - Official documentation (`https://learn.chatgpt.com/docs/codex/cli`, `https://learn.chatgpt.com/docs/developer-commands?surface=cli`, repo `https://github.com/openai/codex`) catalogs all commands and establishes that **no documented native `codex update` CLI verb exists**. npm-installed binaries explicitly reject self-update (issue #24035: `"refuse self-update this install should be updated through npm"`).
  - Registry & Runner Correction: `toolchain_updater_registry.py` (line 48) and `workstation-daily-update.sh` (line 192) erroneously declare `codex update`. This must be corrected to explicit npm authority: `npm --prefix ~/.npm-global install --global @openai/codex@<target>` (or Stage 3 filtered npm updates).
  - Decision: Assign `codex` to **npm-global** under `~/.npm-global`. Standalone binaries and Homebrew casks MUST NOT coexist.
- **Qoder**:
  - Official documentation (`https://docs.qoder.com/cli/quickstart`, `https://docs.qoder.com/cli/installation`) defines standalone distribution with `~/.local/bin/qodercli` and dispatcher `~/.qoder/entry`, supporting native `qoder update`. Vendor installation docs explicitly state that npm package `@qoder-ai/qodercli` is *"not recommended for new installations / retained for compatibility"*.
  - Decision: Assign `qoder` to **Standalone Vendor** dispatcher. The `qoder` wrapper routing to `~/.qoder/entry` is vendor-supported and retained. The shadowing npm-global package `qodercli` and third-party Homebrew casks MUST NOT coexist and are staged for removal.
- **GitNexus**:
  - Official distribution (`https://www.npmjs.com/package/gitnexus`, `https://github.com/abhigyanpatwari/GitNexus`) is npm-global (`npm install -g gitnexus`). There is no official Homebrew formula. Native dependencies include `@ladybugdb/core` and `tree-sitter`. Upstream docs specifically recommend global npm installation (`npm i -g gitnexus`) to establish deterministic binary paths and eliminate `npx` cold-cache timeout risks (>30s) in agent MCP servers.
  - Decision: Assign `gitnexus` to **npm-global** under `~/.npm-global`. Migration from the isolated toolchain (`~/.local/share/home-toolchain`) or local symlinks occurs ONLY after native binding compilation and MCP server smoke tests (`mcp-router` tool invocation) pass. Pre-existing overrides are evaluated with evidence, not discarded blindly.
- **Prime Agent**:
  - Local development exception. Upstream `origin/main` on `PrimeIntellect-ai/prime-agent` completed a total rewrite to Rust and deleted `package.json`. The local installation links TypeScript packages from `platform/prime-agent/packages/coding-agent` to `/opt/homebrew/lib/node_modules/prime-agent`. It is decoupled from upstream and excluded from automated package manager updates.
- **Update Registry Contracts**: Each tool declaration in `toolchain_updater_registry.py` must explicitly record the writer binary, dispatch mode (`native`, `delegating`, `none`), and supported verb.

### 5. Idempotent Apply Plan & Staged Mutation with Native Smoke Pre/Post

The implementation plan supports actual idempotent application and tool installation capability rather than dry-run only:
1. **Inspection & Preflight**: Gather active resolution, package manager receipts, running process PIDs, and disk usage.
2. **Native Smoke Pre-Check**: Run `<tool> --version`, `<tool> help`, or MCP status for each candidate.
3. **Normalization & Duplicate Removal**: Authorize duplicate removal ONLY when all five gates pass:
   - *Reference Check*: No script, wrapper, or LaunchAgent references the target path.
   - *Process Check*: No running process (`lsof`, `fuser`, or `pgrep`) holds open handles to the binary.
   - *Manifest Reconciliation*: The retained alternative path is declared authoritative in the manifest.
   - *Dependency Check*: Shared libraries, node_modules, and virtualenvs remain functional.
   - *External Approval*: User has approved the exact file path removal.
4. **Targeted Upgrades**: Execute updates against specific package targets and versions. Verify that exit code 0 reflects actual version progression; recognize `already_target` as valid when active readback matches target version and smoke checks pass.
5. **Native Smoke Post-Check**: Re-run tool-specific verification to validate post-mutation operation.
6. **Rollback & Quarantine**: If smoke fails, execute immediate rollback from captured backup, restore the previous executable, and quarantine the failed package.

### 6. Measurable Shell Startup Optimization & Protected Dotfiles

Shell latency reduction must be measured and reproducible:
- **Benchmarking**: Measure startup times with component-level profiling (`zsh/zprof` or high-resolution loop). Record repeated cold (un-cached completion) and warm medians across N runs (e.g. 5 runs each), reporting median and variance rather than arbitrary promised targets.
- **Runtime Architecture**: Choose system Homebrew `node` as the primary development runtime. Defer expensive NVM or versioned manager sourcing via lazy shims only for repositories requiring legacy Node versions.
- **Completion Caching**: Cache `compinit` completion dumps (e.g. `.zcompdump`) with daily invalidation checks rather than auditing completions on every shell spawn.
- **Protected `.zshenv`**: Secret-bearing `.zshenv` contains sensitive API keys and tokens. It SHALL NOT be tracked in version control, scanned for plaintext values, or modified by bootstrap templates. PATH variables are centralized in `.zprofile` / `.zshrc`.

### 7. Docker Volume Hygiene & Persistent Data Protection

Persistent database and stateful services must be protected from routine cleanup:
- **Docker Command Semantics**:
  - `docker system prune --volumes` and `docker compose down -v` destroy unused named volumes.
  - Safe storage hygiene (`docker-disk-guard.sh --prune`) executes `docker system prune` without `--volumes` or `--all`, preserving named volumes and cache layers.
  - Generic broad prunes (`docker system prune -a --volumes -f`) are strictly prohibited in automated and routine workflows.
- **Protected Volume Inventory**: Maintain an explicit allowlist of persistent named volumes:
  - `omniroute_data`: SQLite WAL database for OmniRoute routing and proxy configuration.
  - Microservices PostgreSQL, Temporal, Kafka, and Redis volumes.
- **Cleanup Gates**: Any command affecting volumes requires explicit volume identity inspection and confirmation that no protected volume is targeted.

### 8. AgentMemory Health Restoration, Version Alignment & Bounded Watchdog

AgentMemory operational stability is restored via evidence-backed service management:
- **Health Verification**: Check health via HTTP GET `/agentmemory/health` on port 3111 (not root `/` which returns 404).
- **Version Alignment**: Verify that the installed `agentmemory` package (0.9.30) aligns with pinned `iii-engine` (0.22.1). Read version from package metadata rather than assuming the current version.
- **Port & Process Conflicts**: If an incompatible engine process claims port 49134, or the AgentMemory API port 3111 is occupied by an unexpected process, record the foreign PID and process details in a quarantine report. DO NOT terminate arbitrary PIDs.
- **Bounded Watchdog**: Configure LaunchAgent watchdog (`com.agentmemory.server.plist`) with `ThrottleInterval` (for example, 30 seconds) and `KeepAlive` with `SuccessfulExit: false` to prevent unbounded restart loops.
- **Idempotent Decision Seeding**: Restore service health and seed approved toolchain decisions idempotently into AgentMemory via REST API (`/agentmemory/observations`), avoiding direct SQLite WAL database manipulation.

### 9. Fail-Closed, Write-Receipt Gated Notion Knowledge Synchronization

`sync-notion-knowledge.sh` provides public documentation mirroring with strict security controls:
- **Dynamic Home Directory Redaction**: Dynamic regex `s#/Users/[^/]+/#~/#g` replaces any username prefix with `~/` or `~/Developer/`.
- **Explicit Disclosure Allowlist**: Restrict synchronized sections to explicitly allowlisted topics: `concepts`, `entities`, `specs`, `freshness`, and `onboarding-runbook`.
- **Fail-Closed Residual Scan**: Scan rendered Markdown payloads for lingering credential patterns (`sk-*`, `ghp_*`, `AKIA*`, bearer tokens, private keys) before transmission, aborting upload on detection.
- **Write-Receipt Gating**: Require a validated Notion API write receipt (valid JSON containing page ID and exit 0) before advancing the document SHA-256 in `MANIFEST_FILE`. Swallowed errors (`|| true`) SHALL NOT update the manifest.
- **Offline Retry**: Offline or failed sync runs leave `MANIFEST_FILE` unchanged, allowing automatic incremental retry on the next execution.
- **Environment-Supplied Identifiers**: Parameterize `KNOWLEDGE_ROOT_ID` and section page IDs via environment variables or configuration profiles; remove hardcoded workspace IDs and tokens from script bodies.
- **Strict Read-Only `--dry-run`**: When `--dry-run` is active, the script SHALL NOT touch log files, create missing directories, or mutate manifest section mappings during discovery.

### 10. Retention and Removal Decision Table with Concrete Candidates

The toolchain review establishes explicit classifications for installed components:

| Candidate | Current Resolution | Action Classification | Rationale & Evidence | Gated Pre-Conditions |
|---|---|---|---|---|
| `codex` | `~/.npm-global/bin/codex` (active), standalone copy | Normalize / Retain npm-global | OpenAI documentation supports npm-global; single active owner avoids updater conflicts. | Verify npm executable resolution; remove standalone copy only after reference check. |
| `qoder` | `~/.local/bin/qodercli` + dispatcher, npm shadow | Normalize / Retain Standalone | Vendor quick-start specifies standalone installer with dispatcher; npm bundle is a shadowing duplicate. | Verify `~/.qoder/entry` dispatcher; remove npm package after reference/process checks. |
| `gitnexus` | `~/.local/share/home-toolchain/bin/gitnexus` | Normalize / Retain npm-global | Vendor README specifies npm-global install; no official Homebrew cask. | Native binding compilation and MCP smoke test must pass before cutover. |
| `newman` | `~/.local/share/home-toolchain/bin/newman` | Retain (Isolated Toolchain) | Pinned to 6.2.2 with `newman-reporter-htmlextra` for Postman collection execution and Faker v5 compatibility. | Keep isolated toolchain lockfile intact; do not force global migration. |
| `bruno` | `~/.local/share/home-toolchain/bin/bru` | Targeted Upgrade Candidate | Registry reports 4.2.0 active, 4.2.1 available upstream; targeted minor patch. | Pre-upgrade smoke on collection run; post-upgrade verification of `bru --version`. |
| `opencode` | `/opt/homebrew/bin/opencode` (brew), npm duplicate | Retain Homebrew / Prune npm | Formula is active and maintained; npm package is a duplicate install. | Verify Homebrew resolution; prune npm copy after five-point check. |
| `prime-agent` | `/opt/homebrew/lib/node_modules/prime-agent` | Retain Local Development | Upstream Rust divergence on `origin/main`; keep local TypeScript build linked. | Exclude from automated update runner; maintain local symlink. |
| Python 3.10 | `/opt/homebrew/opt/python@3.10` | Manual Review Candidate | Formula deprecated in Homebrew; check if any active service or virtualenv depends on it. | Audit virtualenv dependencies before proposing formula uninstallation. |
| Ollama | Port 11434 collision (background service vs runner) | Manual Review Candidate | Competing background service claims default port; verify if external GPU daemon or Docker runner is primary. | Report port collision in quarantine report; do not stop service automatically. |

## Risks / Trade-offs

- **External Gate Friction**: Requiring explicit execution packets and approvals for external mutations prevents accidental damage, but requires deliberate operator handoffs between central planning and host execution.
- **Template Rendering Overhead**: Rendering launchd plists requires a bootstrap execution step before launchctl registration, but eliminates host-specific hardcoded path failures across different macOS accounts.
- **Lazy Shell Runtime Trade-off**: Deferring NVM initialization is expected to reduce startup cost, but the benefit SHALL be measured on the target workstation rather than assumed. Legacy Node projects must still trigger lazy loading hooks or use explicit paths.
- **Isolated Toolchain Decoupling**: Preserving Newman in `~/.local/share/home-toolchain` isolates legacy Postman dependencies from global npm packages, requiring separate maintenance tracking.
- **Notion Sync Network Dependency**: Enforcing write receipts and fail-closed validation requires active internet connectivity for state advancement, but completely eliminates silent drift and false-green status pages.
