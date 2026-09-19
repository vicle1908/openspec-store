# Design: Workstation Health and Tooling Maintenance

## Context

macOS developer workstations host heterogeneous toolchains (Node/npm, Bun, Homebrew, Python, Go, Docker, OrbStack) alongside background orchestration agents (OMP, Claude Code, Hermes, Orca) and remote access services (Apple Remote Desktop, AnyViewer, Cockpit). See `proposal.md` for motivation.

## Goals / Non-Goals

**Goals:**
- Provide a repeatable, verified sequence for upgrading developer package managers and global runtimes.
- Migrate unmanaged applications and scripts into declarative Homebrew casks and formulae.
- Reclaim significant disk headroom (>30 GiB) using a strict three-tier safety classification with explicit user selection gates.
- Remediate crash-looping user LaunchAgents (`com.tdt.webhook-receiver`, `Antigravity Tools`, `com.omniroute.update-check`) non-destructively.
- Preserve all remote access channels and local security forks without disruption.

**Non-Goals:**
- Enabling the macOS Application Firewall without verified remote port rule definitions.
- Automatic merging or rebasing of diverged local security forks (`prime-agent`).
- Touching dataless iCloud trees or linked worktrees (`WHO-project`).

## Decisions

### Decision 1: Declarative Package Management Consolidation
- **Rationale**: Standalone `.app` bundles in `/Applications` and loose shell scripts in `/usr/local/bin` drift from security updates. Migrating applications (`Discord`, `Zalo`, `LarkSuite`, `InstantView`, `Hermes`, `Google Drive`) to Homebrew casks and CLIs (`gitlab-runner`, `fastlane`, `openspec`) to formulae unifies update tracking under `brew upgrade` while preserving existing application data.
- **Alternative Considered**: Leaving unmanaged apps to internal auto-updaters; rejected due to lack of centralized visibility and version tracking.

### Decision 2: Three-Tier Storage Classification with Explicit Execution Gates
- **Rationale**: Accidental deletion of persistent databases or dataless iCloud files causes catastrophic state loss. We partition candidates:
  - **Tier 1 (Safe Ephemeral Caches)**: Inactive RAM purge, Homebrew cache (`~/Library/Caches/Homebrew`), Homebrew temporary staging (`/opt/homebrew/var/homebrew/tmp/.caskroom`), and expired execution caches (`~/.npm/_npx`, `~/.cache/uv`).
  - **Tier 2 (Review-First Build Artifacts & Staging)**: Local SPM build caches (`RealtimeApp/.build`), legacy IDE backups, and completed installer DMGs (`Toolbox/download`). Requires explicit interactive confirmation displaying literal paths and commands.
  - **Tier 3 (Strictly Protected Assets - NEVER Delete)**: Docker raw virtual disk (`Docker.raw`), persistent database volumes (`omniroute_omniroute-data`, `tdt-local-full`), active Google Chrome profile databases, and active virtual environments (`.venv`).
- **Alternative Considered**: Automated unbounded cleanup via system cleaner tools; rejected due to high risk of corrupting Docker volumes and active development stores.

### Decision 3: Non-Destructive Daemon Remediation
- **Rationale**: LaunchAgent exit code 126 on `com.tdt.webhook-receiver` was caused by a missing virtualenv binary (`.venv/bin/uvicorn`). Running `uv sync` in the deployment directory reconstructs the environment exactly from `uv.lock`. LaunchAgent exit code 78 on `Antigravity Tools` was caused by a binary filename discrepancy (`antigravity_tools` vs `antigravity-tools`), resolved cleanly via relative bundle symlink rather than editing signed app packages or plist templates.
- **Alternative Considered**: Deleting or disabling the LaunchAgents; rejected because both services are required components of the local development ecosystem.

### Decision 4: Fail-Closed Security & Remote Connectivity Continuity
- **Rationale**: The macOS Application Firewall is currently disabled (`State = 0`). Turning it on without interactive prompt permissions risks dropping active remote connections (Apple Remote Desktop :3283, AnyViewer :30193, Cockpit :19528). Similarly, `prime-agent` carries 2 local security commits on top of an upstream fork that has advanced 313 commits; auto-rebasing carries high lockfile merge conflict risk and must remain owner-gated.
- **Alternative Considered**: Enabling firewall with automatic rules; rejected due to unacceptable risk of developer lockout.

## Risks / Trade-offs

| Risk | Mitigation |
| :--- | :--- |
| **Remote Access Lockout** | Keep firewall state unchanged; document required port rules before any future toggle. |
| **Diverged Fork Merge Conflicts** | Keep `prime-agent` untouched at current HEAD; document ahead/behind state for repository maintainer review. |
| **Daemon Re-failure** | Verify process survival post-kickstart via `launchctl list` and inspect stdout/stderr logs for clean listener binding. |
| **Dataless File Eviction / Hydration Deadlocks** | Exclude all iCloud Drive trees (`com~apple~CloudDocs`) from recursive cleanup or file-content read scans. |
