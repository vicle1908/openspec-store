# Proposal

## Why

The development Mac has multiple active installation roots and conflicting update authorities: Homebrew, npm-global, isolated Node tooling (`~/.local/share/home-toolchain`), `~/.local`, and local development bundles resolve different copies of the same CLIs. This causes stale shadowed executables, PATH precedence drift between interactive shells and scheduled runners, slow shell startup from eager completion and runtime initialization, unsafe cleanup paths that risk persistent named volumes, and a configuration that cannot be reproduced reliably on another Mac.

The inventory also identified deprecated and orphaned Homebrew entries, an Ollama service collision on the default development port, hardcoded user paths (`/Users/androidteam`), and AgentMemory/`iii-engine` runtime generation drift. A declarative ownership, bootstrap, and verification contract is required before targeted upgrades, deduplications, or removals can be executed safely under explicit gates.

## What Changes

- **Central Store Authoring Boundary**: Define the canonical authoring and schema home within `platform/openspec-store` (`scripts/`, `config/`, `docs/`, `openspec/changes/portable-mac-development-workstation/`). Central `/opsx:apply` `allowedEditRoots` strictly covers `openspec-store` only.
- **External Execution and Evidence Gates**: Model all external filesystem mutations—including deployment mirrors (`~/Developer/scripts/`), user shell profiles (`~/.zshrc`, `~/.zshenv`), LaunchAgents (`~/Library/LaunchAgents/`), global package directories (`~/.npm-global`, `/opt/homebrew`, `~/.local/share/home-toolchain`), and remote services (Notion via `ntn`, AgentMemory REST API)—as strictly gated external operations requiring separate exact-root scope authorization and complete External Execution Packets (exact root, immutable source commit, bounded command, timestamps, exit code, counts, source preservation, collision checks, read-back verification, and manifest/evidence hashes).
- **Declarative Manifests & Layered Profiles**: Introduce a versioned workstation manifest format backed by JSON Schema (`config/workstation-manifest.schema.json` and `config/workstation-toolchain-manifest.json`) in the store, complemented by minimal, tool-native layered profiles:
  - `config/Brewfile` for Homebrew formulae, casks, and taps.
  - `config/npm-global-tools.json` for npm-global CLI tools.
  - `config/uv-tools.json` for uv-managed Python tools.
  - Optional capability profiles (`profile: db-tools` for psql/redis-cli, `profile: rust-dev` for rustup/cargo) rather than mandating unnecessary developer tool additions across all machines.
- **Single Source of Truth vs Generated Projections**: Establish versioned intent manifests in `openspec-store` as the sole source of truth; all launchd plists, shell PATH snippets, Notion runbook mirrors, and AgentMemory decision entries are generated, sanitized projections.
- **Portable Bootstrap & launchd Rendering**: Implement a bootstrap and verification engine that discovers macOS architecture (`arm64` vs `x86_64`), Homebrew prefix (`/opt/homebrew` vs `/usr/local`), and `$HOME`, rendering concrete absolute paths into LaunchAgent plist templates at bootstrap time (because launchd does not expand `$HOME` or `~` in path keys).
- **Single PATH Precedence Policy & Protected Dotfiles**: Align interactive zsh startup (`~/.zshrc`) and scheduled maintenance runners (`workstation-daily-update.sh`) to one documented PATH precedence order. Protect secret-bearing `.zshenv` from version-control tracking, text logging, or modification.
- **Official Distribution Decisions & Ownership Matrix**: Establish one authoritative installation owner and update authority per CLI:
  - **Codex**: Declared npm-global owner (`npm install -g @openai/codex` in `~/.npm-global`), updated only through explicit npm authority (`npm --prefix ~/.npm-global install --global @openai/codex@<target>`). Standalone binary and Homebrew copies SHALL NOT coexist.
  - **Qoder**: Official standalone vendor distribution owning `~/.local/bin/qodercli` and `~/.qoder/entry` dispatcher (`https://docs.qoder.com/cli/quick-start`). The `qoder` wrapper routing to `~/.qoder/entry` is vendor-supported and retained. npm-global (`qodercli`) and Homebrew copies SHALL NOT coexist; shadow copies removed after reference verification.
  - **GitNexus**: Official npm-global owner (`npm install -g gitnexus`). Migrate from isolated `~/.local/share/home-toolchain` or local symlinks to npm-global ONLY after the lockfile-declared native dependencies compile and MCP smoke tests pass; existing overrides evaluated with evidence, not dropped blindly.
  - **Prime Agent**: Local development exception; keep local TypeScript packages linked to `/opt/homebrew/lib/node_modules/prime-agent` decoupled from upstream `origin/main` Rust rewrite.
- **Idempotent Apply Plan & Staged Mutation**: Define a phased mutation workflow with pre- and post-mutation native smoke checks (`<tool> --version`, `<tool> help`, MCP ping). Authorize duplicate removal only after a five-point check: (1) reference check, (2) running process check, (3) manifest reconciliation, (4) dependency integrity check, and (5) explicit external gate approval. Updater executions that exit zero without reaching target version are flagged as failures; `already_target` is recognized as valid when confirmed by active readback and smoke.
- **Shell Performance Profiling**: Benchmark shell startup using component-level timing, measuring repeated cold and warm medians with variance reporting (avoiding unverified fixed performance targets). Select Homebrew current `node` as default system runtime, with optional versioned runtime profiles (NVM) lazy-loaded on demand for legacy projects without introducing another unmanaged tool manager.
- **Docker Volume Hygiene & Protected State**: Confirm exact Docker `--volumes` semantics: `docker system prune --volumes` and `docker compose down -v` remove unused named volumes, whereas safe volume-preserving prunes (`docker-disk-guard.sh --prune`) omit `--volumes` and `--all`. Prohibit generic broad prunes (`docker system prune -a --volumes -f`); maintain an explicit protected volume inventory (e.g. OmniRoute's named SQLite volume `omniroute_data`, PostgreSQL database volumes) with restore scopes.
- **AgentMemory Health Restoration & Bounded Watchdog**: Check health via HTTP GET `/agentmemory/health` on port 3111 (not root `/` which returns 404). Verify pinned engine version against installed package metadata (`agentmemory` 0.9.30 pinning `iii-engine` 0.22.1). Incompatible engine ports and foreign PIDs are quarantined in reports rather than killed arbitrarily. Configure LaunchAgent watchdog with bounded restart limits to prevent spin loops. Idempotently restore service health and seed approved toolchain decisions without raw SQLite WAL database mutation or manual DB migration.
- **Fail-Closed Notion Knowledge Synchronization**: Enhance `sync-notion-knowledge.sh` with dynamic home directory redaction regex (`/Users/*/<path>` to `~/<path>` or `~/Developer/<path>`), an explicit disclosure allowlist, and a fail-closed residual token scanner. Require valid Notion API write receipts before updating document SHA-256 hashes in `MANIFEST_FILE`. Unchanged manifests ensure offline retry without dropping state. Root and section IDs are supplied via environment/configuration profiles rather than hardcoded secrets. Enforce that `--dry-run` is genuinely read-only (no log file touching, no manifest creation or section discovery mutation).

## Capabilities

### New Capabilities

- `portable-workstation-toolchain` - Declarative ownership, bootstrap, verification, and portability behavior for macOS development tooling.

### Preserved Existing Capability Contracts

This change integrates with and preserves the behavior of existing main specifications without altering specs outside the change frontier:

- `openspec/specs/workstation-toolchain-inventory/spec.md`: Preserves sanctioned install locations (`~/.npm-global`, `~/.local/share/home-toolchain`, system package managers), the singular authoritative npm global prefix, preferred package manager sources, and read-only duplication reporting before any copy is reclaimable.
- `openspec/specs/agent-cli-inventory-coverage/spec.md`: Preserves reconciliation between declared covered agent CLIs and installed CLIs, explicit covered/uncovered status, and the invariant that undeclared tools are never silently removed or updated.
- `openspec/specs/workstation-storage-hygiene/spec.md`: Preserves safety-gated storage cleanup, classification of candidates, protection of stateful volumes, and the requirement that duplication is handled via owning tool commands rather than raw filesystem deletion.
- `openspec/specs/notion-knowledge-sync/spec.md`: Preserves fail-closed credential/path sanitization, idempotent SHA-256 tracking, and error handling.
- `openspec/specs/secrets/spec.md` & `openspec/specs/coding-agent-credential-loading/spec.md`: Preserves fail-closed secret exclusion, ensuring no credentials or signed-in states are committed to git or included in portable manifests.
- `openspec/specs/memory-core/spec.md` & `openspec/specs/agentmemory-provider-stability/spec.md`: Preserves structured memory contracts, valid LLM endpoint/model requirements (`OPENAI_BASE_URL=http://localhost:20128/v1`), and provider stability.

## Non-Goals

- No automatic package upgrades, removals, Homebrew cleanup, service restarts, or shell configuration changes are authorized by this planning change. User approval for planning does NOT constitute authorization for external machine mutations.
- No migration of credentials, signed-in CLI state, private keys, Docker volumes, or raw AgentMemory SQLite databases to another Mac.
- No replacement of OpenSpec, Homebrew, npm, uv, Docker Desktop, or the existing `ntn` synchronization mechanism.
- No creation of a sprawling custom dotfile framework or configuration daemon.
- No broad, generic, or un-gated filesystem deletion.
- No direct implementation in repositories outside the selected workstation automation ownership boundary.

## Multi-Root Governance & External Execution Gates

Workstation automation spans central planning and external host roots. The boundaries are defined as follows:

1. **Central Store Authoring Boundary**: `/Users/androidteam/Developer/platform/openspec-store`. All schemas, manifest templates, migration plans, verification scripts, and documentation are authored and maintained here under version control.
2. **External Execution Roots**:
   - Deployed automation mirror: `/Users/androidteam/Developer/scripts/`
   - User shell configuration: `~/.zshrc`, `~/.zshenv`
   - LaunchAgent descriptors: `~/Library/LaunchAgents/`
   - Package manager roots: `/opt/homebrew`, `~/.npm-global`, `~/.local/share/home-toolchain`, `~/.local/bin`
   - Remote / background services: Notion via `ntn`, AgentMemory REST API (`http://localhost:3111`)
3. **External Execution Packet Contract**: Any mutation targeting external roots requires an explicit external execution packet containing:
   - Exact target root and destination path
   - Immutable source commit hash and script identity
   - Bounded execution command and parameter scope
   - Timestamps and execution duration
   - Process exit status and standard error captures
   - Item counts (processed, modified, skipped, failed)
   - Source-preservation result (backup copy or rollback path)
   - Collision and error detection result
   - Destination read-back verification result (version, hash, file mode)
   - Manifest and evidence SHA-256 digests
   - Explicit exclusions for `.git`, credential-bearing paths, and destructive deletions unless authorized by exact path.

## Official Distribution Decisions & Ownership Matrix

Official vendor guidance and repository evidence establish the following authoritative ownership assignments:

| Tool | Authoritative Installation Owner | Active Path Pattern | Update Authority | Release Channel | Dispatch Mode | Verification Smoke Command | Status / Caveat Notes |
|---|---|---|---|---|---|---|---|
| `claude` | Vendor Standalone | `~/.local/bin/claude` | Native CLI | stable | native | `claude --version` | Official standalone binary with native auto-updater. |
| `codex` | npm-global | `~/.npm-global/bin/codex` | npm authority | latest | delegating | `codex --version` | Global npm package `@openai/codex`. No documented native `codex update` verb exists; npm installs reject self-update (issue #24035). Updated via `npm --prefix ~/.npm-global install --global @openai/codex@<target>` (or Stage 3 filtered npm update). Standalone binary and Homebrew copies MUST NOT coexist. |
| `qoder` | Standalone Vendor | `~/.local/bin/qodercli` | Vendor Dispatcher (`~/.qoder/entry`) | stable | native | `qoder --version` | Standalone installer with `~/.qoder/entry` dispatcher and `qoder update` native verb. Vendor docs note npm package `@qoder-ai/qodercli` is not recommended for new installs. Vendor-supported `qoder` wrapper retained. npm `qodercli` shadow removed after check. |
| `gitnexus` | npm-global | `~/.npm-global/bin/gitnexus` | npm authority | latest | delegating | `gitnexus --version && gitnexus status` | Migrated from `~/.local/share/home-toolchain` only after native binding (`@ladybugdb/core`) and MCP smoke tests pass. Eliminates cold `npx` timeout risks (>30s) in agent MCP servers. |
| `pi` | Vendor Standalone | `~/.pi/agent/bin/pi` | Native CLI (`pi update --self`) | stable | native | `pi --version` | Managed standalone runtime prepended to PATH. |
| `auggie` | npm-global | `~/.npm-global/bin/auggie` | Native CLI | latest | native | `auggie --version` | Native CLI updater with non-interactive confirmation skip. |
| `opencode` | Homebrew Formula | `/opt/homebrew/bin/opencode` | Homebrew | stable | delegating | `opencode --version` | Delegated to `brew upgrade opencode`. npm duplicate removed after verification. |
| `prime-agent` | Local Development Node Module | `/opt/homebrew/lib/node_modules/prime-agent` | Manual Workspace Build | local-dev | none | `prime-agent --version` | Symlinked to `platform/prime-agent/packages/coding-agent`. Decoupled from upstream Rust rewrite on `origin/main`. |
| `newman` | Isolated JS Toolchain | `~/.local/share/home-toolchain/bin/newman` | npm in isolated root | 6.2.2 | delegating | `newman --version` | Pinned with `newman-reporter-htmlextra` (1.23.1) and Faker v5 compatibility for Postman collection execution. |
| `bruno` | Isolated JS Toolchain | `~/.local/share/home-toolchain/bin/bru` | npm in isolated root | 4.2.1 | delegating | `bru --version` | Targeted patch candidate to resolve 4.2.0 vs 4.2.1 registry drift. |
| `uv` | System Homebrew / Standalone | `/opt/homebrew/bin/uv` | Homebrew | stable | delegating | `uv --version` | Manages Python environments and tools (`uv tool`). |
| `bun` | Standalone Vendor | `~/.bun/bin/bun` | Native CLI (`bun upgrade`) | stable | native | `bun --version` | Fast JS/TS runtime and package manager. |
| `docker` | Docker Desktop / CLI | `/opt/homebrew/bin/docker` | Docker Desktop | stable | delegating | `docker --version && docker compose version` | Managed via official Docker Desktop plugin lifecycle (`docker-service.sh`). |

## Research Basis

- **OpenAI Codex CLI**: `https://developers.openai.com/codex/cli/` and `https://github.com/openai/codex` (verified npm-global and standalone binary distribution methods; channel-sensitive updater behavior).
- **Qoder CLI**: `https://docs.qoder.com/cli/quick-start` and `https://docs.qoder.com/cli/installation` (verified standalone dispatcher architecture at `~/.qoder/entry` and binary at `~/.local/bin/qodercli`).
- **GitNexus**: `https://www.npmjs.com/package/gitnexus` and `https://github.com/abhigyanpatwari/GitNexus` (verified official npm-global packaging and native binding dependencies; absence of official Homebrew formula).
- **Homebrew Bundle & Brewfile**: `https://docs.brew.sh/Brew-Bundle-and-Brewfile` (verified Brewfile DSL for formulae, casks, and taps; confirmed exclusion of vendor-managed standalone and npm-global CLIs).
- **launchd Architecture & Path Expansion**: Apple launchd documentation and runtime verification (confirmed that launchd plists do not expand `$HOME`, `~`, or environment variables in `ProgramArguments`, `StandardOutPath`, or `StandardErrorPath`, necessitating template rendering at bootstrap time).
- **Docker Volume Hygiene**: Docker CLI engine reference (confirmed that `docker system prune --volumes` and `docker compose down -v` prune unused named volumes, whereas volume-preserving prunes require omitting `--volumes` and `--all`).
- **AgentMemory Runtime**: `agentmemory` package metadata and local inspection (confirmed `agentmemory` 0.9.30 pins `iii-engine` 0.22.1; health check requires HTTP GET `/agentmemory/health`).
