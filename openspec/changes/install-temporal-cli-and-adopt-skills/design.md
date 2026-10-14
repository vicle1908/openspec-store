# Design: install-temporal-cli-and-adopt-skills

## Context

The Go microservices platform (Temporal 1.31.2) and SHB enterprise workflow modernization require reproducible inner-loop development, deterministic replay verification, and cluster operational diagnostics. Previously, workstation parity relied on ad hoc setups, and agent runtimes lacked upstream Temporal developer guidance. See `proposal.md` for full motivation.

## Goals / Non-Goals

**Goals:**
- Provide official Temporal CLI v1.9.1 via Homebrew in `/opt/homebrew/bin/temporal` with shell completions.
- Adopt upstream `temporalio/skill-temporal-developer` and `temporalio/skill-temporal-ops` into the canonical workspace skills root (`~/Developer/.agents/skills/`).
- Reconcile multi-agent discovery via `sync-workspace-agent-skills.py` with zero malformed entries.
- Maintain strict compliance with OpenSpec capability formatting and strict validation gates.

**Non-Goals:**
- Deploying persistent background Temporal server daemons to macOS launchd or system services.
- Modifying microservices Go code or Temporal SDK dependencies.
- Forking, renaming, or locally patching official Temporal skills source files.

## Decisions

- **Decision 1: Homebrew installation over manual curl archive**: Homebrew bottles for macOS arm64 provide clean uninstallation, automated zsh completions at `/opt/homebrew/share/zsh/site-functions`, and standard placement under `/opt/homebrew/bin/temporal` (which is already present in user PATH across all subshells).
- **Decision 2: Direct workspace skill mirroring via npx skills**: Adopting skills with `npx skills add temporalio/skill-<name>` places canonical directories in `~/Developer/.agents/skills/` and creates universal agent symlinks, ensuring instant propagation to Claude Code, Codex, Cursor, and Hermes without duplication.
- **Decision 3: Non-normative companion separation**: Workspace-specific banking compliance and saga compensation routines remain separate companion skills, leaving the upstream `temporal-developer` and `temporal-ops` vendor tiers unmutated.

## Risks / Trade-offs

- **[Risk: Local port collisions when running start-dev]** → *Mitigation*: Default dev server uses 7233 and UI on 8233, configurable via `--port` and `--ui-port` if Docker Compose Temporal is active.
- **[Risk: Skill entry case-sensitivity on macOS APFS]** → *Mitigation*: `sync-workspace-agent-skills.py --check` enforces canonical uppercase `SKILL.md` and detects any hidden plugin containers.
- **[Risk: Stale skill cache across agent sessions]** → *Mitigation*: Running the workspace sync dispatcher re-links user-level agent roots atomically.
