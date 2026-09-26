# Design: Dev Tooling, CLIs, Applications, and Agent Skills Upgrade

## Architecture & Staged Rollout Overview

Upgrading host-level developer infrastructure and establishing reliable daily maintenance requires isolating failure domains and eliminating unconstrained package sweeps.

The unified architecture addresses both the immediate ecosystem upgrade and ongoing daily automation:

```
┌────────────────────────────────────────────────────────┐
│ Stage 1: Pre-Upgrade Freeze & Baseline Telemetry       │
│ - Snapshot Homebrew & NPM global packages              │
│ - Run pre-upgrade openspec validate --all --strict     │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│ Stage 2: Applications, Casks & Utility CLIs            │
│ - Upgrade 13 Homebrew casks (Docker, Zed, etc.)        │
│ - Upgrade global npm utilities (BrightData, KiloCode)   │
│ - Align GitNexus to 1.6.12 across prefixes             │
│ - Upgrade graphifyy via uv tool (0.9.65 -> 0.9.68)     │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│ Stage 3: Cross-Agent Skills Parity                     │
│ - Re-generate Graphify platform skills (Pi, OpenCode)  │
│ - Fix sync-workspace-agent-skills.py layout resolution │
│ - Verify sync-workspace-agent-skills.py --check (0)    │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│ Stage 4: Coding Agent CLIs & Extensions                │
│ - claude update (2.1.283)                              │
│ - npm upgrade codex (0.157.0), opencode (1.18.32)      │
│ - npm upgrade pi extensions (subagents, mcp-adapter)   │
│ - Run live headless PONG verification probes           │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│ Stage 5: OpenSpec CLI Upgrade & Store Validation Gate   │
│ - npm upgrade @fission-ai/openspec (1.11.0 -> 1.13.2)  │
│ - Run post-upgrade openspec validate --all --strict    │
│ - Verify zero regression delta against Stage 1         │
└──────────────────────────┬─────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────┐
│ Stage 6: Unified Daily Scheduled Automation            │
│ - Retire com.user.brew-npm-update and com.microservices│
│ - Deploy unified ~/Developer/scripts/workstation-daily-update.sh │
│ - Filter npm updates to exclude local git packages     │
│ - Register com.developer.workstation-daily-update      │
│   (08:00 AM daily, supports --check and --apply)       │
└────────────────────────────────────────────────────────┘
```

## Daily Automation Design: Eliminating Failure Points

### 1. Root Cause Resolution for `prime-agent` 404
- **Problem:** Running unconstrained `npm update -g` attempts to resolve `prime-agent` on `registry.npmjs.org`, where it does not exist because it was built from a local git repository. This crashed both historical daily LaunchAgents.
- **Solution:** `workstation-daily-update.sh` explicitly queries registry-backed packages and filters out `prime-agent` or other local/private builds before invoking `npm update -g <package>`.

### 2. Consolidated Scheduler Ownership
- **Problem:** Two separate LaunchAgents ran daily 37 minutes apart (`08:23 AM` and `09:00 AM`) with overlapping responsibilities and disparate logging.
- **Solution:** Unload both legacy plists and register a single LaunchAgent:
  - Label: `com.developer.workstation-daily-update`
  - Schedule: Daily at `08:00 AM`
  - Logs: `~/Library/Logs/workstation-daily-update.log`
  - Modes:
    - `--check`: Probes for outdated packages across all 7 layers and outputs a machine-readable summary.
    - `--apply`: Executes safe updates, updates agent CLIs, regenerates skills, and validates the OpenSpec store.

## Risk Stratification & Mitigation

### 1. Store Integrity Risk (High)
- Pre- and post-flight strict validation runs against all 400 specs ensure OpenSpec CLI 1.13.2 introduces no rule regressions.

### 2. Provider Routing Breakage (Medium)
- Live headless probes verify custom model launchers (`_claude_model_default` in `~/.zshrc`) continue passing CLI arguments after updates.

### 3. Container & Docker Daemon Restart (Medium)
- Post-upgrade checks probe Docker socket accessibility (`docker ps`) and verify Kind clusters remain attached.

## Rollback Protocol

If any stage fails verification:
- **Homebrew Casks:** Reinstall pinned versions using Homebrew cached bottles or download previous DMG releases.
- **NPM Global Packages:** Re-install explicit prior versions recorded in the Stage 1 snapshot manifest:
  `npm install -g <package>@<pinned-version> --prefix ~/.npm-global`
- **OpenSpec CLI:** Roll back to `1.11.0` via:
  `npm install -g @fission-ai/openspec@1.11.0 --prefix ~/.npm-global`
- **Agent Skills:** Revert manifest file changes in `openspec-store/config/` via `git checkout`.
- **Scheduled Updates:** Unload `com.developer.workstation-daily-update` via `launchctl unload`.
